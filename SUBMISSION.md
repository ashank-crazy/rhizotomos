# Submission kit

Copy for the Devpost page, the pitch video's narration and the live-demo script. Every number matches
[RESULTS.md](RESULTS.md); after rerunning the pipeline, check them again.

## Devpost page

| Field | Text |
|---|---|
| Project name | Rhizotomos |
| Elevator pitch | Which plant did Dioscorides mean? Claude repeats the Kew/ZHAW plant-identity method on the Greek of *De materia medica*, and every step is scored against the experts' own data. |
| Challenge track | Track 1: Traditional Knowledge Mining |
| Try it out | https://ashank-crazy.github.io/rhizotomos/ and https://github.com/ashank-crazy/rhizotomos |
| Built with | python, pandas, lxml, openpyxl, tei-xml, javascript, html, css, github-pages, github-actions, make, claude, claude-code |
| Video | https://youtu.be/38F6FljmmDI |
| Slides | the 10-slide PDF, `rhizotomos-deck.pdf` |
| Team | Sanchay Singh and Ashank Kumar |

### About the project

Paste the block below into Devpost's "About the project" box (it accepts Markdown). The first seven headings are
Devpost's own; the last four cover what the rules ask for: limits, data sources, AI use and the team.

~~~markdown
## Inspiration

Every study that turns a historical remedy into a modern lead, whether in natural-product chemistry, pharmacology or the history of medicine, first has to decide which species an old plant name refers to. Take κυκλάμινος (*De materia medica* 2.164). Dioscorides describes leaves like ivy, mottled with whitish spots, a bare stem four fingers long, purplish flowers and a black, somewhat flat root, and scholars have proposed five different *Cyclamen* species for it. Whatever is looked up next is looked up under one of those names, and the usual answers come from dictionaries, many of them doubtful.

In 2024, botanists at Kew and ZHAW (Lardos et al.) published a systematic way to decide, and applied it by hand to 61 plants. It is careful and slow. They also published every match call and verdict under CC BY, which turns their work into an answer key. That gave us a question we could actually test: can an AI model do the same job, and how close does it come?

## What it does

**Rhizotomos** (ῥιζοτόμος, "root-cutter", the ancient Greek word for a herbalist) has Claude repeat the experts' method step by step on the Greek of Dioscorides' *De materia medica*, and scores every step against the experts' own data. Think of a line-up: the ancient description is the witness statement, the candidate species are the suspects, the match calls are the evidence and the experts' score is the verdict.

1. **Read (Claude).** Sorts each Greek chapter into the experts' 36 characters across 13 organs. Every statement quotes the Greek, and code checks that all 699 quotes occur in their chapter.
2. **Match (Claude, blind).** Calls each statement against each candidate's description in the Flora of Turkey or the Flora of Cyprus: good, partial, no or absent, with the paper's definitions.
3. **Score (code).** The experts' own rule: organs that agree minus organs that disagree. STRONG is 5 or more, MODERATE 3 to 4, WEAK 2 or less. Applied to the experts' own calls, it reproduces 117 of their 120 verdicts.

Two passes keep the stages apart. **Pass E** matches the experts' reading, which tests the matching step alone. **Pass A** matches Claude's own reading, end to end from the Greek.

The **explorer** has a page for each of the 61 plants: the Greek chapter with every quote highlighted and linked to its statement, Claude's reading next to the experts', and every candidate with its grade from the experts and from both passes. Opening a candidate shows each statement, the flora's words and both calls side by side, with disagreements highlighted. The Validation page has every figure with its interval and baselines.

**Results** over the 122 candidates described in the floras. Ranges are 95% bootstrap intervals over plants.

| Reading | Matching | Same verdict | Same best candidate (31 plants) |
|---|---|---|---|
| experts' | **Claude** (pass E) | **76%** (68–84%) | **88%** (77–96%) |
| experts' | Claude (pass E, repeat run) | 79% (72–85%) | 86% (74–96%) |
| **Claude, from the Greek** | **Claude** (pass A) | **60%** (51–69%) | **80%** (67–91%) |
| experts' | everything called "good" | 61% | 78% |
| Claude's | everything called "good" | 52% | 74% |
| experts' | shared words | 28% | 63% |
| – | species most often proposed in the literature | – | 68% |
| – | always MODERATE / random pick | 42% | 57% |

## How we built it

