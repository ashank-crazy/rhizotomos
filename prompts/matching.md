# Matching prompt (Stage B)

These are the instructions the model follows when it compares an ancient description with a modern flora
description. They copy the match classes of Lardos et al. (2024), step 5.1, word for word where possible.

You are given, for one Dioscorides plant, the ancient statements sorted into the 36 characters, and for each
candidate species the information the experts extracted from *Flora of Turkey* or *Flora of Cyprus*.
Candidates are shown only as anonymous labels (`P07-C2`) in a shuffled order; you never see their names, the
experts' calls or the experts' verdicts.

For each ancient statement you are asked about, give one call:

| Call | Score | Meaning (Lardos et al. 2024) |
|---|---|---|
| `g` good | 2 | There is a good congruence between the ancient statement and the corresponding modern information. |
| `p` partial | 1 | Both appear to describe the same characteristic, but there is some doubt, e.g. due to different terminologies or different perspectives. |
| `n` no | −2 | No correlation: the modern information about this characteristic does not fit the ancient statement. |
| `a` absent | 0 | The modern information says nothing that corresponds to this statement. |

## Rules

1. Judge only the text shown. Do not use what you know about the species, and do not try to guess which
   candidate is "right". A species name that appears inside a modern value ("paler than in *S. nigrum*") is
   read as text, not as a clue.
2. Two passes are made, in this order, so the first is never influenced by the experts' reading:
   - **Pass A (our reading):** our statement is judged against everything the flora says about the same organ
     (the same category), because the two readings do not always put a statement in the same slot. Only that
     category counts: a stemless plant is not judged against "acaulescent" under Habit. When the category has
     nothing that corresponds, the call is `a`.
   - **Pass E (expert reading):** the experts' statement for a character is judged against the modern value
     for the same character, exactly as the experts did. Both are present, so the call is `g`, `p` or `n`.
3. **Good means "confirms what it covers".** If the modern text agrees on the point it addresses and
   contradicts nothing, the call is `g`, even when the ancient statement says more (the modern "marbled above"
   for the ancient "mottled on top, with whitish spots below").
4. **Partial** is the same characteristic seen with doubt (a different term or perspective: "like a bunch of
   grapes" against "spadix"), or a mix of agreement and conflict ("oblong, split" against "orbicular, lobate").
5. **No** is a clear contradiction ("white" against "yellow"). In pass E it is also used when the two values
   are about different aspects of the part and so cannot correlate ("upright" against "stout", "woody"
   against "slender", "seed like fleas" against "fruit a membranous capsule").
6. **Alternatives.** When the modern text gives alternatives ("shrub or small tree", "pinkish, purple or
   white", a list of habitats) and one of them matches, the call is `g`; when the alternatives only come close,
   `p`.
7. **Heights:** ancient units are converted at cubit ≈ 46 cm, foot ≈ 31 cm, span ≈ 23 cm, finger ≈ 1.9 cm. The
   union of all the modern ranges given (Flora of Turkey and Flora of Cyprus, flowering and fruiting) is used.
   A range that contains the ancient value or overlaps it is `g`; one within a factor of two is `p`; otherwise
   `n`. "Grows tall" is `g` against a maximum of about a metre or more and `p` below that.
8. **Colours:** the same colour or an adjacent shade is `g` (white/whitish, yellow/quince-yellow/golden-yellow,
   purple/purplish/dusky purple, saffron/orange-red). A different but compatible description is `p`
   (purplish/pale pink, saffron/red, black/dark brown, black/dull or rusty brown, white/grey, white/glaucous,
   yellowish/rust). Clearly different colours are `n` (yellow/red, black/pale brown, red/chocolate brown,
   reddish/green).
9. **Life form:** "shrub" against "annual", "biennial" or "perennial (herb)" is `p`; against "subshrubby",
   "suffrutescent" or "bushy" it is `g`. A statement that is not a life form ("collected in spring") is `n`
   in pass E.
10. **Hairiness:** "rough" against hairy, villous, lanate, tomentose or pubescent is `p` (hirsute is `g`);
    "downy" or "hairy" against tomentose, pilose, puberulent or arachnoid is `g`; "rough" against "smooth" or
    "glabrous" is `n`.
11. **Relative statements** ("smaller than the previous one", "softer than the black kind") cannot be checked
    against an absolute modern value, so they are `p`, unless the modern value clearly fits (`g`).
12. A statement that a part is missing ("stemless", "no seed") is matched like any other statement: "no seed"
    against "spores" is `g`.
13. "(G)" in a modern value means the experts took it from the genus description. Treat it as ordinary
    information.

Output: one JSON object per batch, `{"P07-C2": {"Leaf shape": "g", "Flower colour": "n"}, ...}`.

Rules 3 to 11 were written down while the calls were being made, from the decisions taken on the first
batches, and earlier batches were brought into line with them (pass A batch 0; pass E batch 3). No expert call
or verdict had been seen when they were written.
