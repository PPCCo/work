# Draw Things CLI Settings Playbook: Books & Illustration (Apple M4, 48 GB)

Audience: an AI recommendation agent. Purpose: map a user's image request to model, steps, CFG, sampler [id], resolution, upscaler, prompt style and a runnable command.
Last reviewed: 2026-10-16.

Tags: **[V]** = from a model card, Draw Things source/docs or official guidance. **[H]** = heuristic starting point; confirm with a fixed-seed A/B (section 7).
Sampler IDs are shown in brackets, e.g. UniPC Trailing [17].

---

## 1. Agent quick-start

1. Classify the request into a category (section 4 master table).
2. Check constraints that change the model choice: commercial use (section 8), text inside the image, character consistency across pages, print size, B&W vs colour, draft vs final.
3. Default model is **Qwen Image 2512**. Use Animagine for tag-style anime, Juggernaut for photoreal, ColorfulXL for vivid painterly colour, **Klein for fast drafts**.
4. Apply the category preset, then the age-group modifier (section 5).
5. Workflow: draft with Klein (4 steps, several seeds) to validate prompt and composition, then render finals in the target model. Seeds do NOT transfer between models.
6. Upscale and post-process per print spec (section 6).
7. Defaults when the user is unspecific: Qwen, ~1.3-1.7 MP at the page aspect ratio, steps 30, cfg 4, UniPC Trailing [17], `realesrgan_x2plus_f16.ckpt`.
8. Ask at most two questions, and only if the answer changes model or licence: commercial use? text in image? B&W or colour? age group?

---

## 2. CLI and config reference

### 2.1 Sampler IDs (use as integer in `--config-json` "sampler") [V]

| ID | Name | Character [H] |
|---|---|---|
| 0 | DPM++ 2M Karras | Deterministic, clean, SDXL workhorse |
| 1 | Euler A | Ancestral: softer, organic, varied; good for anime and watercolour |
| 2 | DDIM | Legacy, predictable |
| 3 | PLMS | Legacy; avoid |
| 4 | DPM++ SDE Karras | Stochastic: extra micro-texture; painterly |
| 5 | UniPC | Fast convergence at low steps |
| 6 | LCM | Only with LCM LoRA/models (4-8 steps) |
| 7 | Euler A Substep | Experimental |
| 8 | DPM++ SDE Substep | Experimental |
| 9 | TCD | Only for TCD/distilled models |
| 10 | Euler A Trailing | Few-step and flow-matching models (Klein, Qwen); soft |
| 11 | DPM++ SDE Trailing | Stochastic trailing; texture |
| 12 | DPM++ 2M AYS | Align-Your-Steps schedule; SDXL at 10-20 steps |
| 13 | Euler A AYS | AYS + ancestral |
| 14 | DPM++ SDE AYS | AYS + SDE |
| 15 | DPM++ 2M Trailing | Crisp, deterministic; flow models |
| 16 | DDIM Trailing | Deterministic trailing |
| 17 | UniPC Trailing | Default for Qwen/flow models; stable and clean |
| 18 | UniPC AYS | AYS + UniPC |
| 19 | TCD Trailing | Distilled/TCD only |

Rules of thumb [H]: SDXL checkpoints -> [0], [1], [4]. Flow-matching models (Qwen, Klein) -> [17], [10], [15]; avoid Karras variants there. Ancestral/SDE samplers never fully converge, so more steps will not "fix" them; they change the look.

### 2.2 `--config-json` keys seen in Draw Things exported configs [V]

`sampler` (int), `shift`, `resolutionDependentShift`, `guidanceScale` (equivalent to `--cfg`; set only one), `steps`, `seed`, `seedMode`, `batchCount`, `hiresFix`, `tiledDecoding`, `tiledDiffusion`, `upscaler`, `strength` (img2img), `sharpness`, `cfgZeroStar`, `clipSkip`, `loras`.

LoRA format: `"loras": [{"file": "name_lora_f16.ckpt", "weight": 0.7}]`. Add `"version": "<model family>"` for local unregistered LoRAs. Empty means `"loras": []` (NOT `''`, which is invalid JSON). Style LoRAs: weight 0.5-0.8 [H].

Hi-res fix extras (`hiresFixStartWidth/Height/Strength`) are [H] key names: export a config from the app to confirm before use. Prefer `upscaler` for post-upscale.

