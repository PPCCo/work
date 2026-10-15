# Draw Things CLI Recipe Book for an Image-Generation Agent

Audience: an AI agent / recommendation engine choosing models, LoRAs, prompts and settings from vague user requests.
Scope: SDXL checkpoints (Juggernaut XL v9, Juggernaut XL X, ColorfulXL v6, Animagine XL v3.1) and Flux Klein, run through `draw-things-cli generate`.

## 0. Read first: verification status

- **Not run end to end.** Draw Things is macOS-only and these recipes were written on Linux. JSON validity, shell syntax, LoRA filenames and 64-pixel dimension multiples were checked by script. Image quality was not. Treat every numeric value as a tuned starting point.
- **Sampler integers are UNVERIFIED.** The official source for the enum could not be fetched. The mapping in section 2 is recalled, not confirmed. Fix: run `draw-things-cli generate --help`, or compare against the Draw Things app config JSON. If it differs, change section 2 and apply it to every `"sampler"` value.
- **`schedule_sampler` is omitted.** As far as I know, Draw Things encodes the schedule inside the sampler variant (Karras, Trailing, AYS), so no separate key is needed. If your build requires it, add `"schedule_sampler": <n>` to each `--config-json`.
- **LoRA files** must be resolvable by Draw Things (models folder). If `file` is not found, import or convert the LoRA first (`draw-things-cli models import`, unverified syntax).
- **Klein filename** `flux_2_klein_4b_q6p.ckpt` comes from the official README example. Use your installed Klein filename if it differs.
- **Output path** uses `"$HOME/..."` in double quotes. A quoted `'~/...'` is not expanded by the shell and would create a literal `~` folder.

## 1. Conventions

- Dimensions are multiples of 64. SDXL native: `1024x1024`. Portrait page: `832x1216`. Landscape: `1216x832`. Wide: `1344x768`. Draft speed: `768x768`.
- Klein: native `1024x1024`. Keep the same aspect set.
- Every recipe has a `--seed`. Change it to get variations. Keep the same seed only when comparing other settings.
- Kids recipes carry a safety negative block. Do not remove it for audiences under 13.
- Klein distilled (cfg 1) ignores negative prompts. Klein recipes omit `--negative-prompt`. Phrase exclusions positively.
- SDXL LoRAs do not load on Klein. Klein recipes use `"loras": []`.

## 2. Enums and parameter bands

### Sampler integers (UNVERIFIED, see section 0)

| Int | Name | Use for |
|---|---|---|
| 0 | DPM++ 2M Karras | Line art, illustration, painting, sketches. Clean, stable edges |
| 1 | Euler A | Animagine, anime, tag prompts |
| 4 | DPM++ SDE Karras | Photo and photorealism. More micro-detail, slower per step |
| 7 | Euler A Trailing | Flux Klein |

### Parameter bands by model family

| Family | Steps | cfg | Notes |
|---|---|---|---|
| Juggernaut XL v9 / X (photo) | 30-38 | 4-5 | cfg above 6 looks fried. SDE sampler wants fewer steps than 2M |
| Juggernaut XL v9 / X (illustration, line art) | 28-34 | 6-7 | Higher cfg for strict prompt adherence on line art |
| ColorfulXL v6 | 26-32 | 6-7 | Saturated, flat-friendly. Best default for kids and flat styles |
| Animagine XL v3.1 | 26-30 | 5-7 | Danbooru tag syntax, `Euler A` |
| Flux Klein distilled | 4 | 1.0 | Natural-language prompts, no negative prompt, no weight syntax |

### LoRA weights

| LoRA file | Trigger words | Weight | Works with |
|---|---|---|---|
| `StorybookRedmondV2-KidsBook-KidsRedmAF.safetensors` | `KidsRedmAF, Kids Book` | 0.6-0.9 | ColorfulXL, Juggernaut |
| `ColoringBookRedmond-ColoringBook-ColoringBookAF.safetensors` | `ColoringBookAF, Coloring Book` | 0.5-1.0 | ColorfulXL, Juggernaut |
| `LineAniRedmondV2-Lineart-LineAniAF.safetensors` | `LineAniAF, lineart` | 0.6-0.9 | Animagine |
| `add-detail-xl.safetensors` (Detail Tweaker XL mirror) | none | 0.5-1.5 (range -3 to 3). Use 0.5-0.8 on line art | Any SDXL |
| `AnalogRedmondV2-Analog-AnalogRedmAF.safetensors` | `AnalogRedmAF, Analog` | 0.4-0.8 | Juggernaut |
| `3d_render_style_xl.safetensors` | `3d style, 3d, 3d render` | 0.5-0.8 | Animagine, ColorfulXL |
| `pixar-style.safetensors` (slider) | `pixar-style` | 1.5-2.5 | ColorfulXL |
| `oil-painting-slider.safetensors` (renamed from "oil painting") | `oil painting` | 1.5-2.5 | ColorfulXL, Juggernaut v9 |
| `epic-oil-painting-slider.safetensors` (renamed) | `epic oil painting` | 1.5-2.5 | Juggernaut v9, ColorfulXL |
| `sketch-style-xl.safetensors` | `sketch, monochrome, greyscale, traditional media` | 0.6-0.9 | Animagine (trained for Animagine 2.0) |

Stacking: at most 2 style LoRAs. Keep the sum of weights at or below about 1.5, except for sliders, which use their own scale. A detail LoRA added to a line-art LoRA must stay at 0.8 or lower, or it adds shading.

## 3. Routing: request to recipe

Extract these fields from the user request. Apply the default when a field is missing.

| Field | Values | Default |
|---|---|---|
| genre | reading_book, coloring, line_art, mandala, sketch, anime_2d, anime_3d, digital, photo, oil, photoreal | ask only if no genre can be inferred |
| audience | toddler (2-4), early (5-7), middle (8-12), adult (18+), senior_accessible | adult for mandala, photo, oil, photoreal. early for reading_book |
| color | color, b/w | per genre |
| detail | low, medium, high | derived from audience |
| aspect | square, portrait, landscape | portrait for pages, landscape for scenes |

Model selection rules:

1. Black-and-white page for coloring (any age): ColorfulXL or Juggernaut + ColoringBook LoRA. ColorfulXL for toddler through early. Juggernaut for middle and adult density.
2. Flat, saturated, friendly color (kids book, vector-like): ColorfulXL.
3. Anything photographic or painterly-realistic: Juggernaut. X for modern clean detail, v9 for portraits and film looks.
4. Anime, manga, tag-driven characters: Animagine.
5. User wants speed, natural-language prompting, or multi-reference character consistency: Klein.
6. If a requested style has no matching LoRA, use prompt-only recipes. Do not invent LoRA filenames.

Conflicts and hybrids:

