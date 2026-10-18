# Qwen-Image 2.1 x Draw Things CLI: Book-Cover Playbook (agent-consumable)

Doc date: 2026-10-19 | Model file: `qwen_image_2.1_q8p.ckpt` | Host: MacBook Pro M4, 12-core, 48 GB | Tool: `draw-things-cli`
Purpose: let a recommendation agent pick model, size, steps, cfg, sampler, upscaler, LoRA and prompt for book covers (with embedded title / series / publisher text) and edits.

**Evidence tags used throughout**
- `[V]` verified in published sources (list at the end).
- `[R]` reasoned starting default, not benchmarked. A/B test with a fixed seed before trusting.
- `[P]` probe the local CLI first (command given in section 3.3). Behaviour could not be confirmed from docs.

---

## 0. Hard gates (evaluate BEFORE recommending anything)

| Gate | Rule |
|---|---|
| G1 License `[V]` | Qwen-Image-2.1 ships under the **Qwen Research License: non-commercial (research/evaluation) only**; commercial use needs a separate license from Qwen. Earlier Qwen-Image 1.0 / Edit / Layered / 2512 were Apache 2.0 (per published reports; confirm on the model card). Whether the licence covers *generated images* is not spelled out in its text: treat as unresolved. |
| G1 action | Assume `commercial=true` unless the user says otherwise (selling, KDP, client work, monetised channel). If true: warn once, then offer (a) get a written commercial licence from Qwen, (b) use `qwen_image_2512_*` for T2I and `qwen_image_edit_2511_*` for edits (Apache-2.0 lineage, loses 2.1-only features: native RGBA, 10 refs, annotation edits), (c) use 2.1 for non-commercial drafts/mood-boards only. LoRAs/derivatives of 2.1 inherit the research licence `[V]`. |
| G2 Text | Never trust embedded text without verification (section 10.2). Publisher/series text under ~3% of image height is unreliable: composite it in post with a properly licensed font. |
| G3 Print | Final deliverable must be sRGB, target pixel size (section 4.3), no stray alpha channel unless intentional. |

---

## 1. Corrections to common assumptions

| Claim | Fact |
|---|---|
| "10-16 reference images" | **Up to 10** `[V]` (every official source says 10). |
| "7B model" | 7B is the *visual generation component* (32 single-stream DiT layers); text/image encoder is a separate Qwen3-VL-8B `[V]`. |
| "No edit checkpoint needed" | Correct: one checkpoint does T2I + edit + RGBA `[V]`. |
| Native resolution | Official native sizes start at 2048x2048 up to 2752x1536 `[V]`; 1024x1024 works (used as the official "first run" size in third-party guides) `[V]`. |
| Transparency | Triggered by **prompt wording**, not a flag `[V]` (section 6.4). |
| Default sampling | Official pipeline: **40 steps, CFG 1.0 (guidance off)** `[V]`. At CFG 1.0 the negative prompt has **no effect**; it only matters when `--cfg` > 1 (section 5.2). |

---

## 2. Feature cheat-sheet

| Feature | What it does | How to trigger | Limits / tips |
|---|---|---|---|
| Unified T2I + edit | Same weights generate and edit | No `--image` = generate. With `--image` = edit `[P]` | Don't load a separate edit ckpt. |
| Multi-reference (<=10) | Combine identity, outfit, style, product from several images into one scene | Refer to refs as `<image1>`, `<image2>`... in the prompt `[V]` | Order matters; give each ref one role ("subject from <image1>, style from <image2>"). Reuse of the prefix KV cache makes extra refs cheap `[V]`. CLI multi-ref flag: `[P]`. |
| Local / regional edit | Change only a region | Draw a circle / painted annotation on the input, or supply a separate mask `[V]` | Always add "keep everything else unchanged". Mask flag in CLI: `[P]`. |
| Native RGBA | Real alpha channel, ready to composite | Prompt format in 6.4 `[V]` | Many upscalers drop alpha: verify (6.4). |
| Subject extraction | Cut a subject out of a photo as RGBA | Edit prompt + RGBA phrase | Same alpha caveats. |
| Identity / product preservation | Keeps faces, logos, products stable across edits | Describe what must stay | Use for series mascots and recurring characters. |
| Typography | Improved text rendering | Exact text in double quotes + position + style | Section 7. |
| Prompt enhancers | Official PE-T2I / PE-I2I (9B) rewrite vague prompts into long precise ones `[V]` | Optional | The agent can play this role itself: expand to 60-150 words using the formula in 5.1. |

---

## 3. Draw Things CLI conventions

### 3.1 Command shape (matches the user's template; advanced keys go in `--config-json`)
```bash
mkdir -p "$HOME/Dev/tmp"
draw-things-cli generate \
  --model qwen_image_2.1_q8p.ckpt \
  --output "$HOME/Dev/tmp/name.png" \
  --prompt "..." --negative-prompt "..." \
  --width 1024 --height 1536 --steps 30 --cfg 3.0 --seed 42 \
  --config-json '{"sampler":15,"seedMode":2,"upscaler":"RealESRGAN_x4plus_anime_6B.safetensors","upscalerScaleFactor":4}'
```
- Use `"$HOME/..."`, not `'~/...'`: a tilde inside quotes is not expanded by the shell.
- Precedence `[V]`: CLI flags > `--config-json` > model recommended settings. Omit a key to inherit the model default (use this for `shift`).
- `--config-json` = `JSGenerationConfiguration` JSON, **camelCase keys only; unknown keys are silently ignored; enum fields take numbers; an out-of-range enum crashes the CLI** `[V]`. Typos fail silently, so verify effects (output dimensions, look).
- `""` disables `upscaler` `[V]`.

### 3.2 Config keys used in this playbook
| Key | Value | Note |
|---|---|---|
| `sampler` | int 0-19 (table below) | `[V]` enum |
| `seedMode` | 2 = Scale Alike (keeps composition when resolution changes) | `[V]` enum, `[R]` choice. 0 Legacy, 1 Torch CPU, 3 NVIDIA GPU |
| `upscaler` | exact file name string | `[P]` Draw Things may list upscalers under a converted name; confirm by checking that output size is 4x. |
| `upscalerScaleFactor` | 4 | `[P]` key name unconfirmed; harmless if ignored |
| `loras` | `[{"file":"x_lora_f16.ckpt","weight":0.8}]` | Unregistered local LoRAs may also need `"version"` `[V]`; import through the app so it registers the correct value `[P]` |
| `shift` | omit (auto) | Auto/dynamic shift is the recommended setup `[V]`; only set when a LoRA card says so (e.g. few-step LoRA: `1.0`). |