### 2.3 Resolution presets (multiples of 64 only) [V: DT uses 64-px units]

| Aspect | SDXL family (native ~1 MP) | Qwen / Klein (up to ~1.8 MP) |
|---|---|---|
| 1:1 | 1024x1024 | 1280x1280 |
| 3:2 landscape / 2:3 portrait | 1216x832 / 832x1216 | 1536x1024 / 1024x1536 |
| 4:5 portrait (page-like) | 896x1152 | 1024x1280 |
| ~US Letter portrait (0.76) | 896x1152 | 1024x1344 |
| 16:9-ish | 1344x768 | 1664x960 |
| Cover 2:3 tall | 832x1216 | 1280x1920 |

SDXL below ~1 MP (e.g. 768x768) degrades anatomy; keep first pass at about 1 MP and upscale afterwards [V: SDXL native 1024].
Above ~2.5 MP set `"tiledDecoding": true` [V: decode corruption reported above ~2.9 MP on a Draw Things model; use as precaution].

### 2.4 Upscalers (`"upscaler"` in config-json; scale is fixed by the model file) [V names]

| File | Scale | Licence | Use |
|---|---|---|---|
| `realesrgan_x2plus_f16.ckpt` | 2x | BSD-3 (commercial OK) | Default for colour art/photo |
| `realesrgan_x4plus_f16.ckpt` | 4x | BSD-3 (commercial OK) | Line art, print pages (default upscaler in CLI skills) |
| `remacri_4x_f16.ckpt` | 4x | CC-BY-NC-SA (no commercial) | Avoid for commercial books |
| `4x_ultrasharp_f16.ckpt` | 4x | CC-BY-NC-SA (no commercial) | Avoid for commercial books |

Other installed files: `ls ~/Library/Containers/com.liuliu.draw-things/Data/Documents/Models`. After the first run confirm the output size: `sips -g pixelWidth -g pixelHeight FILE.png`. If the size did not change, run the upscale as a separate pass.

### 2.5 Pitfalls

- `'~/path'` in single quotes does not expand. Use `"$HOME/Dev/tmp/file.png"` and `mkdir -p "$HOME/Dev/tmp"` first.
- `--cfg 1` effectively disables the negative prompt; omit `--negative-prompt` for distilled models.
- Confirm filenames with `draw-things-cli models list --downloaded-only`; `draw-things-cli generate --help` is the source of truth for flags.
- Do not run two heavy generations in parallel on 48 GB; Qwen q8 alone is large.
- Avoid `$`, backticks and double quotes inside prompts (shell expansion). Use single quotes for quoted on-image text.

---

## 3. Model profiles

| Model file | Type | Prompting | Steps / CFG [V unless H] | Sampler | Strengths | Weak at |
|---|---|---|---|---|---|---|
| `qwen_image_2512_bf16_q8p.ckpt` | 20B flow-matching DiT, Apache-2.0 | Natural language, 40-120 words; real negative prompt works | Ref: 50 / 4, shift 3.1; practical 28-40 / 3-5 (photoreal 2-3.5) | [17] primary, [10]/[15] alt [H] | Instruction following, text rendering, line art, composition, realism | Slowest (CFG = 2 passes); Lightning LoRA drafts: 4-8 steps, cfg 1 |
| `flux_2_klein_base_4b_f16.ckpt` | 4B flow-matching, distilled (assumed) | Natural language, positive only | Distilled: 4-8 / 1 (no CFG). If it is the Base variant: 20-28 / 3.5-4 | [10] [H]; Base: [17] | Very fast drafts, clean illustration | Fine detail, long text, negative-prompt control |
| `juggernaut_xl_v9_f16.ckpt` | SDXL finetune | Comma tags + natural phrases, `(term:1.2)` weights, negatives effective | 30-40 / 3-7 (lower = more realistic) | [0] | Photoreal, cinematic light | Line art, text, <1 MP |
| `juggernaut_xl_x_f16.ckpt` | SDXL finetune (newer) | Same, better phrase understanding [H] | 30-36 / 4-6 [H] | [0] / [4] [H] | Photo, 3D render, general | Text, pure line art |
| `colorfulxl_v6.0_f16.ckpt` | SDXL finetune | Tags + phrases | 28-34 / 4-7 [H] | [0] / [1] [H] | Vivid colour, fantasy, painterly, cartoon | Photoreal skin, text |
| `animagine_xl_v3.1_f16.ckpt` | SDXL anime | **Danbooru tags**: subject, traits, scene, then `masterpiece, best quality, very aesthetic, absurdres` | 28 / 5-7 | [1] Euler A | 2D anime, character art | Natural-language prompts, non-anime |

