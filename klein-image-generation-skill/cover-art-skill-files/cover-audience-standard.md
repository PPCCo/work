# Standard: cover design by audience

The framework's four audience values drive art direction, typography, copy and
the claims a cover is allowed to make. The value in `project.yaml` is the source
of truth; never infer the audience from the topic.

---

## early-reader-6-8

**Who buys it**: an adult, usually a parent or grandparent, scanning a grid of
thumbnails on a phone. The child may influence the choice but rarely completes
it. The cover therefore has two jobs at once — delight the child and reassure the
adult that this is age-appropriate and worth the money.

- **Art**: one hero character, front-facing, friendly, filling the lower two
  thirds. Flat bold shapes or warm gouache. Bright saturated palette.
- **Type**: rounded heavy display face, centred, high contrast, large.
- **Reassurance**: put the age range and the count on the cover — "Ages 6-8",
  "50 Big Pictures". Adults buy specificity.
- **Fails**: muted palettes, ironic design, small type, crowded scenes, anything
  that reads as scary, more than two characters.
- **Default packs**: `kids_activity_bold`, `kids_illustrated_scene`.

## middle-grade-9-12

**Who buys it**: an adult pays, but the child has veto power and exercises it.
The single biggest failure mode is a cover that looks like it is for younger
children — a nine-year-old will reject it instantly.

- **Art**: dynamic, slightly cinematic, stronger perspective, richer colour, more
  detail than the 6-8 band but still one clear focal point.
- **Type**: energetic display face, larger subtitle carrying the hook.
- **Reassurance**: the hook belongs on the cover — what will they learn or do.
- **Fails**: pastel nurseries, chibi proportions, baby animals, rounded bubble
  fonts, anything condescending.
- **Default pack**: `middle_grade_adventure`.

## teen-13-17

**Who buys it**: the teen, or an adult hoping the teen will open it. Design-led
covers win; anything that looks like a school worksheet loses.

- **Art**: graphic, symbolic, restrained palette, generous negative space. A
  single strong object or shape beats a scene.
- **Type**: editorial sans, often left-aligned, confident and quiet.
- **Reassurance**: the subtitle does the work; the art sets the tone.
- **Fails**: cartoon mascots, exclamation marks, primary-colour schemes,
  clip-art energy, anything that talks down.
- **Default pack**: `teen_graphic_bold`.

## adult-general

**Who buys it**: someone deciding in under two seconds whether this looks
professionally published. Credibility is the whole game, and restraint is how it
is signalled.

- **Art**: minimal and symbolic, or a clean geometric motif. The artwork
  supports the type rather than competing with it.
- **Type**: the dominant element. Serif for authority, geometric sans for
  practical and productivity titles.
- **Reassurance**: concrete promise in the subtitle — the number, the timeframe,
  the outcome.
- **Fails**: cluttered collages, three or more type styles, stock-photo look,
  drop shadows, anything that reads as self-published in the pejorative sense.
- **Default packs**: `adult_nonfiction_minimal`, `adult_puzzle_clean`.

---

## Cross-cutting rules

**Large-print editions** (common in adult puzzle lines) say so on the cover in
type at least as large as the subtitle. It is the purchase reason.

**Claims must match the interior.** Puzzle counts, page counts, difficulty
levels and age ranges on the cover are checked against the built interior before
the final gate. A mismatch is a blocker, not a note.

**Children's titles never** depict a real child, a photoreal child, a child in
unresolved danger, or anything frightening or sexualised — in any style pack, for
any seasonal theme.

**Accessibility.** Aim for 4.5:1 contrast on every text element, avoid carrying
meaning by colour alone, and check the greyscale render produced by
`thumbnail_test.py`; a cover that dies in greyscale will also die for readers
with low vision and on e-ink devices.
