# Submission kit

Copy for the Devpost page, plus the scripts for the pitch video and the live demo. Text in [square brackets] is for
the team to fill in. Every number matches [RESULTS.md](RESULTS.md); after rerunning the pipeline, check them again.

## Devpost page

| Field | Text |
|---|---|
| Project name | Rhizotomos |
| Elevator pitch | Which plant did Dioscorides mean? Claude repeats the Kew/ZHAW plant-identity method on the Greek of *De materia medica*, and every step is scored against the experts' own data. |
| Challenge track | Track 1: Traditional Knowledge Mining |
| Try it out | https://ashank-crazy.github.io/rhizotomos/ and https://github.com/ashank-crazy/rhizotomos |
| Built with | python, pandas, lxml, openpyxl, javascript, html, css, github-pages, tei-xml, claude |
| Video | [YouTube link] |
| Slides | the 10-slide PDF |
| Team | [Name, role, affiliation] and [Name, role, affiliation] |

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

Two passes keep the stages apart. **Pass E** matches the experts' reading, which tests the matching step alone. **Pass A** matches Claude's own reading, end to end from the Greek.

**Blind by design.** Candidates appeared only as anonymous labels (P07-C2) in a shuffled order. No expert call or verdict was opened until both passes were complete, and the calling rules were written down before that. Seven plants had some expert data looked at while the code was being built; they are listed in the repository, and every figure is also reported without them.

## Results

The reference is the experts' verdict for each of the 122 candidates described in the floras. Ranges are 95% bootstrap intervals over plants.

| Reading | Matching | Same verdict | Same best candidate (31 plants) |
|---|---|---|---|
| experts' | **Claude** (pass E) | **76%** (68–84%) | **88%** (77–96%) |
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

## The prototype

The explorer is a static website with a page for each of the 61 plants: the Greek chapter with every quote highlighted and linked to its statement, Claude's reading next to the experts', the synonyms from the manuscripts, and every candidate with its grade from the experts, from Claude on the experts' reading and from Claude on the Greek. Opening a candidate shows each statement, the flora's words, Claude's call and the experts' call, with disagreements highlighted. The Validation page has every figure with its interval and baselines, the confusion matrices and the reading coverage.

## Data sources

- Dioscorides, *De materia medica*, ed. M. Wellmann (1906–1914), TEI XML from First1KGreek (Open Greek and Latin), CC BY-SA 4.0.
- Lardos A, Patmore K, Allkin R, Lazarou R, Nesbitt M, Scott AC, Zipser B (2024). A systematic methodology to assess the identity of plants in historical texts: a case study based on the Byzantine pharmacy text John the Physician's Therapeutics. *Journal of Ethnopharmacology* 322: 117622, doi:10.1016/j.jep.2023.117622. Article and research data (figshare) CC BY 4.0: the expert reading, the candidate lists, modern descriptions from Flora of Turkey and Flora of Cyprus, the match calls and the verdicts.

## Technologies

- Python with pandas, openpyxl and lxml for ingestion, the benchmark, scoring and evaluation, run end to end by a Makefile.
- A static HTML, CSS and JavaScript explorer with no framework and no backend, on GitHub Pages.
- Claude (Opus 5.5) in Claude Code, for the code, the readings and the match calls.

Everything the model produced is committed as data, so `make all` rebuilds every number in the README, RESULTS.md and the explorer without a model, an API key or the network, and two runs give identical files.

## AI use and what already existed

- **Claude (Opus 5.5) in Claude Code** wrote the code and the explorer, read the Greek of the 61 chapters and made all 1,533 match calls. With no API budget, the readings and calls were made inside the Claude Code session, following the prompts in the repository, and committed as data. [Add any other AI tools the team used, and what for.]
- **Already existing:** the Greek text and its digitisation, the method, the expert data and the scoring rule (Lardos et al. 2024), and the Python libraries.
- **Built during the hackathon:** ingestion, the benchmark, the reading and matching prompts and their outputs, the scoring and evaluation code, the baselines, the explorer and the documentation.

## Limitations