- Audience beats style. "Adult coloring book for a 6 year old" means use the early recipe.
- Kids coloring in anime style: use B2 and add `cute anime style, big eyes` to the prompt. Do not use Animagine with human child tags.
- Anime characters are always written as adults (`mature female`, `adult`). Kids anime-style content uses animals or creatures.
- Mandala for kids: C2. Mandala for adults: C1.
- Consistency across book pages: keep an identical character descriptor block in every prompt. Klein with a reference image is the stronger option.

## 4. Negative prompt blocks

Commands inline these in full. Use the names when composing new ones.

- `NEG_LINEART`: color, colored, shading, gray, grayscale fill, gradient, shadow, filled areas, solid black fills, texture, photo, 3d render, text, watermark, signature, border, frame, blurry, messy lines, broken lines, sketch
- `NEG_KIDS`: scary, violence, blood, weapon, creepy, nsfw, nude, suggestive, text, watermark
- `NEG_PHOTO`: cartoon, illustration, painting, drawing, anime, 3d render, cgi, plastic skin, oversmoothed, deformed, extra fingers, bad anatomy, lowres, blurry, watermark, text
- `NEG_ANIME` (Animagine): nsfw, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digits, fewer digits, worst quality, low quality, jpeg artifacts, signature, watermark, blurry, unfinished, displeasing

## 5. Prompt anatomy

- **Line art / coloring:** `[trigger words], [subject + action], [detail level], [line weight], pure white background, no shading, centered`
- **Reading book:** `[trigger words], [character descriptor block], [action], [setting], [mood/lighting], [palette]`
- **Animagine:** `[count/subject tags], [appearance], [action], [setting], masterpiece, best quality, very aesthetic, absurdres, safe`
- **Photo:** `[RAW photo], [subject], [light], [lens + aperture], [texture cues], [grain]`
- **Painting:** `[trigger word], [subject], [brushwork cues], [surface], [palette], [art-movement anchor]`
- **Klein:** one or two natural sentences. Medium, subject, line/texture rules, background. State exclusions as "no X".

## 6. Evaluation rubric

Score each output 0-2 per row. Accept at 8 or higher. Regenerate with a new seed first. After two failures change the model or LoRA weight, not only the seed.

| Check | Applies to | Pass condition (heuristic) |
|---|---|---|
| Prompt match | all | Subject, count and action match the request |
| Clean line art | coloring, mandala, line_art | Under about 2% non-white, non-black pixels. No gray fills. Mostly closed regions |
| Line weight fits age | coloring | Toddler: thick, few regions. Adult: fine, dense, uniform |
| No text or watermark | all | None visible |
| Symmetry | mandala | Left-right mirror difference is low. Center is near the canvas center |
| Anatomy | people, animals | Correct fingers, limbs, eyes |
| Style fidelity | all | Reads as the requested medium (impasto, graphite, flat vector) |
| Child safety | audience under 13 | No frightening, suggestive or violent content |
| Print readiness | print books | Native resolution is enough for the target size (see tips) |

## 7. Tuning cheat sheet

| Symptom | Change |
|---|---|
| Gray shading or fills in line art | Add `shading, gray` to negative. Lower detail LoRA. Raise cfg by 0.5 |
| Lines too thin | Prompt `extra thick bold outlines`. Raise ColoringBook weight by 0.1 |
| Too busy for age | Add `simple shapes, minimal detail, large open areas`. Remove detail LoRA |
| Burnt or oversharpened photo | Lower cfg by 0.5-1. Drop detail LoRA weight |
| Plastic skin | Add `visible pores, natural skin texture`. Use `NEG_PHOTO` plastic-skin terms |
| LoRA overpowers subject | Lower weight by 0.2. Move trigger words to the end of the prompt |
| Style too weak | Raise weight by 0.1-0.2. Repeat the trigger word once |
| Mandala asymmetric | Say `perfect radial symmetry, centered`. Raise steps by 4. Or mirror a half in post |
| Anime hands bad | Add `bad hands` to negative. Prefer poses with hands hidden |
| Flat, dull color | Raise cfg by 0.5. Switch to ColorfulXL |

Draft vs final: for drafts use `768x768` and steps minus 30%. Regenerate the chosen composition at full settings.

## 8. Practical tips

- **Print size:** 1024 px is only 3.4 inches at 300 DPI. A US Letter page needs 2550x3300. Generate at `832x1216`, then upscale about 2.5-3x with an external upscaler. Coloring pages upscale well because lines are simple.
- **Black-and-white cleanup:** convert to grayscale, then threshold so any gray becomes white or black. This fixes most stray gray fills.
- **Variation batch:** generate 4 seeds and score with the rubric. Vary cfg by 0.5 on seeds 3 and 4.
- **Book characters:** write the descriptor block once (species, colors, clothes, size) and paste it into every page prompt.

## 9. Recipe index

| ID | Genre | Audience | Model | LoRAs | Steps | cfg | Sampler |
|---|---|---|---|---|---|---|---|
| A1 | reading_book | toddler | ColorfulXL | Storybook 0.8 | 28 | 6 | 0 |
| A2 | reading_book | early | ColorfulXL | Storybook 0.8 | 30 | 6 | 0 |
| A3 | reading_book | middle | Juggernaut X | Storybook 0.6 | 30 | 5.5 | 4 |
| A4 | reading_book | early (anime-leaning) | Animagine | none | 28 | 6 | 1 |
| A5 | reading_book | early | Klein | none | 4 | 1 | 7 |
| B1 | coloring | toddler | ColorfulXL | ColoringBook 0.9 | 26 | 7 | 0 |
| B2 | coloring | early | ColorfulXL | ColoringBook 0.9 | 28 | 7 | 0 |
| B3 | coloring | middle | Juggernaut v9 | ColoringBook 0.8 | 30 | 6.5 | 0 |
| B4 | coloring | adult | Juggernaut X | ColoringBook 0.6 + Detail 0.6 | 32 | 6.5 | 0 |
| B5 | coloring | adult (botanical) | ColorfulXL | ColoringBook 0.8 | 30 | 7 | 0 |
| B6 | coloring | senior_accessible | ColorfulXL | ColoringBook 1.0 | 26 | 7 | 0 |
| B7 | line_art | adult (manga ink) | Animagine | LineAni 0.8 | 28 | 6 | 1 |
| B8 | coloring | adult | Klein | none | 4 | 1 | 7 |
| C1 | mandala | adult | Juggernaut X | ColoringBook 0.5 + Detail 0.6 | 34 | 7 | 0 |
| C2 | mandala | toddler to early | ColorfulXL | ColoringBook 0.9 | 26 | 7 | 0 |
| C3 | mandala | adult | Klein | none | 4 | 1 | 7 |
| D1 | sketch | general (graphite) | Juggernaut v9 | none | 30 | 5.5 | 0 |
| D2 | sketch | general (anime) | Animagine | Sketch Style 0.8 | 28 | 6 | 1 |
| D3 | sketch | general (charcoal/ink) | ColorfulXL | none | 28 | 6 | 0 |
| D4 | sketch | general | Klein | none | 4 | 1 | 7 |
| E1 | anime_2d | teen/adult (character) | Animagine | none | 28 | 6 | 1 |
| E2 | anime_2d | all (scenery) | Animagine | none | 28 | 6 | 1 |
| E3 | anime_2d | all | Klein | none | 4 | 1 | 7 |
| F1 | anime_3d | adult (character) | Animagine | 3D Render 0.7 | 28 | 6 | 1 |
| F2 | anime_3d | early (Pixar-like animal) | ColorfulXL | Pixar 1.8 | 30 | 6 | 0 |
| F3 | anime_3d | all | Klein | none | 4 | 1 | 7 |
| G1 | digital | general (concept art) | ColorfulXL | Detail 0.8 | 30 | 6 | 0 |
| G2 | digital | general (flat vector) | ColorfulXL | none | 28 | 6.5 | 0 |
| G3 | digital | general | Klein | none | 4 | 1 | 7 |
| H1 | photo | adult (portrait) | Juggernaut X | none | 32 | 4.5 | 4 |
| H2 | photo | general (landscape) | Juggernaut X | none | 30 | 5 | 4 |
| H3 | photo | general (analog film) | Juggernaut v9 | Analog 0.6 | 30 | 5 | 4 |
| H4 | photo | general | Klein | none | 4 | 1 | 7 |
| I1 | oil | general (classical landscape) | ColorfulXL | Oil Painting 1.5 | 32 | 6 | 0 |
| I2 | oil | general (expressive portrait) | Juggernaut v9 | Epic Oil Painting 1.5 | 32 | 5.5 | 0 |
| I3 | oil | general | Klein | none | 4 | 1 | 7 |
| J1 | photoreal | adult (portrait) | Juggernaut X | Detail 1.0 | 38 | 4.5 | 4 |
| J2 | photoreal | general (macro) | Juggernaut X | Detail 0.8 | 36 | 5 | 4 |
| J3 | photoreal | general | Klein | none | 4 | 1 | 7 |

