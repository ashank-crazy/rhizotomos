"""Score every stage against the experts' own data.

    python -m rhizotomos.evaluate    writes data/derived/results.json and RESULTS.md

Stage A, reading: the characters our reading fills, against those the experts filled (Data file 3).
Stage B, matching: the pass E calls against the experts' calls on the same pairs (Data file 9).
Stage C, verdicts: the experts' Stage 5 rule (benchmark.verdict) applied to each set of calls, against the
verdicts the same rule gives on the experts' own calls, which reproduce Data file 11 (see benchmark.py).

Each figure is given for all plants and for the plants whose expert data was never seen while the readings and
calls were made (data/llm/contamination.json), with a 95% bootstrap interval over plants.
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

from rhizotomos import baseline
from rhizotomos.benchmark import (CALL_VALUE, CATEGORIES, binomial, expert_verdicts, link_candidate, records, sheet,
                                  verdict)
from rhizotomos.matching import CALLS, CATEGORY_OF, calls_by_candidate, items, load_benchmark, load_calls
from rhizotomos.reading import load_readings

ROOT = Path(__file__).resolve().parents[2]
CONTAMINATION = ROOT / "data/llm/contamination.json"
OUT_JSON = ROOT / "data/derived/results.json"
OUT_MD = ROOT / "RESULTS.md"
GRADES = ["WEAK", "MODERATE", "STRONG"]
MATCH = ["no", "partial", "good"]
BOOT = 2000


def mean(xs):
    """math.fsum is correctly rounded, so the result does not depend on the Python version (3.12 changed how
    the built-in sum adds floats)."""
    xs = list(xs)
    return math.fsum(xs) / len(xs) if xs else None


def rounded(obj, places=6):
    """Floats rounded for results.json, so the last digit of a float never changes the file."""
    if isinstance(obj, float):
        return round(obj, places)
    if isinstance(obj, dict):
        return {k: rounded(v, places) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [rounded(v, places) for v in obj]
    return obj


def kappa(pairs, labels, weighted=False):
    """Cohen's kappa of (rater 1, rater 2) pairs; with linear weights over the order of `labels` if weighted."""
    if not pairs:
        return None
    k, idx = len(labels), {l: i for i, l in enumerate(labels)}
    obs = Counter((idx[a], idx[b]) for a, b in pairs)
    rows = Counter(idx[a] for a, _ in pairs)
    cols = Counter(idx[b] for _, b in pairs)
    w = (lambda i, j: abs(i - j) / (k - 1)) if weighted else (lambda i, j: float(i != j))
    n = len(pairs)
    seen = math.fsum(w(i, j) * c for (i, j), c in obs.items()) / n
    chance = math.fsum(w(i, j) * rows[i] * cols[j] for i in range(k) for j in range(k)) / n / n
    return 1 - seen / chance if chance else None


def spearman(rows, key):
    a = pd.Series([r[key] for r in rows], dtype=float)
    b = pd.Series([r["expert_score"] for r in rows], dtype=float)
    rho = a.rank().corr(b.rank())  # Pearson on average ranks is Spearman's rho, without needing scipy
    return None if pd.isna(rho) else float(rho)


def interval(rows, stat, seed=0):
    """95% bootstrap interval of stat(rows), resampling whole plants. Each draw gets its own plant key, so a
    plant drawn twice counts twice."""
    groups = defaultdict(list)
    for r in rows:
        groups[r["plant"]].append(r)
    keys, rng, vals = sorted(groups), random.Random(seed), []
    for _ in range(BOOT):
        draw = [dict(r, plant=(k, i)) for i, k in enumerate(rng.choices(keys, k=len(keys))) for r in groups[k]]
        v = stat(draw)
        if v is not None:
            vals.append(v)
    vals.sort()
    return [round(vals[int(0.025 * len(vals))], 3), round(vals[int(0.975 * len(vals)) - 1], 3)] if vals else None


# Stage A: reading

def most_common(counter, n=6):
    """Like Counter.most_common, but ties are broken by name, so reruns give the same file."""
    return sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))[:n]


