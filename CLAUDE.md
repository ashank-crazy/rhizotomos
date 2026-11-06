# CLAUDE.md

Guidance for Claude Code working in this repository. [README.md](README.md) explains the project for people and
[RESULTS.md](RESULTS.md) holds the numbers. [AGENTS.md](AGENTS.md) is the original plan and is out of date: it
describes stages that were never built.

## What this is

Rhizotomos repeats the plant-identity method of Lardos et al. (2024) on the Greek of Dioscorides' *De materia
medica* and scores every step against the experts' published data. Claude reads the Greek (Stage A), Claude matches
each statement against each candidate's flora description in two blind passes (Stage B), and the experts' own
Stage 5 rule, in code, scores the candidates (Stage C). Built for EthnoHack 2026, Track 1.

## Commands

```bash
make setup   # python3 -m venv .venv && pip install -r requirements.txt
make all     # ingest -> benchmark -> check -> evaluate -> site
make check   # every Greek quote occurs in its chapter; every pair has exactly one allowed call
make serve   # the explorer at http://localhost:8000
```

Modules run as `PYTHONPATH=src .venv/bin/python -m rhizotomos.<module>`. `reading show N` and
`matching show ai|expert N` print batch N exactly as the model was given it.

There are no tests besides `make check`. `make all` must run clean, without a model or the network, and two runs
must give byte-identical files on any Python from 3.11 to 3.13 (floats are summed with `math.fsum` and rounded
before writing). CI (`.github/workflows/reproduce.yml`) enforces this on every push.

## Layout

| Path | What it holds |
|---|---|
| `src/rhizotomos/ingest.py` | Wellmann TEI → `data/derived/dmm_chapters.jsonl` (827 chapters, manuscript synonym lists) |
| `src/rhizotomos/benchmark.py` | Expert data files → `data/derived/benchmark.json`; `verdict()` is the experts' scoring rule |
| `src/rhizotomos/reading.py`, `matching.py` | Show batches to the model and check what came back |
| `src/rhizotomos/baseline.py` | Word-overlap and "everything good" matchers |
| `src/rhizotomos/evaluate.py` | Metrics, bootstrap intervals, baselines → `data/derived/results.json`, `RESULTS.md` |
| `src/rhizotomos/site.py` | Everything the explorer needs → `docs/data.js` |
| `prompts/` | The reading and matching instructions Claude followed |
| `data/raw/` | The Greek TEI (First1KGreek) and the Lardos et al. figshare files, unchanged |
| `data/llm/` | Claude's readings (`reading/`), match calls (`matching/ai/` = pass A, `matching/expert/` = pass E, `matching/expert_r2/` = a second, independent run of pass E), `contamination.json` |
| `docs/` | The static explorer, served by GitHub Pages from `main` `/docs` |
| `SUBMISSION.md` | Devpost copy, pitch-video script, live-demo script |

## Rules that keep the results honest

- Never edit generated files by hand: `data/derived/`, `RESULTS.md` and `docs/data.js`. Change the code and run
  `make all`.
- `data/raw/` is source data. Leave it unchanged.
- `data/llm/` is the output under test. Do not change a reading or call after looking at expert data. If a rule in
  `prompts/matching.md` changes, apply it to every batch and record that in the prompt's closing note.
- Keep the matching blind: candidates appear only as anonymous labels (`P07-C2`) in shuffled order, with no species
  names, expert calls or verdicts shown while calls are made. Pass A is made before pass E.
- Any plant whose expert reading, calls or verdicts (data files 3, 9, 11) are looked at during development goes into
  `data/llm/contamination.json`, and every figure is also reported without those plants. A new run of calls gets
  its own list there (`repeat_run_plants` for `expert_r2`), since the explorer shows expert verdicts per plant.
- Every statement in a reading carries a Greek quote that must occur in its chapter; `make check` enforces this.
- Report each Claude figure beside its baselines (everything "good", shared words, most cited, always MODERATE, random
  pick) and with 95% bootstrap intervals over plants (2,000 resamples, seed 0).
- Keep output deterministic: sort before writing, and never rely on set or dict iteration order for ties
  (see `most_common` in `evaluate.py`).
- When the numbers change, bring `README.md`, `SUBMISSION.md` and the slide deck in line with `RESULTS.md` by hand.

## Conventions

- Python with pandas, openpyxl and lxml only, pinned in `requirements.txt`. No scipy: Spearman is Pearson on ranks.
- The explorer is plain HTML, CSS and JavaScript with no framework and no build step; its data is
  `window.RHIZOTOMOS` from `docs/data.js`. Keep both light and dark themes, a table alongside every chart, and no
  horizontal scroll at 375px wide.
- Licences: code MIT; the Greek text and anything derived from it CC BY-SA 4.0; the figshare data CC BY 4.0. Credit
  both sources, as in `DATA_LICENSES.md`.
- No medical claims anywhere. Identifications are hypotheses about historical texts, not advice on any plant.