### 3.3 Probe block (run once; record results)
```bash
draw-things-cli generate --help
draw-things-cli models list --downloaded-only
```
Look for: repeated `--image` or reference flags (multi-ref), `--mask`, `--strength`, upscaler options. If `--image` behaves as classic img2img (ignores structure at `--strength 1.0`), lower to 0.45-0.75 and describe the final state in the prompt.

### 3.4 Sampler IDs `[V]` (SamplerType enum)
| ID | Name | Use here `[R]` |
|---|---|---|
| **15** | DPM++ 2M Trailing | **Default**: crisp lines, text, photo, edits |
| **10** | Euler A Trailing | Soft/painterly/organic media |
| 17 | UniPC Trailing | <=20-step drafts |
| 11 | DPM++ SDE Trailing | Alt for painterly grain |
| 1 | Euler A | Acceptable fallback for 10 |
| 9 / 19 | TCD / TCD Trailing | Only with a few-step distilled LoRA `[P]` |
| 6 | LCM | Only with an LCM LoRA |
| 0,2,3,4,5,7,8,12,13,14,16,18 | Karras / DDIM / PLMS / AYS / UniPC / Substep | Avoid: SD-era schedules |

---

## 4. Baseline recipe

### 4.1 Modes
| Mode | cfg | Negative prompt | Cost | When |
|---|---|---|---|---|
| A guidance-free (official default) | 1.0 | inert, omit | 1x | drafts, edits, speed priority |
| B guided (used in examples) | 2.0-3.5 | active | ~2x per step `[R]` | strict constraints (line art, no-shading, kids safety), or when A drifts |

Rule: for any genre, A/B same seed at cfg 1.0 (no negative) vs the listed cfg. Keep the cheaper one if quality is equal. Raise cfg for strict constraints, lower it if colours burn or textures go crunchy.

### 4.2 Steps
Draft 18-20 (sampler 17 or 15) | Final 28-36 | Text-heavy or photoreal 36-40 | Few-step LoRA 4-8. More steps do not always help.

### 4.3 Sizes (all multiples of 64)
| Aspect | Base ~1 MP (default) | High ~2-3 MP (photoreal / small text) |
|---|---|---|
| 2:3 | 1024x1536 | 1152x1728 or 1280x1920 |
| 3:4 | 1152x1536 | 1536x2048 |
| 1:1 | 1024x1024 | 1536x1536 (2048x2048 native) |
| 4:3 / 3:2 | 1536x1152 / 1536x1024 | 2048x1536 / 1920x1280 |
| 16:9 / 9:16 | 1792x1024 / 1024x1792 | 2752x1536 / 1536x2752 (native) |

Front-cover pixel targets at 300 dpi incl. 0.125 in bleed on top/bottom/outer edge `[R]`, confirm against the printer template:
| Trim | Target px | Base aspect |
|---|---|---|
| 6x9 in | 1838x2775 | 2:3 |
| 5x8 in | 1538x2475 | 2:3 (crop) |
| 7x10 in | 2138x3075 | 2:3 (crop) |
| 8.5x8.5 in | 2588x2625 | 1:1 |
| 8.5x11 in | 2588x3375 | 3:4 |
| eBook | 1600x2560 | 2:3 (crop) |

Pipeline: base image -> 4x upscaler (via config) -> fill-crop/downscale to target:
```bash
magick "$HOME/Dev/tmp/in.png" -resize 1838x2775^ -gravity center -extent 1838x2775 -colorspace sRGB "$HOME/Dev/tmp/out_6x9.png"
```
(`brew install imagemagick`). Check upscale worked: `sips -g pixelWidth -g pixelHeight file.png` (expect 4x base). Keep safe zone: title >= 8% inside trim.

---

## 5. Prompting

### 5.1 Prompt formula (natural language, 60-150 words, English)
`[medium + style] + [subject + action + setting] + [composition: focal point, empty area reserved for text] + [palette + lighting] + [TEXT BLOCKS] + [constraints stated positively]`

Text-block pattern (<=3 blocks): `Title at the top centre in <font look>, <colour> with <outline/effect>: "EXACT TEXT". Series line ... : "...". Publisher at the very bottom in small clean sans-serif: "...".`
- Quote exact strings with double quotes; one position + one style per block; titles <= 6 words; say "exactly" in edits.
- Reserve space: "calm empty sky area at the top for the title".
- State constraints positively ("pure white background", "flat colours"): at cfg 1.0 negatives do nothing.
- No coordinate API: place text with words (top third, centred, lower-left, bottom band). For pixel-exact placement, generate art without text and overlay type in post.
- Don't name living artists, trademarks, or known characters.

### 5.2 Negative prompts (only active when cfg > 1)
Reusable blocks, append to a genre-specific block:
- Universal: `blurry, low resolution, jpeg artifacts, watermark, signature, misspelled text, garbled letters, duplicated text, cropped title`
- Figures: `extra fingers, deformed hands, bad anatomy, extra limbs`
- Line art: `color fill, shading, gradient, gray tones, crosshatching, sketchy overlapping lines, filled black areas, background texture`
- Kids safety: `scary, dark mood, gore, weapons, creepy eyes, sharp teeth`
- Photo/real: `illustration, cgi, plastic skin, oversharpened, hdr halo, noise`
- Anti-medium (use the opposite of the target): painterly -> `flat vector, digital gloss`; flat -> `photorealistic, soft shading`.
Keep to 8-15 terms; long lists dilute.

