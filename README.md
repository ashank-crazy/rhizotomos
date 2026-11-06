# Rhizotomos

[![reproduce](https://github.com/ashank-crazy/rhizotomos/actions/workflows/reproduce.yml/badge.svg)](https://github.com/ashank-crazy/rhizotomos/actions/workflows/reproduce.yml)

**Which plant did Dioscorides mean?** Rhizotomos has an AI model (Claude) repeat, step by step, the plant-identity
method that botanists at Kew and ZHAW applied by hand to 61 plants of Dioscorides' *De materia medica*, and checks
every step against the experts' own published data.

**Explorer:** https://ashank-crazy.github.io/rhizotomos/ · plant pages with the Greek, both readings and every
candidate species, plus the full validation.

Built for [EthnoHack 2026](https://ethnohack2026.devpost.com/), Track 1: Traditional Knowledge Mining.

## Why it matters

Any study that turns a historical remedy into a modern lead starts by deciding which species an old plant name
refers to. The usual answers come from dictionaries, and many are doubtful. Lardos et al. (2024) built a systematic
alternative: code what the ancient text says about each plant, code the same characters from modern floras, judge
every match, and score each candidate species. It is careful and slow, so it was applied to 61 plants. If a model
can do the same steps reliably, and we can measure how reliably, the method can reach the rest of the text.

Think of a line-up. The ancient description is the witness statement, the candidate species are the suspects, and
the experts have already solved 61 cases, so the detective can be scored.

## Results

The reference is the experts' botanical verdict (STRONG / MODERATE / WEAK) for each of the 122 candidates described
in the floras. Their scoring rule, re-applied in code to their published match calls, reproduces 117 of the 120
verdicts they published. Ranges are 95% bootstrap intervals over plants. Full tables: [RESULTS.md](RESULTS.md).

| Reading | Matching | Same verdict | Weighted κ | Same best candidate (31 plants) |
|---|---|---|---|---|
| experts' | **Claude** (pass E) | **76%** (68–84%) | **0.70** | **88%** (77–96%) |
| experts' | Claude (pass E, repeat run) | 79% (72–85%) | 0.73 | 86% (74–96%) |
| **Claude, from the Greek** | **Claude** (pass A) | **60%** (51–69%) | **0.50** | **80%** (67–91%) |
| experts' | everything called "good" | 61% | 0.45 | 78% |
| Claude's | everything called "good" | 52% | 0.33 | 74% |
| experts' | shared words | 28% | 0.00 | 63% |
| – | species most often proposed in the literature | – | – | 68% |
| – | always MODERATE / random pick | 42% | 0 | 57% |

- **Single statements.** On the 798 statement pairs the experts judged, Claude gives the same good / partial / no
  call 71% of the time (weighted κ 0.56), and agrees on whether a statement fits or contradicts in 92%. Matching by
  shared words agrees on 24%.
- **Calling everything "good" is a strong baseline**, because the experts' rule rewards how much a flora says about a
  candidate. Claude's matching adds 15 points of verdict agreement on the experts' reading and 8 on its own.
- **Reading the Greek is the harder step.** Claude's reading covers 83% of the organs and 67% of the characters the
  experts coded. The experts extracted modern descriptions only for the characters in their own reading, so
  anything else Claude reads has nothing to be matched against; per candidate it finds 3.25 agreeing organs against
  the experts' 4.14.
- **Not flattered by leakage.** On the 54 plants whose expert data was never seen during development, the figures
  are 78% (pass E) and 61% (pass A) for verdicts, 91% and 84% for the best candidate.
- **Stable from run to run.** Pass E was made a second time, in a new session, from the same blind batches. The two
  runs give the same call on 88% of the 800 statements (weighted κ 0.82), the same verdict for 89% of candidates
  (κ 0.86) and the same best candidate for 98% of plants. Against the experts the repeat run scores 70% on calls,
  79% on verdicts and 86% on the best candidate, so the headline figures are not one lucky run.
- Every one of the 699 statements Claude took from the Greek carries a quote that code found in the chapter.

## How it works

| Stage | What happens | Checked against |
|---|---|---|
| 0 Ingest | Wellmann's TEI edition → 827 chapters with their manuscript synonym lists (`ingest.py`) | – |
| Benchmark | The experts' data files → 61 plants, 141 candidates, readings, modern descriptions, calls, verdicts (`benchmark.py`) | Their published verdicts: 117/120 |
| A Read | Claude reads each chapter and sorts what it says into the experts' 36 characters, each with a Greek quote (`prompts/reading.md`, `data/llm/reading/`) | Data file 3: coverage; quotes checked by code |
| B Match | Each statement against each candidate's flora description: good / partial / no / absent, with the paper's definitions (`prompts/matching.md`, `data/llm/matching/`) | Data file 9: call by call |
| C Score | The experts' Stage 5 rule: average the calls in each of 13 organs, count organs that agree minus those that disagree; STRONG ≥ 5, MODERATE 3–4, WEAK ≤ 2 (`benchmark.verdict`) | Data file 11 |

Two passes keep the stages apart. **Pass A** matches Claude's own reading (end to end); **pass E** matches the
experts' reading, which isolates the matching step. Pass A was done first. Pass E was later repeated in a new
session (`data/llm/matching/expert_r2/`) to measure run-to-run variation.

**Blind by design.** Candidates appeared only as anonymous labels (`P07-C2`) in a shuffled order; Claude never saw
their names, the experts' calls or verdicts while making calls. No expert call or verdict was opened until both
passes were complete, and the calling rules were written into `prompts/matching.md` before that. Seven plants had
some expert data looked at while the code was being built; they are listed in `data/llm/contamination.json` and every
figure is also reported without them. The same file lists the one further plant seen before the repeat run.

## Reproduce

Everything model-made is committed, so every number rebuilds without a model, an API key or the network:

```bash
make setup   # python3 -m venv .venv && pip install -r requirements.txt
make all     # ingest -> benchmark -> check -> evaluate -> site
make serve   # the explorer at http://localhost:8000
```

`make all` rewrites `data/derived/`, `RESULTS.md` and `docs/data.js`; two runs give identical files, on Python
3.11, 3.12 and 3.13 alike. GitHub Actions (`.github/workflows/reproduce.yml`) reruns `make all` on every push and
fails if any committed file changes.

## Repository

```
src/rhizotomos/   ingest.py, benchmark.py, reading.py, matching.py, baseline.py, evaluate.py, site.py
prompts/          reading.md and matching.md: the instructions Claude followed
data/raw/         the Greek TEI text and the Lardos et al. research data, unchanged
data/llm/         Claude's readings (61 plants) and match calls (733 in pass A, 800 in pass E, 800 in its repeat run),
                  contamination.json
data/derived/     chapters, benchmark.json, results.json
docs/             the static explorer (GitHub Pages)
```

## AI use and what already existed

- **Claude (Opus 5.5) in Claude Code** wrote the code and the explorer, read the Greek of the 61 chapters, and made
  all 2,333 match calls (pass A, pass E and its repeat run). The project had no API budget, so the readings and calls
  were made inside Claude Code sessions rather than through an API, following the prompts in `prompts/`, and are
  committed as data.
- **Already existing:** the Greek text (Wellmann's edition, digitised by First1KGreek), the method, the expert data
  and the scoring rule (Lardos et al. 2024), and the Python libraries pandas, openpyxl and lxml.

## Limitations

- The modern side is the experts' extraction from the floras, which covers only characters in their own reading, so
  Claude's own reading is penalised for statements outside it. Matching against descriptions Claude extracts itself
  is untested.
- One model made every reading and call. Pass E was made twice (88% of calls and 89% of verdicts the same), but the
  reading of the Greek and pass A were made once, so their run-to-run variation is not measured. The calling rules
  were refined during the first batches (and earlier batches brought into line), all before any expert result was
  opened.
- 61 plants and 122 scored candidates is a small benchmark, and the intervals are wide.
- This reproduces the experts' botanical Stage 5 only. Their final identifications also weigh medicinal uses and
  expert review.
- Identifications are hypotheses about historical texts. Nothing here is medical advice or a claim that a plant is
  safe or effective.

## Sources and licences

- Lardos A, Patmore K, Allkin R, Lazarou R, Nesbitt M, Scott AC, Zipser B (2024). A systematic methodology to assess
  the identity of plants in historical texts: a case study based on the Byzantine pharmacy text John the Physician's
  Therapeutics. *Journal of Ethnopharmacology* 322: 117622.
  [doi:10.1016/j.jep.2023.117622](https://doi.org/10.1016/j.jep.2023.117622). Article and research data CC BY 4.0.
- Dioscorides, *De materia medica*, ed. M. Wellmann (1906–1914), via
  [First1KGreek](https://github.com/OpenGreekAndLatin/First1KGreek), CC BY-SA 4.0.
- Code: MIT ([LICENSE](LICENSE)). Data licences in detail: [DATA_LICENSES.md](DATA_LICENSES.md).
