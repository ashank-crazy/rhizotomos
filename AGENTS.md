# Rhizotomos — project brief

> **Status, 5 Nov 2026.** This is the original plan. The project had no API budget, so the plan changed: Claude
> read the Greek and made every match call inside a Claude Code session, for the 61 benchmark plants only, and
> the results are committed as data. Built: ingest, benchmark, Stage A (reading), Stage C (matching, two blind
> passes), the experts' own Stage 5 scoring rule in place of a new ranking model, baselines, evaluation and the
> explorer. Not built: the GBIF/POWO prior, the trained Stage D model, Stage E (all of DMM) and Stage F. See
> README.md for what exists and RESULTS.md for the numbers. Note the stage letters below differ from the README's.

**Which plant did Dioscorides mean?** Rhizotomos uses an LLM and open biodiversity data to automate the plant-identity
method of Lardos et al. (2024, Kew + ZHAW). It checks every stage against those experts' own data, then extends the
method from their 61 plants to the whole of Dioscorides' *De materia medica* (DMM, 1st c. CE).

- Hackathon: EthnoHack 2026 (https://ethnohack2026.devpost.com/), **Track 1 — Traditional Knowledge Mining**
- Deadline: **Sun 8 Nov 2026, 10:00 CET (09:00 UTC, 14:30 IST)**. Late submissions are rejected. Plan to submit Saturday night.
- Each team can win only one prize, so the target is the Track 1 first prize (€2,000).

## The problem we pitch

Any study that turns an ancient remedy into a modern lab lead depends on knowing which species an ancient plant
name refers to. Lardos et al. show that the standard dictionary identifications are often doubtful. Their fix was a
six-stage method: code the plant descriptions in DMM, code the same characters from modern floras, judge each
character match, and rank the candidate species. They did all of it by hand, for 61 DMM plants, in a project funded
by the Wellcome Trust. We automate that method, measure how often it agrees with their experts, and run it on every
plant chapter. Pitch line: *every "ancient remedy → modern drug" pipeline inherits these misidentifications.*

## Data (all open; cite every source in the README and in DATA_LICENSES.md)

1. **Greek text of DMM.** Wellmann edition (1906–14) from First1KGreek, licensed CC BY-SA 4.0.
   https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/master/data/tlg0656/tlg001/tlg0656.tlg001.1st1K-grc1.xml
   - TEI layout: `div[subtype=book]` covers books 1–5 and `div[subtype=chapter][n]` gives 835 chapters, plus a preface.
     Chapter `n` restarts in each book, so build ids as `"{book}.{chapter}"`. Sections are `div[subtype=section]`.
   - `<note type="footnote">` holds the critical apparatus. Notes that begin with **`RV:`** are the Recensio Vulgaris
     synonym lists, which give Greek, "Romans" (Latin), Egyptian and Dacian names. Store these separately as
     `rv_synonyms`. Remove every other note from the text.
   - Drop `<del>` content and keep `<add>`. `<lb>` and `<pb>` are line and page breaks.
2. **Expert benchmark.** Lardos et al. raw research data on figshare, licensed CC BY 4.0, a 2.77 MB zip:
   https://figshare.com/ndownloader/articles/23736189?private_link=2e0f64b5794892ed4679
   Read `Directory to the Research Data.pdf` first. The files that matter:
   - DF2 `Plant names JC-DMM`: links the 13th-century Byzantine text *John the Physician's Therapeutics* (JC) to
     DMM plants. DMM chapters are numbered as in Beck (2005), which should match Wellmann. Check this by Greek name.
   - DF3 `DMM plant descriptions`: expert coding of DMM characters. This is the **gold standard for Stage A**.
   - DF4 / DF8: historical and modern medicinal uses, coded into 21 categories. Reuse those categories.
   - DF5 `List of candidate plants and MPNS validation`: the 130 candidate species and their accepted names.
   - DF6 `Modern plant descriptions`: characters coded from Flora of Turkey and Flora of Cyprus. Use this as the
     modern side of the benchmark.
   - DF9 `Botanical comparative analysis`: 1,213 expert match calls (good / partial / no / absent). This is the
     **gold standard for Stage C**.
   - DF11 `Statistical evaluation`: a Strong / Moderate / Weak verdict for each candidate. This is the **gold
     standard for Stage D**.
3. **The paper itself** for the method definitions: Lardos et al., *J Ethnopharmacol* 322:117622 (2024), CC BY,
   doi:10.1016/j.jep.2023.117622. Section 2.2 has the six stages and the match definitions.
4. **GBIF API** (no key needed): `api.gbif.org/v1/species/match?name=` and occurrence counts per country with
   `occurrence/search?taxonKey=…&country=GR&limit=0`. Use GR, CY, TR, LB, SY, IL, JO, EG and IT for the Eastern
   Mediterranean prior. Dioscorides came from Cilicia, in present-day Turkey.
5. **POWO** (Kew, via `pykew`): accepted names, native range as WGSRPD codes, and descriptions where they exist.
   **Wikidata / Wikipedia**: Modern Greek vernacular names, plus open descriptions for species outside the benchmark.

## Pipeline

| Stage | What it does | Checked against |
|---|---|---|
| 0 Ingest | TEI → `data/dmm_chapters.jsonl` `{id, book, chapter, text, rv_synonyms}` | — |
| A Extract | LLM reads the Greek of each chapter and returns JSON: `is_plant`, `names`, `characters{life_form, habit, height, stem, leaf, flower, fruit, seed, root, habitat, geography}`, `uses[{indication, part, preparation, category}]` and "like plant X" comparisons. **Every value carries `greek_quote`, which must be an exact substring of the chapter.** Code rejects any quote that is not. | DF3: precision and recall for each character type, on the benchmark plants |
| B Modern coding | Benchmark: take DF6 as it is. Scaling: the LLM codes the same schema from POWO and Wikipedia descriptions. Report the "absent" rate (the experts had 33% absent). | DF6, on benchmark species coded from open sources |
| C Match | For each pair of DMM character and candidate character, return good / partial / no / absent, using the rubric from the paper | DF9: Cohen's κ and a confusion matrix over 1,213 items |
| D Rank | Interpretable score for each candidate from botanical match counts, use congruence and the Eastern Mediterranean GBIF/POWO prior. Logistic or ordinal model with **leave-one-name-out CV**, giving calibrated probabilities. | DF11: agreement with the experts' "Strong" picks, Spearman correlation with S/M/W, calibration plot |
| E Scale | For every plant chapter, the LLM proposes 1–8 candidate species from the scholarship. Each one is resolved through GBIF/POWO, and unresolvable names are dropped. Then run A–D. Output `data/atlas.json`. Flag a chapter **contested** when top-1 < 0.6 or the top two are within 0.15. | — |
| F Bridge (stretch) | For contested chapters, count PubMed hits (E-utilities) for each candidate × use. Show cases where the choice of species changes what evidence exists. Make no efficacy claims. | — |

Ablations and baselines for Stage D. These are where the scientific credibility comes from, so do not skip them:
- botanical only → + uses → + geography
- baseline 1: the first or dictionary identification
- baseline 2: **ask the LLM zero-shot "which species is this?"** We must show what the evidence-grounded method adds.
  If it adds nothing, say so honestly and lean on auditability and calibrated uncertainty instead.

## Explorer (static site on GitHub Pages; no backend)

- Search by Greek name, modern binomial or chapter id.
- Chapter page: Greek text with evidence spans highlighted by character, RV synonyms, ranked candidates with
  probability bars, a table of matches for each character, a native-range map, and the **name chain**:
  DMM name → JC 13th-century name (from DF2) → Modern Greek vernacular (from Wikidata) → accepted binomial.
- Validation page: every benchmark metric, the confusion matrices and the ablation table.
- Atlas page: all chapters sorted by confidence, with the contested list.

## Rules to obey

- Use a public repo. Code is MIT licensed. Excerpts of the Greek text and data derived from it are CC BY-SA 4.0.
  Figshare-derived data is CC BY 4.0 with attribution. List every licence in `DATA_LICENSES.md`.
- The README must state which AI tools were used and for what (Codex for development, plus the LLM in the
  pipeline), and which parts already existed (datasets, libraries).
- **Cache every LLM response** in a committed JSONL file keyed by `(model, prompt_hash)`, so judges can rerun the whole
  pipeline without an API key. Use numbered scripts or `make all` to reproduce every number in the README.
- Present no prediction as medical fact. Show uncertainty and limitations everywhere.

## Schedule

- **Tue 3 Nov:** Stage 0, then Stage A on the benchmark plants, with Stage A metrics.
- **Wed 4 Nov:** Stages C–D on the benchmark, giving the first table of metrics and ablations. Have Claude review it.
- **Thu 5 Nov:** Stage E across all of DMM, producing `atlas.json`.
- **Fri 6 Nov:** Build and deploy the explorer. Do Stage F if there is time.
- **Sat 7 Nov:** README, slide deck (at most 10, as PDF), pitch video (at most 10 min on YouTube, unlisted), a 2–3 min
  demo cut for the live judging presentation, and the Devpost page. **Submit.**
- **Sun 8 Nov morning:** buffer only. The deadline is 10:00 CET.

Slide outline: hook → problem → data → method → validation numbers → demo → atlas findings → one contested case study
→ limitations → impact and next steps (ETHCSTWIN database, other Byzantine texts).