## 10. Recipes: kids reading book illustrations

### A1: Toddler board-book page (ages 2-4)
Use when: very simple, bold, friendly picture, one character, plain background.

```bash
draw-things-cli generate \
--model colorfulxl_v6.0_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_reading_toddler_bear.png" \
--prompt "KidsRedmAF, Kids Book, a smiling round brown bear holding a red balloon, simple big shapes, flat soft colors, bold friendly outlines, plain pale yellow background, centered, minimalist, picture book illustration" \
--negative-prompt "scary, violence, blood, weapon, creepy, nsfw, nude, suggestive, text, watermark, busy background, tiny details, realistic, dark, complex shading" \
--width 1024 --height 1024 --steps 28 --cfg 6 --seed 101 \
--config-json '{
"sampler": 0,
"loras": [
  {"file": "StorybookRedmondV2-KidsBook-KidsRedmAF.safetensors", "weight": 0.8, "mode": "all"}
]
}'
```

Why: ColorfulXL gives flat saturated color. cfg 6 keeps shapes simple. Square suits board books. "plain background, minimalist" limits clutter.
Eval: one subject, no text, no background objects. Fix: if busy, add `isolated subject` and lower LoRA to 0.7.

### A2: Early-reader scene (ages 5-7)
Use when: a character in a setting, warm and readable, with some background.

```bash
draw-things-cli generate \
--model colorfulxl_v6.0_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_reading_early_fox_forest.png" \
--prompt "KidsRedmAF, Kids Book, a small orange fox with a blue scarf walking along a forest path, tall friendly trees, mushrooms and wildflowers, warm afternoon light, soft watercolor-like texture, gentle colors, children book illustration, wide scene" \
--negative-prompt "scary, violence, blood, weapon, creepy, nsfw, nude, suggestive, text, watermark, photo, realistic, dark, horror, deformed, extra limbs" \
--width 1216 --height 832 --steps 30 --cfg 6 --seed 102 \
--config-json '{
"sampler": 0,
"loras": [
  {"file": "StorybookRedmondV2-KidsBook-KidsRedmAF.safetensors", "weight": 0.8, "mode": "all"}
]
}'
```

Why: landscape fits two-page spreads. Weight 0.8 keeps the storybook look without flattening the scene. Warm light and "gentle colors" bias toward a calm mood.
Eval: character is readable at thumbnail size, with clear space for page text. Fix: add `empty sky area for text` to reserve space.

### A3: Middle-grade painterly adventure (ages 8-12)
Use when: richer detail, more atmosphere, adventure or fantasy.

```bash
draw-things-cli generate \
--model juggernaut_xl_x_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_reading_middle_island_map.png" \
--prompt "KidsRedmAF, Kids Book, two young explorers with backpacks and a small green dragon on a rocky cliff overlooking a glowing island archipelago, painterly storybook illustration, rich detail, dramatic sunset sky, adventure mood, detailed foliage" \
--negative-prompt "scary, violence, blood, weapon, creepy, nsfw, nude, suggestive, text, watermark, photo, lowres, blurry, deformed, extra limbs, bad anatomy" \
--width 1216 --height 832 --steps 30 --cfg 5.5 --seed 103 \
--config-json '{
"sampler": 4,
"loras": [
  {"file": "StorybookRedmondV2-KidsBook-KidsRedmAF.safetensors", "weight": 0.6, "mode": "all"}
]
}'
```

Why: Juggernaut X adds depth and lighting. A lower LoRA weight (0.6) keeps detail instead of flat shapes. SDE sampler gives richer texture at cfg 5.5.
Eval: faces and hands acceptable at this detail level. Fix: if too realistic, raise LoRA to 0.8 and add `flat painterly shapes`.

### A4: Early-reader, cartoon/anime-leaning (animal characters)
Use when: user wants a manga or anime flavor for a kids book. Uses animals to avoid childlike human anime tags.

```bash
draw-things-cli generate \
--model animagine_xl_v3.1_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_reading_early_anime_cat.png" \
--prompt "no humans, cat, solo, cute, chibi, big sparkling eyes, wearing a tiny red cape, sitting on a pile of books, cozy library, warm light, soft colors, children book illustration, masterpiece, best quality, very aesthetic, absurdres, safe" \
--negative-prompt "nsfw, lowres, bad anatomy, text, error, worst quality, low quality, jpeg artifacts, signature, watermark, blurry, unfinished, displeasing, scary, creepy, realistic" \
--width 1024 --height 1024 --steps 28 --cfg 6 --seed 104 \
--config-json '{
"sampler": 1,
"loras": []
}'
```

Why: Animagine plus `Euler A` is its native setup. `no humans` and the `safe` rating tag keep the output child-appropriate. No LoRA avoids fighting Animagine's own style.
Eval: no humanoid child figure, clean eyes. Fix: add `simple background` if cluttered.