### 5.3 Age modifiers (apply on top of genre profile)
| Age | Complexity | Palette / line | Text | Tweak |
|---|---|---|---|---|
| 0-2 board | 1 subject, centred, plain bg | primary colours, thick outlines | title >= 12% height | cfg +0.5, add kids-safety negatives |
| 3-5 | 1 hero + simple props | pastel/gouache, rounded shapes | title >= 10% | sampler 10 |
| 6-8 | 2-3 characters, dynamic pose | saturated cel colours | bold outlined title | sampler 15 |
| 9-12 | richer scene, depth | wider palette | clean sans/serif | steps +2 |
| 13-17 / YA | cinematic, mood | contrast, atmosphere | stylised, large | allow darker lighting, drop "scary" negative, keep gore negative |
| Adult | any | any | refined, small caps OK if >= 3% | high-res base for small text |

---

## 6. Feature recipes (executable)

### 6.1 Text-to-image cover (+ text)
See genre commands (section 9).

### 6.2 Edit: global fix (single reference) `[P]`
```bash
draw-things-cli generate \
  --model qwen_image_2.1_q8p.ckpt \
  --image "$HOME/Dev/tmp/qwen21_kids_picture_fox.png" \
  --output "$HOME/Dev/tmp/qwen21_edit_title_fix.png" \
  --prompt "Edit this book cover: correct the title so it reads exactly \"Fox in the Rain\" with the same lettering style, size and position. Keep the fox, raincoat, mushroom umbrella, background, colours, series line and publisher name unchanged." \
  --negative-prompt "changed characters, new objects, different style, misspelled text, blur, watermark" \
  --width 1024 --height 1536 --steps 30 --cfg 2.0 --strength 1.0 --seed 42 \
  --config-json '{"sampler":15,"seedMode":2}'
```
Match `--width/--height` to the input. Edit formula: `Change <X> to <Y>. Keep <list> unchanged.`

### 6.3 Edit: regional via painted annotation
```bash
# 1) paint a red ellipse around the target area (cx,cy rx,ry) on a COPY
magick "$HOME/Dev/tmp/qwen21_kids_picture_fox.png" -fill none -stroke red -strokewidth 6 \
  -draw "ellipse 512,1470 340,50 0,360" "$HOME/Dev/tmp/qwen21_annot.png"
# 2) edit only inside it
draw-things-cli generate \
  --model qwen_image_2.1_q8p.ckpt \
  --image "$HOME/Dev/tmp/qwen21_annot.png" \
  --output "$HOME/Dev/tmp/qwen21_edit_region.png" \
  --prompt "Edit only inside the red ellipse: change the small text to read exactly \"Lantern Hill Press\" in clean sans-serif. Remove the red ellipse from the result. Keep everything outside the ellipse identical." \
  --negative-prompt "changes outside the marked area, red outline left visible, misspelled text, blur" \
  --width 1024 --height 1536 --steps 30 --cfg 2.0 --strength 1.0 --seed 42 \
  --config-json '{"sampler":15,"seedMode":2}'
```
Mask route: if `--mask` exists (3.3), pass a white-on-black mask and drop the ellipse step `[P]`. Hand-fix remaining text in post if drift persists.

### 6.4 Native transparency (RGBA)
Official trigger phrase `[V]`: `This is an RGBA image with transparency. <subject>. The image has alpha channel and the background is transparent.`
```bash
draw-things-cli generate \
  --model qwen_image_2.1_q8p.ckpt \
  --output "$HOME/Dev/tmp/qwen21_rgba_mascot.png" \
  --prompt "This is an RGBA image with transparency. A cheerful cartoon red fox mascot waving, flat cel colours, thick clean outline, full body, centred. The image has alpha channel and the background is transparent." \
  --negative-prompt "background, floor shadow, scenery, cropped limbs, blur, watermark" \
  --width 1024 --height 1024 --steps 30 --cfg 2.0 --seed 42 \
  --config-json '{"sampler":15,"seedMode":2}'
sips -g hasAlpha "$HOME/Dev/tmp/qwen21_rgba_mascot.png"   # expect: hasAlpha: yes
magick "$HOME/Dev/tmp/qwen21_kids_picture_fox.png" \( "$HOME/Dev/tmp/qwen21_rgba_mascot.png" -resize 40% \) \
  -gravity southeast -geometry +60+220 -composite "$HOME/Dev/tmp/qwen21_cover_with_mascot.png"
```
No upscaler in this step (alpha safety). If an upscaler is needed: upscale RGB, upscale/resize the alpha separately, recombine with `magick rgb.png alpha.png -compose CopyOpacity -composite out.png`. Always re-check `hasAlpha`.

### 6.5 Subject extraction from a photo
```bash
draw-things-cli generate \
  --model qwen_image_2.1_q8p.ckpt \
  --image "$HOME/Dev/tmp/lighthouse_photo.png" \
  --output "$HOME/Dev/tmp/qwen21_extract_lighthouse.png" \
  --prompt "This is an RGBA image with transparency. Extract the lighthouse from <image1> with clean edges, preserving its exact appearance and details. The image has alpha channel and the background is transparent." \
  --negative-prompt "sky remnants, background fragments, halo edges, changed details" \
  --width 1024 --height 1536 --steps 30 --cfg 2.0 --strength 1.0 --seed 42 \
  --config-json '{"sampler":15,"seedMode":2}'
```

### 6.6 Multi-reference + series consistency `[P]`
Prompt grammar `[V]`: `Place <image1>'s subject into <image2>'s scene.` Series example:
`Create a new cover for Book 2 using <image1> as the layout, palette and typography reference and <image2> as the character reference. New title "..." . Keep the series banner and publisher block identical to <image1>.`
```bash
# if the CLI accepts repeated --image / reference flags (see probe), pass both. Fallback when only ONE image is accepted: build a side-by-side reference sheet and say "left panel / right panel" in the prompt.
magick "$HOME/Dev/tmp/book1_cover.png" "$HOME/Dev/tmp/character_sheet.png" -resize x1536 +append "$HOME/Dev/tmp/refs_sheet.png"
```
Series habits: fixed seed per series, identical layout sentence and text-block wording each volume, always attach the previous cover as `<image1>`.

---

## 7. Cover-text tactics
- Title <= 6 words; series + publisher <= 4 words each; <= 3 blocks.
- Keep publisher >= 3% of image height at base size (about 46 px on 1536). Smaller: overlay in post.
- Run OCR after generation when `tesseract` is installed (`brew install tesseract`; `tesseract img.png - | head`); compare to expected strings. Mismatch -> shorten text, +6 steps, raise base size, or edit-fix (6.2/6.3), else overlay.
- Upscalers can warp thin letters: prefer thick strokes/outlines for small text; for glyph-critical covers upscale the text-free art and overlay type afterwards.
- Style LoRAs can break lettering: lower weight to 0.6 or do art and text in two passes.