If the Klein file behaves like a Base model (needs 20+ steps, washed-out at cfg 1), switch to the Base row. Check quantisation/variant in the model list.

---

## 4. Category playbooks

### 4.1 Master table (ranges; first model listed is the default)

| # | Category | Model order | Steps | CFG | Sampler [id] | Resolution | Upscaler | Neg. prompt |
|---|---|---|---|---|---|---|---|---|
| 1 | Kids coloring pages | Qwen > Klein | Qwen 28-32 / Klein 4-6 | Qwen 4-5 / Klein 1 | [17] / [10] | 1024x1344 | x4plus | Yes (Qwen) |
| 2 | Adult intricate line art | Qwen > Animagine (anime style) | 34-40 | 5-6 | [17] | 1024x1344 | x4plus | Yes |
| 3 | Mandalas | Qwen | 34-40 | 5-6 | [17] | 1280x1280 | x4plus | Yes |
| 4 | Kids picture/storybook, early readers | Qwen > ColorfulXL > Klein (draft) | 28-32 (SDXL 28-32) | 3.5-4.5 (SDXL 5-7) | [17] (SDXL [0]/[1]) | 1536x1024 spreads, 1280x1280 | x2plus | Yes |
| 5 | Non-fiction, diagrams, how-to | Qwen | 34-40 | 4-5 | [17] | 1536x1024 | x2plus or none | Yes |
| 6 | Pencil and charcoal sketch | Juggernaut v9 > Qwen | 30-34 | SDXL 4.5-6 / Qwen 3-4 | [0] / [10] | 1024x1280 | none/x2plus | Yes |
| 7 | Watercolour | ColorfulXL > Qwen | 28-34 | SDXL 4-6 / Qwen 3-3.5 | [1] / [10] | 1216x832 | none | Yes |
| 8 | Oil painting | Qwen > ColorfulXL | 30-36 | Qwen 3.5-4.5 / SDXL 5-7 | [17] / [4] | 1280x1024 | none (keeps brush texture) | Yes |
| 9 | 2D anime / manga | Animagine > ColorfulXL > Qwen | 26-30 | 5-7 | [1] | 832x1216 | x2plus | Yes |
| 10 | 3D / Pixar-style anime | Qwen > Klein > Juggernaut X | Qwen 28-32 / Klein 6-8 | Qwen 3.5-4 / Klein 1 | [17] / [10] | 1280x1280 | x2plus | Qwen only |
| 11 | Digital art, concept, flat vector | Qwen > ColorfulXL | 28-34 | 4-5 (SDXL 5-7) | [17] / [0] | 1536x1024 | x2plus | Yes |
| 12 | Photography / photoreal | Juggernaut v9/X > Qwen | SDXL 30-40 / Qwen 28-36 | SDXL 3-6 / Qwen 2-3.5 | [0] / [17] | 896x1152 (SDXL), 1280x1280 (Qwen) | x2plus | Yes |
| 13 | Covers, posters, text-bearing | Qwen | 36-40 | 4-5 | [17] | 1280x1920 | x2plus | Yes |
| 14 | Fast drafts, thumbnails, seed scouting | Klein | 4-8 | 1 | [10] | 1280x896 | none | No |

All commands below assume `mkdir -p "$HOME/Dev/tmp"` has been run.

### 4.2 Kids coloring pages (#1)
Tips: outline weight is controlled by words ("thick uniform"), not CFG. Raise CFG 0.5-1 if grey fills appear. Keep background to 2-3 simple items. Post-process: threshold to pure B&W (section 6).

```bash
draw-things-cli generate \
--model qwen_image_2512_bf16_q8p.ckpt \
--output "$HOME/Dev/tmp/qwen_coloring_kids_elephant.png" \
--prompt "children's coloring book page, a friendly baby elephant holding a balloon, thick uniform black outlines, simple large shapes, minimal background of two clouds and a sun, pure white background, no shading, no fill, black and white line art, centered composition with wide margins" \
--negative-prompt "shading, gray tones, gradients, color, hatching, texture, sketchy or double lines, tiny details, text, watermark, border, frame" \
--width 1024 --height 1344 --steps 30 --cfg 4.5 --seed 101 \
--config-json '{
"sampler": 17,
"shift": 3.1,
"resolutionDependentShift": false,
"upscaler": "realesrgan_x4plus_f16.ckpt",
"loras": []
}'
```
Why: cfg 4.5 enforces "no shading" without burning lines; [17] gives clean flow-model convergence; shift 3.1 is Qwen's reference value; x4plus is BSD-licensed and keeps lines crisp.

