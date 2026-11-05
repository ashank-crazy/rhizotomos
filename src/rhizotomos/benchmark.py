"""Load the Lardos et al. (2024) research data (figshare, CC BY 4.0) into one clean benchmark file.

For each of the 61 "rich" DMM plants it records the experts' reading of Dioscorides (Data file 3), and for
each of the plant's candidate species the modern flora description (Data file 6), the experts' match call
for every character (Data file 9) and their final verdict (Data file 11).
"""

import difflib
import glob
import json
import re
import unicodedata
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/figshare"
CHAPTERS = ROOT / "data/derived/dmm_chapters.jsonl"
OUT = ROOT / "data/derived/benchmark.json"

# The 36 characters the experts compared, grouped into the 13 feature categories of their Stage 5.
CATEGORIES = {
    "Lifeform": ["Life form"],
    "Habit": ["Habitus general", "Habitus detail 1", "Habitus detail 2"],
    "Height": ["Height"],
    "Stem": ["Stem general", "Stem detail 1", "Stem detail 2", "Stem detail 3"],
    "Leaf": ["Leaf general", "Leaf size", "Leaf shape", "Leaf edge", "Leaf surface", "Leaf detail 1", "Leaf detail 2"],
    "Flower": ["Flower general", "Flower colour", "Flower detail 01"],
    "Fruit": ["Fruit general", "Fruit shape", "Fruit structure", "Fruit colour", "Fruit detail 1"],
    "Seed": ["Seed general", "Seed colour", "Seed detail 1"],
    "Root": ["Root general", "Root colour", "Root detail 1", "Root detail 2"],
    "Properties": ["Smell properties", "Taste properties"],
    "Ethnobotany": ["Ethnobotany"],
    "Habitat": ["Habitat"],
    "Distribution": ["Distribution"],
}
CHARACTERS = [c for chars in CATEGORIES.values() for c in chars]
# Data file 3 names two characters differently from the later files.
DF3_ALIASES = {"Leaf margin": "Leaf edge", "Flower detail 1": "Flower detail 01"}
CALL_VALUE = {"good": 2, "partial": 1, "no": -2, "absent": 0}
# Data file 9 spells one plant differently from Data file 3.
DF9_ALIASES = {"staphylinos (wild)": "stavylinos (wild)"}
# Data file 3 spellings that differ from Wellmann's headwords (one typo, two spelling variants).
SPELLING = {"κευταύριον": "κενταύρειον", "σιδερίτις": "σιδηρῖτις", "άλλυσσον": "ἄλυσσον"}


def sheet(n, name):
    path = glob.glob(str(RAW / f"Data file {n} - *.xlsx"))[0]
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    return list(wb[name].iter_rows(values_only=True))


def norm_header(h):
    return re.sub(r"\s+", " ", str(h or "")).strip()


def records(rows):
    header = [norm_header(h) for h in rows[0]]
    return [dict(zip(header, r)) for r in rows[1:]]


def cell(v):
    """Empty and the experts' 'x' placeholder both mean the source says nothing about this character."""
    if v is None:
        return None
    v = re.sub(r"\s+", " ", str(v)).strip()
    return None if v in ("", "x", "X") else v


def plain_greek(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(ch for ch in s if unicodedata.category(ch) != "Mn").replace("ς", "σ")


def binomial(name):
    """Genus and species, ignoring authors, parenthesised notes and the hybrid sign ('Iris x germanica')."""
    words = [w for w in re.sub(r"\(.*?\)", " ", name).split() if w not in ("x", "×")]
    return " ".join(words[:2]).lower()


def wellmann_id(ref):
    """'DMM ΙΙΙ, 12' (sometimes typed with Greek capital iotas) -> '3.12'; None when no chapter is given."""
    m = re.search(r"([IVΙ]+)\s*,\s*(\d+\w?)", (ref or "").replace("Ι", "I"))
    if not m:
        return None
    book = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5}[m.group(1)]
    return f"{book}.{m.group(2)}"