### A5: Early-reader, Flux Klein (fast, reference-friendly)
Use when: speed or multi-reference character consistency matters. Negative prompt not supported.

```bash
draw-things-cli generate \
--model flux_2_klein_4b_q6p.ckpt \
--output "$HOME/Dev/tmp/klein_reading_early_rabbit.png" \
--prompt "A children picture book illustration of a small grey rabbit in a yellow raincoat jumping in a puddle, soft watercolor style, warm gentle colors, simple green meadow background, cheerful mood, no text" \
--width 1024 --height 1024 --steps 4 --cfg 1 --seed 105 \
--config-json '{
"sampler": 7,
"loras": []
}'
```

Why: Klein distilled is built for 4 steps at cfg 1. Natural-language style description replaces LoRAs. "no text" is phrased positively because negatives are ignored.
Eval: style stays soft and watercolor-like. Fix: repeat the style phrase once for stronger effect.

## 11. Recipes: coloring books and line art

### B1: Toddler coloring page (ages 2-4)
Use when: very big shapes, one subject, thick lines.

```bash
draw-things-cli generate \
--model colorfulxl_v6.0_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_coloring_toddler_elephant.png" \
--prompt "ColoringBookAF, Coloring Book, a big happy elephant waving, very simple shapes, extra thick bold black outlines, large open areas to color, minimal detail, pure white background, centered, full body" \
--negative-prompt "color, colored, shading, gray, grayscale fill, gradient, shadow, filled areas, solid black fills, texture, photo, 3d render, text, watermark, border, frame, blurry, messy lines, broken lines, sketch, small details, tiny patterns, intricate, busy background" \
--width 1024 --height 1024 --steps 26 --cfg 7 --seed 201 \
--config-json '{
"sampler": 0,
"loras": [
  {"file": "ColoringBookRedmond-ColoringBook-ColoringBookAF.safetensors", "weight": 0.9, "mode": "all"}
]
}'
```

Why: weight 0.9 strengthens the coloring-page look. cfg 7 enforces "thick" and "no shading". Fewer steps are fine for simple shapes.
Eval: few regions, thick uniform lines, no gray. Fix: lines thin: add `jumbo outlines`. Add `one single subject` if multiple appear.

### B2: Early-reader coloring page (ages 5-7)
Use when: medium detail, a simple scene, clear closed shapes.

```bash
draw-things-cli generate \
--model colorfulxl_v6.0_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_coloring_early_dragon.png" \
--prompt "ColoringBookAF, Coloring Book, a friendly dragon reading a book under a big tree, simple leaves and mushrooms, medium detail, thick clean black outlines, pure white background, no shading, portrait page" \
--negative-prompt "color, colored, shading, gray, grayscale fill, gradient, shadow, filled areas, solid black fills, texture, photo, 3d render, text, watermark, border, frame, blurry, messy lines, broken lines, sketch, scary, nsfw, tiny details" \
--width 832 --height 1216 --steps 28 --cfg 7 --seed 202 \
--config-json '{
"sampler": 0,
"loras": [
  {"file": "ColoringBookRedmond-ColoringBook-ColoringBookAF.safetensors", "weight": 0.9, "mode": "all"}
]
}'
```

Why: portrait ratio matches book pages. "medium detail" and "simple leaves" cap complexity for small hands.
Eval: all shapes closed, background not overfilled. Fix: if cluttered, add `simple background, few objects`.

### B3: Middle-grade coloring page (ages 8-12)
Use when: more detail and pattern, still clear linework.

```bash
draw-things-cli generate \
--model juggernaut_xl_v9_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_coloring_middle_reef.png" \
--prompt "ColoringBookAF, Coloring Book, an underwater coral reef with a sea turtle, a manta ray and tropical fish, detailed but clear black linework, patterned shells and scales, seaweed and bubbles, pure white background, no shading" \
--negative-prompt "color, colored, shading, gray, grayscale fill, gradient, shadow, filled areas, solid black fills, texture, photo, 3d render, text, watermark, border, frame, blurry, messy lines, broken lines, sketch, scary, nsfw" \
--width 832 --height 1216 --steps 30 --cfg 6.5 --seed 203 \
--config-json '{
"sampler": 0,
"loras": [
  {"file": "ColoringBookRedmond-ColoringBook-ColoringBookAF.safetensors", "weight": 0.8, "mode": "all"}
]
}'
```

Why: Juggernaut handles denser patterns than ColorfulXL. Weight 0.8 keeps lines clean without forcing thick strokes.
Eval: pattern density moderate, no gray fill. Fix: lines too fine: raise weight to 0.9 and add `medium line weight`.

### B4: Adult intricate coloring page
Use when: dense, fine, mandala-like or zentangle detail.

```bash
draw-things-cli generate \
--model juggernaut_xl_x_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_coloring_adult_owl.png" \
--prompt "ColoringBookAF, intricate adult coloring book page, a mystical owl perched on a crescent moon, complex mandala patterns in the feathers, dense zentangle details, fine uniform black linework, pure white background, centered, high detail" \
--negative-prompt "color, colored, shading, gray, grayscale fill, gradient, shadow, filled areas, solid black fills, texture, photo, 3d render, text, watermark, border, frame, blurry, messy lines, broken lines, sketch, bold thick lines, cartoon" \
--width 1024 --height 1024 --steps 32 --cfg 6.5 --seed 204 \
--config-json '{
"sampler": 0,
"loras": [
  {"file": "ColoringBookRedmond-ColoringBook-ColoringBookAF.safetensors", "weight": 0.6, "mode": "all"},
  {"file": "add-detail-xl.safetensors", "weight": 0.6, "mode": "all"}
]
}'
```

Why: coloring LoRA at 0.6 leaves room for Juggernaut's detail. Detail Tweaker adds fine pattern density. Keep it at 0.6 to avoid shading. More steps resolve small structures.
Eval: uniform fine lines, many small regions, no gray. Fix: if gray appears, drop Detail to 0.3 and add `pure black lines only` to the prompt.

### B5: Adult botanical coloring page
Use when: elegant, realistic-leaning flora or nature, calm style.

```bash
draw-things-cli generate \
--model colorfulxl_v6.0_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_coloring_adult_peonies.png" \
--prompt "ColoringBookAF, Coloring Book, botanical illustration of peonies and ferns in a vase, fine elegant line art, varied petal details, delicate veins on leaves, pure white background, no shading" \
--negative-prompt "color, colored, shading, gray, grayscale fill, gradient, shadow, filled areas, solid black fills, texture, photo, 3d render, text, watermark, border, frame, blurry, messy lines, broken lines, sketch, cartoon, thick lines" \
--width 832 --height 1216 --steps 30 --cfg 7 --seed 205 \
--config-json '{
"sampler": 0,
"loras": [
  {"file": "ColoringBookRedmond-ColoringBook-ColoringBookAF.safetensors", "weight": 0.8, "mode": "all"}
]
}'
```