- The modern side is the experts' extraction from the floras, which covers only characters in their own reading. Matching against descriptions Claude extracts itself is untested.
- One model made every reading and call in one working session, without repeated runs, so run-to-run variation is not measured.
- 61 plants and 122 scored candidates is a small benchmark, and the intervals are wide.
- This reproduces the experts' botanical scoring only. Their final identifications also weigh medicinal uses and expert review.
- Identifications are hypotheses about historical texts. Nothing here is medical advice or a claim that a plant is safe or effective.

## Impact and what's next

- **The whole book.** All 827 chapters are already ingested with their manuscript synonym lists. Next, read every plant chapter and score the candidates scholars have proposed for it.
- **Triage for specialists.** Flag the chapters where the usual identification fits the Greek worst, so scarce expert time goes where the doubt is greatest.
- **Other herbals.** Nothing in the steps is specific to Dioscorides: John the Physician, Galen and later Byzantine pharmacy texts can go through them too.
- **A stronger modern side.** Extract flora descriptions for every candidate from open sources, and repeat runs to measure variation.

Firmer identifications help every study that starts from a historical remedy, from natural-product chemistry to the history of medicine.

## Team

[Name, role, affiliation]
[Name, role, affiliation]
~~~

## Pitch video

About 9 minutes at a steady pace (the limit is 10). Record the deck in Present mode with voice-over, and switch to a
screen recording of the explorer in part 5. The voice-over is the deck's speaker notes. YouTube, unlisted, is fine.

| Part | Starts | On screen |
|---|---|---|
| 1 | 0:00 | Slide 1, title |
| 2 | 0:30 | Slide 2, the problem |
| 3 | 1:10 | Slide 3, the line-up |
| 4 | 2:00 | Slide 4, what Rhizotomos does |
| 5 | 2:55 | Slide 5, then the explorer |
| 6 | 5:00 | Slide 6, headline results |
| 7 | 5:35 | Slide 7, baselines |
| 8 | 6:15 | Slide 8, what drives the results |
| 9 | 7:15 | Slide 9, safeguards and limits |
| 10 | 8:10 | Slide 10, next steps; finish by about 9:00 |

**1. Title.** Hi, we are [team]. Rhizotomos is the ancient Greek word for a root-cutter, a herbalist. Our question is
one that every ethnopharmacology project quietly depends on: when Dioscorides wrote about a plant two thousand years
ago, which species did he mean? We built a system in which Claude repeats, step by step, a method that botanists at
Kew and ZHAW published in 2024, and we score every one of those steps against the experts' own published data.

**2. The problem.** Any study that turns a historical remedy into a modern lead first has to decide which species an
old plant name means. Take cyclamen. Dioscorides describes kyklaminos in the first century, John the Physician uses
the same name in the thirteenth, and scholars have proposed five different Cyclamen species for it. Whatever comes
next, the chemistry, the pharmacology, the history, is looked up under one of those names. Dictionaries give a single
answer, and it is often doubtful. In 2024, botanists at Kew and ZHAW published a systematic way to decide, and
applied it by hand to 61 plants.

**3. The line-up.** Their method works like a police line-up. The witness statement is what the ancient text says,
coded into 36 characters such as height, leaf shape or flower colour. The suspects are the species scholars have
proposed, each described from the modern floras of Turkey and Cyprus. The evidence is a call for every pair: does
the flora confirm the statement, partly confirm it, contradict it, or say nothing? The verdict counts the organs that
agree minus those that contradict, and grades each suspect strong, moderate or weak. The experts solved 61 cases this
way and published every call, 1,186 of them. That is an answer key, so a model doing the same job can be scored.

**4. What Rhizotomos does.** Rhizotomos has Claude do the two expert steps and leaves the scoring to the experts' own
rule. In stage A, Claude reads the Greek and sorts what each chapter says into the same 36 characters, and every
statement must carry a quote that code then finds in the chapter. In stage B, Claude judges each statement against
each candidate's flora description. Candidates appear only as anonymous labels in a shuffled order, so Claude can't
lean on what it knows about a species. Stage C is the experts' rule in code; applied to their own calls, it
reproduces 117 of their 120 verdicts. We run two passes. Pass E starts from the experts' reading, so it tests
matching alone. Pass A starts from the Greek, so it tests the whole chain.