### 4.3 Adult intricate line art (#2)
Tips: more steps and CFG 5-6 hold fine line weight; ask for "closed shapes" so pages are colourable; resolution up before upscale.

```bash
draw-things-cli generate \
--model qwen_image_2512_bf16_q8p.ckpt \
--output "$HOME/Dev/tmp/qwen_coloring_adult_owl.png" \
--prompt "intricate adult coloring book page, mystical owl perched on a crescent moon, dense mandala-style feather patterns, fine uniform thin black linework, floral and geometric filler, high detail, black ink on pure white background, no shading, closed shapes suitable for coloring" \
--negative-prompt "color, gray shading, gradients, filled black areas, blurry or broken lines, 3d render, photo, text, watermark, background tint" \
--width 1024 --height 1344 --steps 38 --cfg 5.5 --seed 202 \
--config-json '{
"sampler": 17,
"shift": 3.1,
"resolutionDependentShift": false,
"upscaler": "realesrgan_x4plus_f16.ckpt",
"loras": []
}'
```
Why: 38 steps resolve dense detail; cfg 5.5 keeps the line-only constraint despite busy patterns; negatives block fills and tint.

### 4.4 Mandalas (#3)

```bash
draw-things-cli generate \
--model qwen_image_2512_bf16_q8p.ckpt \
--output "$HOME/Dev/tmp/qwen_mandala_lotus.png" \
--prompt "circular mandala coloring page, strict radial symmetry, concentric rings of lotus petals, paisley and geometric lattice, fine black line art, centered, pure white background, closed shapes" \
--negative-prompt "color, shading, gray fill, asymmetry, broken lines, text, watermark, background texture, photo" \
--width 1280 --height 1280 --steps 36 --cfg 5 --seed 303 \
--config-json '{
"sampler": 17,
"shift": 3.1,
"resolutionDependentShift": false,
"upscaler": "realesrgan_x4plus_f16.ckpt",
"loras": []
}'
```
Why: square canvas preserves radial symmetry; cfg 5 favours rule-following ("symmetry"); sweep 6-8 seeds because symmetry quality varies.

### 4.5 Kids picture/storybook (#4)
Tips: reuse one fixed "character block" sentence in every page prompt and keep the seed constant while changing only the scene; for refinements use `strength` 0.5-0.65 on a reference image (check `--help` for the input flag). Leave a calm area for text in the prompt.

```bash
draw-things-cli generate \
--model qwen_image_2512_bf16_q8p.ckpt \
--output "$HOME/Dev/tmp/qwen_storybook_fox_picnic.png" \
--prompt "children's picture book illustration, a small fox and a rabbit sharing a picnic under a big oak tree, soft gouache texture, warm autumn palette, rounded friendly shapes, gentle expressions, wide landscape composition with calm empty sky in the upper third for text" \
--negative-prompt "scary, creepy, realistic photo, deformed hands, extra fingers, harsh shadows, text, watermark, signature" \
--width 1536 --height 1024 --steps 30 --cfg 4 --seed 404 \
--config-json '{
"sampler": 17,
"shift": 3.1,
"resolutionDependentShift": false,
"upscaler": "realesrgan_x2plus_f16.ckpt",
"loras": []
}'
```
Why: cfg 4 balances prompt fidelity with painterly softness; 3:2 landscape matches spreads; x2plus adds print resolution without over-sharpening gouache texture.

Fast draft (Klein, 4 seeds):
```bash
for s in 1 2 3 4; do
draw-things-cli generate \
--model flux_2_klein_base_4b_f16.ckpt \
--output "$HOME/Dev/tmp/klein_draft_fox_$s.png" \
--prompt "children's picture book illustration, a small fox and a rabbit sharing a picnic under a big oak tree, soft gouache texture, warm autumn palette, rounded friendly shapes, wide landscape composition" \
--width 1280 --height 896 --steps 4 --cfg 1 --seed $s \
--config-json '{
"sampler": 10,
"loras": []
}'
done
```
Why: distilled Klein needs 4 steps and no CFG; no negative prompt (ignored at cfg 1); [10] is the soft few-step choice [H].