def head_names(dmm_name):
    """'χαμαίμηλον, in ανθεμίς' is described in the chapter on ἀνθεμίς; 'ηλιοτρόπιον το μέγα, σκορπίουρον'
    is headed by its first name. Returns plain-Greek prefixes to look for at the start of a chapter."""
    name = re.sub(r"\(.*?\)", "", dmm_name)
    for modern, wellmann in SPELLING.items():
        name = name.replace(modern, wellmann)
    parts = [p.strip() for p in name.split(",")]
    heads = [p[3:] for p in parts if p.startswith("in ")] + [p for p in parts if not p.startswith("in ")]
    return [plain_greek(h.split()[0])[:5] for h in heads if h]


def locate_chapter(dmm_name, ref, chapters):
    """The experts cite Beck's chapter numbers, which follow Wellmann. Trust the reference when the chapter
    opens with the plant's name; otherwise take the nearest chapter that does, and say so."""
    heads = head_names(dmm_name)
    opens_with = lambda cid: any(h in plain_greek(chapters[cid]["text"][:150]) for h in heads)
    cid = wellmann_id(ref)
    if cid in chapters and opens_with(cid):
        return cid, "reference"
    book = cid.split(".")[0] if cid else None
    opening = lambda k: k.split(".")[1] != "0" and any(h in plain_greek(chapters[k]["text"][:40]) for h in heads)
    hits = [k for k in chapters if (book is None or k.startswith(book + ".")) and opening(k)] \
        or [k for k in chapters if opening(k)]
    if hits:
        n = int(re.match(r"\d+", cid.split(".")[1]).group()) if cid else 0
        best = min(hits, key=lambda k: abs(int(re.match(r"\d+", k.split(".")[1]).group()) - n))
        return best, f"relocated from {ref!r}"
    return cid, "reference, chapter opening not matched"


def verdict(calls):
    """The experts' Stage 5 rule (Data file 11): average the scored characters within each category, count
    categories with a positive and a negative average, and grade the difference."""
    pos = neg = 0
    for chars in CATEGORIES.values():
        scored = [CALL_VALUE[calls[c]] for c in chars if calls.get(c) in CALL_VALUE and CALL_VALUE[calls[c]] != 0]
        if scored:
            avg = sum(scored) / len(scored)
            pos += avg > 0
            neg += avg < 0
    score = pos - neg
    return score, "STRONG" if score >= 5 else "MODERATE" if score >= 3 else "WEAK"


def expert_reading(chapters):
    plants = {}
    for r in records(sheet(3, "Plant descriptions DMM")):
        key = cell(r["DMM name (Beck, 2005)"])
        if not key:
            continue
        chars = {}
        for col, v in r.items():
            col = DF3_ALIASES.get(col, col)
            if col in CHARACTERS and cell(v):
                chars[col] = cell(v)
        chapter, located = locate_chapter(cell(r["DMM plant name"]), r["Reference DMM"], chapters)
        plants[key] = {
            "key": key,
            "lemma": r["Lemma tag"],
            "jc_name": cell(r["JC plant name"]),
            "dmm_name": cell(r["DMM plant name"]),
            "chapter": chapter,
            "chapter_located_by": located,
            "expert_reading": chars,
            "comparisons": {},
            "candidates": [],
        }
    for r in records(sheet(3, "DMM plant comparisons")):
        key = cell(r["DMM name (Beck, 2005)"])
        if key in plants:
            plants[key]["comparisons"] = {k.replace(" comparison", ""): cell(v) for k, v in r.items()
                                          if k.endswith("comparison") and cell(v)}
    return plants


def modern_and_calls():
    """Data file 9 lists each DMM plant's row followed by one row per candidate, with a categorisation
    column after every character. Data file 6 has the same modern descriptions without the calls."""
    rows = sheet(9, "Comparison DMM vs. FT_FC")
    header = [norm_header(h) for h in rows[0]]
    out, current = [], None
    for r in rows[1:]:
        rec = dict(zip(header, r))
        name = cell(rec["DMM name"])
        if not name:
            continue
        if str(rec["Reference Flora Turkey"] or "").startswith("DMM"):
            current = DF9_ALIASES.get(name, name)
            continue
        modern, calls = {}, {}
        for c in CHARACTERS:
            if cell(rec.get(c)):
                modern[c] = cell(rec[c])
            call = cell(rec.get(f"Categorisation {c}"))
            calls[c] = call.lower() if call else None
        out.append({
            "dmm_key": current,
            "df_name": cell(rec["Candidate plant (FT or FC synonyms in parenthesis)"]),
            "in_floras": not ("not found" in str(rec["Reference Flora Turkey"]).lower()
                              and "not found" in str(rec["Reference Flora Cyprus"]).lower()),
            "modern": modern,
            "expert_calls": {c: v for c, v in calls.items() if v},
        })
    return out


