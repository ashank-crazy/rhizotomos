# Submission kit

Copy for the Devpost page, the pitch video's narration and the live-demo script. Text in [square brackets] is still to
fill in. Every number matches [RESULTS.md](RESULTS.md); after rerunning the pipeline, check them again.

## Devpost page

| Field | Text |
|---|---|
| Project name | Rhizotomos |
| Elevator pitch | Which plant did Dioscorides mean? Claude repeats the Kew/ZHAW plant-identity method on the Greek of *De materia medica*, and every step is scored against the experts' own data. |
| Challenge track | Track 1: Traditional Knowledge Mining |
| Try it out | https://ashank-crazy.github.io/rhizotomos/ and https://github.com/ashank-crazy/rhizotomos |
| Built with | python, pandas, lxml, openpyxl, javascript, html, css, github-pages, tei-xml, claude |
| Video | [YouTube link, unlisted] |
| Slides | the 10-slide PDF, `rhizotomos-deck.pdf` |
| Team | Sanchay Singh and Ashank Kumar |

### About the project

Paste the block below into Devpost's project description (it accepts Markdown).

~~~markdown
## In short

**Rhizotomos** (ῥιζοτόμος, "root-cutter", the ancient Greek word for a herbalist) asks which plant species Dioscorides meant in his 1st-century *De materia medica*. An AI model, Claude, repeats step by step the plant-identity method that botanists at Kew and ZHAW applied by hand to 61 plants, and every step is scored against the experts' own published data.

## The problem

Every study that turns a historical remedy into a modern lead, whether in natural-product chemistry, pharmacology or the history of medicine, first has to decide which species an old plant name refers to. The usual answers come from dictionaries, and many are doubtful. Take κυκλάμινος (*De materia medica* 2.164): John the Physician uses the same name in the 13th century, and scholars have proposed five different *Cyclamen* species for it. Whatever is looked up next is looked up under one of those names.

Lardos et al. (2024) built a systematic alternative: code what the ancient text says about a plant into botanical characters, code the same characters from modern floras for every candidate species, judge each match, and score each candidate. It is careful and slow, so it was applied to 61 plants. They also published every call and verdict under CC BY, which turns their work into an answer key.

## Our approach

Think of a line-up. The ancient description is the witness statement, the candidate species are the suspects, the match calls are the evidence and the experts' score is the verdict. The experts have solved 61 cases, so a model doing the same job can be scored.

| Stage | Done by | What happens | Checked against |
|---|---|---|---|
| Read | Claude | Sorts each Greek chapter into the experts' 36 characters (13 organs). Every statement quotes the Greek, and code checks that the quote occurs in the chapter. | The experts' reading (629 characters) |
| Match | Claude, blind | Calls each statement against each candidate's flora description: good, partial, no or absent, with the paper's definitions. | The experts' 1,186 calls |
| Score | Code | The experts' own rule: organs that agree minus organs that disagree. STRONG is 5 or more, MODERATE 3–4, WEAK 2 or less. | Their published verdicts: 117 of 120 reproduced |

Two passes keep the stages apart. **Pass E** matches the experts' reading, which tests the matching step alone. **Pass A** matches Claude's own reading, end to end from the Greek. Pass E was then made a second time, in a new session, to measure how much the calls vary from run to run.

**Blind by design.** Candidates appeared only as anonymous labels (P07-C2) in a shuffled order. No expert call or verdict was opened until both passes were complete, and the calling rules were written down before that. Seven plants had some expert data looked at while the code was being built; they are listed in the repository, and every figure is also reported without them.

## Results

The reference is the experts' verdict for each of the 122 candidates described in the floras. Ranges are 95% bootstrap intervals over plants.

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

- **Single statements.** On the 798 pairs the experts judged, Claude gives the same good / partial / no call 71% of the time (weighted κ 0.56), and agrees on fit versus contradiction 92% of the time. Shared-word matching agrees on 24%.
- **Calling everything "good" is a strong baseline**, because the experts' rule rewards how much a flora says. Claude's matching adds 15 points on the experts' reading and 8 on its own.
- **Reading the Greek is the harder step.** Claude covers 83% of the organs and 67% of the characters the experts coded. The experts extracted flora text only for characters in their own reading, so anything else Claude reads has nothing to match against.
- **Not flattered by leakage.** On the 54 plants whose expert data was never seen during development, the figures are 78% and 61% for verdicts, and 91% and 84% for the best candidate.
- **Stable from run to run.** A second, independent run of pass E gives the same call as the first on 88% of the 800 statements (weighted κ 0.82), the same verdict for 89% of candidates and the same best candidate for 98% of plants. Against the experts it scores 79% on verdicts and 86% on the best candidate, so the headline is not one lucky run.