def reading_metrics(plants):
    readings = {r["key"]: r for r in load_readings()}
    out = {}
    for level, f in (("characters", lambda c: c), ("categories", CATEGORY_OF.get)):
        shared = ours_n = theirs_n = 0
        missed, added = Counter(), Counter()
        for p in plants:
            ours = {f(c) for c in readings[p["key"]]["characters"]}
            theirs = {f(c) for c, v in p["expert_reading"].items() if v is not None}
            shared += len(ours & theirs)
            ours_n += len(ours)
            theirs_n += len(theirs)
            missed.update(theirs - ours)
            added.update(ours - theirs)
        prec, rec = shared / ours_n, shared / theirs_n
        out[level] = {"ours": ours_n, "experts": theirs_n, "shared": shared, "precision": prec, "recall": rec,
                      "f1": 2 * prec * rec / (prec + rec), "missed_most": most_common(missed),
                      "added_most": most_common(added)}
    return out


# Stage B: matching

def matching_rows(calls):
    rows = []
    for it in items("expert"):
        for cand in it["candidates"]:
            got = calls.get(cand["label"], {})
            for c in cand["judge"]:
                rows.append({"plant": it["plant"]["key"], "character": c, "ours": CALLS[got[c]],
                             "expert": cand["candidate"]["expert_calls"].get(c)})
    return rows


def compared(rows):
    return [(r["expert"], r["ours"]) for r in rows if r["expert"] in MATCH]


def matching_metrics(rows):
    pairs = compared(rows)
    return {
        "pairs": len(rows),
        "expert_absent": sum(r["expert"] == "absent" for r in rows),
        "expert_missing": sum(r["expert"] is None for r in rows),
        "compared": len(pairs),
        "agreement": mean(a == b for a, b in pairs),
        "kappa": kappa(pairs, MATCH),
        "kappa_linear": kappa(pairs, MATCH, weighted=True),
        "direction_agreement": mean((a == "no") == (b == "no") for a, b in pairs),
        "confusion": {e: {o: sum(1 for r in rows if r["expert"] == e and r["ours"] == o) for o in MATCH}
                      for e in MATCH + ["absent"]},
    }


# Stage C: verdicts

def verdict_rows(by_cand):
    rows = []
    for p in load_benchmark():
        for c in p["candidates"]:
            if c["in_floras"]:
                score, grade = verdict(by_cand.get((p["key"], c["df_name"]), {}))
                rows.append({"plant": p["key"], "candidate": c["df_name"], "score": score, "grade": grade,
                             "expert_score": c["expert_score"], "expert_grade": c["expert_verdict"]})
    return rows


def top_pick(rows, key="score"):
    """Share of plants with two or more candidates where our best-scoring candidate is the experts' best. When
    several of ours tie, each counts for an equal share, which is the chance of picking right among them."""
    by_plant = defaultdict(list)
    for r in rows:
        by_plant[r["plant"]].append(r)
    hits = []
    for rs in by_plant.values():
        if len(rs) < 2:
            continue
        best_e, best_o = max(r["expert_score"] for r in rs), max(r[key] for r in rs)
        theirs = {r["candidate"] for r in rs if r["expert_score"] == best_e}
        ours = [r["candidate"] for r in rs if r[key] == best_o]
        hits.append(sum(c in theirs for c in ours) / len(ours))
    return mean(hits)


def agreement(rows):
    return mean(r["grade"] == r["expert_grade"] for r in rows)


def weighted_kappa(rows):
    return kappa([(r["expert_grade"], r["grade"]) for r in rows], GRADES, weighted=True)


def verdict_metrics(rows, key="score"):
    pairs = [(r["expert_grade"], r["grade"]) for r in rows]
    return {
        "candidates": len(rows),
        "agreement": agreement(rows),
        "kappa_linear": weighted_kappa(rows),
        "spearman": spearman(rows, key),
        "top_pick": top_pick(rows, key),
        "confusion": {e: {o: pairs.count((e, o)) for o in GRADES} for e in GRADES},
    }


def category_counts(by_cand):
    """Mean number of categories per candidate whose average call is positive, and negative."""
    pos = neg = n = 0
    for p in load_benchmark():
        for c in p["candidates"]:
            if not c["in_floras"]:
                continue
            calls, n = by_cand.get((p["key"], c["df_name"]), {}), n + 1
            for chars in CATEGORIES.values():
                s = [CALL_VALUE[calls[ch]] for ch in chars if CALL_VALUE.get(calls.get(ch))]
                pos += bool(s) and sum(s) > 0
                neg += bool(s) and sum(s) < 0
    return {"positive": pos / n, "negative": neg / n}


