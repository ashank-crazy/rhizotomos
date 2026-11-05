"""Stage 0: parse Wellmann's De materia medica (First1KGreek TEI) into one record per chapter.

Each record keeps the running Greek text with the critical apparatus removed, and the
Recensio Vulgaris (RV) synonym lists that Wellmann prints as footnotes beginning "RV:".
"""

import json
import re
import unicodedata
from pathlib import Path

from lxml import etree

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "data/raw/first1k/tlg0656.tlg001.1st1K-grc1.xml"
OUT = ROOT / "data/derived/dmm_chapters.jsonl"
TEI = "{http://www.tei-c.org/ns/1.0}"

# Leading section / line numbers the edition prints inside paragraphs ("1 ἶρις Ἰλλυρικὴ ...").
EDITION_NUMBERS = re.compile(r"(?<!\w)\d+(?!\w)")


def clean(text):
    text = unicodedata.normalize("NFC", text)
    text = EDITION_NUMBERS.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()


def text_without_apparatus(el):
    """Concatenate an element's text, skipping <note> and <del> subtrees but keeping their tails."""
    parts = [el.text or ""]
    for child in el:
        if child.tag not in (f"{TEI}note", f"{TEI}del"):
            parts.append(text_without_apparatus(child))
        parts.append(child.tail or "")
    return "".join(parts)


def rv_synonyms(chapter):
    out = []
    for note in own(chapter, "note"):
        raw = re.sub(r"\s+", " ", "".join(note.itertext())).strip()
        m = re.match(r"^\d*\s*RV:\s*(.*)", raw)
        if m:
            out.append(unicodedata.normalize("NFC", m.group(1)))
    return out


def is_chapter(el):
    return el.tag == f"{TEI}div" and el.get("subtype") == "chapter"


def own(chapter, tag):
    """Elements of `tag` belonging to this chapter. The TEI leaves some chapter divs unclosed, so later
    chapters end up nested inside earlier ones; an element belongs to its nearest chapter ancestor."""
    for el in chapter.iter(f"{TEI}{tag}"):
        anc = el.getparent()
        while not is_chapter(anc):
            anc = anc.getparent()
        if anc is chapter:
            yield el


def chapters():
    tree = etree.parse(str(SRC))
    body = tree.find(f".//{TEI}body")
    for book in body.iter(f"{TEI}div"):
        if book.get("subtype") != "book":
            continue
        b = book.get("n")
        for ch in book.iter(f"{TEI}div"):
            if not is_chapter(ch):
                continue
            n = ch.get("n")
            paras = [clean(text_without_apparatus(p)) for p in own(ch, "p")]
            text = " ".join(p for p in paras if p)
            yield {
                "id": f"{b}.{n}" if n != "preface" else f"{b}.0",
                "book": int(b),
                "chapter": "0" if n == "preface" else n,
                "text": STRAY_SIGLA.sub(" ", text).strip(),
                "rv_synonyms": rv_synonyms(ch),
            }


STRAY_SIGLA = re.compile(r"\bs\d+\b")


def chapter_number(row):
    return int(re.match(r"\d+", row["chapter"]).group())


def merge_mistagged(rows):
    """A few divs are tagged as chapters but are really sections of the chapter before them: their
    number goes backwards ("2" inside 1.123) or repeats (an RV list given its own div). Fold them back."""
    out = []
    for r in rows:
        prev = out[-1] if out else None
        if prev and prev["book"] == r["book"] and r["chapter"] != "0" and chapter_number(r) <= chapter_number(prev) \
                and r["chapter"] != prev["chapter"].rstrip("ab") + "b":
            if r["text"].startswith("RV:"):
                prev["rv_synonyms"].append(r["text"][3:].strip())
            else:
                prev["text"] = f'{prev["text"]} {r["text"]}'
            prev["rv_synonyms"] += r["rv_synonyms"]
            continue
        out.append(r)
    return out


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rows = merge_mistagged(list(chapters()))
    assert len({r["id"] for r in rows}) == len(rows), "duplicate chapter ids remain"
    with OUT.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    chars = sum(len(r["text"]) for r in rows)
    with_rv = sum(1 for r in rows if r["rv_synonyms"])
    print(f"{len(rows)} chapters, {chars:,} Greek characters, {with_rv} with RV synonyms -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