## The prototype

The explorer is a static website with a page for each of the 61 plants: the Greek chapter with every quote highlighted and linked to its statement, Claude's reading next to the experts', the synonyms from the manuscripts, and every candidate with its grade from the experts, from Claude on the experts' reading and from Claude on the Greek. Opening a candidate shows each statement, the flora's words, Claude's call and the experts' call, with disagreements highlighted. The Validation page has every figure with its interval and baselines, the confusion matrices and the reading coverage.

## Data sources

- Dioscorides, *De materia medica*, ed. M. Wellmann (1906–1914), TEI XML from First1KGreek (Open Greek and Latin), CC BY-SA 4.0.
- Lardos A, Patmore K, Allkin R, Lazarou R, Nesbitt M, Scott AC, Zipser B (2024). A systematic methodology to assess the identity of plants in historical texts: a case study based on the Byzantine pharmacy text John the Physician's Therapeutics. *Journal of Ethnopharmacology* 322: 117622, doi:10.1016/j.jep.2023.117622. Article and research data (figshare) CC BY 4.0: the expert reading, the candidate lists, modern descriptions from Flora of Turkey and Flora of Cyprus, the match calls and the verdicts.

## Technologies

- Python with pandas, openpyxl and lxml for ingestion, the benchmark, scoring and evaluation, run end to end by a Makefile.
- A static HTML, CSS and JavaScript explorer with no framework and no backend, on GitHub Pages.
- Claude (Opus 5.5) in Claude Code, for the code, the readings and the match calls.

Everything the model produced is committed as data, so `make all` rebuilds every number in the README, RESULTS.md and the explorer without a model, an API key or the network, and two runs give identical files. GitHub Actions reruns the whole pipeline on Python 3.11, 3.12 and 3.13 on every push and fails if any committed number changes.

## AI use and what already existed

- **Claude (Opus 5.5) in Claude Code** wrote the code and the explorer, read the Greek of the 61 chapters and made all 2,333 match calls (pass A, pass E and its repeat run). With no API budget, the readings and calls were made inside Claude Code sessions, following the prompts in the repository, and committed as data. Claude also made the slide deck and the pitch video, whose narration is a synthetic voice (Deepgram Aura-2) reading our script.
- **Already existing:** the Greek text and its digitisation, the method, the expert data and the scoring rule (Lardos et al. 2024), and the Python libraries.
- **Built during the hackathon:** ingestion, the benchmark, the reading and matching prompts and their outputs, the repeat run, the scoring and evaluation code, the baselines, the explorer, the CI check and the documentation.

## Limitations

- The modern side is the experts' extraction from the floras, which covers only characters in their own reading. Matching against descriptions Claude extracts itself is untested.
- One model made every reading and call. Pass E was made twice, but the reading of the Greek and pass A were made once, so their run-to-run variation is not measured.
- 61 plants and 122 scored candidates is a small benchmark, and the intervals are wide.
- This reproduces the experts' botanical scoring only. Their final identifications also weigh medicinal uses and expert review.
- Identifications are hypotheses about historical texts. Nothing here is medical advice or a claim that a plant is safe or effective.

## Impact and what's next

- **The whole book.** All 827 chapters are already ingested with their manuscript synonym lists. Next, read every plant chapter and score the candidates scholars have proposed for it.
- **Triage for specialists.** Flag the chapters where the usual identification fits the Greek worst, so scarce expert time goes where the doubt is greatest.
- **Other herbals.** Nothing in the steps is specific to Dioscorides: John the Physician, Galen and later Byzantine pharmacy texts can go through them too.
- **A stronger modern side.** Extract flora descriptions for every candidate from open sources, and repeat the reading step to measure its variation too.

Firmer identifications help every study that starts from a historical remedy, from natural-product chemistry to the history of medicine.

## Team

Sanchay Singh and Ashank Kumar.
~~~

## Pitch video

7 minutes 4 seconds (the limit is 10), 1920 × 1080 with burned-in captions. Upload it to YouTube as unlisted and put
the link in the table above. The narration is a synthetic voice (Deepgram Aura-2) reading the script below, and the end
card says so. The pictures are the deck's slides, except part 5, which is real footage of the explorer recorded in a
browser and timed to the narration.

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