def replication():
    """How often the experts' rule on the experts' calls gives the verdict published in Data file 11."""
    df11, agree, checked = expert_verdicts(), 0, 0
    for p in load_benchmark():
        for c in p["candidates"]:
            published = {r["verdict"] for r in link_candidate(c["df_name"], df11.get(p["lemma"], []))}
            if published and c["in_floras"]:
                checked += 1
                agree += c["expert_verdict"] in published
    return {"agree": agree, "checked": checked}


def citations():
    """Data file 5 'Reported Candidate Plants': how often each species was proposed for a lemma."""
    return Counter((r["Lemma tag"], binomial(r["Reported name"])) for r in records(sheet(5, "Reported Candidate Plants")))


def cited_rows(rows):
    """Rows scored by how often the literature proposed the candidate (flora synonyms and the accepted name
    count together)."""
    cites, cands = citations(), {(p["key"], c["df_name"]): (p, c) for p in load_benchmark() for c in p["candidates"]}
    out = []
    for r in rows:
        p, c = cands[(r["plant"], r["candidate"])]
        names = {binomial(c["df_name"]), binomial(c.get("accepted_name") or "")}
        names |= {binomial(s) for s in re.findall(r"\((?:FT|FC),\s*([^)]+)\)", c["df_name"])}
        out.append(dict(r, cited=sum(cites[(p["lemma"], n)] for n in names if n)))
    return out


def subsets(rows, unseen):
    return {"all": rows, "unseen": [r for r in rows if r["plant"] in unseen]}


# Run to run: the first and the repeat run of pass E

PASS_E = "experts' reading + Claude's matching (pass E)"
PASS_A = "Claude's reading + Claude's matching (pass A)"
REPEAT = "experts' reading + Claude's matching (pass E, repeat run)"


def run_pairs(first, repeat):
    """Rows of matching_rows (or verdict_rows) for two runs on the same items, side by side."""
    assert [(a["plant"], a.get("character", a.get("candidate"))) for a in first] == \
           [(b["plant"], b.get("character", b.get("candidate"))) for b in repeat], "runs cover different items"
    return [dict(a, repeat=b) for a, b in zip(first, repeat)]


def stability_metrics(calls, verdicts):
    same_call = lambda rs: mean(r["ours"] == r["repeat"]["ours"] for r in rs)
    call_kappa = lambda rs: kappa([(r["ours"], r["repeat"]["ours"]) for r in rs], MATCH, weighted=True)
    same_grade = lambda rs: mean(r["grade"] == r["repeat"]["grade"] for r in rs)
    grade_kappa = lambda rs: kappa([(r["grade"], r["repeat"]["grade"]) for r in rs], GRADES, weighted=True)
    # The first run's best candidates stand in for the experts' in top_pick.
    same_best = lambda rs: top_pick([dict(r, expert_score=r["score"], score=r["repeat"]["score"]) for r in rs])
    flips = lambda rs: sum((r["grade"] == r["expert_grade"]) != (r["repeat"]["grade"] == r["expert_grade"]) for r in rs)
    return {
        "calls": len(calls), "same_call": same_call(calls), "kappa_linear": call_kappa(calls),
        "same_direction": mean((r["ours"] == "no") == (r["repeat"]["ours"] == "no") for r in calls),
        "candidates": len(verdicts), "same_grade": same_grade(verdicts), "grade_kappa_linear": grade_kappa(verdicts),
        "same_best": same_best(verdicts), "expert_agreement_changed": flips(verdicts),
        "ci": {"same_call": interval(calls, same_call), "same_grade": interval(verdicts, same_grade),
               "same_best": interval(verdicts, same_best)},
    }