---

## 8. Upscaler matrix `[R]`
Only these four are allowed. All are 4x.
| Upscaler | Character | Use for | Avoid for |
|---|---|---|---|
| `RealESRGAN_x4plus_anime_6B.safetensors` | Clean edges, flat colour, keeps lines solid | Anime, cartoon/cel, flat vector, line art, coloring, mandala, outlined text | Photoreal, oil, watercolor (flattens texture) |
| `4x_foolhardy_Remacri_ExtraSmoother.safetensors` | Smooth, organic, fewer crunchy artifacts | Gouache, watercolor, oil, pencil/paper grain, storybook paint, soft photo | Crisp vector lines (slight softening) |
| `4x_NMKD-Superscale-SP_178000_G.safetensors` | Sharp, detail-rich | Digital painting/concept art, 3D renders, product/architecture, crisp graphics | Skin close-ups (oversharpening) |
| `RealESRGAN_x4plus.safetensors` | Faithful, least hallucination | Photography, photoreal portraits, realistic non-fiction | Anime/flat art (soft, plasticky) |

Tie-breakers: mixed media -> pick the dominant *surface* (lines/flat -> anime_6B; texture -> Remacri; micro-contrast -> NMKD; real-world -> x4plus). Oversharpened result -> swap NMKD for Remacri; smeared result -> swap x4plus/Remacri for NMKD. Line art finishing: `magick in.png -colorspace Gray -threshold 55% -type bilevel out.png`.

---

## 9. Genre profiles and example commands
All values `[R]` starting points. Common: seed 42, `seedMode` 2, 4x upscale then downscale (4.3). Publisher/series/author names are fictional placeholders.

| # | Genre (age) | Base size | steps | cfg | Sampler | Upscaler (alt) | LoRA type to seek |
|---|---|---|---|---|---|---|---|
| 1 | Kids picture book (3-5) | 1024x1536 | 30 | 3.0 | 10 | Remacri (anime_6B) | gouache/crayon storybook |
| 2 | Kids early reader (6-8) | 1024x1536 | 30 | 3.0 | 15 | anime_6B (NMKD) | flat vector/cel cartoon |
| 3 | Illustration book (all ages) | 1152x1536 | 32 | 2.5 | 10 | Remacri | ink-and-wash |
| 4 | Kids coloring (3-6) | 1152x1536 | 28 | 3.5 | 15 | anime_6B | thick line-art |
| 5 | Adult coloring / line art | 1152x1536 | 34 | 3.5 | 15 | anime_6B | fine line-art/zentangle |
| 6 | Adult mandala | 1024x1024 | 34 | 3.5 | 15 | anime_6B | mandala/symmetry |
| 7 | Storybook fantasy (6-10) | 1024x1536 | 32 | 2.5 | 10 | Remacri (NMKD) | painterly fantasy |
| 8 | Non-fiction kids/teens (9-14) | 1024x1536 | 30 | 3.0 | 15 | anime_6B (NMKD) | flat editorial vector |
| 9 | Pencil / artistic sketch | 1152x1536 | 32 | 2.5 | 10 | Remacri (NMKD) | graphite/charcoal |
| 10 | Oil painting | 1024x1536 | 36 | 2.5 | 10 | Remacri | impasto/classical oil |
| 11 | Watercolor | 1152x1536 | 32 | 2.5 | 10 | Remacri | wet-on-wet watercolor |
| 12 | 2D anime (teen) | 1024x1536 | 30 | 3.0 | 15 | anime_6B | anime cel/key visual |
| 13 | 3D anime / 3D render (kids-teen) | 1024x1536 | 30 | 2.5 | 15 | NMKD (x4plus) | 3D render/toy |
| 14 | Digital drawing / concept art (YA) | 1024x1536 | 32 | 2.5 | 15 | NMKD (Remacri) | concept-art painterly |
| 15 | Photography (nature/travel) | 1024x1536 | 36 | 2.0 | 15 | x4plus (Remacri) | usually none (base is strong) |
| 16 | Photorealism (portrait/product) | 1152x1728 | 40 | 2.0 | 15 | x4plus (NMKD) | usually none |
| 17 | Adult non-fiction typographic | 1280x1920 | 40 | 3.0 | 15 | anime_6B (NMKD) | none (text fidelity first) |

### 9.1 Kids picture book (3-5)
```bash
draw-things-cli generate \
  --model qwen_image_2.1_q8p.ckpt \
  --output "$HOME/Dev/tmp/qwen21_kids_picture_fox.png" \
  --prompt "Children's picture book cover, soft gouache illustration with visible paper grain, a smiling red fox cub in a yellow raincoat splashing in a puddle beneath a giant mushroom umbrella, warm pastel palette, rounded friendly shapes, one clear focal subject, calm empty sky area at the top for the title. Title at the top centre in bold hand-lettered rounded letters, cream colour with a dark teal outline: \"Fox in the Rain\". Smaller text at the bottom centre: \"A Little Explorers Story\". Publisher name at the very bottom in small clean sans-serif: \"Lantern Hill Press\"." \
  --negative-prompt "scary, dark mood, photorealistic, sharp teeth, clutter, misspelled text, garbled letters, extra limbs, watermark, cropped title" \
  --width 1024 --height 1536 --steps 30 --cfg 3.0 --seed 42 \
  --config-json '{"sampler":10,"seedMode":2,"upscaler":"4x_foolhardy_Remacri_ExtraSmoother.safetensors","upscalerScaleFactor":4}'
```

