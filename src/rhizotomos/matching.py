"""Stage B: the model compares each ancient statement with the modern flora description, blind.

    python -m rhizotomos.matching show PASS N   print batch N of pairs to judge (PASS is "ai" or "expert")
    python -m rhizotomos.matching check PASS    check the call files in data/llm/matching/PASS/

Pass "ai" uses our reading (data/llm/reading) and pass "expert" the experts' reading (Data file 3). Candidates
appear only as anonymous labels in a shuffled order, so the person or model making the calls sees neither their
names nor the experts' calls (Data file 9). The calls follow prompts/matching.md and were made by Claude
(Opus 5.5) inside a Claude Code session, pass "ai" first.
"""

import hashlib
import json
import random
import sys
from pathlib import Path

from rhizotomos.benchmark import CATEGORIES, CHARACTERS
from rhizotomos.reading import load_readings

ROOT = Path(__file__).resolve().parents[2]
BENCHMARK = ROOT / "data/derived/benchmark.json"
MATCH_DIR = ROOT / "data/llm/matching"
PLANTS_PER_BATCH = 10
CALLS = {"g": "good", "p": "partial", "n": "no", "a": "absent"}
CATEGORY_OF = {c: cat for cat, chars in CATEGORIES.items() for c in chars}


def load_benchmark():
    return json.loads(BENCHMARK.read_text(encoding="utf-8"))


def plant_ids(benchmark):
    """Stable anonymous ids, in an order that does not follow the alphabet or the book."""
    order = sorted(benchmark, key=lambda p: hashlib.sha1(p["key"].encode()).hexdigest())
    return {p["key"]: f"P{i + 1:02d}" for i, p in enumerate(order)}


def candidate_labels(plant, pid):
    """Shuffled labels for the candidates that the floras describe."""
    found = [c for c in plant["candidates"] if c["in_floras"]]
    random.Random(plant["key"]).shuffle(found)
    return {f"{pid}-C{i + 1}": c for i, c in enumerate(found)}


def ancient_statements(plant, pass_name, readings):
    """{character: text} for one plant, from our reading or the experts'."""
    if pass_name == "ai":
        return {c: v["en"] for c, v in readings[plant["key"]]["characters"].items()}
    return {c: v for c, v in plant["expert_reading"].items() if v is not None}


def to_judge(statements, modern, pass_name):
    """The characters a call is needed for. Pass "ai" compares by category, pass "expert" by character."""
    if pass_name == "ai":
        cats = {CATEGORY_OF[c] for c, v in modern.items() if v}
        return [c for c in CHARACTERS if c in statements and CATEGORY_OF[c] in cats]
    return [c for c in CHARACTERS if c in statements and modern.get(c)]


def items(pass_name):
    """Every plant with its labelled candidates and the characters to judge, in id order."""
    benchmark = load_benchmark()
    readings = {r["key"]: r for r in load_readings()}
    ids = plant_ids(benchmark)
    out = []
    for plant in sorted(benchmark, key=lambda p: ids[p["key"]]):
        pid = ids[plant["key"]]
        statements = ancient_statements(plant, pass_name, readings)
        cands = []
        for label, c in candidate_labels(plant, pid).items():
            modern = {k: v for k, v in c["modern"].items() if v}
            cands.append({"label": label, "candidate": c, "modern": modern,
                          "judge": to_judge(statements, modern, pass_name)})
        out.append({"pid": pid, "plant": plant, "statements": statements, "candidates": cands})
    return out


def by_category(values):
    lines = {}
    for c in CHARACTERS:
        if c in values:
            lines.setdefault(CATEGORY_OF[c], []).append(f"{c}: {values[c]}")
    return lines


def show(pass_name, n):
    batch = items(pass_name)[n * PLANTS_PER_BATCH:(n + 1) * PLANTS_PER_BATCH]
    for it in batch:
        print(f"## {it['pid']}")
        if pass_name == "ai":
            print("ancient:")
            for cat, lines in by_category(it["statements"]).items():
                print(f"  [{cat}] " + " | ".join(lines))
        for cand in it["candidates"]:
            if not cand["judge"]:
                continue
            print(f"{cand['label']}  judge: {', '.join(cand['judge'])}")
            if pass_name == "ai":
                for cat, lines in by_category(cand["modern"]).items():
                    print(f"  [{cat}] " + " | ".join(lines))
            else:
                for c in cand["judge"]:
                    print(f"  {c}: ancient «{it['statements'][c]}»  modern «{cand['modern'][c]}»")
        print()


def load_calls(pass_name):
    out = {}
    for f in sorted((MATCH_DIR / pass_name).glob("*.json")):
        out.update(json.loads(f.read_text(encoding="utf-8")))
    return out


def check(pass_name):
    calls = load_calls(pass_name)
    allowed = set(CALLS) if pass_name == "ai" else {"g", "p", "n"}
    problems, expected, done = [], 0, 0
    for it in items(pass_name):
        for cand in it["candidates"]:
            if not cand["judge"]:
                continue
            expected += len(cand["judge"])
            got = calls.get(cand["label"])
            if got is None:
                continue
            for c in cand["judge"]:
                if got.get(c) not in allowed:
                    problems.append(f"{cand['label']} {c}: {got.get(c)!r}")
                else:
                    done += 1
            problems += [f"{cand['label']} {c}: not asked" for c in got if c not in cand["judge"]]
    print(f"pass {pass_name}: {done}/{expected} calls made")
    for p in problems:
        print("  PROBLEM", p)
    return not problems


def calls_by_candidate(pass_name, calls=None):
    """{(plant key, candidate df_name): {character: good|partial|no|absent}} including automatic absents.
    `calls` replaces the saved calls of the pass, for the baselines."""
    calls = load_calls(pass_name) if calls is None else calls
    out = {}
    for it in items(pass_name):
        for cand in it["candidates"]:
            got = calls.get(cand["label"], {})
            out[(it["plant"]["key"], cand["candidate"]["df_name"])] = {
                c: CALLS[got[c]] if c in got else "absent" for c in it["statements"]}
    return out


if __name__ == "__main__":
    if sys.argv[1] == "show":
        show(sys.argv[2], int(sys.argv[3]))
    else:
        sys.exit(0 if check(sys.argv[2]) else 1)
