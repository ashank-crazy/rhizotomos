# Rebuild every derived file and number from the committed raw data, readings and calls. No model or network needed.
PY = PYTHONPATH=src .venv/bin/python

.PHONY: all setup ingest benchmark check evaluate site serve

all: ingest benchmark check evaluate site

setup:
	python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

ingest:      # Greek TEI -> data/derived/dmm_chapters.jsonl
	$(PY) -m rhizotomos.ingest

benchmark:   # expert data -> data/derived/benchmark.json (also re-derives the experts' verdicts: 117/120)
	$(PY) -m rhizotomos.benchmark

check:       # every Greek quote occurs in its chapter; every pair has exactly one allowed call
	$(PY) -m rhizotomos.reading check
	$(PY) -m rhizotomos.matching check ai
	$(PY) -m rhizotomos.matching check expert
	$(PY) -m rhizotomos.matching check expert_r2

evaluate:    # -> data/derived/results.json and RESULTS.md
	$(PY) -m rhizotomos.evaluate

site:        # -> docs/data.js for the explorer
	$(PY) -m rhizotomos.site

serve:
	python3 -m http.server 8000 --directory docs
