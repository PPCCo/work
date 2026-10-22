# Prompt Craft for `qwen_image_2512` (via draw-things-cli)

How to turn a design spec into a prompt that renders a *designed* cover with correct embedded text. Qwen-Image models read natural-language art direction well and are comparatively strong at rendering text, so write like a creative director briefing an illustrator, not like a tag list.

> Numbers below (sizes, steps, CFG) are sensible starting points. Confirm them against the model variant and sampler you actually run in Draw Things, and adjust once.

---

## 1. Prompt skeleton (write in this order)

Target **120–260 words** of flowing prose. Each layer is 1–3 sentences.

1. **Format.** `Flat front book cover artwork, portrait, full-bleed, no book mockup, no spine, no 3D book.`
2. **Concept and medium.** What it is and how it is made: `A hand-painted gouache picture-book illustration of…`
3. **Hero subject.** Concrete details: species, pose, expression, clothing, scale, crop, camera angle, the *moment*.
4. **Environment and depth.** Foreground / mid / background; scale contrast; atmosphere.
5. **Light and mood.** Direction, time of day, rim light, shadow color.
6. **Palette with roles.** Dominant (60 %), secondary (30 %), accent (10 %), in plain color words.
7. **Layout.** Where the hero sits, where the quiet zone for the title is, safe margins.
8. **Text layers** (exact strings; see §2).
9. **Finish.** Surface and print quality: `visible paper grain, crisp edges, rich contrast`.
10. **Constraint line.** `No other text, no watermark, no signature, no logo, no extra letters.`

---

## 2. Embedded text, the rules that make it reliable

**Syntax.** Declare each text layer in its own sentence with the exact string in straight double quotes, then style, color, position and size:

```
The title "THE LITTLE FOX WHO LOST HER SPARK" is set in chunky hand-lettered rounded capitals,
warm cream with a deep plum outline and a soft drop shadow, stacked on three lines,
centered in the upper third, spanning about 80% of the cover width.
Above it, the series name "MOONLIT TALES" in small, widely spaced capitals, pale gold.
At the very bottom center, the publisher name "Willowbrook Press" in small clean serif lettering, cream.
```

**Hard rules**
- **Only text layers go in double quotes.** Nothing else in the prompt may use double quotes (use no quotes, or single quotes, for anything else).
- **Exact strings.** Copy the title, series and publisher *character for character* from the brief. Never retype from memory; never "improve" a title.
- **Brevity wins.** Title ≤ 6 words ideal (≤ 8 max), series ≤ 4, publisher ≤ 3. Long titles: move the remainder to a short subtitle line.
- **Describe lettering by traits, not font names.** Weight, width, contrast, terminals, case, finish.
- **State color + contrast + position + size** for every layer. Unspecified placement is the main cause of messy lettering.
- **Put text on calm areas.** Tell the model where the quiet zone is and keep the subject out of it.
- **Close with the "no other text" line**, and keep grids, signs, books and screens in the artwork abstract (`abstract, with no legible characters`).
- **Avoid:** unusual diacritics, all-lowercase micro text, text on curves beyond a gentle arch, more than three text layers, and text smaller than ~3 % of canvas height.