Why: ColorfulXL keeps clean contours. `fine elegant` and `thick lines` in the negative steer toward adult line weight.
Eval: petals distinguishable, lines thin but continuous. Fix: lines break: raise steps to 34.

### B6: Senior-accessible / low-vision coloring page
Use when: calming, large regions, high contrast, easy to see.

```bash
draw-things-cli generate \
--model colorfulxl_v6.0_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_coloring_senior_lighthouse.png" \
--prompt "ColoringBookAF, Coloring Book, a calm lighthouse on a rocky shore with two gulls and gentle waves, simple uncluttered scene, bold clear black outlines, large coloring regions, pure white background, no shading" \
--negative-prompt "color, colored, shading, gray, grayscale fill, gradient, shadow, filled areas, solid black fills, texture, photo, 3d render, text, watermark, border, frame, blurry, messy lines, broken lines, sketch, tiny details, intricate, busy background" \
--width 1216 --height 832 --steps 26 --cfg 7 --seed 206 \
--config-json '{
"sampler": 0,
"loras": [
  {"file": "ColoringBookRedmond-ColoringBook-ColoringBookAF.safetensors", "weight": 1.0, "mode": "all"}
]
}'
```

Why: weight 1.0 gives maximum coloring-page behavior. Mature subject matter with toddler-level region size suits adults who want easy pages. Landscape scenes read well at a distance.
Eval: regions large, lines thick and high contrast. Fix: if regions are small, add `very large shapes`.

### B7: Manga-style ink line art (adult)
Use when: user wants clean ink line art of a character, not a coloring page. Characters are adult.

```bash
draw-things-cli generate \
--model animagine_xl_v3.1_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_lineart_adult_ranger.png" \
--prompt "LineAniAF, lineart, monochrome, greyscale, white background, 1girl, solo, mature female, adult, fantasy ranger with a hooded cloak and bow, standing, clean ink linework, masterpiece, best quality, very aesthetic, absurdres, safe" \
--negative-prompt "nsfw, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digits, worst quality, low quality, jpeg artifacts, signature, watermark, blurry, color, colored, shading, gradient" \
--width 832 --height 1216 --steps 28 --cfg 6 --seed 207 \
--config-json '{
"sampler": 1,
"loras": [
  {"file": "LineAniRedmondV2-Lineart-LineAniAF.safetensors", "weight": 0.8, "mode": "all"}
]
}'
```

Why: Animagine plus LineAni gives manga linework. `monochrome, greyscale` plus the color negatives keep it black and white. `mature female, adult` fixes character age.
Eval: ink-like uniform lines, hands acceptable. Fix: weak lineart: raise LineAni to 0.9.

### B8: Adult coloring page, Flux Klein

```bash
draw-things-cli generate \
--model flux_2_klein_4b_q6p.ckpt \
--output "$HOME/Dev/tmp/klein_coloring_adult_owl.png" \
--prompt "A black-and-white coloring book page for adults: an owl on a crescent moon filled with intricate mandala and zentangle patterns. Clean uniform thin black outlines on a pure white background, no shading, no gray, no color, no text." \
--width 1024 --height 1024 --steps 4 --cfg 1 --seed 208 \
--config-json '{
"sampler": 7,
"loras": []
}'
```

Why: four-step Klein follows line-art instructions well when exclusions are written as `no X`. Fast option for drafts.
Eval: lines clean, little gray. Fix: threshold to pure black and white in post if gray appears.

## 12. Recipes: mandalas

### C1: Adult detailed mandala

```bash
draw-things-cli generate \
--model juggernaut_xl_x_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_mandala_adult_lotus.png" \
--prompt "ColoringBookAF, Coloring Book, intricate circular mandala, perfect radial symmetry, centered, layered lotus petals, paisley and floral motifs, fine uniform black lines, black and white line art, pure white background" \
--negative-prompt "color, colored, shading, gray, grayscale fill, gradient, shadow, filled areas, solid black fills, texture, photo, 3d render, text, watermark, border, frame, blurry, messy lines, broken lines, sketch, asymmetrical, off-center, cropped" \
--width 1024 --height 1024 --steps 34 --cfg 7 --seed 301 \
--config-json '{
"sampler": 0,
"loras": [
  {"file": "ColoringBookRedmond-ColoringBook-ColoringBookAF.safetensors", "weight": 0.5, "mode": "all"},
  {"file": "add-detail-xl.safetensors", "weight": 0.6, "mode": "all"}
]
}'
```

Why: no mandala LoRA exists in this set, so the prompt carries symmetry. Square canvas supports radial layout. Higher steps and cfg 7 improve symmetric structure. Coloring LoRA at 0.5 keeps lines clean without simplifying.
Eval: center within about 5% of canvas center, mirror difference low. Fix: asymmetry persists: generate several seeds, keep the best, or mirror one half in post.

### C2: Simple mandala (toddler to early reader)

```bash
draw-things-cli generate \
--model colorfulxl_v6.0_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_mandala_kids_flower.png" \
--prompt "ColoringBookAF, Coloring Book, a simple round flower mandala, big petals, few large shapes, thick black outlines, radial symmetry, centered, pure white background" \
--negative-prompt "color, colored, shading, gray, grayscale fill, gradient, shadow, filled areas, solid black fills, texture, photo, text, watermark, border, frame, blurry, messy lines, intricate, tiny details, dense patterns, asymmetrical" \
--width 1024 --height 1024 --steps 26 --cfg 7 --seed 302 \
--config-json '{
"sampler": 0,
"loras": [
  {"file": "ColoringBookRedmond-ColoringBook-ColoringBookAF.safetensors", "weight": 0.9, "mode": "all"}
]
}'
```

Why: ColorfulXL with high LoRA weight yields chunky, forgiving shapes. `dense patterns` in the negative blocks adult complexity.
Eval: under about 12 petals, thick lines. Fix: too complex: add `only one ring of petals`.

### C3: Adult mandala, Flux Klein

```bash
draw-things-cli generate \
--model flux_2_klein_4b_q6p.ckpt \
--output "$HOME/Dev/tmp/klein_mandala_adult.png" \
--prompt "A perfectly symmetrical circular mandala coloring page, centered, with layered petals and fine geometric patterns. Thin uniform black lines on a pure white background, no shading, no gray, no color, no text." \
--width 1024 --height 1024 --steps 4 --cfg 1 --seed 303 \
--config-json '{
"sampler": 7,
"loras": []
}'
```

Why: Klein handles symmetry and geometry well. Four steps make it a quick draft path.
Eval: symmetry, line continuity. Fix: symmetry weak: add `radially symmetric, like a kaleidoscope`.

## 13. Recipes: pencil and artistic sketches

### D1: Graphite pencil portrait (prompt-only)