- **Data.** Wellmann's edition of *De materia medica* as TEI XML from First1KGreek: 827 chapters, each with its manuscript synonym lists. The experts' figshare files become the benchmark: 61 plants, their reading, the candidate species, the flora descriptions, 1,186 match calls and the verdicts.
- **Pipeline.** Python with pandas, openpyxl and lxml for ingestion, the benchmark, scoring and evaluation, with bootstrap intervals (2,000 resamples) and five baselines, run end to end by a Makefile.
- **The model's work.** Claude (Opus 5.5) in Claude Code read the 61 chapters and made all 2,333 match calls (pass A, pass E and a repeat run of pass E), following the prompts in the repository. We had no API budget, so the readings and calls were made inside Claude Code sessions and committed as data. Claude also wrote the code and the explorer.
- **Blind by design.** Candidates appeared only as anonymous labels (P07-C2) in shuffled order, with no species names, expert calls or verdicts. Pass A was made before pass E, and no expert call or verdict was opened until both passes were complete.
- **The explorer.** Plain HTML, CSS and JavaScript with no framework and no backend, on GitHub Pages, in light and dark themes.
- **Reproducible.** `make all` rebuilds every number offline, without a model, an API key or the network, and two runs give byte-identical files. GitHub Actions reruns the whole pipeline on Python 3.11, 3.12 and 3.13 on every push and fails if any committed number changes.

## Challenges we ran into

- **Staying blind while building the benchmark.** The code that turns expert data into a benchmark has to look at that data. Seven plants had some expert data seen during development. We listed them in the repository and report every figure without them as well.
- **Consistent judgement.** Calls like "purplish" against "pale pink", or "rough" against "pubescent", need the same answer every time. We wrote the recurring decisions into the matching prompt as rules while the first batches were being called, before any expert call had been seen, and brought the earlier batches into line with them.
- **A baseline that is hard to beat.** Calling every statement "good" already gets 61% of verdicts, because the experts' rule rewards how much a flora says. Every claim has to be made against that, not against chance.
- **The modern side covers only the experts' reading.** The experts extracted flora text only for the characters in their own reading, so anything else Claude reads in the Greek has nothing to be matched against and counts as absent. This is mainly why pass A scores lower.
- **The same numbers on every machine.** Floats are summed with `math.fsum` and rounded, and everything is sorted before it is written, so Python 3.11, 3.12 and 3.13 give identical files.

## Accomplishments that we're proud of

- Matching the experts' reading, Claude gives the same verdict for **76%** of candidates and picks the same best candidate for **88%** of plants: 15 points above calling everything "good" on verdicts.
- From the Greek alone, end to end, the figures are **60%** and **80%**.
- The results hold where they could have been flattered. On the 54 plants nobody looked at during development, pass E scores 78% and 91%, and pass A 61% and 84%.
- A second, independent run of pass E gives the same call as the first on 88% of 800 statements (weighted κ 0.82) and the same best candidate for 98% of plants, so the headline is not one lucky run.
- All 699 Greek quotes are verified in their chapters, the scoring code reproduces 117 of the experts' 120 verdicts, and one command rebuilds every number offline.

## What we learned

- **Reading the Greek is the harder step.** Given the experts' reading, Claude's single calls agree with theirs 71% of the time (weighted κ 0.56), and on fit versus contradiction 92% of the time. Claude's own reading covers 83% of the organs and 67% of the characters the experts coded, and that is where pass A loses ground.
- **Baselines change the story.** Without the "everything good" baseline, 76% would look like more than it is. Anyone using the method, by hand or with a model, should know that its rule favours candidates whose floras say more.
- **Scoring absorbs noise.** Between two runs, 88% of single calls agree but 98% of best candidates do, so the verdicts are more stable than the calls they are built from.
- **Open expert data makes AI work checkable.** Because Lardos and colleagues published every call and verdict, each step could be scored on its own, not only the final answer.

## What's next for Rhizotomos

- **The whole book.** All 827 chapters are already ingested with their manuscript synonym lists. Next, read every plant chapter and score the candidates scholars have proposed for it.
- **Triage for specialists.** Flag the chapters where the usual identification fits the Greek worst, so scarce expert time goes where the doubt is greatest.
- **Other herbals.** Nothing in the steps is specific to Dioscorides: John the Physician, Galen and later Byzantine pharmacy texts can go through them too.
- **A stronger modern side.** Extract flora descriptions for every candidate from open sources, and repeat the reading step to measure its variation too.

Firmer identifications help every study that starts from a historical remedy, from natural-product chemistry to the history of medicine.

## Limitations

- The modern side is the experts' extraction from the floras, which covers only characters in their own reading. Matching against descriptions Claude extracts itself is untested.
- One model made every reading and call. Pass E was made twice, but the reading of the Greek and pass A were made once, so their run-to-run variation is not measured.
- 61 plants and 122 scored candidates is a small benchmark, and the intervals are wide.
- This reproduces the experts' botanical scoring only. Their final identifications also weigh medicinal uses and expert review.
- Identifications are hypotheses about historical texts. Nothing here is medical advice or a claim that a plant is safe or effective.