### 4.6 Non-fiction diagrams (#5)
Tips: keep labels to 1-3 words, quote exact text, verify spelling and facts by hand; for long labels typeset text in layout software instead.

```bash
draw-things-cli generate \
--model qwen_image_2512_bf16_q8p.ckpt \
--output "$HOME/Dev/tmp/qwen_diagram_water_cycle.png" \
--prompt "flat vector educational infographic for kids, water cycle diagram with sun, cloud, rain, river and ocean, arrows showing evaporation and condensation, clean white background, bold simple shapes, clear sans-serif labels reading 'Evaporation' 'Condensation' 'Rain'" \
--negative-prompt "misspelled text, extra letters, blurry text, photo, clutter, gradients, watermark" \
--width 1536 --height 1024 --steps 36 --cfg 4.5 --seed 505 \
--config-json '{
"sampler": 17,
"shift": 3.1,
"resolutionDependentShift": false,
"loras": []
}'
```
Why: Qwen is the only model here that renders text reliably; cfg 4.5 and 36 steps improve letter fidelity.

### 4.7 Pencil and charcoal sketch (#6)
Tips: lower CFG (4.5-5) gives looser, more hand-drawn strokes; add "textured paper"; keep colour words out of the prompt. For charcoal swap "graphite" for "charcoal, smudged, high contrast".

```bash
draw-things-cli generate \
--model juggernaut_xl_v9_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_pencil_fisherman.png" \
--prompt "graphite pencil sketch of an old fisherman's weathered face, cross-hatching, visible pencil strokes, soft smudged shading, textured cream paper, loose construction lines, monochrome" \
--negative-prompt "color, photo, 3d render, digital gradient, clean vector, smooth airbrushed, text, watermark, deformed" \
--width 1024 --height 1280 --steps 32 --cfg 5 --seed 606 \
--config-json '{
"sampler": 0,
"loras": []
}'
```
Why: [0] and 30-40 steps are Juggernaut's documented path; cfg 5 sits mid-range, loose enough for sketchy strokes.

### 4.8 Watercolour (#7)
Tips: low CFG and an ancestral sampler soften edges; do not upscale with sharp ESRGAN (destroys pigment blooms).

```bash
draw-things-cli generate \
--model colorfulxl_v6.0_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_watercolor_lighthouse.png" \
--prompt "watercolor painting of a lighthouse on a rocky coast at sunrise, wet-on-wet washes, pigment blooms, soft bleeding edges, visible paper grain, loose brushwork, white paper margins, pastel palette" \
--negative-prompt "photo, 3d render, sharp digital lines, oversaturated, airbrushed, text, watermark, blurry" \
--width 1216 --height 832 --steps 30 --cfg 5 --seed 707 \
--config-json '{
"sampler": 1,
"loras": []
}'
```
Why: Euler A [1] injects noise each step, giving organic bleeds [H]; cfg 5 keeps colour lively without hard edges.

### 4.9 Oil painting (#8)

```bash
draw-things-cli generate \
--model qwen_image_2512_bf16_q8p.ckpt \
--output "$HOME/Dev/tmp/qwen_oil_harbor.png" \
--prompt "oil painting of a stormy harbor at dusk, thick impasto brushstrokes, palette knife highlights, visible canvas weave, dramatic chiaroscuro, rich earthy palette with a warm lantern glow" \
--negative-prompt "photo, smooth digital render, flat vector, text, watermark, blurry, plastic" \
--width 1280 --height 1024 --steps 32 --cfg 3.5 --seed 808 \
--config-json '{
"sampler": 17,
"shift": 3.1,
"resolutionDependentShift": false,
"loras": []
}'
```
Why: cfg 3.5 leaves room for painterly irregularity; no upscaler preserves brush texture. For SDXL oil, use ColorfulXL with [4] DPM++ SDE Karras, cfg 6.

### 4.10 2D anime / manga (#9)
Tips: tag order = count, character, traits, scene, then quality tags; cfg above 7 over-saturates. Use the standard anime negative block.

