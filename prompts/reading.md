# Reading prompt (Stage A)

These are the instructions the model follows when it reads a chapter of Dioscorides, *De materia medica*,
in Wellmann's Greek. They mirror how Lardos et al. (2024) coded the plant descriptions (Data file 3), so the two
readings can be compared character by character.

You are given one chapter of the Greek text and the names of the plant types to describe (for example
`hyoskyamos (purple flowers)` when a chapter describes several kinds). For each type, return what the chapter says
about that plant, sorted into these 36 characters:

| Category | Characters |
|---|---|
| Lifeform | Life form (tree, shrub, undershrub, herb …) |
| Habit | Habitus general, Habitus detail 1, Habitus detail 2 |
| Height | Height |
| Stem | Stem general, Stem detail 1, Stem detail 2, Stem detail 3 |
| Leaf | Leaf general, Leaf size, Leaf shape, Leaf edge, Leaf surface, Leaf detail 1, Leaf detail 2 |
| Flower | Flower general, Flower colour, Flower detail 01 |
| Fruit | Fruit general, Fruit shape, Fruit structure, Fruit colour, Fruit detail 1 |
| Seed | Seed general, Seed colour, Seed detail 1 |
| Root | Root general, Root colour, Root detail 1, Root detail 2 |
| Properties | Smell properties, Taste properties |
| Ethnobotany | Ethnobotany (non-medicinal uses and lore: food, household, dye, ritual) |
| Habitat | Habitat (where it grows: mountains, marshes, rocky places …) |
| Distribution | Distribution (regions named, including "the best comes from …") |

Rules:

1. Record only what the chapter says **directly** about this plant. When a feature is described only by comparison
   with another plant ("leaves like those of the olive"), do not put it in a character. Put it under `comparisons`,
   keyed by category. The experts excluded comparisons the same way.
2. Use the specific slot when one fits (colour, shape, size, surface, edge). Use `general` for the main statement
   about an organ and the `detail` slots, in order, for further statements about it. Leave out characters the chapter
   does not mention.
3. Each value has `en`, a short faithful English rendering (at most 12 words), and `greek`, the **exact contiguous
   words from the chapter** that support it. Keep the quote minimal. It is checked mechanically against the text.
4. Heights keep the ancient unit and add a modern equivalent: cubit ≈ 46 cm, foot ≈ 31 cm, span ≈ 23 cm,
   palm ≈ 7.7 cm, finger ≈ 1.9 cm.
5. Do not use outside knowledge of what the plant "really" is. Read only what the text says.

Output, one object per plant type:

```json
{"key": "iris (Illyrian)", "chapter": "1.1",
 "characters": {"Leaf shape": {"en": "sword-like", "greek": "ὅμοια ξιφίῳ"}},
 "comparisons": {"Leaf": {"en": "…", "greek": "…"}}}
```