### 9.2 Kids early reader (6-8)
```bash
draw-things-cli generate \
  --model qwen_image_2.1_q8p.ckpt \
  --output "$HOME/Dev/tmp/qwen21_kids_reader_gutter.png" \
  --prompt "Early-reader chapter book cover, flat vector cartoon style with bold clean outlines and cel colours, two kids and a robot dog racing paper boats down a rainy street gutter, dynamic diagonal composition, bright saturated primary palette, plain light-blue sky background. Title across the top in chunky outlined block capitals, yellow with a thick navy outline: \"The Great Gutter Race\". Series banner under the title in a red ribbon: \"Robo-Pup Readers\". Publisher in small sans-serif at the bottom left: \"Lantern Hill Press\"." \
  --negative-prompt "photorealistic, gradients, soft shading, gray tones, blurry, extra fingers, deformed hands, misspelled text, watermark, cropped title" \
  --width 1024 --height 1536 --steps 30 --cfg 3.0 --seed 42 \
  --config-json '{"sampler":15,"seedMode":2,"upscaler":"RealESRGAN_x4plus_anime_6B.safetensors","upscalerScaleFactor":4}'
```

### 9.3 Illustration book (ink and watercolor)
```bash
draw-things-cli generate \
  --model qwen_image_2.1_q8p.ckpt \
  --output "$HOME/Dev/tmp/qwen21_illustration_lighthouse.png" \
  --prompt "Illustrated storybook anthology cover, loose ink linework with transparent watercolour washes on cream paper, a lighthouse keeper and an owl sharing tea on a rocky island at dusk, delicate hand-drawn details, muted teal and ochre palette, generous margins. Title in elegant hand-drawn serif capitals, dark brown, centred in the top third: \"Tales from the Lantern Coast\". Series line below in small italics: \"The Lighthouse Folio\". Publisher at the bottom centre in small caps: \"Lantern Hill Press\"." \
  --negative-prompt "photo, 3d render, heavy digital gradients, neon colours, blurry, misspelled text, garbled letters, watermark, harsh outlines" \
  --width 1152 --height 1536 --steps 32 --cfg 2.5 --seed 42 \
  --config-json '{"sampler":10,"seedMode":2,"upscaler":"4x_foolhardy_Remacri_ExtraSmoother.safetensors","upscalerScaleFactor":4}'
```

### 9.4 Kids coloring book (3-6), line art
```bash
draw-things-cli generate \
  --model qwen_image_2.1_q8p.ckpt \
  --output "$HOME/Dev/tmp/qwen21_coloring_kids_dino.png" \
  --prompt "Children's coloring book cover, thick uniform black outlines on a pure white background, a friendly dinosaur holding a balloon surrounded by simple stars and flowers, large open shapes that are easy to colour, no shading, no fills. Title at the top in big bubble letters outlined in black with white fill: \"Dino Colouring Fun\". Banner under it: \"Ages 3 to 6\". Publisher at the bottom in small plain capitals: \"Lantern Hill Press\"." \
  --negative-prompt "color fill, shading, gradient, gray tones, crosshatching, thin sketchy lines, filled black areas, texture, photo, misspelled text, watermark" \
  --width 1152 --height 1536 --steps 28 --cfg 3.5 --seed 42 \
  --config-json '{"sampler":15,"seedMode":2,"upscaler":"RealESRGAN_x4plus_anime_6B.safetensors","upscalerScaleFactor":4}'
```
Interior pages: same recipe without text blocks; finish with the threshold command (section 8).

### 9.5 Adult coloring book, intricate line art
```bash
draw-things-cli generate \
  --model qwen_image_2.1_q8p.ckpt \
  --output "$HOME/Dev/tmp/qwen21_coloring_adult_owl.png" \
  --prompt "Intricate adult coloring book cover, fine uniform black ink lines on pure white, a mystical owl perched on a crescent moon wrapped in flowers, leaves and ornamental patterns, dense zentangle-style details, perfectly closed shapes, no shading, no colour. Title in an ornate black outline serif across the top, white inside: \"Midnight Owls\". Series text below in small plain capitals: \"Mystic Garden Colouring Series\". Publisher at the bottom: \"Lantern Hill Press\"." \
  --negative-prompt "color, shading, gray fill, gradient, sketchy overlapping lines, broken lines, blurry, smudges, background texture, photo, misspelled text, watermark" \
  --width 1152 --height 1536 --steps 34 --cfg 3.5 --seed 42 \
  --config-json '{"sampler":15,"seedMode":2,"upscaler":"RealESRGAN_x4plus_anime_6B.safetensors","upscalerScaleFactor":4}'
```

### 9.6 Adult mandala coloring
```bash
draw-things-cli generate \
  --model qwen_image_2.1_q8p.ckpt \
  --output "$HOME/Dev/tmp/qwen21_mandala_adult.png" \
  --prompt "Adult mandala coloring book cover, perfectly symmetrical radial mandala with layered petals, paisley and geometric lace patterns, crisp fine black lines on pure white, centred and filling 80 percent of the frame, no shading, no colour. Title in an elegant black outline serif at the top: \"Mandala Serenity\". Subtitle at the bottom in small plain capitals: \"50 Calming Designs\". Publisher in tiny capitals under it: \"Lantern Hill Press\"." \
  --negative-prompt "color, shading, gray fill, gradient, asymmetry, off-centre, broken lines, blurry, smudges, background texture, photo, misspelled text, watermark" \
  --width 1024 --height 1024 --steps 34 --cfg 3.5 --seed 42 \
  --config-json '{"sampler":15,"seedMode":2,"upscaler":"RealESRGAN_x4plus_anime_6B.safetensors","upscalerScaleFactor":4}'
```

### 9.7 Storybook fantasy (6-10)
```bash
draw-things-cli generate \
  --model qwen_image_2.1_q8p.ckpt \
  --output "$HOME/Dev/tmp/qwen21_storybook_ember_dragon.png" \
  --prompt "Fantasy storybook cover, rich digital painting with soft painterly brushwork and glowing light, a young girl with a lantern leading a small dragon through an enchanted forest of giant glowing mushrooms, magical teal and amber palette, misty depth layers, characters in the lower third, open space at the top. Title in decorative golden fantasy lettering with a subtle glow: \"Mira and the Ember Dragon\". Series line in small cream capitals: \"The Glimmerwood Tales\". Publisher at the bottom in small plain capitals: \"Lantern Hill Press\"." \
  --negative-prompt "photo, grim, horror, gore, blurry, deformed hands, extra limbs, muddy colours, misspelled text, watermark, cropped title" \
  --width 1024 --height 1536 --steps 32 --cfg 2.5 --seed 42 \
  --config-json '{"sampler":10,"seedMode":2,"upscaler":"4x_foolhardy_Remacri_ExtraSmoother.safetensors","upscalerScaleFactor":4}'
```