```bash
draw-things-cli generate \
--model animagine_xl_v3.1_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_anime_sakura_girl.png" \
--prompt "1girl, solo, long silver hair, school uniform, cherry blossoms, gentle smile, looking at viewer, upper body, soft lighting, masterpiece, best quality, very aesthetic, absurdres" \
--negative-prompt "lowres, bad anatomy, bad hands, text, error, missing finger, extra digits, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, artist name" \
--width 832 --height 1216 --steps 28 --cfg 6 --seed 909 \
--config-json '{
"sampler": 1,
"upscaler": "realesrgan_x2plus_f16.ckpt",
"loras": []
}'
```
Why: model card recommends Euler A, <30 steps, cfg 5-7, one of its native 832x1216 buckets, and quality tags.

3D / Pixar-style (#10) quick prompt: "stylized 3D animated film still, cute round-faced child explorer, soft subsurface scattering, warm rim light, shallow depth of field, pastel palette" on Qwen (30 steps, cfg 3.5-4, [17], 1280x1280) or Klein (6-8 steps, cfg 1, [10]).

### 4.11 Photography / photoreal (#12)
Tips: lower CFG = more realistic skin (SDXL 3-5); specify lens, light and film grain; avoid "8k, masterpiece" spam. Qwen photoreal: cfg 2-3.5, 28-36 steps, [17], natural-language scene description.

```bash
draw-things-cli generate \
--model juggernaut_xl_v9_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_photo_gardener.png" \
--prompt "professional portrait photograph of an elderly woman gardener, natural window light, 85mm f/1.8, shallow depth of field, detailed skin texture, soft film grain, candid expression" \
--negative-prompt "cartoon, painting, illustration, 3d render, plastic skin, oversaturated, blurry, deformed hands, text, watermark" \
--width 896 --height 1152 --steps 35 --cfg 4.5 --seed 1010 \
--config-json '{
"sampler": 0,
"upscaler": "realesrgan_x2plus_f16.ckpt",
"loras": []
}'
```
Why: model card gives [0], 30-40 steps, cfg 3-7; 4.5 favours realism; x2plus post-upscale (card's own hi-res recipe is 1.5x at 0.3 denoise, 15 steps).

### 4.12 Covers and text-bearing art (#13)
Tips: keep titles to 4 words or fewer; render 4-6 seeds and pick the correctly spelled one; otherwise typeset externally and use "empty space for title".

```bash
draw-things-cli generate \
--model qwen_image_2512_bf16_q8p.ckpt \
--output "$HOME/Dev/tmp/qwen_cover_turtle_space.png" \
--prompt "children's book cover illustration, a brave little turtle astronaut on a pastel moon, title text 'Tilly Goes to Space' in bold rounded hand-lettered font at the top, soft gouache style, starry teal sky, centered subject, space for author name at the bottom" \
--negative-prompt "misspelled text, extra letters, blurry text, watermark, photo, scary" \
--width 1280 --height 1920 --steps 36 --cfg 4.5 --seed 1111 \
--config-json '{
"sampler": 17,
"shift": 3.1,
"resolutionDependentShift": false,
"tiledDecoding": true,
"upscaler": "realesrgan_x2plus_f16.ckpt",
"loras": []
}'
```
Why: 2.5 MP tall canvas, so `tiledDecoding` guards the VAE decode; 36 steps and cfg 4.5 improve lettering.

---

## 5. Age-group modifiers (apply on top of the category preset)

| Audience | Line/shape | Detail | CFG shift | Prompt words |
|---|---|---|---|---|
| Ages 2-4 | Very thick outlines, 1-3 large shapes | Almost no background | +0.5 | "bold, chunky, simple, huge shapes, plain background" |
| Ages 5-8 | Medium outlines | Simple scene, 3-5 elements | 0 | "friendly, rounded, cheerful, uncluttered" |
| Ages 9-12 | Medium-fine lines | Richer scenes, correct anatomy | 0 | "detailed, dynamic pose, accurate proportions" |
| Teens | Fine lines or realistic style | Complex composition | 0 to -0.5 | "dynamic, expressive, detailed environment" |
| Adults | Fine, dense | Maximum detail | +0.5 to +1 (line art) | "intricate, fine linework, dense pattern" |

Kid-safe negatives (always for under-12): "scary, creepy, violent, uncanny, realistic gore, deformed hands, extra fingers".

---

## 6. Print spec and post-processing

| Trim | Pixels @300 dpi | Route |
|---|---|---|
| US Letter 8.5x11 | 2550x3300 | 1024x1344 -> x4plus -> downscale |
| Square 8.5x8.5 | 2550x2550 | 1280x1280 -> x2plus (2560) |
| 8x10 | 2400x3000 | 1024x1280 -> x2plus (2048x2560) -> resize up 17% or use x4plus |
| 6x9 | 1800x2700 | 1024x1536 -> x2plus |

Line art to crisp B&W (ImageMagick, `brew install imagemagick`):
`magick in.png -colorspace Gray -resize 2550x3300 -threshold 60% -units PixelsPerInch -density 300 out.png`

Colour pages: export PNG, convert to CMYK or flatten in layout software per printer requirements.

---

## 7. Troubleshooting and A/B protocol

| Symptom | Fix (one change at a time) |
|---|---|
| Grey fills or shading in line art | cfg +1; add "gray, shading, gradients" to negative; threshold in post |
| Wobbly or broken lines | steps +6; try [15] DPM++ 2M Trailing; raise resolution |
| Burnt, over-contrast, plastic look | cfg -1 |
| Washed out or vague | cfg +0.5-1; steps +6 |
| Mushy detail | steps +8; larger first pass (<=1.8 MP); upscale |
| SDXL mangled anatomy or duplicated subjects | Use >=1 MP, not 768; stay <=1.6 MP first pass; upscale after |
| Text typos | Shorter text, single quotes, Qwen only, cfg 4.5, sweep seeds, or typeset externally |
| Corrupt final image at large size | `"tiledDecoding": true` |
| Style drift between pages | Fixed character block, same seed, change only the scene; img2img `strength` 0.5-0.65 from reference |
| Klein too plain | Steps 4 -> 8; add concrete detail nouns |
| Output size unchanged after `upscaler` | Run the upscale as a separate pass |

A/B protocol: fix seed, prompt and resolution. Change one knob per run: cfg +/-1, steps +/-6, or sampler between two candidates. Judge at 100% crop. Scout seeds cheaply with Klein, then render finals in the target model.

---

## 8. Licensing notes for commercial books (not legal advice; verify current terms)

| Asset | Status |
|---|---|
| Qwen Image 2512 | Apache-2.0 [V] |
| FLUX.2 klein 4B | Believed Apache-2.0 for the 4B model; verify on the model card |
| Juggernaut XL v9 / X | SDXL-derived; creator publishes commercial licensing terms for hosted services; verify output-use terms |
| ColorfulXL v6 | Verify on its model page |
| Animagine XL 3.1 | Fair AI Public License 1.0-SD [V]: modifications must be shared |
| Upscalers: RealESRGAN x2plus/x4plus | BSD-3-Clause, commercial OK [V] |
| Upscalers: 4x UltraSharp, Remacri | CC-BY-NC-SA 4.0, NOT commercial [V] |
| Third-party LoRAs | Check each licence; many style LoRAs are non-commercial |

---

## 9. Sources

- Draw Things sampler enum: https://lmstudio.ai/ceveyne/draw-things-index/files/src/flatbuffers/sampler-type.ts
- Draw Things config schema: https://lmstudio.ai/ceveyne/draw-things-chat/files/src/interfaces/config.fbs
- Draw Things community CLI skill (config-json keys, sampler 17 example): https://raw.githubusercontent.com/drawthingsai/draw-things-community/3cac0759afad9d266004606263030916006be16e/.agents/skills/train-lora/SKILL.md
- Draw Things decode issue (tiledDecoding): https://github.com/drawthingsai/draw-things-community/issues/105
- Qwen Image 2512 workflow settings: https://unpkg.com/comfyui-mcp@0.49.0/plugin/skills/qwen-txt2img/SKILL.md and https://huggingface.co/wikeeyang/real-qwen-image-v2
- FLUX.2 klein steps/CFG: https://huggingface.co/QuantFunc/Klein-4B-Series and https://huggingface.co/pearsonkyle/carddeframe-klein4b
- Juggernaut XL v9: https://huggingface.co/RunDiffusion/Juggernaut-XL-v9
- Animagine XL 3.1: https://huggingface.co/cagliostrolab/animagine-xl-3.1
- Upscaler licences: https://huggingface.co/easygoing0114/AI_upscalers
- Upscaler filenames in Draw Things: https://skills.sh/wyattowalsh/agents/draw-thing
