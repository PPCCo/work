# FLUX.2 Klein 4B + draw-things-cli — Agent Reference

Consumer: AI agent / recommendation engine. Style: terse, machine-oriented.
Target: MacBook Pro M4 (12-core, 48 GB), `flux_2_klein_4b_q8p.ckpt`, `draw-things-cli generate`.
Verified against: `drawthingsai/draw-things-community` main (2026-10-15) + Hugging Face model cards. Installed CLI may be older: run `draw-things-cli generate --help`.

Tags: **[V]** verified from source/model card · **[H]** heuristic, A/B test on a fixed seed · **[U]** unverified.

---

## 0. Corrections to the template command (read first)

| Template item | Status | Fix |
|---|---|---|
| JSON key style | Keys are **camelCase**, merged by plain dict-override; unknown keys are ignored without error [V] | `guidanceScale`, `upscalerScaleFactor`, `resolutionDependentShift`. Never `guidance_scale`. |
| `"sampler": 0` (DPM++ 2M Karras) | Legacy SD/SDXL sampler | Use `16` (DDIM Trailing), Draw Things' own default for Klein [V]. |
| `--steps 28 --cfg 5.5` | Wrong for the model in use | `flux_2_klein_4b_f16` has no "base" in its name, so it is the **step-distilled** model: steps 4–8, cfg 1.0 [V]. 28 steps / cfg 4–5 suits only `flux_2_klein_base_4b_*` (§2.1). |
| LoRA `.ckpt` names | Placeholders | Real names come from conversion (§3). |
| `--output '~/...'` | Works: CLI expands `~` [V] | Run `mkdir -p ~/Dev/t2` first. |

Precedence [V]: model recommended settings < `--config-json` < explicit flags (`--steps --cfg --width --height --seed --strength`) < `--negative-prompt`.
Flags that exist [V]: `--prompt --prompt-file --negative-prompt --steps --cfg --width --height --strength --seed --image(repeatable) --output --models-dir --config-json --config-file --[no-]download-missing --offline`. Width/height must be multiples of 64.

---

## 1. Model variants (decide first)