```bash
draw-things-cli generate \
--model juggernaut_xl_v9_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_sketch_graphite_fisherman.png" \
--prompt "graphite pencil sketch portrait of an elderly fisherman, detailed cross-hatching, visible paper grain, soft smudged shading, hand-drawn, on off-white sketchbook paper, monochrome" \
--negative-prompt "color, photo, digital painting, 3d render, smooth gradient, airbrushed, text, watermark, border, anime" \
--width 832 --height 1216 --steps 30 --cfg 5.5 --seed 401 \
--config-json '{
"sampler": 0,
"loras": []
}'
```

Why: no verified pencil LoRA fits Juggernaut, so style cues carry it. Juggernaut v9 renders faces and tonal range well. cfg 5.5 avoids over-crisp digital edges.
Eval: visible hatching and paper grain, no color. Fix: too photographic: add `rough sketch lines, construction lines`.

### D2: Anime pencil/monochrome sketch

```bash
draw-things-cli generate \
--model animagine_xl_v3.1_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_sketch_anime_scarf.png" \
--prompt "face focus, 1girl, solo, mature female, short hair, scarf, looking at viewer, upper body, sketch, monochrome, greyscale, traditional media, masterpiece, best quality, very aesthetic, absurdres, safe" \
--negative-prompt "nsfw, lowres, bad anatomy, bad hands, text, error, worst quality, low quality, jpeg artifacts, signature, watermark, blurry, color, colored" \
--width 832 --height 1216 --steps 28 --cfg 6 --seed 402 \
--config-json '{
"sampler": 1,
"loras": [
  {"file": "sketch-style-xl.safetensors", "weight": 0.8, "mode": "all"}
]
}'
```

Why: this LoRA was trained on Animagine-family tags (`sketch, monochrome, greyscale, traditional media`). Weight 0.8 gives a clear sketch look.
Eval: monochrome, visible pencil strokes. Fix: if color leaks, add `colorful` to the negative. Compatibility with Animagine 3.1 is unconfirmed.

### D3: Loose charcoal / ink landscape sketch

```bash
draw-things-cli generate \
--model colorfulxl_v6.0_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_sketch_charcoal_village.png" \
--prompt "loose charcoal and ink sketch of a mountain village, expressive gestural strokes, smudged charcoal shadows, white paper, high contrast, monochrome, artistic study" \
--negative-prompt "color, photo, 3d render, clean vector, smooth digital, text, watermark, border" \
--width 1216 --height 832 --steps 28 --cfg 6 --seed 403 \
--config-json '{
"sampler": 0,
"loras": []
}'
```

Why: ColorfulXL's illustrative bias handles loose marks well. cfg 6 allows some looseness.
Eval: gestural strokes, strong value contrast. Fix: too clean: add `rough, unfinished, bold sweeping strokes`.

### D4: Sketch, Flux Klein

```bash
draw-things-cli generate \
--model flux_2_klein_4b_q6p.ckpt \
--output "$HOME/Dev/tmp/klein_sketch_pencil_cat.png" \
--prompt "A detailed graphite pencil sketch of a sleeping cat on a windowsill, cross-hatching, visible paper grain, soft smudged shading, monochrome, on off-white paper." \
--width 1024 --height 1024 --steps 4 --cfg 1 --seed 404 \
--config-json '{
"sampler": 7,
"loras": []
}'
```

Why: Klein responds to medium and texture words directly.
Eval: pencil grain visible. Fix: add `no color, no digital smoothness`.

## 14. Recipes: 2D anime

### E1: Anime character key visual (adult character)

```bash
draw-things-cli generate \
--model animagine_xl_v3.1_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_anime2d_knight_cliff.png" \
--prompt "1girl, solo, mature female, long silver hair, armor, red cape, holding a sword, standing on a cliff at sunset, wind, dynamic pose, cinematic lighting, detailed background, masterpiece, best quality, very aesthetic, absurdres, safe" \
--negative-prompt "nsfw, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digits, fewer digits, worst quality, low quality, jpeg artifacts, signature, watermark, blurry, unfinished, displeasing" \
--width 832 --height 1216 --steps 28 --cfg 6 --seed 501 \
--config-json '{
"sampler": 1,
"loras": []
}'
```

Why: native Animagine settings (`Euler A`, cfg 5-7, about 28 steps) with its recommended quality tags. Portrait ratio fits a character.
Eval: hands and sword readable, lighting consistent. Fix: bad hands: add `hands behind back` or hide hands.

### E2: Anime scenery (no characters)

```bash
draw-things-cli generate \
--model animagine_xl_v3.1_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_anime2d_scenery_station.png" \
--prompt "scenery, no humans, a small rural train station in summer, blue sky with large clouds, green fields, wildflowers, soft sunlight, detailed background, anime style, masterpiece, best quality, very aesthetic, absurdres, safe" \
--negative-prompt "nsfw, lowres, text, error, worst quality, low quality, jpeg artifacts, signature, watermark, blurry, unfinished, displeasing, humans" \
--width 1216 --height 832 --steps 28 --cfg 6 --seed 502 \
--config-json '{
"sampler": 1,
"loras": []
}'
```

Why: `scenery, no humans` is Animagine's tag pair for backgrounds. Landscape ratio suits environments.
Eval: no figures, clean sky gradients. Fix: stray figures: add `1girl, 1boy, solo` to the negative.

### E3: Anime, Flux Klein

```bash
draw-things-cli generate \
--model flux_2_klein_4b_q6p.ckpt \
--output "$HOME/Dev/tmp/klein_anime2d_mage.png" \
--prompt "A 2D anime illustration of an adult woman mage with long blue hair casting a glowing spell in a night forest, cel shading, clean line art, vibrant colors, cinematic lighting." \
--width 1024 --height 1024 --steps 4 --cfg 1 --seed 503 \
--config-json '{
"sampler": 7,
"loras": []
}'
```

Why: no tag syntax needed. `cel shading, clean line art` pin the 2D style.
Eval: flat shading, no realism. Fix: realistic skin: add `flat anime colors, no realistic shading`.

## 15. Recipes: 3D anime and 3D character styles

### F1: 3D-rendered anime character (adult)

```bash
draw-things-cli generate \
--model animagine_xl_v3.1_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_anime3d_pilot.png" \
--prompt "3d style, 3d render, 1girl, solo, mature female, short black hair, pilot jacket, goggles on head, smiling, standing in front of a small plane, soft studio lighting, masterpiece, best quality, very aesthetic, absurdres, safe" \
--negative-prompt "nsfw, lowres, bad anatomy, bad hands, text, error, worst quality, low quality, jpeg artifacts, signature, watermark, blurry, flat color, 2d, sketch" \
--width 832 --height 1216 --steps 28 --cfg 6 --seed 601 \
--config-json '{
"sampler": 1,
"loras": [
  {"file": "3d_render_style_xl.safetensors", "weight": 0.7, "mode": "all"}
]
}'
```