## Data sources

- Dioscorides, *De materia medica*, ed. M. Wellmann (1906–1914), TEI XML from First1KGreek (Open Greek and Latin), CC BY-SA 4.0.
- Lardos A, Patmore K, Allkin R, Lazarou R, Nesbitt M, Scott AC, Zipser B (2024). A systematic methodology to assess the identity of plants in historical texts: a case study based on the Byzantine pharmacy text John the Physician's Therapeutics. *Journal of Ethnopharmacology* 322: 117622, doi:10.1016/j.jep.2023.117622. Article and research data (figshare) CC BY 4.0: the expert reading, the candidate lists, modern descriptions from Flora of Turkey and Flora of Cyprus, the match calls and the verdicts.

## AI use and what already existed

- **Claude (Opus 5.5) in Claude Code** wrote the code and the explorer, read the Greek of the 61 chapters and made all 2,333 match calls (pass A, pass E and its repeat run). With no API budget, the readings and calls were made inside Claude Code sessions, following the prompts in the repository, and committed as data. Claude also made the slide deck and the pitch video, whose narration is a synthetic voice (Deepgram Aura-2) reading our script.
- **Already existing:** the Greek text and its digitisation, the method, the expert data and the scoring rule (Lardos et al. 2024), and the Python libraries.
- **Built during the hackathon:** ingestion, the benchmark, the reading and matching prompts and their outputs, the repeat run, the scoring and evaluation code, the baselines, the explorer, the CI check and the documentation.

## Team

Sanchay Singh and Ashank Kumar.
~~~

## Pitch video

https://youtu.be/38F6FljmmDI · 7 minutes 4 seconds (the limit is 10), 1920 × 1080 with burned-in captions. The
narration is a synthetic voice (Deepgram Aura-2) reading the script below, and the end card says so. The pictures are
the deck's slides, except part 5, which is real footage of the explorer recorded in a browser and timed to the
narration.

| Part | Starts | On screen |
|---|---|---|
| 1 | 0:00 | Slide 1, title |
| 2 | 0:29 | Slide 2, one name, five species |
| 3 | 1:09 | Slide 3, the line-up |
| 4 | 1:56 | Slide 4, the three stages and two passes |
| 5 | 2:50 | The explorer: search, κυκλάμινος, its candidates, the matches, the Greek, Validation |
| 6 | 4:00 | Slide 6, headline results |
| 7 | 4:33 | Slide 7, baselines |
| 8 | 5:04 | Slide 8, six checks |
| 9 | 5:44 | Slide 9, what this does not show |
| 10 | 6:21 | Slide 10, next steps and thanks |
| 11 | 6:55 | End card: links, team, AI use and data credits |

**1. Title.** Rhizotomos is the ancient Greek word for a root-cutter: a herbalist. Our question sits under every study
that starts from an ancient remedy. When Dioscorides described a plant two thousand years ago, which species did he
mean? We had Claude repeat, step by step, a method botanists published in 2024 for answering exactly that, and we
scored every step against the experts' own data.

**2. One name, five species.** Take one chapter. Dioscorides calls this plant kyklaminos: leaves like ivy, mottled
with whitish spots, a bare stem four fingers long, purplish flowers, and a black, somewhat flat root. Scholars have
proposed five different species of Cyclamen for it. Whichever one a study picks, everything after it inherits that
choice, and the usual answers come from dictionaries, many of them doubtful. In 2024, botanists at Kew and ZHAW
published a systematic way to decide, and applied it by hand to 61 plants.

**3. The line-up.** Think of their method as a police line-up. The ancient description is the witness statement,
coded into 36 characters, from height and leaf shape to flower colour, root and habitat. The suspects are the species
proposed before, each described from the floras of Turkey and Cyprus. Every statement is checked against every
suspect: good, partial, no, or absent from the flora. Then a fixed rule turns the evidence into a verdict, strong,
moderate or weak, by counting the organs that agree minus those that disagree. The experts published every one of
their 1,186 calls, and every verdict, under an open licence. For us, that is an answer key.

**4. Three stages, two passes.** Rhizotomos hands each of those steps to Claude, and checks every one. In stage A,
Claude reads Wellmann's Greek and sorts each chapter into the same 36 characters, quoting the text; code confirms that
all 699 quotes occur in their chapter. In stage B, Claude matches each statement against each candidate's flora
description, blind: candidates appear only as anonymous labels, in shuffled order. In stage C, the experts' own
scoring rule, in code, turns the calls into verdicts. On the experts' own calls it reproduces 117 of their 120. We run
this two ways. Pass E gives Claude the experts' reading, to test the matching alone. Pass A starts from Claude's own
reading of the Greek.