| Variant | File pattern | Steps | CFG | Sampler | Shift | Use |
|---|---|---|---|---|---|---|
| **Distilled 4B** (user's) | `flux_2_klein_4b_{f16,q8p,q6p,i8x}.ckpt` | **4** (use 4–8, ≤12 [H]) | **1** | 16 | 3, `resolutionDependentShift:false` | Fast default; best with LoRAs per BFL [V] |
| **Base 4B** | `flux_2_klein_base_4b_{q8p,q6p,i8x}.ckpt` | **30** (20–50) | **4** | 16 | `resolutionDependentShift:true` | More diversity, LoRA training, strong CFG control |

Draw Things defaults above are from its shipped `configs.json` [V]. Distilled: CFG>1 is unneeded and wastes compute; the plain `--negative-prompt` has no effect at CFG 1 [H]. BFL card: distilled example = 4 steps, guidance 1.0, Apache-2.0 [V].
Klein = text-to-image + edit/reference model (`modifier: kontext`), 1024² default, Qwen3-4B text encoder, **no prompt upsampling** → prompts must carry all detail [V]. Text rendering is unreliable [V].

---

## 2. Config reference

### 2.1 Minimal JSON shapes (merge onto recommended settings)
```json
{"sampler":16,"shift":3,"resolutionDependentShift":false}
```
Distilled. Add as needed:
```json
{"upscaler":"realesrgan_x2plus_f16.ckpt","upscalerScaleFactor":2,
 "loras":[{"file":"NAME_lora_f16.ckpt","weight":0.85,"mode":"all","version":"flux2_4b"}]}
```
Base: `{"sampler":16,"resolutionDependentShift":true}` + `--steps 30 --cfg 4`.

### 2.2 Other keys worth knowing [V keys exist; values H]
`seed`, `strength` (img2img), `hiresFix`/`hiresFixWidth`/`hiresFixHeight`/`hiresFixStrength` (Klein spec has `hiresFixScale 24` → two-pass alternative to upscaler), `tiledDecoding` (VRAM relief for >1.5 MP), `batchCount`, `sharpness`, `colorCalibration` (`"none"|"lab"`), `upscalerScaleFactor` (`2|4`, `0` = model native).

### 2.3 Sampler IDs (`"sampler": N`) [V]
| N | Name | N | Name |
|---|---|---|---|
| 0 | DPM++ 2M Karras | 10 | **Euler A Trailing** |
| 1 | Euler A | 11 | DPM++ SDE Trailing |
| 2 | DDIM | 12 | DPM++ 2M AYS |
| 3 | PLMS | 13 | Euler A AYS |
| 4 | DPM++ SDE Karras | 14 | DPM++ SDE AYS |
| 5 | UniPC | 15 | **DPM++ 2M Trailing** |
| 6 | LCM | 16 | **DDIM Trailing** ← default |
| 7 | Euler A Substep | 17 | UniPC Trailing |
| 8 | DPM++ SDE Substep | 18 | UniPC AYS |
| 9 | TCD | 19 | TCD Trailing |

Klein picks [H except 16]: **16** default for everything · **10** softer/painterly, more seed variety · **15** crisper detail, good with Base 20–30 steps · **11** organic texture (photo) · **17** alt if LoRA output is unstable. Avoid 0–9 (Karras/legacy SD-era) on this flow model. 12/13/14/18 (AYS) are SD-tuned: [U].
Rule: change **one** variable per A/B; same seed.

### 2.4 Resolution
Multiples of 64. Native 1024². Generate ≤ ~1.3 MP, then upscale. Portrait print page: 768×1024 (3:4). Square: 1024×1024. Wide spread: 1024×768 or 1280×768.
Upscale output size = `width × upscalerScaleFactor`. 768×1024 ×4 = 3072×4096 ≈ 8.5×11 in @ ~360 dpi.

---

## 3. LoRAs

### 3.1 Compatibility rules [V]
- Klein **4B** LoRAs only (`flux2_4b`). **9B / FLUX.2-dev / FLUX.1 / SDXL LoRAs do not load on 4B.** A LoRA is dropped silently if version ≠ base version.
- LoRAs trained on **base 4B** also load on **distilled 4B**; BFL says distilled "typically gives better results" [V].
- `draw-things-cli` loads **only Draw Things `.ckpt` LoRAs** (`*_lora_f16.ckpt` in the Models dir). Raw `.safetensors` is ignored (zero pixel diff in third-party test) [V]. Convert first (§3.4).
- For an unregistered `.ckpt`, add `"version":"flux2_4b"` to its `loras[]` entry [V]. Harmless when registered.
- Weight range: −1.5…2.5 typical; use 0.6–1.0; stack ≤ 2 LoRAs, summed weight ≤ ~1.5 [H].
- Trigger word: put **first** in the prompt.

### 3.2 Self-train a LoRA (native CLI) [V flags; values H]
Best route for coloring-book line style, mandala style, house storybook style. Dataset = images + same-name `.txt` captions. Captions: trigger word first, **content only** (omit style words) [BFL]. 20–40 images. Train on **Base 4B**; use on distilled. Output auto-registers as `<output>_<step>_lora_f32.ckpt`.
```bash
draw-things-cli train lora --model flux_2_klein_base_4b_q6p.ckpt --dataset ~/Dev/datasets/kids_coloring \
  --output kids_coloring --name "Kids Coloring Lines" --steps 1500 --rank 32 --learning-rate 1e-4 \
  --save-every 250 --resolution 768 --dry-run
```
Drop `--dry-run` to train. BFL's best checkpoint was ~1500 of 3000 steps; later steps over-realistic [V]. Test every saved step at weight 0.8–1.0. Generate with `{"file":"kids_coloring_1500_lora_f32.ckpt","weight":0.9,"mode":"all"}`.

---

## 4. Upscalers [V names; usage notes H]
Set `"upscaler":"<file>"` + `"upscalerScaleFactor":2|4`. Applied after VAE decode. Files are Draw Things-format `.ckpt` served from Draw Things' CDN and **auto-downloaded on first use** (default `--download-missing`). **No Hugging Face repo with this format was found**; raw HF ESRGAN `.pth` files are not loadable by the CLI. Pre-fetch instead of using `hf`:
```bash
draw-things-cli generate --model flux_2_klein_4b_q8p.ckpt --prompt "a plain white square" \
  --width 512 --height 512 --steps 1 --cfg 1 --output '~/Dev/t2/_warm.png' \
  --config-json '{"upscaler":"realesrgan_x4plus_anime_6b_f16.ckpt","upscalerScaleFactor":4}'
```
(Repeat per file.)

| File (`upscaler`) | Native | Best for | Caveat |
|---|---|---|---|
| `realesrgan_x4plus_anime_6b_f16.ckpt` | 4× | **Line art, coloring pages, anime, flat vector** | Threshold lines after (§5.4) |
| `realesrgan_x2plus_f16.ckpt` | 2× | **Sketch, painting, photo** gentle 2× | – |
| `realesrgan_x4plus_anime_6b_f16.ckpt` | 4× | General photo/real | Can smooth texture |
| `remacri_4x_f16.ckpt` | 4× | **Painting, photo, film grain** natural texture | – |
| `4x_ultrasharp_f16.ckpt` | 4× | Mandala fine detail, architecture, 3D | Ringing/over-sharpen on skin |
| `esrgan_4x_universal_upscaler_v2_sharp_f16.ckpt` | 4× | Sharp general illustration | Halos on thin lines |

Rules [H]: factor 2 by default (4× of 1024² = 16 MP; heavy). 4× only for print of 768×1024 line art. Never upscale a rough draft: lock composition at 512–768 / 4 steps first. Don't stack `upscaler` + `hiresFix`.
Optional: SeedVR2 3B (`seedvr2_3b_q8p.ckpt`) exists as a restoration model in Draw Things; CLI use as an upscaler is [U].

---

## 5. Prompting Klein without a negative prompt

Klein has no prompt upsampling → write 40–120 words, concrete, positive only. [V: BFL "write detailed, descriptive prompts"; H: length]

### 5.1 Slot template (front-load what matters)
`[trigger] + [subject + count] + [action/pose] + [setting] + [medium/technique] + [palette] + [lighting] + [composition/framing] + [finish constraints]`

### 5.2 Rules
1. **Say what IS present, not what is absent.** Convert each wanted "no X" into the positive state that excludes it (§5.3).
2. **Medium words beat quality words.** "gouache, visible paper grain" > "masterpiece, 8k" [H].
3. **Exact colors with hex codes** — BFL-documented: `#E63946` [V]. Use for flat/kids/brand palettes.
4. **Structured JSON prompt** for multi-element scenes (BFL-documented keys: subject, background, lighting, style, camera angle, composition) [V]. Pass via `--prompt-file`.
5. **Specify line weight and fill state** for line art: "very thick bold uniform outlines", "closed contours", "empty white interior".
6. **Age is conveyed by visual complexity, not by the phrase "for a 4-year-old".** Describe shape count, line weight, proportions, palette (§6.1) [H].
7. **Camera/lens words only for photography.** They push non-photo styles toward realism [V: DeverStyle note].
8. **Text in image: avoid.** Ask for "wordless", add type in layout software. If unavoidable: ≤3 uppercase words in quotes; expect errors [V].
9. **One hero subject per prompt** for kids' pages; counts ≤5 are reliable [H].
10. **Reserve space** for typography: "empty sky area at top for the title" [H].
11. **LoRA active →** trigger first; drop style words that fight it; same weight sweep (0.6/0.8/1.0) on one seed.
12. **Iterate cheaply:** 8 seeds at 512×512 / 4 steps → pick → re-render at final size with same seed and (if wanted) 6–8 steps → upscale. [H]
13. **Fix, don't pile on:** if a defect appears, rewrite the offending clause positively, not append more adjectives.
14. **Avoid trademarked/studio/artist names**; use descriptors ("stylized 3D animated feature-film look").

### 5.3 Negative → positive rewrite table
| Wanted effect | Positive phrasing |
|---|---|
| no color / no gray / no shading | `pure black outlines on pure white paper, uncolored, flat, empty white interiors` |
| no background clutter | `isolated on a seamless pure white background` |
| no text / watermark | `wordless illustration` (and omit signage, books with titles, posters) |
| no blur | `tack-sharp focus, crisp edges` |
| no bad hands | `hands tucked in pockets` / `paws hidden behind the back` / `holding a basket with both hands, fingers curled around the handle` |
| not scary (kids) | `gentle friendly smiling expression, warm soft light, rounded shapes` |
| not photorealistic | `flat 2D shapes, hand-drawn look, visible brush or pencil marks` |
| no overlapping lines (coloring) | `every shape fully enclosed by a single continuous outline, generous spacing between elements` |
| no empty space (mandala) | `pattern fills the entire frame edge to edge` |
| not oversaturated | `muted, desaturated earthy palette` |

### 5.4 Coloring-page post-process (clean 1-bit lines after upscale) [H]
```bash
magick in.png -colorspace Gray -level 15%,85% -threshold 60% out.png   # brew install imagemagick
```
Use for kids/adult coloring pages only. Raise threshold % for thicker lines, lower for thinner.

---

## 6. Age & genre specification

### 6.1 Age profiles (visual spec the prompt must encode) [H]
| Audience | Subject | Shapes/detail | Line (coloring) | Palette (illustration) | Tone |
|---|---|---|---|---|---|
| 0–3 board book | 1 hero, centered | ≤10 big shapes | very thick bold, ~4 mm at print | 3–4 primaries, flat, cream bg | calm, friendly |
| 3–5 preschool | 1–2 subjects | simple scene, 2–3 props | very thick/thick, closed shapes | bright, saturated, flat/soft | cheerful |
| 6–8 early reader | hero + sidekick | scene w/ narrative props | medium (~2 mm) | warm, expressive, gouache/watercolor | story-driven |
| 9–12 middle grade | dynamic poses, depth | richer detail, perspective | medium-fine | moodier, tonal range | adventure OK |
| 13–17 teen | realistic proportions | high detail, editorial cleanliness | fine | muted/sophisticated | mature-appropriate, no gore |
| Adult | any | dense, intricate | fine (~0.3–0.6 mm) | any | any legal |

### 6.2 Preset matrix (A = distilled `flux_2_klein_4b_f16`; B = Base 4B)
Sampler default **[16]**; "alt" = A/B candidate [H]. Steps/cfg: A → `steps / 1.0`; B → `steps / cfg`.

| Preset ID | Size | A steps | B steps/cfg | Alt sampler | Upscaler (factor) | LoRA |
|---|---|---|---|---|---|---|
| `coloring_kids_0-5` | 768×1024 | 4 | 28 / 4.0 | – | anime6b (4) print / none | self-trained |
| `coloring_kids_6-9` | 768×1024 | 6 | 30 / 4.0 | – | anime6b (4) print | self-trained |
| `coloring_teen_adult` | 1024×1024 | 8 | 36 / 4.5 | 15 | anime6b (2) or ultrasharp (2) | self-trained |
| `mandala_adult` | 1024×1024 | 8 | 36 / 4.5 | 15 | ultrasharp (2) | self-trained |
| `picture_book_0-5` | 1024×768 | 4–6 | 28 / 4.0 | 10 | none / realesrgan_x2plus (2) | – |
| `picture_book_6-9` | 1024×768 | 6–8 | 30 / 4.0 | 10 | realesrgan_x2plus (2) | `light_fantasy` if fantasy |
| `middle_grade_cover` | 768×1024 | 8 | 30 / 4.0 | – | remacri (2) | `vintage_book_cover` |
| `nonfiction_kids_8-12` | 1024×768 | 6–8 | 30 / 4.0 | 15 | esrgan_universal_sharp (2) | – |
| `nonfiction_teen_13-17` | 1280×768 | 8 | 32 / 4.0 | 15 | ultrasharp (2) | – |
| `sketch_pencil_ink` | 768×1024 | 8 | 30 / 4.0 | 10 | realesrgan_x2plus (2) | – |
| `oil_painting` | 1024×768 | 8 | 32 / 4.0 | 10 | remacri (2) | – |
| `watercolor` | 1024×768 | 6–8 | 30 / 3.5 | 10 | realesrgan_x2plus (2) | – |
| `anime_2d` | 768×1024 | 6 | 28 / 4.0 | – | anime6b (2) | – |
| `render_3d_stylized` | 1024×1024 | 8 | 30 / 4.0 | 15 | ultrasharp (2) | – |
| `digital_concept_art` | 1280×768 | 8 | 32 / 4.0 | 15 | remacri (2) | – |
| `photo_portrait` | 768×1024 | 8 | 32 / 4.0 | 11 | remacri (2) | – |
| `photo_landscape_real` | 1280×768 | 8 | 32 / 4.0 | 15 | remacri (2) | – |
| `character_sheet` | 1024×1024 | 8 | n/a | – | none | `spritesheet` @1.1 |

If a preset lists a self-trained LoRA and none exists: run it prompt-only (examples below do), recommend training (§3.5) when the user repeats the same style ≥3 times.

---

## 7. Executable examples (distilled `flux_2_klein_4b_q8p.ckpt` unless stated)

Prereq: `mkdir -p ~/Dev/t2`. Settings are starting points [H]; sampler 16 is the verified default. Each "Why" is the rationale the engine can reuse.

### E01 · `coloring_kids_0-5` — toddler coloring page (print)
```bash
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--output '~/Dev/t2/klein_coloring_toddler_elephant.png' \
--prompt "childrens coloring book page for toddlers, one big friendly elephant waving its trunk, extremely simple rounded shapes, ten large shapes in total, very thick bold black outlines of uniform weight, large open white areas to color, pure white background, black line art only on white paper" \
--width 768 --height 1024 --steps 4 --cfg 1.0 \
--config-json '{
"sampler": 16,
"shift": 3,
"resolutionDependentShift": false,
"upscaler": "realesrgan_x4plus_anime_6b_f16.ckpt",
"upscalerScaleFactor": 4
}'
```
Why: 4 steps suffice for 1 simple subject. Shape-count + "very thick bold" encode age. Anime-6b 4× keeps hard line edges; output 3072×4096 ≈ US Letter @360 dpi.

### E02 · `coloring_kids_6-9` — early-reader scene coloring page
```bash
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--output '~/Dev/t2/klein_coloring_kids_picnic.png' \
--prompt "childrens coloring book page, a smiling fox and a rabbit having a picnic under an oak tree, a basket of apples, a checkered blanket, a few flowers and two clouds, medium-thick clean black outlines, every shape fully enclosed by one continuous line, generous spacing between elements, cheerful storybook proportions, pure white background, black line art on white paper" \
--width 768 --height 1024 --steps 6 --cfg 1.0 \
--config-json '{
"sampler": 16,
"shift": 3,
"resolutionDependentShift": false,
"upscaler": "realesrgan_x4plus_anime_6b_f16.ckpt",
"upscalerScaleFactor": 2
}'
```
Why: 2 characters + named props gives narrative detail. "Fully enclosed" + "generous spacing" replace the missing negative prompt for gaps and tangles. Factor 2 is enough for screen/light print.

### E03 · `coloring_teen_adult` — intricate adult coloring page
```bash
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--output '~/Dev/t2/klein_coloring_adult_owl.png' \
--prompt "intricate adult coloring book page, mystical owl perched on a crescent moon, feathers composed of detailed mandala patterns, stars and floral ornaments filling the frame, fine thin uniform black linework, dense zentangle detail, every shape fully enclosed, pure white background, black ink line art only, high contrast" \
--width 1024 --height 1024 --steps 8 --cfg 1.0 \
--config-json '{
"sampler": 16,
"shift": 3,
"resolutionDependentShift": false,
"upscaler": "realesrgan_x4plus_anime_6b_f16.ckpt",
"upscalerScaleFactor": 2
}'
```
Why: 8 steps resolve fine detail; "fine thin uniform" sets line weight; "fills the frame" avoids empty areas. Compare sampler 15 on the same seed.

### E04 · `mandala_adult` — mandala
```bash
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--output '~/Dev/t2/klein_mandala_lotus.png' \
--prompt "circular mandala coloring page, perfect eight-fold radial symmetry, concentric rings of lotus petals, paisley, geometric lattice and fine dotwork, crisp black lines of even weight, centered on a pure white square background, black and white line art, every shape fully enclosed, pattern fills the frame edge to edge" \
--width 1024 --height 1024 --steps 8 --cfg 1.0 \
--config-json '{
"sampler": 15,
"shift": 3,
"resolutionDependentShift": false,
"upscaler": "4x_ultrasharp_f16.ckpt",
"upscalerScaleFactor": 2
}'
```
Why: symmetry is stated numerically (eight-fold). Sampler 15 [alt] for crisper repeating detail; UltraSharp preserves hairlines (re-threshold with §5.4).

### E05 · `picture_book_0-5` — watercolor picture book
```bash
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--output '~/Dev/t2/klein_picturebook_bear_puddle.png' \
--prompt "childrens picture book illustration, a small brown bear in a yellow raincoat splashing in a puddle on a village lane, soft watercolor and gouache texture, warm muted palette of ochre, sage green and dusty blue, gentle morning light, visible paper grain, loose ink outlines, wide shot with empty space at the top for text, wholesome and cozy" \
--width 1024 --height 768 --steps 6 --cfg 1.0 \
--config-json '{
"sampler": 10,
"shift": 3,
"resolutionDependentShift": false,
"upscaler": "realesrgan_x2plus_f16.ckpt",
"upscalerScaleFactor": 2
}'
```
Why: medium + palette words fix the look; "empty space at the top" reserves text area. Sampler 10 [alt] gives softer washes. x2plus keeps paper grain.

### E06 · `picture_book_6-9` — fantasy storybook with LoRA
```bash
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--output '~/Dev/t2/klein_storybook_dragon_library.png' \
--prompt "light_fantasy, a young girl and a tiny dragon reading a book together in a castle library, luminous golden light through tall windows, vibrant jewel colors, painterly brushwork, whimsical storybook composition, wide framing" \
--width 768 --height 1024 --steps 8 --cfg 1.0 \
--config-json '{
"sampler": 16,
"shift": 3,
"resolutionDependentShift": false,
"loras": [
    {"file": "light_fantasy_lora_f16.ckpt", "weight": 0.85, "mode": "all", "version": "flux2_4b"}
  ],
  "upscaler": "realesrgan_x2plus_f16.ckpt",
  "upscalerScaleFactor": 2
}'
```
Why: trigger first, content-only prompt after (LoRA supplies style). Trained at 512², so stay ≤768 wide. LoRA authored on base, applied to distilled per BFL. Sweep weight 0.6/0.85/1.0.

### E07 · `picture_book_0-5` — board book, flat hex palette
```bash
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--output '~/Dev/t2/klein_boardbook_duck_ball.png' \
--prompt "board book illustration for babies and toddlers, one smiling yellow duck next to one red ball, flat vector shapes, thick rounded forms, colors #E63946 red, #FFD166 yellow and #118AB2 blue only, solid pale cream background #FFF8E7, centered composition, matte flat color with smooth uniform surfaces" \
--width 1024 --height 1024 --steps 4 --cfg 1.0 \
--config-json '{
"sampler": 16,
"shift": 3,
"resolutionDependentShift": false
}'
```
Why: hex codes (BFL-documented) lock a limited palette; 2 objects only; 4 steps are enough for flat art.

### E08 · `middle_grade_cover` — vintage adventure cover art with LoRA
```bash
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--output '~/Dev/t2/klein_cover_island_lighthouse.png' \
--prompt "book cover, vintage adventure novel illustration of two kids and a dog in a rowboat approaching a misty island with a lighthouse, 1950s gouache poster style, limited palette of teal, cream and orange, bold simple shapes, wordless artwork with an empty sky area at the top reserved for the title" \
--width 768 --height 1024 --steps 8 --cfg 1.0 \
--config-json '{
"sampler": 16,
"shift": 3,
"resolutionDependentShift": false,
"loras": [
    {"file": "vintage_book_cover_lora_f16.ckpt", "weight": 0.9, "mode": "all", "version": "flux2_4b"}
  ],
  "upscaler": "remacri_4x_f16.ckpt",
  "upscalerScaleFactor": 2
}'
```
Why: trigger `book cover` first. "Wordless" + reserved area because the LoRA tends to invent titles and text is unreliable. Remacri keeps print grain.

### E09 · `nonfiction_kids_8-12` — science diagram art
```bash
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--output '~/Dev/t2/klein_nonfiction_volcano.png' \
--prompt "educational illustration for a childrens science book, cross-section of a volcano showing the magma chamber, vertical conduit, crater and rising ash cloud, flat vector style with clean outlines, each rock layer a distinct bright color, simple friendly rendering, pure white background, wordless diagram" \
--width 1024 --height 768 --steps 6 --cfg 1.0 \
--config-json '{
"sampler": 15,
"shift": 3,
"resolutionDependentShift": false,
"upscaler": "esrgan_4x_universal_upscaler_v2_sharp_f16.ckpt",
"upscalerScaleFactor": 2
}'
```
Why: name each structure to be drawn; distinct layer colors aid learning. Add labels in layout software (text rendering is unreliable).

### E10 · `nonfiction_teen_13-17` — technical editorial illustration
```bash
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--output '~/Dev/t2/klein_nonfiction_jet_engine.png' \
--prompt "technical editorial illustration, exploded view of a modern turbofan jet engine, components separated along a central axis, precise vector line work with subtle gradients, muted slate and orange palette, soft shadow beneath, pure white background, wordless" \
--width 1280 --height 768 --steps 8 --cfg 1.0 \
--config-json '{
"sampler": 15,
"shift": 3,
"resolutionDependentShift": false,
"upscaler": "4x_ultrasharp_f16.ckpt",
"upscalerScaleFactor": 2
}'
```
Why: restrained palette and "precise vector" read as mature/infographic. UltraSharp suits hard-edged mechanical detail.

### E11 · `sketch_pencil_ink` — graphite portrait
```bash
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--output '~/Dev/t2/klein_sketch_pencil_fisherman.png' \
--prompt "graphite pencil sketch portrait of an elderly fisherman with a weathered face and woolen cap, loose cross-hatching, soft smudged shading, visible paper grain, off-white sketchbook paper, three-quarter view, unfinished edges fading into blank paper" \
--width 768 --height 1024 --steps 8 --cfg 1.0 \
--config-json '{
"sampler": 10,
"shift": 3,
"resolutionDependentShift": false,
"upscaler": "realesrgan_x2plus_f16.ckpt",
"upscalerScaleFactor": 2
}'
```
Why: technique words (cross-hatching, smudge, grain) carry the look; "fading into blank paper" gives the sketch vignette without a negative. x2plus is gentle on grain.

### E12 · `sketch_pencil_ink` — charcoal / ink-wash artistic sketch
```bash
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--output '~/Dev/t2/klein_sketch_ink_wash_street.png' \
--prompt "loose ink and charcoal sketch of an old European street at dusk, expressive pen hatching, diluted gray ink wash for shadows, rough broken contour lines, bare cream paper left untouched for the lit windows, sketchbook page, monochrome" \
--width 1024 --height 768 --steps 8 --cfg 1.0 \
--config-json '{
"sampler": 10,
"shift": 3,
"resolutionDependentShift": false,
"upscaler": "realesrgan_x2plus_f16.ckpt",
"upscalerScaleFactor": 2
}'
```
Why: "bare paper left untouched" is the positive form of "no fill". Monochrome stated explicitly.

### E13 · `oil_painting`
```bash
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--output '~/Dev/t2/klein_oil_stormy_cliff.png' \
--prompt "oil painting of a stormy sea cliff at golden hour, thick impasto brush strokes, palette knife highlights, rich cadmium and ultramarine pigments, visible canvas weave, dramatic chiaroscuro, romantic landscape, landscape format" \
--width 1024 --height 768 --steps 8 --cfg 1.0 \
--config-json '{
"sampler": 10,
"shift": 3,
"resolutionDependentShift": false,
"upscaler": "remacri_4x_f16.ckpt",
"upscalerScaleFactor": 2
}'
```
Why: physical-material vocabulary (impasto, knife, canvas weave) beats "painterly". Remacri keeps natural brush texture.

### E14 · `watercolor`
```bash
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--output '~/Dev/t2/klein_watercolor_venice.png' \
--prompt "loose watercolor painting of a Venetian canal at dawn, wet-on-wet washes bleeding into each other, granulating pigments, soft blooms, bare white paper left for highlights, muted blue and rose palette, cold-press paper texture" \
--width 1024 --height 768 --steps 6 --cfg 1.0 \
--config-json '{
"sampler": 10,
"shift": 3,
"resolutionDependentShift": false,
"upscaler": "realesrgan_x2plus_f16.ckpt",
"upscalerScaleFactor": 2
}'
```
Why: wet-on-wet + blooms + bare paper are watercolor-specific cues; fewer steps keeps washes soft.

### E15 · `anime_2d`
```bash
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--output '~/Dev/t2/klein_anime_swordswoman.png' \
--prompt "2D anime key visual, a silver-haired swordswoman on a rooftop at dusk, wind-blown hair and scarf, crisp cel shading, clean line art, vibrant sunset gradient sky in magenta and orange, dynamic low-angle composition, flat color blocks with sharp-edged shadow shapes" \
--width 768 --height 1024 --steps 6 --cfg 1.0 \
--config-json '{
"sampler": 16,
"shift": 3,
"resolutionDependentShift": false,
"upscaler": "realesrgan_x4plus_anime_6b_f16.ckpt",
"upscalerScaleFactor": 2
}'
```
Why: "cel shading", "flat color blocks", "sharp-edged shadow shapes" exclude painterly rendering positively. Anime-6b upscaler matches the style.

### E16 · `render_3d_stylized`
```bash
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--output '~/Dev/t2/klein_3d_fox_cub.png' \
--prompt "stylized 3D animated feature-film render of a curious fox cub in a mossy forest, soft fur with subsurface scattering, large expressive eyes, warm rim lighting, shallow depth of field, rounded appealing proportions, smooth clay-like shading, volumetric light rays" \
--width 1024 --height 1024 --steps 8 --cfg 1.0 \
--config-json '{
"sampler": 15,
"shift": 3,
"resolutionDependentShift": false,
"upscaler": "4x_ultrasharp_f16.ckpt",
"upscalerScaleFactor": 2
}'
```
Why: render-engine vocabulary (subsurface scattering, rim light, DOF) drives the 3D look; no studio names.

### E17 · `digital_concept_art`
```bash
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--output '~/Dev/t2/klein_concept_sky_city.png' \
--prompt "digital concept art of a floating sky-city at sunrise, layered atmospheric perspective, painterly brushwork, strong silhouette, warm and cool color contrast, cinematic wide composition, detailed architecture with glowing windows" \
--width 1280 --height 768 --steps 8 --cfg 1.0 \
--config-json '{
"sampler": 15,
"shift": 3,
"resolutionDependentShift": false,
"upscaler": "remacri_4x_f16.ckpt",
"upscalerScaleFactor": 2
}'
```
Why: concept-art cues are composition-level (silhouette, atmospheric perspective, temperature contrast). Wide size suits the subject.

### E18 · `photo_portrait`
```bash
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--output '~/Dev/t2/klein_photo_portrait_cafe.png' \
--prompt "photograph of a woman in her thirties laughing by a sunlit cafe window, 85mm lens at f/1.8, shallow depth of field, soft natural window light, Kodak Portra 400 film color, visible skin texture and fine pores, candid expression, warm tones" \
--width 768 --height 1024 --steps 8 --cfg 1.0 \
--config-json '{
"sampler": 11,
"shift": 3,
"resolutionDependentShift": false,
"upscaler": "remacri_4x_f16.ckpt",
"upscalerScaleFactor": 2
}'
```
Why: lens + light + film stock + skin texture are the realism levers (camera words are valid here only). Sampler 11 [alt] for organic texture. Avoid UltraSharp on skin.

### E19 · `photo_landscape_real`
```bash
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--output '~/Dev/t2/klein_photo_alpine_lake.png' \
--prompt "photorealistic landscape photograph of an alpine lake at sunrise, 24mm wide angle, polarizing filter, mist hovering above still water, pink light on snowy peaks, sharp foreground pebbles, deep depth of field, natural color grading" \
--width 1280 --height 768 --steps 8 --cfg 1.0 \
--config-json '{
"sampler": 15,
"shift": 3,
"resolutionDependentShift": false,
"upscaler": "remacri_4x_f16.ckpt",
"upscalerScaleFactor": 2
}'
```
Why: wide lens + deep focus + "natural color grading" prevents the over-processed look.

### E20 · `character_sheet` — LoRA for pose consistency
```bash
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--output '~/Dev/t2/klein_charsheet_hedgehog.png' \
--prompt "2x2 sprite sheet, a cheerful cartoon hedgehog in a blue scarf, four poses: standing, walking, jumping, waving, identical character design in every cell, flat colors, clean outlines, plain pale green background" \
--width 1024 --height 1024 --steps 8 --cfg 1.0 \
--config-json '{
"sampler": 16,
"shift": 3,
"resolutionDependentShift": false,
"loras": [
    {"file": "klein4b_spritesheet_lora_f16.ckpt", "weight": 1.1, "mode": "all", "version": "flux2_4b"}
  ]
}'
```
Why: author-recommended weight 1.1 and trigger phrase `2x2 sprite sheet`. Use the output as a pose reference for a kids' book cast.

### E21 · Base-variant example (30+ steps, real CFG)
```bash
draw-things-cli generate \
--model flux_2_klein_base_4b_q6p.ckpt \
--output '~/Dev/t2/klein_base_coloring_adult_fox.png' \
--prompt "intricate adult coloring book page, a fox curled around a sunflower, feathered tail made of leaf and paisley patterns, fine thin uniform black linework, dense floral background filling the frame, every shape fully enclosed, pure white background, black ink line art only" \
--width 1024 --height 1024 --steps 36 --cfg 4.5 \
--config-json '{
"sampler": 15,
"resolutionDependentShift": true,
"upscaler": "realesrgan_x4plus_anime_6b_f16.ckpt",
"upscalerScaleFactor": 2
}'
```
Why: Base needs steps 20–50 and cfg ~4 (Draw Things default 30 / 4.0); 4.5 tightens prompt adherence for dense line art. Sampler 15 [alt]; remove it to test 16.

### E22 · Photo → coloring page via reference image [U: behavior untested]
```bash
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--image ~/Dev/t2/input_photo.jpg \
--output '~/Dev/t2/klein_photo_to_coloring.png' \
--prompt "redraw this photo as a childrens coloring book page, simplified shapes, thick clean black outlines, every shape fully enclosed, pure white background, black line art only, uncolored" \
--width 768 --height 1024 --steps 8 --cfg 1.0 \
--config-json '{
"sampler": 16,
"shift": 3,
"resolutionDependentShift": false
}'
```
Why: Klein is an edit/reference model. Instruction-style prompt. If composition drifts, add `--strength 0.8` and compare.

### E23 · Structured JSON prompt via file (BFL-documented format)
```bash
cat > ~/Dev/t2/prompt_e23.json <<'EOF'
{
  "subject": "a ceramic coffee cup with steam on a rustic oak table",
  "background": "blurred warm kitchen with morning window light",
  "lighting": "soft side light from the left, gentle highlights on the glaze",
  "style": "clean commercial product photograph, natural color",
  "camera angle": "eye level, slightly off-center",
  "composition": "cup in the lower third, negative space on the right"
}
EOF
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--output '~/Dev/t2/klein_json_prompt_cup.png' \
--prompt-file ~/Dev/t2/prompt_e23.json \
--width 1024 --height 768 --steps 8 --cfg 1.0 \
--config-json '{
"sampler": 16,
"shift": 3,
"resolutionDependentShift": false
}'
```
Why: separates concerns so edits touch one field. Use for complex multi-element scenes or batch generation by templating one field.

### E24 · Seed sweep (draft loop before final render)
```bash
for s in 101 102 103 104 105 106 107 108; do
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--output "~/Dev/t2/sweep_${s}.png" \
--prompt "childrens picture book illustration, a small brown bear in a yellow raincoat splashing in a puddle, soft watercolor and gouache texture, warm muted palette" \
--width 512 --height 512 --steps 4 --cfg 1.0 --seed $s \
--config-json '{"sampler": 16, "shift": 3, "resolutionDependentShift": false}'
done
```
Why: 4-step 512² drafts are cheap. Pick the winner, then rerun with the **same seed**, final size, 6–8 steps, and upscaler. [H: composition can shift with size; re-check.]

---

## 8. Recommendation-engine logic

### 8.1 Inputs to resolve from the user (ask only for blockers; else default and state the assumption)
`genre` · `audience_age` · `output_medium` (screen | print | cover) · `variant` (distilled default; Base only if filename contains `base`) · `speed_vs_quality` · `style_lock_needed` (same look across many images?) · `has_loras` (check Models dir) · `text_needed` (→ plan layout-software overlay).

### 8.2 Decision order
1. **Variant:** filename has `base` → Base column (30 steps / cfg 4); else distilled (4–8 steps / cfg 1.0).
2. **Preset:** map genre+age to §6.2 row. Unknown genre → nearest row; use sampler 16.
3. **LoRA:**
   - A verified 4B LoRA fits (§3.3) **and** its converted `.ckpt` exists → use it (weight 0.85 start).
   - Else prompt-only. If the user needs a consistent house style across ≥ ~20 images → recommend §3.5 training.
   - Never load a 9B/dev/SDXL LoRA. Never exceed 2 LoRAs.
4. **Size/upscaler:** generate ≤ 1.3 MP; pick upscaler from §4 by medium; factor 2 unless 4× print of line art; skip upscaler for drafts.
5. **Prompt:** fill §5.1 slots; apply §5.3 rewrites; add age cues from §6.1; reserve text space if a cover.
6. **Iterate:** E24 sweep → one-variable A/B (sampler → steps → LoRA weight) on a fixed seed.
7. **Emit:** full command in the template format, `--config-json` with camelCase keys only, plus a one-line rationale.

### 8.3 Quick selectors
- Fast draft: steps 4, 512–768 px, no upscaler.
- Maximum detail on distilled: steps 8 (12 cap), sampler 15, upscaler ×2.
- Softer/painterly: sampler 10, steps 6.
- Strict line art: sampler 16, "fully enclosed" + line-weight words, anime-6b upscaler, §5.4 threshold.
- Prompt ignored/flat on distilled: shorten to one subject, steps +2, never raise CFG first.
- Need exact brand colors: hex codes (§5.2-3) or JSON prompt (E23).

### 8.4 Pre-flight checklist (agent must pass before emitting a command)
- [ ] Model file exists (`draw-things-cli models list --downloaded-only`).
- [ ] `--config-json` parses (valid JSON; no trailing commas); keys camelCase; **no `schedule_sampler`**.
- [ ] `sampler` ∈ {16,10,15,11,17} unless deliberately testing.
- [ ] width/height multiples of 64; final MP reasonable (≤ ~16 MP after upscale).
- [ ] Distilled → `--cfg 1.0`, steps ≤ 12. Base → steps 20–50, cfg 3.5–5.
- [ ] Every `loras[].file` is a converted `*_lora_*.ckpt` present in the Models dir; `version:"flux2_4b"`; weight 0.6–1.2; ≤ 2 LoRAs.
- [ ] Prompt: no negations of the form "no X"/"without X"; trigger word first if LoRA; no `"`, `$`, backtick, `!` (shell-unsafe inside double quotes).
- [ ] `~/Dev/t2` exists.

### 8.5 Failure → fix
| Symptom | Likely cause | Fix |
|---|---|---|
| LoRA has no effect | `.safetensors` not converted; version mismatch; wrong file name | Convert (§3.4); `version:"flux2_4b"`; `ls` Models dir; verify with same-seed A/B |
| Burnt/oversaturated colors | CFG > 1 on distilled | `--cfg 1.0` |
| Muddy/over-smoothed | steps too many on distilled, or too-strong LoRA | steps 6–8; LoRA weight −0.2 |
| Gray fills or shading in line art | style words missing | add "pure black outlines on pure white paper, uncolored, empty white interiors" |
| Broken/unclosed lines | too many elements | one subject, fewer props, "every shape fully enclosed", larger spacing |
| Fake text / title | cover or sign in prompt | "wordless", remove signage; overlay type in layout app |
| Extra limbs/hands | open hands in frame | hide hands or give a simple grip phrase (§5.3) |
| Photo looks plastic | no realism levers | lens, light, film stock, skin texture; sampler 11; Remacri not UltraSharp |
| Upscaled lines gray/soft | AA after ESRGAN | §5.4 threshold; anime-6b upscaler |
| Composition changes between draft and final | size changed | re-sweep at final aspect ratio; keep same aspect |
| `invalidConfigurationJSON` error | bad JSON or wrong value type | validate JSON; numbers unquoted; booleans `true/false` |
| Out-of-memory / slow | 16 MP upscale | factor 2; `"tiledDecoding": true` [H] |

### 8.6 Licensing notes
Klein 4B: Apache-2.0 (commercial OK) [V]. Klein 9B is non-commercial → another reason to avoid 9B artefacts. LoRA licenses vary ("other" = inherit Klein terms; penguinoh is CC BY-NC). Check per-LoRA before commercial book publishing. Kids' books: review every image for anatomy/content before print.

---

## 9. Sources
- Draw Things CLI/source: https://github.com/drawthingsai/draw-things-community (sampler enum `config.fbs`; `JSGenerationConfiguration`; `configs.json` Klein defaults; `UpscalerZoo`; `LoRAImporter`)
- LoRA conversion wrapper (third-party): https://github.com/vcspr/drawthings-lora-convert
- BFL Klein 4B: https://huggingface.co/black-forest-labs/FLUX.2-klein-4B · Base: https://huggingface.co/black-forest-labs/FLUX.2-klein-base-4B
- BFL LoRA guide: https://huggingface.co/blog/black-forest-labs/flux-2-klein-lora · prompting: https://docs.bfl.ml/flux_2/flux2_overview
- LoRAs: https://huggingface.co/giannisan/light-fantasy-flux2-klein-base-lora · https://huggingface.co/Norod78/flux2-klein-4b-base-lora-vintage-book-cover · https://huggingface.co/fal/flux-2-klein-4b-spritesheet-lora · https://huggingface.co/adirik/pixel-art-lora-flux.2-klein-4B · https://huggingface.co/easygoing0114/FLUX.2-klein-4B_clear