Why: Animagine supplies the anime anatomy, the LoRA adds 3D shading. Weight 0.7 keeps both. `2d, flat color` in the negative reinforces depth.
Eval: smooth 3D shading, anime proportions. Fix: too realistic: lower LoRA to 0.5.

### F2: Pixar-style kid-friendly animal

```bash
draw-things-cli generate \
--model colorfulxl_v6.0_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_anime3d_early_fox.png" \
--prompt "pixar-style, a cute baby fox wearing a yellow raincoat, big expressive eyes, soft rim lighting, 3d animated movie still, pastel colors, friendly mood, simple soft background" \
--negative-prompt "scary, violence, blood, weapon, creepy, nsfw, nude, suggestive, text, watermark, 2d, flat, sketch, realistic photo, uncanny, dark" \
--width 1024 --height 1024 --steps 30 --cfg 6 --seed 602 \
--config-json '{
"sampler": 0,
"loras": [
  {"file": "pixar-style.safetensors", "weight": 1.8, "mode": "all"}
]
}'
```

Why: the Pixar LoRA is a slider, so weight 1.8 sits in its working range (about 1.5-2.5). ColorfulXL adds cheerful color. The kids safety block remains.
Eval: soft 3D look, friendly eyes. Fix: weak style: raise to 2.2.

### F3: 3D character, Flux Klein

```bash
draw-things-cli generate \
--model flux_2_klein_4b_q6p.ckpt \
--output "$HOME/Dev/tmp/klein_anime3d_robot.png" \
--prompt "A 3D animated movie still of a small friendly robot watering a plant in a sunny greenhouse, soft studio lighting, smooth stylized shading, vibrant colors, shallow depth of field." \
--width 1024 --height 1024 --steps 4 --cfg 1 --seed 603 \
--config-json '{
"sampler": 7,
"loras": []
}'
```

Why: describing the render look in words works on Klein with no LoRA.
Eval: stylized, not photo. Fix: add `stylized cartoon proportions`.

## 16. Recipes: digital drawings

### G1: Fantasy concept art

```bash
draw-things-cli generate \
--model colorfulxl_v6.0_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_digital_floating_city.png" \
--prompt "digital painting of a floating island city at golden hour, waterfalls, airships, rich saturated color, painterly brushwork, concept art, highly detailed, dramatic clouds" \
--negative-prompt "photo, lowres, blurry, text, watermark, oversaturated, jpeg artifacts, deformed, cropped" \
--width 1216 --height 832 --steps 30 --cfg 6 --seed 701 \
--config-json '{
"sampler": 0,
"loras": [
  {"file": "add-detail-xl.safetensors", "weight": 0.8, "mode": "all"}
]
}'
```

Why: ColorfulXL is strong on saturated illustration. Detail Tweaker at 0.8 adds fine structure in architecture without overbaking.
Eval: coherent perspective, no smeared detail. Fix: noisy: lower Detail to 0.5.

### G2: Flat vector-style illustration

```bash
draw-things-cli generate \
--model colorfulxl_v6.0_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_digital_flat_cafe.png" \
--prompt "flat vector illustration of a cozy coffee shop interior, limited color palette, clean geometric shapes, minimal gradients, modern editorial illustration, warm tones" \
--negative-prompt "photo, 3d render, realistic, texture, noise, heavy gradient, text, watermark, blurry, shadows" \
--width 1216 --height 832 --steps 28 --cfg 6.5 --seed 702 \
--config-json '{
"sampler": 0,
"loras": []
}'
```

Why: no LoRA keeps shapes flat. cfg 6.5 enforces "limited palette, minimal gradients".
Eval: flat fills, few colors. Fix: too textured: add `solid color fills, no texture`.

### G3: Digital illustration, Flux Klein

```bash
draw-things-cli generate \
--model flux_2_klein_4b_q6p.ckpt \
--output "$HOME/Dev/tmp/klein_digital_dragon.png" \
--prompt "A polished digital illustration of a dragon curled around a mountain peak at sunrise, vivid colors, soft gradients, detailed scales, painterly digital art style." \
--width 1024 --height 1024 --steps 4 --cfg 1 --seed 703 \
--config-json '{
"sampler": 7,
"loras": []
}'
```

Why: quick draft of illustrated concepts, style set by words.
Eval: coherent anatomy. Fix: add `clean silhouette, readable composition`.

## 17. Recipes: photography

### H1: Natural-light portrait

```bash
draw-things-cli generate \
--model juggernaut_xl_x_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_photo_portrait_window.png" \
--prompt "RAW photo, portrait of a middle-aged woman with freckles, natural window light, 85mm f/1.8, shallow depth of field, detailed skin texture, soft film grain, candid expression" \
--negative-prompt "cartoon, illustration, painting, drawing, anime, 3d render, cgi, plastic skin, oversmoothed, deformed, extra fingers, bad anatomy, lowres, blurry, watermark, text" \
--width 832 --height 1216 --steps 32 --cfg 4.5 --seed 801 \
--config-json '{
"sampler": 4,
"loras": []
}'
```

Why: low cfg (4.5) prevents the burnt look. Real lens language (85mm f/1.8) drives realistic depth. SDE Karras adds skin micro-detail.
Eval: believable skin, natural eyes. Fix: plastic skin: add `visible pores`, lower cfg to 4.

### H2: Landscape photograph

```bash
draw-things-cli generate \
--model juggernaut_xl_x_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_photo_landscape_lake.png" \
--prompt "RAW photo, misty alpine lake at sunrise, golden hour light, 24mm wide angle, f/8, sharp foreground rocks, high dynamic range, layered mountains, crisp detail" \
--negative-prompt "cartoon, illustration, painting, drawing, anime, 3d render, cgi, oversaturated, lowres, blurry, watermark, text, people" \
--width 1216 --height 832 --steps 30 --cfg 5 --seed 802 \
--config-json '{
"sampler": 4,
"loras": []
}'
```

Why: f/8 and wide-angle language push deep focus. cfg 5 keeps color natural. Landscape ratio matches photographic framing.
Eval: no HDR halos, believable light. Fix: over-processed: lower cfg to 4.5.

### H3: Analog film street photo

```bash
draw-things-cli generate \
--model juggernaut_xl_v9_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_photo_film_alley.png" \
--prompt "AnalogRedmAF, Analog, street photograph of a rainy narrow alley at night, neon reflections on wet pavement, 35mm film, Kodak Portra 400, visible grain, candid, a lone person with an umbrella" \
--negative-prompt "cartoon, illustration, painting, drawing, anime, 3d render, cgi, oversharpened, digital look, lowres, watermark, text" \
--width 832 --height 1216 --steps 30 --cfg 5 --seed 803 \
--config-json '{
"sampler": 4,
"loras": [
  {"file": "AnalogRedmondV2-Analog-AnalogRedmAF.safetensors", "weight": 0.6, "mode": "all"}
]
}'
```