### 9.8 Non-fiction for kids/teens (9-14), flat editorial
```bash
draw-things-cli generate \
  --model qwen_image_2.1_q8p.ckpt \
  --output "$HOME/Dev/tmp/qwen21_nonfiction_space.png" \
  --prompt "Non-fiction book cover for ages 9 to 14, modern flat vector editorial illustration, a cutaway of the solar system with a small astronaut pointing at Saturn, clean geometric shapes, limited palette of deep navy, coral and mustard, strong visual hierarchy, tidy margins. Title in bold geometric sans-serif capitals, white on the navy area at the top: \"SPACE: THE BIG PICTURE\". Subtitle in smaller sans-serif: \"Facts, Maps and Mind-Blowing Numbers\". Series text at the bottom left: \"Know More Series\". Publisher at the bottom right: \"Lantern Hill Press\"." \
  --negative-prompt "photorealistic, clutter, gradients, neon, blurry, misspelled text, garbled letters, watermark, tiny unreadable text, cropped title" \
  --width 1024 --height 1536 --steps 30 --cfg 3.0 --seed 42 \
  --config-json '{"sampler":15,"seedMode":2,"upscaler":"RealESRGAN_x4plus_anime_6B.safetensors","upscalerScaleFactor":4}'
```

### 9.9 Pencil / artistic sketch
```bash
draw-things-cli generate \
  --model qwen_image_2.1_q8p.ckpt \
  --output "$HOME/Dev/tmp/qwen21_sketch_fisherman.png" \
  --prompt "Artistic graphite pencil sketch on cream sketchbook paper, loose expressive strokes with cross-hatching and smudged shading, portrait of an old fisherman looking out to sea, visible paper grain, monochrome grey tones, edges fading into blank paper. Title in refined hand-lettered pencil capitals at the top: \"Salt and Graphite\". Subtitle at the bottom in small pencil script: \"A Sketchbook of Harbour Faces\". Publisher in tiny capitals: \"Lantern Hill Press\"." \
  --negative-prompt "colour, digital gloss, clean vector lines, 3d render, photo, blurry, misspelled text, watermark, heavy black fills" \
  --width 1152 --height 1536 --steps 32 --cfg 2.5 --seed 42 \
  --config-json '{"sampler":10,"seedMode":2,"upscaler":"4x_foolhardy_Remacri_ExtraSmoother.safetensors","upscalerScaleFactor":4}'
```

### 9.10 Oil painting
```bash
draw-things-cli generate \
  --model qwen_image_2.1_q8p.ckpt \
  --output "$HOME/Dev/tmp/qwen21_oil_last_tide.png" \
  --prompt "Classical oil painting on canvas with visible impasto brushstrokes and fine craquelure, a stormy sea with a lone sailing ship under breaking golden light, dramatic chiaroscuro, rich ultramarine, umber and gold palette, museum quality. Title in gold serif capitals with a soft shadow, centred near the top: \"The Last Tide\". Author line in small gold serif: \"Elena Marsh\". Publisher in small capitals at the bottom: \"Lantern Hill Press\"." \
  --negative-prompt "digital look, flat vector, photo, plastic gloss, blurry, oversaturated, misspelled text, watermark, cropped title" \
  --width 1024 --height 1536 --steps 36 --cfg 2.5 --seed 42 \
  --config-json '{"sampler":10,"seedMode":2,"upscaler":"4x_foolhardy_Remacri_ExtraSmoother.safetensors","upscalerScaleFactor":4}'
```

### 9.11 Watercolor
```bash
draw-things-cli generate \
  --model qwen_image_2.1_q8p.ckpt \
  --output "$HOME/Dev/tmp/qwen21_watercolor_poppies.png" \
  --prompt "Delicate watercolour painting on textured cold-press paper, wet-on-wet washes and soft bleeding edges, a field of wild poppies and a small cottage in morning mist, airy pastel palette with white paper left showing, gentle light. Title in thin hand-painted serif letters in deep green: \"Poppy Fields\". Subtitle in small italics: \"A Year in the Meadow\". Publisher at the bottom in tiny capitals: \"Lantern Hill Press\"." \
  --negative-prompt "digital gloss, hard outlines, photo, heavy black, oversaturated, blurry, misspelled text, watermark" \
  --width 1152 --height 1536 --steps 32 --cfg 2.5 --seed 42 \
  --config-json '{"sampler":10,"seedMode":2,"upscaler":"4x_foolhardy_Remacri_ExtraSmoother.safetensors","upscalerScaleFactor":4}'
```

### 9.12 2D anime (teen)
```bash
draw-things-cli generate \
  --model qwen_image_2.1_q8p.ckpt \
  --output "$HOME/Dev/tmp/qwen21_anime2d_lanterns.png" \
  --prompt "Japanese 2D anime key-visual illustration, clean cel shading, crisp lineart, a schoolgirl with windswept silver hair holding a glowing paper lantern on a rooftop at twilight, city lights bokeh, vibrant magenta and cyan palette, cinematic composition with the character on the right third. Title in stylish bold sans-serif with a neon glow, upper left: \"Lanterns Over Tokyo\". Volume text in small capitals: \"Vol. 1\". Publisher at the bottom: \"Lantern Hill Press\"." \
  --negative-prompt "3d render, photo, western comic style, blurry, deformed hands, extra fingers, bad anatomy, muddy colours, misspelled text, watermark, cropped title" \
  --width 1024 --height 1536 --steps 30 --cfg 3.0 --seed 42 \
  --config-json '{"sampler":15,"seedMode":2,"upscaler":"RealESRGAN_x4plus_anime_6B.safetensors","upscalerScaleFactor":4}'
```

