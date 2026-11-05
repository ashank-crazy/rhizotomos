"""Matching baselines that use no model, on the same pairs as pass E (the experts' reading).

    calls("word overlap")   a pair is good when at least half the content words of the ancient statement
                            appear in the modern value, partial when some do, and no otherwise; heights are
                            compared as numbers with the rule of prompts/matching.md
    calls("all good")       every pair is called good; with pass_name "ai" this is done on the pass A pairs
                            (our reading against each category), which shows what coverage alone gives

All return {label: {character: g|p|n}} in the format of data/llm/matching/expert/*.json.
"""

import re

from rhizotomos.matching import items

STOP = set("""a an the and or of in on at to with as is are be it its by from for than that this these those
very somewhat rather quite more less little even also like one two three four after before when has have having
into which there their them they then grow grows growing""".split())
SUFFIXES = ("ishly", "ish", "ness", "ing", "ed", "es", "ly", "s", "y")
UNIT_CM = {"mm": 0.1, "cm": 1.0, "m": 100.0, "ft": 30.5}


def stem(word):
    for s in SUFFIXES:
        if word.endswith(s) and len(word) - len(s) >= 3:
            return word[:-len(s)]
    return word


def words(text):
    return {stem(w) for w in re.findall(r"[a-z]+", text.lower()) if w not in STOP and len(w) > 2}


def lengths(text):
    """Every length in a text, in cm: '17-28 cm / 13-29 cm' -> [17, 28, 13, 29]. The experts' '(0.92 cm)' for
    two cubits is a slip for metres, so a value under 5 'cm' is read as metres."""
    out, pending = [], []
    for tok in re.finditer(r"\d+(?:\.\d+)?|(?<![a-z])(?:mm|cm|m|ft)(?![a-z])", text.lower()):
        t = tok.group()
        if t[0].isdigit():
            pending.append(float(t))
        elif pending:
            factor = 100.0 if t == "cm" and max(pending) < 5 else UNIT_CM[t]
            out += [v * factor for v in pending]
            pending = []
    return out


def height_call(ancient, modern):
    a, m = lengths(ancient), lengths(modern)
    if not a or not m:
        return None
    if min(a) <= max(m) and max(a) >= min(m):
        return "g"
    gap = min(a) / max(m) if min(a) > max(m) else min(m) / max(a)
    return "p" if gap <= 2 else "n"


def word_call(ancient, modern):
    a, shared = words(ancient), words(ancient) & words(modern)
    if not shared:
        return "n"
    return "g" if len(shared) / len(a) >= 0.5 else "p"


def calls(kind, pass_name="expert"):
    out = {}
    for it in items(pass_name):
        for cand in it["candidates"]:
            got = {}
            for c in cand["judge"]:
                if kind == "all good":
                    got[c] = "g"
                    continue
                ancient, modern = it["statements"][c], cand["modern"][c]
                got[c] = (height_call(ancient, modern) if c == "Height" else None) or word_call(ancient, modern)
            if got:
                out[cand["label"]] = got
    return out