**5. Demo.** On slide 5, about 25 seconds: Here is one chapter, cyclamen. Underlined are the statements Claude coded
from the Greek; in italic, the comparisons with other plants: leaves like ivy, flowers like a rose, a root like a
turnip. Let's open it in the explorer.

Then the screen recording, about 1 minute 40 seconds:

- *Home page.* The explorer has a page for each of the 61 plants, and the tiles at the top are the headline results.
  *(Type "cyclamen" in the search box and open κυκλάμινος.)*
- *Candidate species table.* Five candidates; four are described in the floras. The experts graded three strong and
  one weak. From the experts' reading, Claude's calls give exactly the same scores, and from the Greek it still ranks
  Cyclamen graecum first. Notice that the species proposed most often, persicum, is not the experts' best.
- *Show matches on Cyclamen graecum.* Every match is laid out: what Dioscorides says, what the flora says, Claude's
  call and the experts' call. Highlighted rows are where they differ, like the leaf: Dioscorides says mottled above
  and below, the flora only marbled above. The experts called that partial, Claude called it good.
- *Scroll to "The Greek text and the two readings" and point at a highlight.* Every statement is tied to its words in
  the Greek, and code checked that all 699 quotes really are in the text.
- *Open Validation.* And every figure in this talk is here, with its interval and its baselines.

**6. Headline results.** Across all 61 plants and 122 scored candidates: starting from the experts' reading, Claude
reaches the experts' verdict for 76 percent of candidates, and picks the same best candidate in 88 percent of the 31
plants where there is a choice to make. Starting from the Greek itself, end to end, it is 60 percent and 80 percent.
The ranges are 95 percent bootstrap intervals over plants; they are wide because the benchmark is small, and we
report them everywhere.

**7. Baselines.** Are those numbers good? We compared them with every shortcut we could think of, always on the same
reading. Calling every statement a match is the strongest, because the experts' rule rewards how much a flora says
about a candidate: 61 percent. Claude's matching adds 15 points on top of that, and 8 points on its own reading.
Matching by shared words does worse than always answering moderate. For the best candidate, Claude also beats picking
the species proposed most often in the literature, 68 percent, and a random pick, 57 percent.

**8. What drives the results.** Three things explain these numbers. First, single calls: on the 798 statement pairs
the experts judged, Claude gives the same call 71 percent of the time, and agrees on whether a statement fits or
contradicts in 92 percent. Matching by shared words gets 24. Second, coverage: calling everything good already scores
well, because the experts' rule rewards how much a flora says, and Claude's judgement adds 15 points to that. Third,
reading the Greek is the harder step. Claude finds 83 percent of the organs the experts coded, but the experts
extracted flora text only for the characters in their own reading, so whatever else Claude reads has nothing to match
against. Even with every call set to good, switching to Claude's reading drops agreement from 61 to 52 percent, so
much of the gap is coverage, not matching.

**9. Safeguards and limits.** We built this to be checked rather than trusted. The calls were blind: candidates were
anonymous labels in a shuffled order, and no expert call or verdict was opened until both passes were complete. Every
statement quotes the Greek, and code found all 699 quotes. Our scoring reproduces the experts' own verdicts. Seven
plants had some expert data looked at while we built the code; without them, the results are as good or better. And
everything is committed, so one command rebuilds every number without a model or an API key. The limits are real too:
the modern side is the experts' extraction, one model made every call in one session, the benchmark is small, we
reproduce only the botanical stage, and none of this is medical advice.

**10. Next.** What next? The whole of De materia medica is already ingested, 827 chapters with their manuscript
synonym lists, so the same reading and matching can run on every plant chapter. Scored against the candidates
scholars have proposed, it becomes a triage tool: it can point specialists to the chapters where the usual
identification fits the Greek worst. And nothing in the steps is specific to Dioscorides. John the Physician, Galen
and later Byzantine pharmacy texts can go through them too. The explorer, the code and all the data are public.
Claude, in Claude Code, wrote the code, read the Greek and made every match call; the text, the method and the expert
data are other people's work, and they are credited. Thank you.

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
| 2:25 | Method, scroll to Limitations | The calls were blind, and the limits are stated: the flora text is the experts' extraction, one run, a small benchmark, and no medical claims. |
| 2:45 | Back to the home page | Everything rebuilds offline with one command. Thank you. |
