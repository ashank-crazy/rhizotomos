"""Build the data file of the static explorer in docs/ (GitHub Pages, no server).

    python -m rhizotomos.site    writes docs/data.js from the benchmark, the readings, the calls and the results

Run `python -m rhizotomos.evaluate` first: the explorer shows data/derived/results.json.
"""

import json
import re
import unicodedata
from pathlib import Path

from rhizotomos.benchmark import CATEGORIES, CHARACTERS
from rhizotomos.matching import CATEGORY_OF, calls_by_candidate, load_benchmark
from rhizotomos.reading import load_chapters, load_readings

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "data/derived/results.json"
CONTAMINATION = ROOT / "data/llm/contamination.json"
OUT = ROOT / "docs/data.js"
PASS_E = "experts' reading + Claude's matching (pass E)"
PASS_A = "Claude's reading + Claude's matching (pass A)"
APOSTROPHES = str.maketrans({"ʼ": "'", "᾿": "'", "’": "'", "̓": "'", "ʹ": "'"})


def folded(text):
    """Text without accents, breathings, case or repeated spaces, with the index of each kept character in the
    original, so a match can be mapped back."""
    out, index = [], []
    for i, ch in enumerate(text):
        for base in unicodedata.normalize("NFD", ch.translate(APOSTROPHES)):
            if unicodedata.combining(base):
                continue
            base = " " if base.isspace() else base.lower()
            if base == " " and out and out[-1] == " ":
                continue
            out.append(base)
            index.append(i)
    return "".join(out), index


def locate(quote, text, folded_text):
    """(start, end) of a quote in the chapter: exact first, then ignoring accents. None when not found."""
    q = re.sub(r"\s+", " ", unicodedata.normalize("NFC", quote)).strip()
    pos = text.find(q)
    if pos >= 0:
        return pos, pos + len(q)
    fq = folded(q)[0].strip()
    norm, index = folded_text
    pos = norm.find(fq) if fq else -1
    if pos < 0:
        return None
    return index[pos], index[pos + len(fq) - 1] + 1


def slug(key):
    return re.sub(r"[^a-z0-9]+", "-", key.lower()).strip("-")


def chapter_order(cid):
    book, ch = cid.split(".")
    return int(book), int(re.match(r"\d+", ch).group())


def comparisons(comps):
    """Our comparisons are {organ: {en, greek}} or {organ: [{en, greek}, ...]}."""
    out = []
    for organ, v in comps.items():
        for c in v if isinstance(v, list) else [v]:
            out.append({"organ": organ, **c})
    return out


def main():
    chapters, readings = load_chapters(), {r["key"]: r for r in load_readings()}
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    seen = json.loads(CONTAMINATION.read_text(encoding="utf-8"))["plants"]
    verdicts = {(r["plant"], r["candidate"]): r for r in results.pop("candidates")}
    calls_e, calls_a = calls_by_candidate("expert"), calls_by_candidate("ai")

    plants, missing = [], []
    for p in sorted(load_benchmark(), key=lambda p: (chapter_order(p["chapter"]), p["key"])):
        text = chapters[p["chapter"]]["text"]
        ftext, reading = folded(text), readings[p["key"]]
        quotes = []
        for c in CHARACTERS:
            if c in reading["characters"]:
                v = reading["characters"][c]
                quotes.append({"char": c, "cat": CATEGORY_OF[c], "en": v["en"], "greek": v["greek"], "kind": "character"})
        for c in comparisons(reading.get("comparisons", {})):
            quotes.append({"char": f"Comparison ({c['organ']})", "cat": c["organ"], "en": c["en"],
                           "greek": c["greek"], "kind": "comparison"})
        for q in quotes:
            span = locate(q["greek"], text, ftext)
            q["span"] = list(span) if span else None
            if not span:
                missing.append((p["key"], q["char"]))

        cands = []
        for c in p["candidates"]:
            v = verdicts.get((p["key"], c["df_name"]), {})
            e = calls_e.get((p["key"], c["df_name"]), {})
            cands.append({
                "name": c.get("accepted_name") or c["df_name"], "df_name": c["df_name"], "family": c.get("family"),
                "in_floras": c["in_floras"], "cited": v.get("cited"),
                "expert": [c["expert_score"], c["expert_verdict"]],
                "E": v.get("configs", {}).get(PASS_E), "A": v.get("configs", {}).get(PASS_A),
                "modern": {k: c["modern"][k] for k in CHARACTERS if c["modern"].get(k)},
                "calls": {k: {"x": c["expert_calls"].get(k), "E": e.get(k)}
                          for k in CHARACTERS if k in p["expert_reading"] and p["expert_reading"][k]},
                "callsA": {k: v for k, v in calls_a.get((p["key"], c["df_name"]), {}).items()},
            })
        cands.sort(key=lambda c: (not c["in_floras"], -(c["expert"][0] if c["expert"][0] is not None else -99)))
        plants.append({
            "key": p["key"], "slug": slug(p["key"]), "greek": p["dmm_name"], "jc": p["jc_name"],
            "chapter": p["chapter"], "located_by": p["chapter_located_by"], "seen": seen.get(p["key"]),
            "text": text, "rv": chapters[p["chapter"]].get("rv_synonyms") or [],
            "quotes": quotes, "expert": {k: p["expert_reading"][k] for k in CHARACTERS if p["expert_reading"].get(k)},
            "expert_comparisons": p.get("comparisons") or {}, "candidates": cands,
        })

    # No build date: the file must be byte-identical on every rebuild.
    data = {"characters": CHARACTERS, "categories": CATEGORIES, "results": results, "plants": plants}
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("window.RHIZOTOMOS = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n",
                   encoding="utf-8")
    n_quotes = sum(len(p["quotes"]) for p in plants)
    print(f"{len(plants)} plants, {n_quotes} quotes, {n_quotes - len(missing)} located in the chapter text; "
          f"not located: {missing}")
    print(f"-> {OUT.relative_to(ROOT)} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