def main():
    plants = load_benchmark()
    contamination = json.loads(CONTAMINATION.read_text(encoding="utf-8"))
    seen = set(contamination["plants"])
    unseen = {p["key"] for p in plants} - seen
    # Before the repeat run, a few more plants had been seen (see contamination.json).
    unseen_repeat = unseen - set(contamination.get("repeat_run_plants", {}))
    results = {"plants": {"all": len(plants), "unseen": len(unseen), "unseen_repeat": len(unseen_repeat)},
               "seen_plants": sorted(seen), "seen_before_repeat": sorted(set(contamination.get("repeat_run_plants", {})))}

    results["reading"] = {"all": reading_metrics(plants),
                          "unseen": reading_metrics([p for p in plants if p["key"] in unseen])}

    match_calls = {"Claude (pass E)": load_calls("expert"),
                   "Claude (pass E, repeat run)": load_calls("expert_r2"),
                   "word overlap": baseline.calls("word overlap"),
                   "all good": baseline.calls("all good")}
    unseen_for = lambda name: unseen_repeat if "repeat" in name else unseen
    results["matching"] = {}
    for name, calls in match_calls.items():
        rows = matching_rows(calls)
        results["matching"][name] = {k: matching_metrics(v) for k, v in subsets(rows, unseen_for(name)).items()}
        results["matching"][name]["ci"] = {
            "agreement": interval(rows, lambda rs: mean(a == b for a, b in compared(rs))),
            "kappa_linear": interval(rows, lambda rs: kappa(compared(rs), MATCH, weighted=True))}

    configs = {
        PASS_E: calls_by_candidate("expert"),
        REPEAT: calls_by_candidate("expert_r2"),
        PASS_A: calls_by_candidate("ai"),
        "experts' reading + word overlap": calls_by_candidate("expert", match_calls["word overlap"]),
        "experts' reading + everything good": calls_by_candidate("expert", match_calls["all good"]),
        "Claude's reading + everything good": calls_by_candidate("ai", baseline.calls("all good", "ai")),
    }
    results["replication"] = replication()
    experts_calls = {(p["key"], c["df_name"]): c["expert_calls"] for p in plants for c in p["candidates"]}
    results["category_counts"] = {"experts": category_counts(experts_calls),
                                  "pass E": category_counts(configs[PASS_E]),
                                  "pass A": category_counts(configs[PASS_A])}
    results["verdicts"], table = {}, {}
    for name, by_cand in configs.items():
        rows = verdict_rows(by_cand)
        results["verdicts"][name] = {k: verdict_metrics(v) for k, v in subsets(rows, unseen_for(name)).items()}
        results["verdicts"][name]["ci"] = {"agreement": interval(rows, agreement),
                                           "kappa_linear": interval(rows, weighted_kappa),
                                           "top_pick": interval(rows, top_pick)}
        for r in rows:
            table.setdefault((r["plant"], r["candidate"]), dict(r, configs={}))["configs"][name] = [r["score"], r["grade"]]

    call_pairs = run_pairs(matching_rows(match_calls["Claude (pass E)"]), matching_rows(match_calls["Claude (pass E, repeat run)"]))
    verdict_pairs = run_pairs(verdict_rows(configs[PASS_E]), verdict_rows(configs[REPEAT]))
    results["stability"] = {k: stability_metrics(c, v) for (k, c), (_, v) in
                            zip(subsets(call_pairs, unseen_repeat).items(), subsets(verdict_pairs, unseen_repeat).items())}

    rows = cited_rows(verdict_rows(configs["experts' reading + everything good"]))
    majority = Counter(r["expert_grade"] for r in rows).most_common(1)[0][0]
    results["baselines"] = {
        k: {"most_cited_top_pick": top_pick(v, "cited"),
            "chance_top_pick": top_pick([dict(r, flat=0) for r in v], "flat"),
            "majority_grade": majority,
            "majority_agreement": mean(r["expert_grade"] == majority for r in v),
            "plants_with_choice": sum(1 for n in Counter(r["plant"] for r in v).values() if n > 1)}
        for k, v in subsets(rows, unseen).items()}
    results["baselines"]["ci"] = {"most_cited_top_pick": interval(rows, lambda rs: top_pick(rs, "cited"))}
    for r in rows:
        table[(r["plant"], r["candidate"])]["cited"] = r["cited"]
    results["candidates"] = [{k: v for k, v in r.items() if k not in ("score", "grade")} for r in table.values()]

    results = rounded(results)  # RESULTS.md and the explorer then show exactly the same numbers
    OUT_JSON.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    OUT_MD.write_text(report(results), encoding="utf-8")
    print(report(results))


def pct(x):
    return "–" if x is None else f"{100 * x:.0f}%"


def num(x):
    return "–" if x is None else f"{x:.2f}"


def ci(c, fmt):
    return f" ({fmt(c[0])}–{fmt(c[1])})" if c else ""