**5. The explorer.** This is the explorer, a static site with a page for each of the 61 plants. Search by a Greek,
English or Latin name, and open kyklaminos. *(Types "cyclamen", opens κυκλάμινος.)* The experts rate Cyclamen graecum
first, with a score of 6, then hederifolium and persicum at 5, and cyprium at 0. Given the experts' reading, Claude's
calls produce exactly the same four scores. From the Greek alone, Claude scores them 5, 4, 4 and 0: two verdicts drop
a grade, but graecum still comes first. Open a candidate, and every statement is there: the experts' reading, the
flora text it was matched against, and both calls side by side. Highlighted rows are where Claude disagrees. Below is
the Greek itself. Every quote Claude used is highlighted, and pointing at one finds its row in the reading. And the
validation page holds every figure in this film, each beside its baselines and with its interval.

**6. Headline results.** Across all 61 plants, here is the result. Matching the experts' reading, Claude gives the
same verdict for 76% of the 122 candidates, and picks the same best candidate for 88% of the 31 plants with a choice
to make. From the Greek, end to end, the figures are 60 and 80%. The ranges are bootstrap intervals over plants, and
on the 54 plants nobody looked at during development, the figures hold.

**7. Baselines.** Those numbers only mean something next to baselines. The strongest is surprisingly simple: call
every statement good. Because the experts' rule rewards how much a flora says, that alone gets 61% of verdicts.
Claude's matching adds 15 points over it on the experts' reading, and 8 on its own. Shared words get 28%. For the best
candidate, the species most often proposed before is right 68% of the time, and a random pick 57.

**8. Six checks.** Six checks sit behind those numbers. Every Greek quote is found in its chapter. The scoring code
reproduces 117 of 120 verdicts. The matching is blind. Leave out the seven plants seen during development, and pass E
scores 78 and 91%. We made pass E a second time, in a new session: 88% of calls and 98% of best candidates came out
the same. And one command rebuilds every number offline, without a model or an API key, which GitHub Actions checks
on every push.

**9. Limits.** What this does not show. Reading the Greek is the harder step: Claude's reading covers 83% of the
organs the experts coded, and that is where pass A loses ground. The modern side is still the experts' extraction from
the floras, so Claude extracting its own is untested. Sixty-one plants is a small benchmark, and the intervals are
wide. This covers the botanical stage only; the experts' final identifications also weigh medicinal uses and review.
And nothing here is a medical claim: these are hypotheses about historical texts.

**10. Next.** Where it goes next. All 827 chapters of Wellmann's text are already ingested. Scoring every chapter
would let experts start with the close calls, instead of working through every plant by hand. And the same steps fit
other Greek herbals, from John the Physician to Galen. Rhizotomos is by Sanchay Singh and Ashank Kumar, built with
Claude in Claude Code, on data published by Lardos and colleagues and the First1KGreek edition. Thank you.

### Presenting live instead

If the pitch is given in person, present the deck (its speaker notes hold the same narration) and replace part 5 with
the live demo below.

## Live demo

Two to three minutes. Beforehand, open https://ashank-crazy.github.io/rhizotomos/ in a fresh window and zoom to
125–150% so the room can read it. If the network fails, run `make serve` and use http://localhost:8000.

| Time | Do | Say |
|---|---|---|
| 0:00 | Home page | Rhizotomos repeats the Kew/ZHAW plant-identity method on Dioscorides' Greek. Each of the experts' 61 plants has a page, and the tiles are the headline results: 76% same verdict, 88% same best candidate. |
| 0:20 | Type "cyclamen" in the search box, open κυκλάμινος | Take cyclamen, *De materia medica* 2.164. Scholars have proposed five species for this one name. |
| 0:35 | Candidate species table | The experts rank *C. graecum* first. From their reading, Claude's calls give exactly their scores; from the Greek, two candidates drop to moderate, but *graecum* stays first. The species proposed most often, *persicum*, is not the experts' best. |
| 1:00 | Show matches on *C. graecum* | Each line is one statement: the Greek, the flora's words, Claude's call and the experts' call. Highlighted rows are disagreements, for example the leaf: mottled above and below, against marbled above. |
| 1:35 | Scroll to the Greek, point at πορφυρίζοντα | Every statement is tied to its words in the chapter, here "purplish". Code checked all 699 quotes. |
| 1:55 | Validation | Every figure with its 95% interval and the baselines. Calling every statement good already gets 61%, because the rule rewards how much a flora says; Claude adds 15 points. |
| 2:25 | Method, scroll to Limitations | The calls were blind, and the limits are stated: the flora text is the experts' extraction, the reading of the Greek was made once, the benchmark is small, and there are no medical claims. |
| 2:45 | Back to the home page | Everything rebuilds offline with one command. Thank you. |
