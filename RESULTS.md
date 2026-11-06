# Results

All figures compare Rhizotomos with the published expert data of Lardos et al. (2024). "Unseen" leaves out the 7 plants whose expert data was looked at while the pipeline was built (adianton, akanthe aspre, aloe, alyssos, amaranton, ampelos agria, staphis agria); the other 54 were never seen before both matching passes were complete. Ranges are 95% bootstrap intervals over plants.

## Sanity check

The experts' Stage 5 rule, applied to the experts' own match calls, gives the verdict they published for 117 of 120 candidates. These re-derived verdicts are the reference below.

## Stage C: verdicts (STRONG / MODERATE / WEAK)

| Reading | Matching | Agreement | Weighted κ | Spearman ρ | Same top pick | Agreement, unseen | Top pick, unseen |
|---|---|---|---|---|---|---|---|
| experts' reading | Claude's matching (pass E) | 76% (68%–84%) | 0.70 (0.59–0.79) | 0.83 | 88% (77%–96%) | 78% | 91% |
| experts' reading | Claude's matching (pass E, repeat run) | 79% (72%–85%) | 0.73 (0.63–0.82) | 0.80 | 86% (74%–96%) | 80% | 91% |
| Claude's reading | Claude's matching (pass A) | 60% (51%–69%) | 0.50 (0.39–0.61) | 0.68 | 80% (67%–91%) | 61% | 84% |
| experts' reading | word overlap | 28% (20%–36%) | 0.00 (0.00–0.02) | -0.07 | 63% (46%–79%) | 26% | 65% |
| experts' reading | everything good | 61% (50%–71%) | 0.45 (0.33–0.59) | 0.63 | 78% (66%–90%) | 65% | 79% |
| Claude's reading | everything good | 52% (42%–63%) | 0.33 (0.18–0.48) | 0.48 | 74% (61%–86%) | 55% | 75% |
| – | most often proposed in the literature (Data file 5) | – | – | – | 68% (53%–84%) | – | 72% |
| – | always MODERATE | 42% | 0 | – | – | 43% | – |
| – | random pick | – | – | – | 57% | – | 58% |

122 candidates described in the floras; "same top pick" is over the 31 plants with two or more such candidates.

Pass A scores lower than the experts mainly through coverage: per candidate it finds 3.25 categories with a positive average against the experts' 4.14 (pass E 4.16), while negative categories are about as rare (0.32, 0.43, 0.37). The modern descriptions were extracted by the experts only for the characters in their own reading, so a statement of ours in any other category has nothing to be matched against and counts as absent.

Confusion, experts' reading + Claude's matching (pass E) (rows: experts, columns: ours):

| | WEAK | MODERATE | STRONG |
|---|---|---|---|
| WEAK | 20 | 14 | 0 |
| MODERATE | 4 | 39 | 8 |
| STRONG | 0 | 3 | 34 |

Confusion, Claude's reading + Claude's matching (pass A) (rows: experts, columns: ours):

| | WEAK | MODERATE | STRONG |
|---|---|---|---|
| WEAK | 30 | 3 | 1 |
| MODERATE | 20 | 26 | 5 |
| STRONG | 1 | 19 | 17 |

## Stage B: matching single statements

Each pair is one ancient statement from the experts' reading against the modern value for the same character, exactly the pairs the experts judged.

| Matcher | Pairs compared | Agreement | κ | Weighted κ | Same direction | Agreement, unseen | Weighted κ, unseen |
|---|---|---|---|---|---|---|---|
| Claude (pass E) | 798 | 71% (67%–75%) | 0.49 | 0.56 (0.48–0.61) | 92% | 72% | 0.56 |
| Claude (pass E, repeat run) | 798 | 70% (66%–74%) | 0.47 | 0.54 (0.46–0.60) | 92% | 72% | 0.55 |
| word overlap | 798 | 24% (21%–27%) | 0.06 | 0.09 (0.07–0.11) | 33% | 23% | 0.08 |
| all good | 798 | 54% (49%–60%) | 0.00 | 0.00 (0.00–0.00) | 90% | 57% | 0.00 |

Of the 800 pairs, the experts called 0 "absent" although both texts say something, and left 2 without a call; pass E has no "absent" option, so these are left out of the agreement figures.

Confusion, Claude (pass E) (rows: experts, columns: ours):

| | no | partial | good |
|---|---|---|---|
| no | 49 | 29 | 3 |
| partial | 24 | 180 | 81 |
| good | 5 | 90 | 337 |
| absent | 0 | 0 | 0 |

## Run to run: pass E made twice

Pass E was made a second time, in a new session, from the same blind batches and without opening the first run's calls (`data/llm/matching/expert_r2/`). The two runs are compared with each other, and each with the experts. "Unseen" here also leaves out kyklaminos, seen before the repeat run, so it covers 53 plants.

| | All | Unseen |
|---|---|---|
| Same call in both runs (800 statement pairs) | 88% (85%–90%) | 88% |
| Weighted κ between the runs, calls | 0.82 | 0.82 |
| Same fit-or-contradiction in both runs | 98% | 98% |
| Same verdict in both runs (122 candidates) | 89% (84%–94%) | 89% |
| Weighted κ between the runs, verdicts | 0.86 | 0.85 |
| Same best candidate in both runs | 98% (95%–100%) | 98% |
| Candidates whose agreement with the experts changed | 13 | 11 |

Against the experts, the first run gives the same call on 71% of statements and the repeat run on 70%; the same verdict on 76% and 79% of candidates; the same best candidate on 88% and 86% of plants.

## Stage A: reading the Greek

Which of the 36 characters (and 13 categories) our reading fills, against the experts' reading (Data file 3). This measures coverage, not whether the content agrees; content is tested by pass A above.

| Level | Ours | Experts' | Shared | Precision | Recall | F1 | Recall, unseen |
|---|---|---|---|---|---|---|---|
| characters | 576 | 629 | 422 | 73% | 67% | 70% | 67% |
| categories | 399 | 393 | 327 | 82% | 83% | 83% | 84% |

Characters the experts filled and we did not, most often: Leaf detail 1 (16), Habitus detail 1 (13), Habitus general (13), Leaf shape (13), Stem detail 1 (13), Fruit general (12).
Characters we filled and the experts did not, most often: Stem general (21), Ethnobotany (20), Root general (9), Habitus general (8), Leaf general (8), Seed general (7).