def report(res):
    n_all, n_unseen = res["plants"]["all"], res["plants"]["unseen"]
    out = ["# Results", "",
           f"All figures compare Rhizotomos with the published expert data of Lardos et al. (2024). \"Unseen\" "
           f"leaves out the {n_all - n_unseen} plants whose expert data was looked at while the pipeline was built "
           f"({', '.join(res['seen_plants'])}); the other {n_unseen} were never seen before both matching passes "
           f"were complete. Ranges are 95% bootstrap intervals over plants.", ""]

    rep = res["replication"]
    out += ["## Sanity check", "",
            f"The experts' Stage 5 rule, applied to the experts' own match calls, gives the verdict they published "
            f"for {rep['agree']} of {rep['checked']} candidates. These re-derived verdicts are the reference below.", ""]

    out += ["## Stage C: verdicts (STRONG / MODERATE / WEAK)", "",
            "| Reading | Matching | Agreement | Weighted κ | Spearman ρ | Same top pick | Agreement, unseen | Top pick, unseen |",
            "|---|---|---|---|---|---|---|---|"]
    for name, v in res["verdicts"].items():
        reading, matching = name.split(" + ")
        a, u, c = v["all"], v["unseen"], v["ci"]
        out.append(f"| {reading} | {matching} | {pct(a['agreement'])}{ci(c['agreement'], pct)} | "
                   f"{num(a['kappa_linear'])}{ci(c['kappa_linear'], num)} | {num(a['spearman'])} | "
                   f"{pct(a['top_pick'])}{ci(c['top_pick'], pct)} | {pct(u['agreement'])} | {pct(u['top_pick'])} |")
    b, bu = res["baselines"]["all"], res["baselines"]["unseen"]
    out.append(f"| – | most often proposed in the literature (Data file 5) | – | – | – | "
               f"{pct(b['most_cited_top_pick'])}{ci(res['baselines']['ci']['most_cited_top_pick'], pct)} | – | "
               f"{pct(bu['most_cited_top_pick'])} |")
    out.append(f"| – | always {b['majority_grade']} | {pct(b['majority_agreement'])} | 0 | – | – | "
               f"{pct(bu['majority_agreement'])} | – |")
    out.append(f"| – | random pick | – | – | – | {pct(b['chance_top_pick'])} | – | {pct(bu['chance_top_pick'])} |")
    first = next(iter(res["verdicts"].values()))["all"]
    out += ["", f"{first['candidates']} candidates described in the floras; \"same top pick\" is over the "
            f"{b['plants_with_choice']} plants with two or more such candidates.", ""]
    cc = res["category_counts"]
    out += [f"Pass A scores lower than the experts mainly through coverage: per candidate it finds "
            f"{cc['pass A']['positive']:.2f} categories with a positive average against the experts' "
            f"{cc['experts']['positive']:.2f} (pass E {cc['pass E']['positive']:.2f}), while negative categories are "
            f"about as rare ({cc['pass A']['negative']:.2f}, {cc['experts']['negative']:.2f}, "
            f"{cc['pass E']['negative']:.2f}). The modern descriptions were extracted by the experts only for the "
            f"characters in their own reading, so a statement of ours in any other category has nothing to be "
            f"matched against and counts as absent.", ""]
    for name, v in ((n, res["verdicts"][n]) for n in (PASS_E, PASS_A)):
        out += [f"Confusion, {name} (rows: experts, columns: ours):", "",
                "| | " + " | ".join(GRADES) + " |", "|---|" + "---|" * len(GRADES)]
        out += [f"| {e} | " + " | ".join(str(v["all"]["confusion"][e][o]) for o in GRADES) + " |" for e in GRADES]
        out.append("")

    out += ["## Stage B: matching single statements", "",
            "Each pair is one ancient statement from the experts' reading against the modern value for the same "
            "character, exactly the pairs the experts judged.", "",
            "| Matcher | Pairs compared | Agreement | κ | Weighted κ | Same direction | Agreement, unseen | Weighted κ, unseen |",
            "|---|---|---|---|---|---|---|---|"]
    for name, m in res["matching"].items():
        a, u, c = m["all"], m["unseen"], m["ci"]
        out.append(f"| {name} | {a['compared']} | {pct(a['agreement'])}{ci(c['agreement'], pct)} | {num(a['kappa'])} | "
                   f"{num(a['kappa_linear'])}{ci(c['kappa_linear'], num)} | {pct(a['direction_agreement'])} | "
                   f"{pct(u['agreement'])} | {num(u['kappa_linear'])} |")
    m = res["matching"]["Claude (pass E)"]["all"]
    out += ["", f"Of the {m['pairs']} pairs, the experts called {m['expert_absent']} \"absent\" although both texts "
            f"say something, and left {m['expert_missing']} without a call; pass E has no \"absent\" option, so "
            f"these are left out of the agreement figures.", "",
            "Confusion, Claude (pass E) (rows: experts, columns: ours):", "",
            "| | " + " | ".join(MATCH) + " |", "|---|" + "---|" * len(MATCH)]
    out += [f"| {e} | " + " | ".join(str(m["confusion"][e][o]) for o in MATCH) + " |" for e in MATCH + ["absent"]]
    out.append("")

    s, su = res["stability"]["all"], res["stability"]["unseen"]
    e1, e2 = res["verdicts"][PASS_E]["all"], res["verdicts"][REPEAT]["all"]
    m1, m2 = res["matching"]["Claude (pass E)"]["all"], res["matching"]["Claude (pass E, repeat run)"]["all"]
    out += ["## Run to run: pass E made twice", "",
            "Pass E was made a second time, in a new session, from the same blind batches and without opening the "
            "first run's calls (`data/llm/matching/expert_r2/`). The two runs are compared with each other, and each "
            f"with the experts. \"Unseen\" here also leaves out {', '.join(res['seen_before_repeat'])}, seen before the "
            f"repeat run, so it covers {res['plants']['unseen_repeat']} plants.", "",
            "| | All | Unseen |", "|---|---|---|",
            f"| Same call in both runs ({s['calls']} statement pairs) | {pct(s['same_call'])}{ci(s['ci']['same_call'], pct)} | {pct(su['same_call'])} |",
            f"| Weighted κ between the runs, calls | {num(s['kappa_linear'])} | {num(su['kappa_linear'])} |",
            f"| Same fit-or-contradiction in both runs | {pct(s['same_direction'])} | {pct(su['same_direction'])} |",
            f"| Same verdict in both runs ({s['candidates']} candidates) | {pct(s['same_grade'])}{ci(s['ci']['same_grade'], pct)} | {pct(su['same_grade'])} |",
            f"| Weighted κ between the runs, verdicts | {num(s['grade_kappa_linear'])} | {num(su['grade_kappa_linear'])} |",
            f"| Same best candidate in both runs | {pct(s['same_best'])}{ci(s['ci']['same_best'], pct)} | {pct(su['same_best'])} |",
            f"| Candidates whose agreement with the experts changed | {s['expert_agreement_changed']} | {su['expert_agreement_changed']} |",
            "",
            f"Against the experts, the first run gives the same call on {pct(m1['agreement'])} of statements and the "
            f"repeat run on {pct(m2['agreement'])}; the same verdict on {pct(e1['agreement'])} and {pct(e2['agreement'])} "
            f"of candidates; the same best candidate on {pct(e1['top_pick'])} and {pct(e2['top_pick'])} of plants.", ""]

    out += ["## Stage A: reading the Greek", "",
            "Which of the 36 characters (and 13 categories) our reading fills, against the experts' reading "
            "(Data file 3). This measures coverage, not whether the content agrees; content is tested by pass A above.", "",
            "| Level | Ours | Experts' | Shared | Precision | Recall | F1 | Recall, unseen |", "|---|---|---|---|---|---|---|---|"]
    for level in ("characters", "categories"):
        a, u = res["reading"]["all"][level], res["reading"]["unseen"][level]
        out.append(f"| {level} | {a['ours']} | {a['experts']} | {a['shared']} | {pct(a['precision'])} | "
                   f"{pct(a['recall'])} | {pct(a['f1'])} | {pct(u['recall'])} |")
    a = res["reading"]["all"]["characters"]
    out += ["", "Characters the experts filled and we did not, most often: "
            + ", ".join(f"{c} ({n})" for c, n in a["missed_most"]) + ".",
            "Characters we filled and the experts did not, most often: "
            + ", ".join(f"{c} ({n})" for c, n in a["added_most"]) + ".", ""]
    return "\n".join(out)


if __name__ == "__main__":
    main()