### 9.13 3D animated / 3D render look
```bash
draw-things-cli generate \
  --model qwen_image_2.1_q8p.ckpt \
  --output "$HOME/Dev/tmp/qwen21_3d_garden_bot.png" \
  --prompt "Stylised 3D animated-feature look, soft global illumination, subsurface scattering, glossy rounded materials, a cheerful robot gardener watering a tiny floating island with oversized flowers, warm sunrise lighting, shallow depth of field, vibrant but harmonious colours. Title in chunky 3D bubble letters with a soft shadow at the top: \"Pip the Garden Bot\". Series line in a rounded ribbon: \"Floating Island Friends\". Publisher in small clean sans-serif at the bottom: \"Lantern Hill Press\"." \
  --negative-prompt "2d flat, line drawing, photo, uncanny face, blurry, noisy, deformed, misspelled text, watermark, cropped title" \
  --width 1024 --height 1536 --steps 30 --cfg 2.5 --seed 42 \
  --config-json '{"sampler":15,"seedMode":2,"upscaler":"4x_NMKD-Superscale-SP_178000_G.safetensors","upscalerScaleFactor":4}'
```

### 9.14 Digital drawing / concept art (YA)
```bash
draw-things-cli generate \
  --model qwen_image_2.1_q8p.ckpt \
  --output "$HOME/Dev/tmp/qwen21_concept_skybound.png" \
  --prompt "Digital concept-art illustration, painterly brushwork with sharp rim lighting, a lone hooded cartographer standing on a cliff above a vast floating-islands archipelago at dawn, atmospheric perspective, teal and orange palette, epic scale, strong silhouette. Title in tall engraved metallic serif capitals, centred in the lower third: \"THE SKYBOUND ATLAS\". Series text above the title in small spaced capitals: \"BOOK ONE OF THE DRIFT SAGA\". Publisher at the very bottom in tiny capitals: \"Lantern Hill Press\"." \
  --negative-prompt "photo, cartoon, flat vector, blurry, low detail, deformed anatomy, extra limbs, oversaturated, misspelled text, watermark" \
  --width 1024 --height 1536 --steps 32 --cfg 2.5 --seed 42 \
  --config-json '{"sampler":15,"seedMode":2,"upscaler":"4x_NMKD-Superscale-SP_178000_G.safetensors","upscalerScaleFactor":4}'
```

### 9.15 Photography (nature)
```bash
draw-things-cli generate \
  --model qwen_image_2.1_q8p.ckpt \
  --output "$HOME/Dev/tmp/qwen21_photo_red_kite.png" \
  --prompt "Professional nature photograph, 85mm lens, shallow depth of field, natural golden-hour light, a red kite gliding over misty moorland with soft bokeh hills, fine feather detail, natural colour grading, calm negative space in the sky at the top. Title in clean elegant serif capitals, white, centred in the sky area: \"Wings Over the Moor\". Subtitle in small light sans-serif: \"A Field Naturalist's Year\". Publisher at the bottom in tiny white capitals: \"Lantern Hill Press\"." \
  --negative-prompt "illustration, painting, cgi, oversharpened, hdr halo, blown highlights, noise, watermark, misspelled text, cropped title" \
  --width 1024 --height 1536 --steps 36 --cfg 2.0 --seed 42 \
  --config-json '{"sampler":15,"seedMode":2,"upscaler":"RealESRGAN_x4plus.safetensors","upscalerScaleFactor":4}'
```

### 9.16 Photorealism (portrait)
```bash
draw-things-cli generate \
  --model qwen_image_2.1_q8p.ckpt \
  --output "$HOME/Dev/tmp/qwen21_photoreal_weaver.png" \
  --prompt "Hyper-realistic studio portrait photograph, 105mm lens, soft key light with gentle rim light, an elderly weaver with deeply textured skin and kind eyes holding a spool of indigo thread, natural skin pores and fine hair detail, dark neutral backdrop, shallow depth of field. Title in refined white serif capitals at the top left: \"Hands of Indigo\". Subtitle in small light sans-serif: \"Portraits of Living Craft\". Publisher at the bottom left in tiny capitals: \"Lantern Hill Press\"." \
  --negative-prompt "cartoon, illustration, plastic skin, airbrushed, uncanny eyes, extra fingers, deformed hands, oversharpened, watermark, misspelled text" \
  --width 1152 --height 1728 --steps 40 --cfg 2.0 --seed 42 \
  --config-json '{"sampler":15,"seedMode":2,"upscaler":"RealESRGAN_x4plus.safetensors","upscalerScaleFactor":4}'
```

### 9.17 Adult non-fiction, typographic
```bash
draw-things-cli generate \
  --model qwen_image_2.1_q8p.ckpt \
  --output "$HOME/Dev/tmp/qwen21_nonfiction_quiet.png" \
  --prompt "Minimalist modern non-fiction book cover, solid warm off-white background with one bold abstract geometric shape in terracotta and charcoal, generous negative space, strict grid alignment. Title in very large bold geometric sans-serif capitals, charcoal, left-aligned in the upper half on two lines: \"THE QUIET\" and \"ADVANTAGE\". Subtitle in medium sans-serif below: \"How Calm Teams Outperform Loud Ones\". Author name in small capitals at the lower left: \"Daniel Reyes\". Publisher at the bottom right in tiny capitals: \"Lantern Hill Press\"." \
  --negative-prompt "photo, clutter, gradients, drop shadows, ornate fonts, blurry, misspelled text, garbled letters, extra words, watermark" \
  --width 1280 --height 1920 --steps 40 --cfg 3.0 --seed 42 \
  --config-json '{"sampler":15,"seedMode":2,"upscaler":"RealESRGAN_x4plus_anime_6B.safetensors","upscalerScaleFactor":4}'
```

---

## 10. Agent decision logic

### 10.1 Requirement slots (fill from the user; defaults when missing)
`genre` (infer; default digital illustration) | `age` (adult) | `trim` (6x9) | `text blocks` (title; series/publisher/author optional) | `mood/palette` (genre default) | `commercial` (**true**, triggers G1) | `speed_vs_quality` (quality) | `existing_image` (none) | `refs` (0) | `needs_transparency` (false) | `series` (false).

