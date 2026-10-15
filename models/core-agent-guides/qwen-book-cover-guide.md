# Qwen-Image-2512 Book Cover Settings Guide for draw-things-cli

Target: `qwen_image_2512_bf16_q8p.ckpt` on MacBook Pro M4 (48 GB). Consumer: AI agent / recommendation engine. Companion file: `book-cover-recommendation-rules.json` (same data, machine-readable).

## 1. Confidence legend

- **Verified**: sampler integers; Qwen-Image-2512 community ranges (steps 20-50, CFG ~2.5-4, euler-family samplers).
- **Unverified, check once**: `upscaler` / `upscalerScaleFactor` config keys; exact upscaler filenames; flag-vs-config precedence. Fallback flags: `--upscaler <file> --upscaler-scale <2|4>`.
- **Heuristic**: per-genre sampler, CFG offsets, upscaler pairing. A/B test 3 seeds before trusting.
- Known issue: q8p Qwen 2512 can output NaN/blue/black for some prompts (draw-things-community #136). Change seed/prompt, alt sampler, or lower resolution.

## 2. Sampler reference (numeric value in brackets)

| Sampler | Use for |
|---|---|
| Euler A Trailing [10] | Soft, painterly, organic, storybook, watercolor, oil, pencil (default for soft styles) |
| DPM++ 2M Trailing [15] | Crisp lines, typography, line art, anime, photo, concept art (default for sharp styles) |
| UniPC Trailing [17] | Alt for photo/realism |
| DPM++ 2M Karras [0] | Legacy alt for line art/mandala |
| Euler A [1] | More random variety; less repeatable |

Full enum: DPM++ 2M Karras [0], Euler A [1], DDIM [2], PLMS [3], DPM++ SDE Karras [4], UniPC [5], LCM [6], Euler A Substep [7], DPM++ SDE Substep [8], TCD [9], Euler A Trailing [10], DPM++ SDE Trailing [11], DPM++ 2M AYS [12], Euler A AYS [13], DPM++ SDE AYS [14], DPM++ 2M Trailing [15], DDIM Trailing [16], UniPC Trailing [17], UniPC AYS [18], TCD Trailing [19].

## 3. Upscaler reference (set in `--config-json`)

| File | Scale | Best for |
|---|---|---|
| `realesrgan_x2plus_f16.ckpt` | 2x | General 2x. Safe default for painterly, photo, mixed content. |
| `realesrgan_x4plus_f16.ckpt` | 4x | General 4x. Photos and realism when >2x is needed. |
| `realesrgan_x4plus_anime_6b_f16.ckpt` | 4x | 4x for flat colour, anime, cel shading, clean line art. |
| `4x_ultrasharp_f16.ckpt` | 4x | 4x crisp edges. Best for ink line art, mandalas, graphic type. |
| `remacri_4x_f16.ckpt` | 4x | 4x texture reconstruction. Good for photo/oil/canvas texture. |

Verify filenames: `ls ~/Library/Containers/com.liuliu.draw-things/Data/Documents/Models | grep -i -E 'esrgan|sharp|remacri'`. After 4x, downscale to print size.

## 4. Universal defaults

- Sizes: multiples of 64. Cover 2:3 = 1024x1536 (draft 640x960). Interior 3:4 = 768x1024 or 1024x1344. Mandala 1024x1024.
- Steps 28-40 final, 20 draft. CFG 3.5-5.5 (lower = organic, higher = strict/line art). Qwen uses true CFG, so negative prompts matter.
- Workflow: draft 4 seeds -> pick -> rerun final with that `seed` in config-json -> upscale. Composition may shift across resolutions; re-draft at final size if it matters.
- `tiledDecoding: true` in config-json if any side >1280. Output paths use `"$HOME/..."` because `~` does not expand in single quotes. Run `mkdir -p "$HOME/Dev/tmp"` once.
- Print px at 300 dpi: 6x9in = 1800x2700; 8.5x11in = 2550x3300; 8.5in square = 2550x2550. Image is front cover only; spine/back/bleed in layout software.

## 5. Prompt strategy

1. Natural sentences, not tag soup (Qwen text encoder is an LLM). 60-150 words for covers, 35-90 for line-art pages.
2. Order: medium -> subject/action -> composition (reserve text area) -> palette/lighting/texture -> text clause.
3. Text: exact strings in double quotes, position + typography style for each, max 3 elements (title, series, publisher), title <=6 words, end with `All text spelled exactly as written`.
4. Medium words first and repeated once at the end for painterly styles.
5. Line art: always state `pure white background, no shading, closed shapes, uniform line weight`.
6. No real brands, characters, people, or living-artist styles. Describe original look instead.
7. Avoid `$`, backticks, `!` in prompts (shell-safe). Avoid weight syntax like `(word:1.3)`; unverified for Qwen.

## 6. Negative prompt strategy

1. 10-25 terms in four groups: wrong-medium, quality artefacts, text-failure, audience-safety.
2. Covers: NEVER put `text`, `letters`, `words` alone in the negative. Use `misspelled text, garbled letters, extra words, watermark`.
3. Interior pages: DO include `text, watermark` plus `color, gray, shading, gradient`.
4. Never negate something the positive prompt asks for. Add terms only after seeing a failure.
5. Age tuning: young kids add `scary, dark, realistic, sharp teeth`; teens add `childish, clip art`; adult art adds `cartoon` unless wanted.

## 7. Age modifiers

| Age | Text | Palette | Composition | Negative add |
|---|---|---|---|---|
| 3-5 | <=4 words, huge rounded | primary, high contrast | one subject | scary, dark, realistic, clutter |
| 6-8 | <=6 words, whimsical | warm saturated | 1-2 characters, depth | horror, gore, harsh shadows |
| 9-12 | <=6 words, bold sans | vivid | dynamic, informative | gore, dense paragraphs |
| 13-17 | short, condensed caps | stylised/neon or restrained | poster-like space | childish, clip art |
| adult | refined serif/thin sans | premium restrained | symmetry, space | childish |

## 8. Profiles (settings + executable example)

Each example is the **final** tier. Draft = same prompt, width/height from table, `--steps 20`, no upscaler.

### `kids_picture_book_3_5`: Picture / early-reading book, ages 3-5

- **Mode**: cover | **Ages**: 3-5 | **Confidence**: 0.68
- **Final**: 1024x1536, steps 32, CFG 4.0, sampler Euler A Trailing [10], upscaler `realesrgan_x2plus_f16.ckpt` x2 -> 2048x3072
- **Draft**: 640x960, steps 20 | **Alt sampler**: DPM++ 2M Trailing [15] | **Alt upscaler**: `realesrgan_x4plus_anime_6b_f16.ckpt`
- **Why**: Euler A Trailing gives soft, forgiving shapes. CFG 4 keeps the exact text and single-subject layout. 2x general upscaler avoids over-sharpening flat colour.
- **Tune**: Letters wrong: shorten title to <=4 words, steps 40, CFG 3.5. Too busy: add 'minimal background, one subject' to prompt.

```bash
draw-things-cli generate \
--model qwen_image_2512_bf16_q8p.ckpt \
--output "$HOME/Dev/tmp/qwen_kids_picture_book_3_5.png" \
--prompt "Children's picture book cover for ages 3 to 5, flat gouache illustration with thick soft outlines. A smiling round baby fox in a red scarf waves from a green hill under a big yellow sun, with a few simple clouds and three flowers. Warm primary colors, one big central character, plenty of empty sky at the top. Title \"Finn the Brave Little Fox\" in large bold rounded hand-lettered capitals in the sky; series name \"Little Woodland Tales\" in small rounded letters at the very top; publisher name \"Maple Lane Press\" in small letters at the bottom center. All text spelled exactly as written, sharp and legible." \
--negative-prompt "scary, dark, realistic, photograph, sharp teeth, clutter, tiny details, misspelled text, garbled letters, extra words, watermark, blurry, deformed hands" \
--width 1024 --height 1536 --steps 32 --cfg 4.0 \
--config-json '{
"sampler": 10,
"upscaler": "realesrgan_x2plus_f16.ckpt",
"upscalerScaleFactor": 2
}'
```

### `kids_storybook_6_8`: Illustrated storybook, ages 6-8

- **Mode**: cover | **Ages**: 6-8 | **Confidence**: 0.68
- **Final**: 1024x1536, steps 34, CFG 4.0, sampler Euler A Trailing [10], upscaler `realesrgan_x2plus_f16.ckpt` x2 -> 2048x3072
- **Draft**: 640x960, steps 20 | **Alt sampler**: DPM++ 2M Trailing [15] | **Alt upscaler**: `remacri_4x_f16.ckpt`
- **Why**: Richer scene than 3-5 so steps 34. Euler A Trailing keeps painterly softness. CFG 4 balances scene detail and title accuracy.
- **Tune**: Characters distorted: steps 40 and reduce to 2 characters. Flat look: add lighting words (rim light, glow).

```bash
draw-things-cli generate \
--model qwen_image_2512_bf16_q8p.ckpt \
--output "$HOME/Dev/tmp/qwen_kids_storybook_6_8.png" \
--prompt "Storybook cover for ages 6 to 8, painterly digital illustration in a soft watercolor-gouache style. Two children and a small owl carrying a lantern walk down a mossy path into a glowing moonlit forest with fireflies and tiny lit cottage windows. Warm golden light against deep teal shadows, layered trees for depth, room for the title in the upper third. Title \"The Lantern Owl of Hollow Wood\" in whimsical serif lettering across the upper third; series name \"Hollow Wood Tales, Book 2\" in small clean letters above the title; publisher name \"Maple Lane Press\" in small letters at the bottom center. All text spelled exactly as written, sharp and legible." \
--negative-prompt "horror, gore, photorealistic, harsh shadows, muddy colors, crowded composition, misspelled text, garbled letters, extra words, watermark, deformed hands, extra fingers" \
--width 1024 --height 1536 --steps 34 --cfg 4.0 \
--config-json '{
"sampler": 10,
"upscaler": "realesrgan_x2plus_f16.ckpt",
"upscalerScaleFactor": 2
}'
```

### `kids_nonfiction_8_12`: Informative non-fiction for kids, ages 8-12

- **Mode**: cover | **Ages**: 8-12 | **Confidence**: 0.65
- **Final**: 1024x1536, steps 36, CFG 4.0, sampler DPM++ 2M Trailing [15], upscaler `realesrgan_x2plus_f16.ckpt` x2 -> 2048x3072
- **Draft**: 640x960, steps 20 | **Alt sampler**: Euler A Trailing [10] | **Alt upscaler**: `4x_ultrasharp_f16.ckpt`
- **Why**: DPM++ 2M Trailing converges cleanly for crisp outlines and sharp lettering. Steps 36 for diagram-like detail. CFG 4 for accuracy.
- **Tune**: Soft outlines: alt sampler Euler A Trailing is NOT better here; raise steps to 42 instead. Lettering weak: use 4x_ultrasharp upscaler.

```bash
draw-things-cli generate \
--model qwen_image_2512_bf16_q8p.ckpt \
--output "$HOME/Dev/tmp/qwen_kids_nonfiction_8_12.png" \
--prompt "Informative non-fiction book cover for ages 8 to 12 about volcanoes. Clean educational illustration of a cutaway volcano showing the magma chamber, rock layers, lava and an ash cloud, with a small curious explorer kid in a helmet pointing at it. Bright saturated flat colors, crisp outlines, bold orange and blue palette, uncluttered composition. Title \"Volcanoes Up Close\" in chunky sans-serif capitals at the top; series name \"Discover Science Series\" in a small colored band above the title; publisher name \"Maple Lane Press\" in small letters at the bottom center. All text spelled exactly as written, sharp and legible." \
--negative-prompt "photograph, gore, scary, dense paragraphs, tiny captions, misspelled text, garbled letters, extra words, watermark, blurry, muddy colors, low contrast" \
--width 1024 --height 1536 --steps 36 --cfg 4.0 \
--config-json '{
"sampler": 15,
"upscaler": "realesrgan_x2plus_f16.ckpt",
"upscalerScaleFactor": 2
}'
```

### `teen_nonfiction_13_17`: Teen non-fiction / informative, ages 13-17

- **Mode**: cover | **Ages**: 13-17 | **Confidence**: 0.65
- **Final**: 1024x1536, steps 36, CFG 4.0, sampler DPM++ 2M Trailing [15], upscaler `4x_ultrasharp_f16.ckpt` x4 -> 4096x6144
- **Draft**: 640x960, steps 20 | **Alt sampler**: UniPC Trailing [17] | **Alt upscaler**: `realesrgan_x2plus_f16.ckpt`
- **Why**: Graphic poster style benefits from DPM++ 2M Trailing precision. 4x ultrasharp keeps typography edges crisp (downscale after).
- **Tune**: Output too large: downscale to print size. Too childish: add 'sophisticated, restrained palette'.

```bash
draw-things-cli generate \
--model qwen_image_2512_bf16_q8p.ckpt \
--output "$HOME/Dev/tmp/qwen_teen_nonfiction_13_17.png" \
--prompt "Modern teen non-fiction book cover about the psychology of sleep and the teenage brain. Bold graphic design with a stylized glowing brain made of layered paper-cut shapes over a deep indigo and electric coral gradient, a crescent moon, minimal clean composition with generous negative space, contemporary editorial poster look. Title \"WIDE AWAKE\" in huge condensed sans-serif capitals across the middle; series name \"The Mind Lab Series\" in small spaced capitals above the title; publisher name \"North Harbor Books\" in small capitals at the bottom center. All text spelled exactly as written, sharp and legible." \
--negative-prompt "childish, cartoon mascot, clip art, stock photo look, cluttered, rainbow colors, misspelled text, garbled letters, extra words, watermark, low contrast, blurry" \
--width 1024 --height 1536 --steps 36 --cfg 4.0 \
--config-json '{
"sampler": 15,
"upscaler": "4x_ultrasharp_f16.ckpt",
"upscalerScaleFactor": 4
}'
```

### `kids_coloring_cover`: Kids coloring book cover (colour cover)

- **Mode**: cover | **Ages**: 3-5, 6-8, 9-12 | **Confidence**: 0.67
- **Final**: 1024x1536, steps 32, CFG 4.0, sampler Euler A Trailing [10], upscaler `realesrgan_x2plus_f16.ckpt` x2 -> 2048x3072
- **Draft**: 640x960, steps 20 | **Alt sampler**: DPM++ 2M Trailing [15] | **Alt upscaler**: `realesrgan_x4plus_anime_6b_f16.ckpt`
- **Why**: Colour cover with line-art teasers. Same recipe as picture-book covers; short 2-word title is the most reliable text case.
- **Tune**: Teaser outlines coloured in: add 'pure white uncolored outlines' and lower CFG slightly is NOT needed; raise CFG to 4.5.

```bash
draw-things-cli generate \
--model qwen_image_2512_bf16_q8p.ckpt \
--output "$HOME/Dev/tmp/qwen_kids_coloring_cover.png" \
--prompt "Cover of a children's coloring book. A cheerful friendly dinosaur holding a giant crayon, bold black outlines with bright flat colors on a pale yellow background, with three uncolored black-and-white line-art dinosaur outlines floating around to hint at the pages inside. Playful, simple, high contrast. Title \"Dino Colors\" in big bubbly multicolor capitals at the top; series name \"Crayon Club\" in small letters above the title; publisher name \"Maple Lane Press\" in small letters at the bottom center. All text spelled exactly as written, sharp and legible." \
--negative-prompt "scary teeth, realistic, photograph, gradient shading, dark background, clutter, misspelled text, garbled letters, extra words, watermark, blurry" \
--width 1024 --height 1536 --steps 32 --cfg 4.0 \
--config-json '{
"sampler": 10,
"upscaler": "realesrgan_x2plus_f16.ckpt",
"upscalerScaleFactor": 2
}'
```

### `adult_coloring_cover`: Adult coloring book cover (colour cover)

- **Mode**: cover | **Ages**: adult | **Confidence**: 0.64
- **Final**: 1024x1536, steps 36, CFG 4.5, sampler DPM++ 2M Trailing [15], upscaler `4x_ultrasharp_f16.ckpt` x4 -> 4096x6144
- **Draft**: 640x960, steps 20 | **Alt sampler**: Euler A Trailing [10] | **Alt upscaler**: `realesrgan_x2plus_f16.ckpt`
- **Why**: Fine ornament needs precise convergence (DPM++ 2M Trailing) and 36 steps. CFG 4.5 enforces symmetry and inset. Ultrasharp keeps gold linework crisp.
- **Tune**: Inset missing: describe it earlier in the prompt. Output 4x large: downscale after.

```bash
draw-things-cli generate \
--model qwen_image_2512_bf16_q8p.ckpt \
--output "$HOME/Dev/tmp/qwen_adult_coloring_cover.png" \
--prompt "Elegant cover for an adult coloring book. A rich, fully colored, highly detailed owl-and-moon mandala centered on a deep navy background with gold accents, plus a small framed inset of the same design as black outline line art on cream paper. Refined symmetrical layout, premium feel. Title \"Midnight Mandalas\" in elegant gold serif capitals at the top; series name \"Calm Hours Coloring Series\" in small gold capitals under the title; publisher name \"Juniper & Ash Press\" in small gold letters at the bottom center. All text spelled exactly as written, sharp and legible." \
--negative-prompt "childish, cartoon, messy lines, muddy colors, flat clip art, cluttered, misspelled text, garbled letters, extra words, watermark, blurry" \
--width 1024 --height 1536 --steps 36 --cfg 4.5 \
--config-json '{
"sampler": 15,
"upscaler": "4x_ultrasharp_f16.ckpt",
"upscalerScaleFactor": 4
}'
```

### `kids_coloring_page_3_6`: Kids coloring page (interior), ages 3-6

- **Mode**: interior | **Ages**: 3-5, 6-8 | **Confidence**: 0.71
- **Final**: 768x1024, steps 28, CFG 5.0, sampler DPM++ 2M Trailing [15], upscaler `realesrgan_x4plus_anime_6b_f16.ckpt` x4 -> 3072x4096
- **Draft**: 576x768, steps 20 | **Alt sampler**: Euler A Trailing [10] | **Alt upscaler**: `4x_ultrasharp_f16.ckpt`
- **Why**: Higher CFG 5 enforces pure white background and no fill. 28 steps is enough for few shapes. Anime 6B 4x keeps thick lines clean. Base 768x1024 x4 = 3072x4096 (>8.5x11 at 300dpi).
- **Tune**: Gray fills appear: CFG 5.5 and add 'solid black lines only' to prompt. Lines too thin: add 'extra thick bold outline'.

```bash
draw-things-cli generate \
--model qwen_image_2512_bf16_q8p.ckpt \
--output "$HOME/Dev/tmp/qwen_kids_coloring_page_3_6.png" \
--prompt "Children's coloring book page for ages 3 to 6. A single big happy elephant holding a balloon, very thick clean black outlines, simple large shapes, pure white background, no shading, no fill, centered with wide white margins, easy to color." \
--negative-prompt "color, gray, shading, gradient, shadows, texture, tiny details, background scenery, text, watermark, sketchy lines, broken lines" \
--width 768 --height 1024 --steps 28 --cfg 5.0 \
--config-json '{
"sampler": 15,
"upscaler": "realesrgan_x4plus_anime_6b_f16.ckpt",
"upscalerScaleFactor": 4
}'
```

### `kids_coloring_page_7_12`: Kids coloring page (interior), ages 7-12

- **Mode**: interior | **Ages**: 9-12, 6-8 | **Confidence**: 0.71
- **Final**: 768x1024, steps 32, CFG 5.0, sampler DPM++ 2M Trailing [15], upscaler `realesrgan_x4plus_anime_6b_f16.ckpt` x4 -> 3072x4096
- **Draft**: 576x768, steps 20 | **Alt sampler**: Euler A Trailing [10] | **Alt upscaler**: `4x_ultrasharp_f16.ckpt`
- **Why**: Same recipe as 3-6 with more steps for medium detail. Closed shapes cue prevents open regions that are hard to colour.
- **Tune**: Too complex: say 'fewer, larger shapes'. Open shapes: add 'every shape fully closed'.

```bash
draw-things-cli generate \
--model qwen_image_2512_bf16_q8p.ckpt \
--output "$HOME/Dev/tmp/qwen_kids_coloring_page_7_12.png" \
--prompt "Coloring book page for ages 7 to 12. A friendly dragon curled around a castle tower with scales, clouds and stars, medium-detail clean black line art, uniform line weight, pure white background, closed shapes ready to color, no shading." \
--negative-prompt "color, gray fill, shading, gradients, shadows, sketchy, messy overlapping lines, text, watermark, blurry, cropped" \
--width 768 --height 1024 --steps 32 --cfg 5.0 \
--config-json '{
"sampler": 15,
"upscaler": "realesrgan_x4plus_anime_6b_f16.ckpt",
"upscalerScaleFactor": 4
}'
```

### `adult_coloring_line_art`: Adult coloring page (interior), intricate line art

- **Mode**: interior | **Ages**: adult, 13-17 | **Confidence**: 0.69
- **Final**: 1024x1344, steps 36, CFG 5.5, sampler DPM++ 2M Trailing [15], upscaler `4x_ultrasharp_f16.ckpt` x4 -> 4096x5376
- **Draft**: 640x832, steps 20 | **Alt sampler**: DPM++ 2M Karras [0] | **Alt upscaler**: `realesrgan_x4plus_anime_6b_f16.ckpt`
- **Why**: 1024 base keeps fine lines separate. CFG 5.5 pushes strict black-on-white. Ultrasharp 4x preserves hairlines; downscale 4096x5376 to 2550x3300.
- **Tune**: Lines merge: raise base to 1152x1536 (needs ~tiledDecoding true). Gray tone: CFG 6 and add 'high contrast pure black ink'.

```bash
draw-things-cli generate \
--model qwen_image_2512_bf16_q8p.ckpt \
--output "$HOME/Dev/tmp/qwen_adult_coloring_line_art.png" \
--prompt "Intricate adult coloring page. A mystical owl perched on a crescent moon surrounded by floral mandala patterns, feathers drawn with fine repeating patterns, fine uniform black ink lines, pure white background, no shading, symmetrical balanced composition, closed shapes, high detail." \
--negative-prompt "3d render, color, grayscale shading, gray shadows, sketch, charcoal, messy lines, blurry, text, watermark, bg color, cropped" \
--width 1024 --height 1344 --steps 36 --cfg 5.5 \
--config-json '{
"sampler": 15,
"upscaler": "4x_ultrasharp_f16.ckpt",
"upscalerScaleFactor": 4
}'
```

### `adult_mandala`: Adult mandala coloring page (interior)

- **Mode**: interior | **Ages**: adult | **Confidence**: 0.69
- **Final**: 1024x1024, steps 36, CFG 5.5, sampler DPM++ 2M Trailing [15], upscaler `4x_ultrasharp_f16.ckpt` x4 -> 4096x4096
- **Draft**: 640x640, steps 20 | **Alt sampler**: DPM++ 2M Karras [0] | **Alt upscaler**: `realesrgan_x4plus_anime_6b_f16.ckpt`
- **Why**: Square canvas suits radial symmetry. DPM++ 2M Trailing yields stable repeating geometry. 4096x4096 output exceeds 8.5in square at 300dpi; downscale.
- **Tune**: Asymmetry: CFG 6 and add 'exact radial symmetry, 12-fold'. Fill artefacts: DPM++ 2M Karras [0] as alt sampler.

```bash
draw-things-cli generate \
--model qwen_image_2512_bf16_q8p.ckpt \
--output "$HOME/Dev/tmp/qwen_adult_mandala.png" \
--prompt "Circular mandala coloring page, perfectly symmetrical radial design with layered petals, paisley, geometric lotus rings and fine dot borders, fine black linework, pure white background, centered with white margin all around, no shading." \
--negative-prompt "color, shading, gradient, asymmetry, off-center, messy lines, blurry, text, watermark, background texture, cropped" \
--width 1024 --height 1024 --steps 36 --cfg 5.5 \
--config-json '{
"sampler": 15,
"upscaler": "4x_ultrasharp_f16.ckpt",
"upscalerScaleFactor": 4
}'
```

### `pencil_sketch`: Pencil / graphite artistic sketch book

- **Mode**: cover | **Ages**: adult, 13-17 | **Confidence**: 0.64
- **Final**: 1024x1536, steps 36, CFG 4.0, sampler Euler A Trailing [10], upscaler `realesrgan_x2plus_f16.ckpt` x2 -> 2048x3072
- **Draft**: 640x960, steps 20 | **Alt sampler**: DPM++ 2M Trailing [15] | **Alt upscaler**: `remacri_4x_f16.ckpt`
- **Why**: Euler A Trailing preserves organic grain and loose strokes. CFG 4 keeps tone monochrome. 2x general upscaler keeps grain rather than smoothing.
- **Tune**: Too clean/digital: lower CFG 3.5, add 'rough, imperfect, hand-drawn'. Colour leaks: add 'monochrome only' and CFG 4.5.

```bash
draw-things-cli generate \
--model qwen_image_2512_bf16_q8p.ckpt \
--output "$HOME/Dev/tmp/qwen_pencil_sketch.png" \
--prompt "Book cover in the style of a graphite pencil sketch on cream paper. An old fisherman mending nets on a harbor pier at dawn, expressive cross-hatching, soft smudged shading, visible paper grain, loose construction lines, monochrome graphite tones. Title \"The Harbor Sketchbook\" in hand-lettered pencil capitals at the top; series name \"Studio Notes Series\" in small pencil letters under the title; publisher name \"Maple Lane Press\" in small pencil letters at the bottom center. All text spelled exactly as written, sharp and legible." \
--negative-prompt "color, saturated, digital gloss, 3d render, cartoon, vector, photograph, clean outlines, misspelled text, garbled letters, extra words, watermark" \
--width 1024 --height 1536 --steps 36 --cfg 4.0 \
--config-json '{
"sampler": 10,
"upscaler": "realesrgan_x2plus_f16.ckpt",
"upscalerScaleFactor": 2
}'
```

### `watercolor`: Watercolor painting book

- **Mode**: cover | **Ages**: adult, 13-17, 6-8, 9-12 | **Confidence**: 0.64
- **Final**: 1024x1536, steps 34, CFG 3.5, sampler Euler A Trailing [10], upscaler `realesrgan_x2plus_f16.ckpt` x2 -> 2048x3072
- **Draft**: 640x960, steps 20 | **Alt sampler**: DPM++ 2M Trailing [15] | **Alt upscaler**: `remacri_4x_f16.ckpt`
- **Why**: Lower CFG 3.5 allows soft bleeding and pigment variation; higher CFG makes it look digital. Euler A Trailing keeps loose edges.
- **Tune**: Text too rigid or garbled: CFG 3.8, steps 40. Too sharp: skip upscaler or use x2plus only.

```bash
draw-things-cli generate \
--model qwen_image_2512_bf16_q8p.ckpt \
--output "$HOME/Dev/tmp/qwen_watercolor.png" \
--prompt "Watercolor painting book cover. A misty lavender field with a lone cottage at sunrise, wet-on-wet washes, soft bleeding edges, pigment blooms, visible cold-press paper texture, white paper left unpainted near the edges, soft peach and lavender palette. Title \"Lavender Mornings\" in delicate hand-painted serif letters in the sky; series name \"The Wash Series\" in small painted letters above the title; publisher name \"Maple Lane Press\" in small painted letters at the bottom center. All text spelled exactly as written, sharp and legible." \
--negative-prompt "vector, hard outlines, digital gradient, oversharpened, plastic, photograph, airbrushed, muddy colors, misspelled text, garbled letters, extra words, watermark" \
--width 1024 --height 1536 --steps 34 --cfg 3.5 \
--config-json '{
"sampler": 10,
"upscaler": "realesrgan_x2plus_f16.ckpt",
"upscalerScaleFactor": 2
}'
```

### `oil_painting`: Oil painting book

- **Mode**: cover | **Ages**: adult | **Confidence**: 0.64
- **Final**: 1024x1536, steps 36, CFG 3.5, sampler Euler A Trailing [10], upscaler `remacri_4x_f16.ckpt` x4 -> 4096x6144
- **Draft**: 640x960, steps 20 | **Alt sampler**: DPM++ 2M Trailing [15] | **Alt upscaler**: `realesrgan_x2plus_f16.ckpt`
- **Why**: CFG 3.5 keeps brushwork natural. Remacri 4x reconstructs canvas/paint texture; downscale 4096x6144 to target.
- **Tune**: Smooth/plastic: add 'visible brushstrokes, thick paint'. Large file: swap to realesrgan_x2plus.

```bash
draw-things-cli generate \
--model qwen_image_2512_bf16_q8p.ckpt \
--output "$HOME/Dev/tmp/qwen_oil_painting.png" \
--prompt "Oil painting book cover. A stormy sea with a lone sailing ship at golden hour, thick impasto brushstrokes, palette-knife highlights, rich warm ochre and deep prussian blue, visible canvas weave, dramatic chiaroscuro, classical composition with calm sky area at the top. Title \"Storm Light\" in engraved gold serif capitals in the sky area; series name \"Masters of the Sea\" in small gold capitals above the title; publisher name \"Juniper & Ash Press\" in small gold capitals at the bottom center. All text spelled exactly as written, sharp and legible." \
--negative-prompt "flat vector, airbrushed, plastic, cgi, photograph, digital noise, oversaturated, cartoon, misspelled text, garbled letters, extra words, watermark" \
--width 1024 --height 1536 --steps 36 --cfg 3.5 \
--config-json '{
"sampler": 10,
"upscaler": "remacri_4x_f16.ckpt",
"upscalerScaleFactor": 4
}'
```

### `anime_2d`: 2D anime illustration book / light novel

- **Mode**: cover | **Ages**: 13-17, adult | **Confidence**: 0.66
- **Final**: 832x1216, steps 32, CFG 4.0, sampler DPM++ 2M Trailing [15], upscaler `realesrgan_x4plus_anime_6b_f16.ckpt` x4 -> 3328x4864
- **Draft**: 576x832, steps 20 | **Alt sampler**: Euler A Trailing [10] | **Alt upscaler**: `4x_ultrasharp_f16.ckpt`
- **Why**: Anime 6B 4x suits cel shading and line clarity. 832x1216 base x4 = 3328x4864. DPM++ 2M Trailing for clean lines.
- **Tune**: Hands wrong: hide hands (behind back, holding object) in prompt. Too soft: alt upscaler 4x_ultrasharp.

```bash
draw-things-cli generate \
--model qwen_image_2512_bf16_q8p.ckpt \
--output "$HOME/Dev/tmp/qwen_anime_2d.png" \
--prompt "2D anime key visual style book cover for a teen light novel. A girl with short silver hair and a school uniform holds a glowing paper lantern on a rooftop at twilight, sakura petals drifting, vivid cel shading, clean linework, detailed twilight sky gradient, dynamic low angle. Title \"The Lantern Girl\" in large stylized brush-script capitals at the top; series name \"Sakura Nights, Vol. 1\" in small clean letters above the title; publisher name \"Kitsune Press\" in small capitals at the bottom center. All text spelled exactly as written, sharp and legible." \
--negative-prompt "3d render, photorealistic, western comic style, bad anatomy, extra fingers, deformed hands, blurry, jpeg artifacts, misspelled text, garbled letters, extra words, watermark" \
--width 832 --height 1216 --steps 32 --cfg 4.0 \
--config-json '{
"sampler": 15,
"upscaler": "realesrgan_x4plus_anime_6b_f16.ckpt",
"upscalerScaleFactor": 4
}'
```

### `anime_3d`: 3D stylized / animated-film look illustration

- **Mode**: cover | **Ages**: 6-8, 9-12, 13-17 | **Confidence**: 0.65
- **Final**: 1024x1536, steps 34, CFG 4.0, sampler DPM++ 2M Trailing [15], upscaler `realesrgan_x2plus_f16.ckpt` x2 -> 2048x3072
- **Draft**: 640x960, steps 20 | **Alt sampler**: Euler A Trailing [10] | **Alt upscaler**: `realesrgan_x4plus_f16.ckpt`
- **Why**: General 2x upscaler preserves smooth shaded surfaces. Do not name studios or characters (IP). CFG 4 balances look and text.
- **Tune**: Too realistic: add 'toy-like, exaggerated proportions'. Flat look: add 'soft volumetric light'.

```bash
draw-things-cli generate \
--model qwen_image_2512_bf16_q8p.ckpt \
--output "$HOME/Dev/tmp/qwen_anime_3d.png" \
--prompt "Stylized 3D animated feature-film look book cover. A cheerful young inventor girl with a goggle headband and a small round robot companion in a cozy workshop, soft global illumination, gentle subsurface scattering, rounded appealing character design, shallow depth of field, warm teal and orange palette. Title \"Zoe and the Gizmo\" in chunky 3D beveled letters at the top; series name \"Workshop Friends\" in small rounded letters above the title; publisher name \"Maple Lane Press\" in small letters at the bottom center. All text spelled exactly as written, sharp and legible." \
--negative-prompt "photorealistic skin pores, uncanny valley, flat 2d, line art, harsh noise, bad anatomy, extra fingers, misspelled text, garbled letters, extra words, watermark" \
--width 1024 --height 1536 --steps 34 --cfg 4.0 \
--config-json '{
"sampler": 15,
"upscaler": "realesrgan_x2plus_f16.ckpt",
"upscalerScaleFactor": 2
}'
```

### `digital_painting`: Digital painting / concept art (fantasy, sci-fi, YA)

- **Mode**: cover | **Ages**: 13-17, adult | **Confidence**: 0.65
- **Final**: 1024x1536, steps 36, CFG 4.0, sampler DPM++ 2M Trailing [15], upscaler `realesrgan_x2plus_f16.ckpt` x2 -> 2048x3072
- **Draft**: 640x960, steps 20 | **Alt sampler**: Euler A Trailing [10] | **Alt upscaler**: `4x_ultrasharp_f16.ckpt`
- **Why**: DPM++ 2M Trailing gives detailed, stable painterly output. Single-word title is the most reliable for stylised lettering.
- **Tune**: Title lost in art: reserve 'dark calm sky area' behind text. More texture: alt upscaler 4x_ultrasharp (downscale).

```bash
draw-things-cli generate \
--model qwen_image_2512_bf16_q8p.ckpt \
--output "$HOME/Dev/tmp/qwen_digital_painting.png" \
--prompt "Epic digital painting fantasy book cover. A lone armored traveler stands on a cliff overlooking a floating-island kingdom at dawn, volumetric light rays, painterly brushwork, dramatic scale, rich color grading, cinematic composition with clear space at the top for the title. Title \"EMBERFALL\" in large metallic engraved capitals at the top; series name \"The Shattered Crown, Book 1\" in small capitals under the title; publisher name \"Raven Gate Publishing\" in small capitals at the bottom center. All text spelled exactly as written, sharp and legible." \
--negative-prompt "photograph, flat vector, cartoon, low detail, muddy, oversaturated, extra limbs, deformed hands, misspelled text, garbled letters, extra words, watermark" \
--width 1024 --height 1536 --steps 36 --cfg 4.0 \
--config-json '{
"sampler": 15,
"upscaler": "realesrgan_x2plus_f16.ckpt",
"upscalerScaleFactor": 2
}'
```

### `photography`: Photography book / documentary / travel / nature

- **Mode**: cover | **Ages**: adult, 13-17 | **Confidence**: 0.65
- **Final**: 1024x1536, steps 36, CFG 3.5, sampler DPM++ 2M Trailing [15], upscaler `realesrgan_x2plus_f16.ckpt` x2 -> 2048x3072
- **Draft**: 640x960, steps 20 | **Alt sampler**: UniPC Trailing [17] | **Alt upscaler**: `remacri_4x_f16.ckpt`
- **Why**: CFG 3.5 avoids over-contrasty HDR look. Camera/lens words anchor photo realism. Light, thin lettering fits photo covers.
- **Tune**: Too CGI: add film stock, 'natural imperfections'. Soft: remacri upscaler.

```bash
draw-things-cli generate \
--model qwen_image_2512_bf16_q8p.ckpt \
--output "$HOME/Dev/tmp/qwen_photography.png" \
--prompt "Photographic book cover. A misty alpine lake at sunrise, shot on a full-frame camera with a 35mm lens, natural light, soft fog, true-to-life color, fine film grain, calm sky area at the top for the title. Title \"Silent Peaks\" in thin elegant white sans-serif capitals in the sky; series name \"Wild Places Series\" in small white capitals above the title; publisher name \"Juniper & Ash Press\" in small white capitals at the bottom center. All text spelled exactly as written, sharp and legible." \
--negative-prompt "illustration, painting, cgi, oversaturated hdr, plastic, heavy vignette, oversharpened, lens flare, misspelled text, garbled letters, extra words, watermark" \
--width 1024 --height 1536 --steps 36 --cfg 3.5 \
--config-json '{
"sampler": 15,
"upscaler": "realesrgan_x2plus_f16.ckpt",
"upscalerScaleFactor": 2
}'
```

### `photorealism`: Photorealism / hyperreal portraits and still life

- **Mode**: cover | **Ages**: adult | **Confidence**: 0.62
- **Final**: 1024x1536, steps 40, CFG 3.5, sampler DPM++ 2M Trailing [15], upscaler `realesrgan_x4plus_f16.ckpt` x4 -> 4096x6144
- **Draft**: 640x960, steps 20 | **Alt sampler**: UniPC Trailing [17] | **Alt upscaler**: `remacri_4x_f16.ckpt`
- **Why**: Steps 40 and CFG 3.5 favour natural skin and fine texture. Use only fictional people (no real named persons).
- **Tune**: Waxy skin: CFG 3.0, add 'pores, natural imperfections'. 4x file large: downscale or use x2plus.

```bash
draw-things-cli generate \
--model qwen_image_2512_bf16_q8p.ckpt \
--output "$HOME/Dev/tmp/qwen_photorealism.png" \
--prompt "Hyperrealistic photoreal cover photograph. A weathered elderly potter with clay-dusted hands at a wheel, natural window light, visible skin texture and fine hair, 85mm portrait lens, shallow depth of field, muted earthy tones, clear dark wall area at the top for the title. Title \"Hands of Clay\" in refined cream serif capitals at the top; series name \"Lives Well Lived\" in small cream capitals above the title; publisher name \"North Harbor Books\" in small cream capitals at the bottom center. All text spelled exactly as written, sharp and legible." \
--negative-prompt "plastic skin, airbrushed, cartoon, illustration, uncanny, extra fingers, deformed hands, oversmoothed, beauty filter, misspelled text, garbled letters, extra words, watermark" \
--width 1024 --height 1536 --steps 40 --cfg 3.5 \
--config-json '{
"sampler": 15,
"upscaler": "realesrgan_x4plus_f16.ckpt",
"upscalerScaleFactor": 4
}'
```

### `editorial_illustration`: Illustration book / editorial / risograph style

- **Mode**: cover | **Ages**: adult, 13-17, 9-12 | **Confidence**: 0.67
- **Final**: 1024x1536, steps 34, CFG 4.0, sampler Euler A Trailing [10], upscaler `realesrgan_x2plus_f16.ckpt` x2 -> 2048x3072
- **Draft**: 640x960, steps 20 | **Alt sampler**: DPM++ 2M Trailing [15] | **Alt upscaler**: `realesrgan_x4plus_anime_6b_f16.ckpt`
- **Why**: Named limited palette controls colour; Euler A Trailing keeps hand-made feel. CFG 4 holds palette and text.
- **Tune**: Too many colours: repeat palette in prompt end. Too clean: add 'misregistered print, grain'.

```bash
draw-things-cli generate \
--model qwen_image_2512_bf16_q8p.ckpt \
--output "$HOME/Dev/tmp/qwen_editorial_illustration.png" \
--prompt "Editorial book illustration cover in ink and gouache with a limited four-color risograph palette of teal, coral, mustard and cream. A surreal giant paper boat carries a tiny city across the night sky, bold simple shapes, subtle paper grain, flat color layers with slight misregistration. Title \"Paper Skies\" in bold hand-cut sans-serif capitals at the top; series name \"The Atlas of Dreams\" in small capitals above the title; publisher name \"Juniper & Ash Press\" in small capitals at the bottom center. All text spelled exactly as written, sharp and legible." \
--negative-prompt "photorealistic, 3d render, glossy gradient, cluttered, generic stock art, extra colors, misspelled text, garbled letters, extra words, watermark, blurry" \
--width 1024 --height 1536 --steps 34 --cfg 4.0 \
--config-json '{
"sampler": 10,
"upscaler": "realesrgan_x2plus_f16.ckpt",
"upscalerScaleFactor": 2
}'
```

## 9. Troubleshooting

| Symptom | Actions (in order) |
|---|---|
| garbled/misspelled text | shorten strings; cfg -0.5; steps +6; move text to simple area; new seed |
| blurry/soft | steps +6; switch sampler 10->15; alt upscaler 4x_ultrasharp; raise base resolution |
| gray fills in line art | cfg +0.5; add 'solid pure black ink lines only'; add color/shading/gray to negative |
| over-smooth plastic look | cfg -0.5; add texture words; remacri or x2plus upscaler |
| blue/black/noise image | new seed; reword prompt; alt sampler; lower resolution; ref draw-things-community #136 |
| wrong colour/medium | put medium first in prompt; strengthen negative for wrong medium; cfg +0.5 |

## 10. Agent decision procedure (short)

Resolve mode (cover vs interior) -> style/medium -> genre -> age -> pick profile (see JSON `selection_rules`) -> apply age modifiers -> choose tier (draft/final/lowmem) -> emit command -> validate (OCR for covers, whiteness check for line art) -> retry up to 3 times using the failure playbook.