def expert_verdicts():
    """Data file 11 rows by JC lemma. A lemma can cover several DMM types (greater/lesser plantain) that share
    candidate species, so one species may appear with more than one verdict."""
    out = {}
    for r in records(sheet(11, "Bot Info Evaluation")):
        if not r.get("CP_ID"):
            continue
        uses = re.search(r"\((\d)\)\s*$", str(r["Accepted_Name with Uses Score"] or ""))
        out.setdefault(r["Lemma tag"], []).append({
            "binomial": binomial(r["Accepted_Name"]),
            "cp_id": r["CP_ID"],
            "accepted_name": r["Accepted_Name"],
            "family": r["Accepted_Family"],
            "verdict": str(r["Strength of Congruence"]).upper().replace("NOT FOUND", "NOT_IN_FLORAS"),
            "uses_score": int(uses.group(1)) if uses else None,
        })
    return out


def link_candidate(df_name, rows):
    """Match a Data file 9 candidate name (with flora synonyms in parentheses, occasional typos) to the
    Data file 11 rows for its lemma by binomial."""
    names = [binomial(df_name)] + [binomial(s) for s in re.findall(r"\((?:FT|FC),\s*([^)]+)\)", df_name)]
    genus = names[0].split()[0] if names[0] else ""
    # Flora synonyms abbreviate the genus: "(FT, V. vinifera ssp. sylvestris)".
    names = [f"{genus} {n.split()[1]}" if re.match(r"^\w\.\s", n) and len(n.split()) > 1 else n for n in names]
    exact = [r for r in rows if r["binomial"] in names]
    if exact:
        return exact
    ratio = lambda r: max(difflib.SequenceMatcher(None, n, r["binomial"]).ratio() for n in names)
    best = max(rows, key=ratio, default=None)
    return [r for r in rows if r["binomial"] == best["binomial"]] if best and ratio(best) >= 0.85 else []


def main():
    chapters = {json.loads(l)["id"]: json.loads(l) for l in CHAPTERS.open(encoding="utf-8")}
    plants = expert_reading(chapters)
    verdicts = expert_verdicts()

    unmatched, checked, agree = [], 0, 0
    for cand in modern_and_calls():
        plant = plants[cand.pop("dmm_key")]
        rows = link_candidate(cand["df_name"], verdicts.get(plant["lemma"], []))
        if not rows:
            unmatched.append((plant["key"], cand["df_name"]))
        else:
            cand.update({k: rows[0][k] for k in ("cp_id", "accepted_name", "family", "uses_score")})
        # Verdicts are re-derived from the experts' own calls with their rule, which keeps them per DMM type.
        score, grade = verdict(cand["expert_calls"])
        cand["expert_score"] = score if cand["in_floras"] else None
        cand["expert_verdict"] = grade if cand["in_floras"] else "NOT_IN_FLORAS"
        df11 = {r["verdict"] for r in rows}
        if df11 and cand["in_floras"]:
            checked += 1
            agree += cand["expert_verdict"] in df11
        plant["candidates"].append(cand)

    OUT.write_text(json.dumps(list(plants.values()), ensure_ascii=False, indent=1), encoding="utf-8")
    cands = [c for p in plants.values() for c in p["candidates"]]
    print(f"{len(plants)} DMM plants, {len(cands)} candidates, {sum(not c['in_floras'] for c in cands)} not in floras, "
          f"{len(unmatched)} not linked to Data file 11: {unmatched}")
    for p in plants.values():
        if p["chapter_located_by"] != "reference":
            print(f"  {p['key']}: {p['chapter']} ({p['chapter_located_by']})")
    print(f"expert rule re-applied to expert calls reproduces Data file 11: {agree}/{checked}")
    print(f"-> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