### 10.2 Routing rules
1. G1 fails -> warn, offer options, continue only on the user's choice.
2. `existing_image` present -> edit path: whole-image change = 6.2; one area = 6.3; many refs = 6.6.
3. `needs_transparency` -> 6.4/6.5, no upscaler (or the alpha-safe route).
4. Text blocks > 3, or any text < 3% height, or exact spelling is critical -> generate text-free art + overlay type; or generate with text then OCR-verify.
5. Line art / coloring / mandala -> mode B, cfg 3.5, sampler 15, anime_6B, threshold finish.
6. `speed` priority -> mode A (cfg 1.0, no negative), 20 steps, sampler 17; optionally a few-step LoRA (section 11). Re-run the winner at final settings.
7. Mixed genre (e.g. "watercolor anime") -> pick dominant medium for sampler/upscaler; cfg -0.5; put the secondary style as a short clause.
8. Ambiguous age -> choose the more conservative column in 5.3 and add kids-safety negatives for anyone under 13.
9. Missing steps/cfg knowledge -> omit `--steps/--cfg` to inherit the model's recommended settings `[V]`, then tune.

### 10.3 Seed sweep and QA
Draft 4 seeds (42, 1337, 2026, 777) at 20 steps -> choose by rubric -> re-run the winner at final steps (same seed, `seedMode` 2 keeps composition even if size changes) -> upscale -> crop/resize -> verify.

Rubric (0-5 each, accept if text >= 4 and total >= 22 of 30): text exactness (OCR) | thumbnail legibility at ~200 px wide | composition + safe zones | anatomy/artifacts | style fidelity to the request | age appropriateness. Add print readiness as pass/fail (size, sRGB, alpha as intended).

### 10.4 Troubleshooting
| Symptom | Fix |
|---|---|
| Misspelled/garbled title | Shorten text; +6 steps; larger base (4.3 "High"); edit-fix 6.2/6.3; else overlay |
| Burnt/oversaturated | cfg -0.5 to -1; or mode A |
| Soft, mushy detail | +6 steps; sampler 15; High base size |
| Gray in line art | Negative "gray tones, shading"; cfg 3.5; threshold finish |
| Edit changes unwanted areas | Add "keep everything else unchanged"; use annotation/mask; match input size; if img2img semantics, lower `--strength` |
| Alpha lost | Skip upscaler or recombine alpha (6.4) |
| Upscaler halos/oversharpen | NMKD -> Remacri; check against 8 |
| Output not 4x base | `upscaler` name not matched or key ignored `[P]`: read the exact name from Draw Things, re-run, re-check dimensions |
| LoRA ruins text | Weight 0.6, or two-pass art then overlay |
| Out of memory | Lower base size one step; close other apps; keep batch 1 |
| CLI crash on config | An enum is out of range (sampler must be 0-19) |

---

## 11. LoRAs
Rules: (1) must be trained on **Qwen-Image-2.1**, not 1.0/2512/Edit (different architecture; the 2512 Lightning/Turbo LoRAs will not fit) `[V]` | (2) <= 2 active | (3) weights: speed 1.0, style 0.6-0.9, subject/character 0.7-1.0 `[R]` | (4) trigger words go first in the prompt | (5) derivatives of 2.1 carry the research licence `[V]` | (6) register by importing in the Draw Things app so the correct `version` is stored `[P]`, then reference by file name | (7) re-test text rendering with every LoRA.

Published 2.1 adapters seen (all research-licensed): few-step LoRAs (Pruna: 5 or 8 steps, no CFG, shift 1.0 `[V]`; Viggle turbo: 4 steps, no CFG `[V]`), and community style LoRAs (one game-style LoRA suggests 25 steps, CFG 4.3, shift 3.1 `[V]`). Draw Things compatibility of any of these: `[P]`.

Genre -> what to look for: coloring/line art = line-art LoRA 0.7-0.9, drop cfg none, keep negatives | watercolor/oil/pencil = media LoRA 0.6-0.8, sampler 10 | anime = cel/anime LoRA 0.7-0.9, sampler 15 | 3D = render/toy LoRA 0.7 | kids = gouache/crayon LoRA 0.6-0.8 | photo = usually none.

Snippets (replace the REPLACE_ file names with the registered names; they will not run unchanged):
```bash
# Style LoRA on a line-art cover (add to 9.5; steps 30, cfg 3.0)
--config-json '{"sampler":15,"seedMode":2,"upscaler":"RealESRGAN_x4plus_anime_6B.safetensors","upscalerScaleFactor":4,"loras":[{"file":"REPLACE_line_art_qwen21_lora_f16.ckpt","weight":0.8}]}'

# Watercolor LoRA (add to 9.11; weight 0.7; trigger word first in the prompt)
--config-json '{"sampler":10,"seedMode":2,"upscaler":"4x_foolhardy_Remacri_ExtraSmoother.safetensors","upscalerScaleFactor":4,"loras":[{"file":"REPLACE_watercolor_qwen21_lora_f16.ckpt","weight":0.7}]}'

# Few-step draft LoRA: 8 steps, cfg 1.0, NO negative prompt, shift 1.0 (draft only; re-run final without it)
--steps 8 --cfg 1.0 --config-json '{"sampler":17,"seedMode":2,"shift":1.0,"loras":[{"file":"REPLACE_fewstep_qwen21_lora_f16.ckpt","weight":1.0}]}'
```

---

## 12. Sources (checked 2026-10-19)
- Qwen-Image-2.1 model card (7B, 10 refs, local edits, RGBA prompt, aspect ratios, 40-step example): https://huggingface.co/Qwen/Qwen-Image-2.1
- Qwen blog: https://qwen.ai/blog?id=qwen-image-2.1
- ComfyUI Wiki (native sizes, Qwen3-VL-8B, RGBA prompt): https://comfyui-wiki.com/en/models/qwen-image/qwen-image-2.1
- Prompt rewriters (PE-I2I, `<image1>` grammar): https://huggingface.co/Qwen/Qwen-Image-2.1-PE-I2I
- License coverage: https://cellcog.ai/blog/qwen-image-2-1/ , https://techaiwire.com/articles/qwen-research-license-explained/ , https://www.eesel.ai/blog/qwen-image-2-1
- Local settings (40 steps / CFG 1, 1024 first run): https://unsloth.ai/docs/models/qwen-image-2.1
- Few-step LoRAs: https://huggingface.co/ameno-tech/Pruna-Qwen-Image-2.1 , https://huggingface.co/Viggle/Qwen-Image-2.1-viggle-turbo
- Draw Things CLI `--config-json` behaviour, sampler/seedMode enums: https://github.com/Wujidadi/dt-cli-wrapper (MANUAL.md, AGENTS.md, parameters/example.toml)
