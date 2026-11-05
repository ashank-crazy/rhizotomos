"""Stage A: the model's reading of the Greek, checked mechanically.

    python -m rhizotomos.reading show N   print batch N of benchmark chapters for reading
    python -m rhizotomos.reading check    validate every reading file in data/llm/reading/

The readings themselves were produced by Claude (Opus 5.5) inside a Claude Code session, following
prompts/reading.md, because the project had no API budget. They are committed so every later number can be
reproduced without a model. Each value carries a Greek quote that must occur in the chapter.
"""

import json
import re
import sys
import unicodedata
from pathlib import Path

from rhizotomos.benchmark import CHARACTERS, plain_greek

ROOT = Path(__file__).resolve().parents[2]
CHAPTERS = ROOT / "data/derived/dmm_chapters.jsonl"
BENCHMARK = ROOT / "data/derived/benchmark.json"
READING_DIR = ROOT / "data/llm/reading"
BATCH_SIZE = 8
SHOW_LIMIT = 1800
LATE_DETAIL = re.compile(r"φύετ|φύεσθ|γεννᾶτ|γίνετ|εὑρίσκ|ὀσμ|γεῦσ|γεύσ|εὐώδ|ὄζ")


def load_chapters():
    return {json.loads(l)["id"]: json.loads(l) for l in CHAPTERS.open(encoding="utf-8")}


def benchmark_chapters():
    """Benchmark chapters in book order, each with the plant types (Beck names) it must describe."""
    by_chapter = {}
    for p in json.loads(BENCHMARK.read_text(encoding="utf-8")):
        by_chapter.setdefault(p["chapter"], []).append(p["key"])
    order = lambda cid: (int(cid.split(".")[0]), int(re.match(r"\d+", cid.split(".")[1]).group()))
    return sorted(by_chapter.items(), key=lambda kv: order(kv[0]))


def shown_text(text):
    """The description usually comes first and the pharmacology after; long chapters are cut, keeping any later
    sentence about habitat, smell or taste."""
    if len(text) <= SHOW_LIMIT:
        return text
    head, rest = text[:SHOW_LIMIT], text[SHOW_LIMIT:]
    late = [s.strip() for s in re.split(r"(?<=[.·;])\s+", rest) if LATE_DETAIL.search(s)]
    return head + " […] " + " […] ".join(late)


def show(n):
    chapters = load_chapters()
    batch = benchmark_chapters()[n * BATCH_SIZE:(n + 1) * BATCH_SIZE]
    for cid, keys in batch:
        print(f"### {cid}  types: {keys}\n{shown_text(chapters[cid]['text'])}\n")


def quote_found(quote, text):
    """Exact (after Unicode NFC) or, failing that, ignoring accents and breathings."""
    nfc = lambda s: re.sub(r"\s+", " ", unicodedata.normalize("NFC", s)).strip()
    if nfc(quote) in nfc(text):
        return "exact"
    return "accent-insensitive" if plain_greek(nfc(quote)) in plain_greek(nfc(text)) else None


def load_readings():
    out = []
    for f in sorted(READING_DIR.glob("*.json")):
        out += json.loads(f.read_text(encoding="utf-8"))
    return out


def check():
    chapters = load_chapters()
    expected = {k for _, keys in benchmark_chapters() for k in keys}
    readings = load_readings()
    problems, found = [], {"exact": 0, "accent-insensitive": 0}
    for r in readings:
        text = chapters[r["chapter"]]["text"]
        items = list(r.get("characters", {}).items()) + [
            (f"comparison {k}", c) for k, v in r.get("comparisons", {}).items() for c in (v if isinstance(v, list) else [v])]
        for char, v in items:
            if not char.startswith("comparison") and char not in CHARACTERS:
                problems.append(f"{r['key']}: unknown character {char!r}")
            how = quote_found(v["greek"], text)
            if how:
                found[how] += 1
            else:
                problems.append(f"{r['key']}: {char}: quote not in chapter {r['chapter']}: {v['greek']!r}")
    missing = expected - {r["key"] for r in readings}
    print(f"{len(readings)} plant readings ({len(missing)} still to read), quotes: {found}")
    for p in problems:
        print("  PROBLEM", p)
    return not problems


if __name__ == "__main__":
    if sys.argv[1] == "show":
        show(int(sys.argv[2]))
    else:
        sys.exit(0 if check() else 1)