Why: Juggernaut v9 handles film color and faces well. Analog LoRA at 0.6 adds grain and tone without hiding detail. The LoRA's exact effect is inferred from its name and trigger.
Eval: grain present, not blurry. Fix: too muddy: lower LoRA to 0.4.

### H4: Photo, Flux Klein

```bash
draw-things-cli generate \
--model flux_2_klein_4b_q6p.ckpt \
--output "$HOME/Dev/tmp/klein_photo_bread.png" \
--prompt "A photograph of a freshly baked sourdough loaf on a wooden board, soft side window light, shallow depth of field, 100mm macro lens, natural crumb texture, warm tones." \
--width 1024 --height 1024 --steps 4 --cfg 1 --seed 804 \
--config-json '{
"sampler": 7,
"loras": []
}'
```

Why: camera terms steer Klein toward photo output. Fast option for quick drafts.
Eval: realistic texture. Fix: looks rendered: add `unretouched, natural imperfections`.

## 18. Recipes: oil painting

### I1: Classical landscape

```bash
draw-things-cli generate \
--model colorfulxl_v6.0_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_oil_valley_dawn.png" \
--prompt "oil painting, a misty pastoral valley at dawn, visible brushstrokes, canvas texture, impasto highlights, warm earth palette, Hudson River School" \
--negative-prompt "photo, digital art, smooth, 3d render, anime, text, watermark, flat color, lowres" \
--width 1216 --height 832 --steps 32 --cfg 6 --seed 901 \
--config-json '{
"sampler": 0,
"loras": [
  {"file": "oil-painting-slider.safetensors", "weight": 1.5, "mode": "all"}
]
}'
```

Why: the oil-painting LoRA is a slider, so 1.5 is a normal weight. Brushwork words reinforce the surface. Art-movement anchor settles composition.
Eval: visible strokes, canvas feel. Fix: too smooth: raise to 2.0.

### I2: Expressive impasto portrait

```bash
draw-things-cli generate \
--model juggernaut_xl_v9_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_oil_sailor_portrait.png" \
--prompt "epic oil painting, portrait of a weathered sailor, thick impasto palette-knife strokes, dramatic chiaroscuro, textured canvas, rich deep colors" \
--negative-prompt "photo, digital art, smooth, airbrushed, 3d render, anime, text, watermark, lowres, deformed" \
--width 832 --height 1216 --steps 32 --cfg 5.5 --seed 902 \
--config-json '{
"sampler": 0,
"loras": [
  {"file": "epic-oil-painting-slider.safetensors", "weight": 1.5, "mode": "all"}
]
}'
```

Why: Juggernaut v9 keeps facial structure. The epic slider adds drama. cfg 5.5 stays painterly.
Eval: palette-knife texture, face coherent. Fix: face distorts: lower to 1.2.

### I3: Oil painting, Flux Klein

```bash
draw-things-cli generate \
--model flux_2_klein_4b_q6p.ckpt \
--output "$HOME/Dev/tmp/klein_oil_harbor.png" \
--prompt "An oil painting of a fishing harbor at dusk with small boats, thick impasto brushstrokes, visible canvas texture, warm golden light, rich colors." \
--width 1024 --height 1024 --steps 4 --cfg 1 --seed 903 \
--config-json '{
"sampler": 7,
"loras": []
}'
```

Why: brushstroke and surface words carry the style.
Eval: strokes visible. Fix: add `palette knife, heavy paint`.

## 19. Recipes: photorealism (hyper-detailed)

### J1: Hyper-detailed portrait

```bash
draw-things-cli generate \
--model juggernaut_xl_x_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_photoreal_elder_portrait.png" \
--prompt "hyperrealistic close-up portrait of an elderly man, deep wrinkles, visible pores, individual eyelashes, catchlight in the eyes, soft studio lighting, 8k, sharp focus on the eyes" \
--negative-prompt "cartoon, illustration, painting, drawing, anime, 3d render, cgi, plastic skin, oversmoothed, deformed, extra fingers, bad anatomy, lowres, blurry, watermark, text" \
--width 832 --height 1216 --steps 38 --cfg 4.5 --seed 1001 \
--config-json '{
"sampler": 4,
"loras": [
  {"file": "add-detail-xl.safetensors", "weight": 1.0, "mode": "all"}
]
}'
```

Why: more steps resolve skin detail. Detail Tweaker at 1.0 sits in its recommended starting zone (about 1.5, lower here to avoid over-texture). Low cfg keeps skin natural.
Eval: eyes sharp, pores believable. Fix: crunchy: lower Detail to 0.6 and cfg to 4.

### J2: Macro / object photorealism

```bash
draw-things-cli generate \
--model juggernaut_xl_x_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_photoreal_dewdrop_web.png" \
--prompt "hyperrealistic macro photograph of dewdrops on a spider web at sunrise, extreme close-up, 100mm macro lens, creamy bokeh, tiny reflections inside each drop, crisp detail" \
--negative-prompt "cartoon, illustration, painting, drawing, anime, 3d render, cgi, oversaturated, lowres, blurry, watermark, text" \
--width 1024 --height 1024 --steps 36 --cfg 5 --seed 1002 \
--config-json '{
"sampler": 4,
"loras": [
  {"file": "add-detail-xl.safetensors", "weight": 0.8, "mode": "all"}
]
}'
```

Why: macro scenes benefit from added fine detail. Square crop suits close-ups.
Eval: sharp drops with soft background. Fix: noisy: lower Detail to 0.5.

### J3: Photorealism, Flux Klein

```bash
draw-things-cli generate \
--model flux_2_klein_4b_q6p.ckpt \
--output "$HOME/Dev/tmp/klein_photoreal_watch.png" \
--prompt "A hyperrealistic studio photograph of a mechanical wristwatch on dark slate, sharp focus on the dial, tiny reflections on the glass, softbox lighting, shallow depth of field, 100mm macro lens." \
--width 1024 --height 1024 --steps 4 --cfg 1 --seed 1003 \
--config-json '{
"sampler": 7,
"loras": []
}'
```

Why: product-style camera language drives realism on Klein. Fast option for drafts.
Eval: crisp details, correct reflections. Fix: add `unretouched, natural imperfections`.

## 20. Known uncertainties

- Sampler integers (section 2) and the absence of a `schedule_sampler` key are unverified.
- LoRA effects were taken from model cards or names, not from test renders. The Analog LoRA's behavior is inferred.
- `sketch-style-xl` was trained on Animagine 2.0. Behavior on 3.1 is untested.
- No dedicated mandala, pencil or kid-line-art LoRA was found for SDXL on Hugging Face. Those recipes rely on prompts plus the coloring-book LoRA.
- Klein base (non-distilled) filename and settings are not covered. Distilled Klein only.
- Detail Tweaker XL comes from an unofficial Hugging Face mirror. The original is on Civitai (model 122359).