**Lettering vocabulary** (pick, don't pile up)
- Kids: `chunky rounded hand-lettered capitals`, `bouncy brush-lettered`, `bubble-style inflated letters`, `cut-paper letters`
- Educational: `bold friendly geometric sans capitals`, `marker-lettered with a thick outline`
- Elegant: `refined high-contrast serif capitals, widely tracked`, `delicate script with a small-caps subtitle`
- Modern/teen: `oversized condensed grotesque capitals`, `bold slab capitals, tight leading`
- Adventure/nonfiction: `bold geometric slab capitals with a dark outline`, `engraved-style capitals`
- Anime/digital: `sleek brush-script display lettering`, `neon tube lettering`, `etched metallic capitals`
- Effects (max two): `soft drop shadow`, `thin inline`, `embossed`, `gold foil`, `subtle ink bleed`

---

## 3. Specificity ladder

Replace generic words with concrete art direction.

| Generic | Specific |
|---|---|
| beautiful forest | misty pine forest at blue hour, lantern-lit path, fern foreground in deep shadow |
| cute animal | a small red fox with oversized ears, head tilted, tail curled around a glowing paper lantern |
| vibrant colors | dominant deep teal, secondary warm cream, accent saffron on the lantern |
| nice lighting | low golden backlight from the left, warm rim light on the fur, cool violet shadows |
| artistic style | gouache with visible brush strokes and paper grain |
| high quality | crisp edges, clean fills, rich tonal contrast |

Do **not** use filler tokens: `masterpiece`, `8k`, `ultra detailed`, `best quality`, `award winning`, `trending on…`. They add nothing and bloat the prompt.

**Never name artists, studios, franchises or characters.** Describe the *attributes* of the style instead (line quality, palette logic, lighting, material).

---

## 4. Medium and finish vocabulary

- **Gouache / picture book:** `opaque gouache, visible brush strokes, soft edges, paper grain`
- **Watercolor:** `wet-on-wet washes, pigment blooms, deckled edges, white paper breathing through`
- **Ink & wash / sketch:** `fine ink linework with a light wash, hatching, paper tooth`
- **Graphite / charcoal:** `soft graphite shading, smudges, visible construction lines, warm toned paper`
- **Oil:** `thick impasto strokes, canvas weave, rich chiaroscuro, glazed shadows`
- **Paper-cut:** `layered cut paper, soft cast shadows between layers, subtle fibers`
- **Flat vector:** `clean flat vector shapes, limited palette, subtle grain overlay`
- **2D anime:** `cel-shaded anime key visual, varied line weight, dynamic pose, light particles`
- **Stylized 3D:** `soft stylized 3D animated-film look, subsurface scattering, cinematic lighting`
- **Photographic:** `shot on a full-frame camera, 85mm, shallow depth of field, natural light, fine grain`
- **Line art for coloring covers:** `bold clean black outlines on white, partially colored with colored pencil`

---

## 5. Base negative prompt

Use as the default and append as needed:

```
misspelled text, garbled letters, extra letters, duplicate text, missing letters, blurry text,
text cut off at the edge, watermark, signature, logo, border, frame mockup, 3D book mockup, spine,
low contrast, cluttered composition, deformed hands, extra fingers, distorted face,
plastic skin, oversaturated glow, muddy colors, jpeg artifacts
```

Adjust by genre: for coloring covers add `gray shading in the line art`; for photography add `CGI look, HDR halo`.

---

## 6. Sizes and parameters (starting points)

| Trim ratio (w:h) | Typical trim | Generate at |
|---|---|---|
| 2:3 (0.667) | 6×9 in | 1056 × 1584 |
| 3:4 (0.75) | 7.5×10 in, 8×10 in | 1104 × 1472 |
| 1:1 | 8.5×8.5 in | 1328 × 1328 |

For trims such as 8.5×11 (0.773), generate at 1104 × 1472 and crop/resize in your existing finishing step. `cover_tools.py size 8.5x11` chooses the nearest.

- **Steps:** 40–50 (fewer with an acceleration LoRA, if you use one).
- **CFG / guidance:** ~4.
- **Seeds:** generate **2 seeds per variant**; text errors are often seed-specific.

---

## 7. Making variants truly different

Changing the seed changes noise, not design. Variants of one book must differ along **at least three axes**:

1. Composition archetype
2. Hero subject / moment / camera angle
3. Palette hue family (and harmony recipe)
4. Light / time of day
5. Medium and surface
6. Lettering treatment and title lockup shape

---

## 8. Surgical fixes (change one thing, regenerate)

| Problem seen | Fix |
|---|---|
| Letter errors / extra letters | New seed first; then shorten the string; then move text to a calmer zone; then simplify the lettering description |
| Title unreadable at thumbnail | Raise contrast (outline, darker/lighter ground behind), enlarge to ~80–90 % width, simplify to fewer lines |
| Extra text appears in the art | Add `abstract, with no legible characters` to the offending element; strengthen the constraint line |
| Subject collides with the title | Rewrite the layout layer: explicit quiet zone, move the subject down/left, crop |
| Bland / flat | Add depth planes, a light direction, a secondary story element, and a material/texture |
| Cluttered | Delete elements; state `simple, uncluttered background`; reduce the number of colors |
| Face or hands off | Change pose to hide hands, simplify camera angle, or switch to a three-quarter view; new seed |
| Looks like a 3D book mockup | Restate `flat front cover artwork, no mockup, no spine`; add `mockup, spine` to the negative prompt |
| Colors muddy | Re-state the palette with roles; remove extra hues; add `clean saturated fills` |
| Too close to a reference image | Change subject/pose, change the hue family, change the lettering shape; never add "in the style of the reference" |

---

## 9. Worked example

*Book:* "The Little Fox Who Lost Her Spark" · series "Moonlit Tales" · publisher "Willowbrook Press" · category `kids-storybook` · ages 4–7.

```
Flat front book cover artwork, portrait, full-bleed, no book mockup, no spine.
A hand-painted gouache picture-book illustration with visible brush strokes and soft paper grain.
A small red fox with oversized ears, head tilted in wonder, walks a winding snowy path carrying a
glowing paper lantern whose warm light pools on the snow; her tail curls around the lantern's handle.
Tall silhouetted pines frame both sides in the foreground, a misty blue valley with tiny lit
windows recedes behind her, and a huge pale moon sits in the upper right. Low moonlight from the
upper right, a warm lantern glow as the key light, cool violet shadows.
Dominant deep midnight blue, secondary soft lavender mist, accent saffron-gold on the lantern and moon.
The fox sits in the lower-left third; the upper third is a calm, softly clouded night sky reserved for lettering.
The title "THE LITTLE FOX WHO LOST HER SPARK" is set in chunky hand-lettered rounded capitals, warm cream
with a deep plum outline and a soft shadow, stacked on three lines, centered in the upper third, spanning about 80% of the width.
Above it, the series "MOONLIT TALES" in small, widely spaced pale-gold capitals.
At the bottom center, the publisher "Willowbrook Press" in small clean cream serif lettering.
Crisp edges, rich tonal contrast, cozy and magical mood.
No other text, no watermark, no signature, no logo, no extra letters.
```
