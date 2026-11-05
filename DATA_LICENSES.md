# Data and licences

The code in this repository is MIT licensed (see `LICENSE`). The data comes from two open sources, each under its
own licence, and everything derived from it keeps that licence.

| Data | Source | Licence | Where it is used |
|---|---|---|---|
| Greek text of Dioscorides, *De materia medica*, ed. M. Wellmann (1906–1914), TEI XML `tlg0656.tlg001.1st1K-grc1.xml` | [First1KGreek](https://github.com/OpenGreekAndLatin/First1KGreek) (Open Greek and Latin) | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) | `data/raw/first1k/`; derived: `data/derived/dmm_chapters.jsonl`, the Greek quotes in `data/llm/reading/`, the chapter text in `docs/data.js` |
| Research data of Lardos et al. (2024), Data files 1–11 and the directory PDF | [figshare, article 23736189](https://figshare.com/articles/dataset/23736189) | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | `data/raw/figshare/`; derived: `data/derived/benchmark.json`, `data/derived/results.json`, the expert readings, modern descriptions, calls and verdicts in `docs/data.js` |
| Method and match definitions | Lardos A, Patmore K, Allkin R, Lazarou R, Nesbitt M, Scott AC, Zipser B (2024). A systematic methodology to assess the identity of plants in historical texts: a case study based on the Byzantine pharmacy text John the Physician's Therapeutics. *Journal of Ethnopharmacology* 322: 117622. [doi:10.1016/j.jep.2023.117622](https://doi.org/10.1016/j.jep.2023.117622) | CC BY 4.0 | `prompts/matching.md` quotes the match definitions of section 5.1 |

Because the derived files mix both sources, treat `data/derived/`, `data/llm/` and `docs/data.js` as CC BY-SA 4.0
with attribution to both: the First1KGreek project for the Greek text, and Lardos et al. (2024) for the expert
data. The readings and match calls in `data/llm/` were made by Claude (Anthropic) for this project.

The modern plant descriptions inside the Lardos et al. data were extracted by those authors from *Flora of Turkey and
the East Aegean Islands* (Davis, ed.) and *Flora of Cyprus* (Meikle); only the short excerpts in their published
data are used here.
