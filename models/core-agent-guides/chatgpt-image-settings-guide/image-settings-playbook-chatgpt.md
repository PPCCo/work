# Draw Things CLI: image-generation settings playbook

Designed for a MacBook Pro M4 (12-core, 48 GB unified memory) using `draw-things-cli` with Qwen Image 2512, FLUX.2 Klein and the listed SDXL checkpoints. Settings are starting points, not guarantees; prompt, checkpoint version, LoRA and resolution change the result.

## Important CLI details

- Use valid JSON: `--config-json '{"sampler":10,"loras":[]}'`. The empty LoRA list is `[]`; `"loras": ''` is invalid JSON.
- In the currently published Draw Things schema the sampler is a numeric enum. Its values are listed below. Check the installed CLI after upgrades because numeric enum IDs can change.
- Draw Things exposes Karras/AYS/Trailing variants as **sampler choices**. Do not paste a ComfyUI-style `"scheduler":"karras"` field into these examples.
- The commands use `--cfg`, as in current Draw Things CLI examples. Check `draw-things-cli generate --help` if your installed build expects a different flag.
- Shell note: use `"$HOME/Dev/tmp/file.png"`, not `'~/Dev/tmp/file.png'` (the tilde does not expand inside single quotes).

Create the output directory once:

```bash
mkdir -p "$HOME/Dev/tmp"
```

## Sampler IDs

| ID | Draw Things sampler | Typical use |
|---:|---|---|
| 0 | DPM++ 2M Karras | Robust SDXL baseline; realistic photos |
| 1 | Euler A | Anime, stylized illustration, expressive variation |
| 2 | DDIM | Simple/legacy comparison |
| 3 | PLMS | Legacy compatibility; rarely a first choice |
| 4 | DPM++ SDE Karras | Alternative SDXL detail/texture comparison |
| 5 | UniPC | General sampler comparison |
| 6 | LCM | Only for compatible LCM model/LoRA workflows |
| 7 | Euler A Substep | Specialised comparison |
| 8 | DPM++ SDE Substep | Specialised comparison |
| 9 | TCD | Compatible TCD workflows |
| 10 | Euler A Trailing | Good starting point for Qwen 2512 and distilled FLUX.2 Klein in Draw Things |
| 11 | DPM++ SDE Trailing | Specialised comparison; can be slower |
| 12 | DPM++ 2M AYS | Alternative for detailed SDXL/illustration tests |
| 13 | Euler A AYS | Creative variation comparison |
| 14 | DPM++ SDE AYS | Advanced comparison |
| 15 | DPM++ 2M Trailing | Trailing-schedule comparison |
| 16 | DDIM Trailing | Trailing-schedule comparison |
| 17 | UniPC Trailing | Useful A/B test against Euler A Trailing on flow models |
| 18 | UniPC AYS | Advanced comparison |
| 19 | TCD Trailing | Compatible TCD workflows |

Numeric mapping comes from Draw Things' published `SamplerType` enum; names/order are not ComfyUI sampler IDs. [Source](https://raw.githubusercontent.com/drawthingsai/draw-things-community/main/Libraries/DataModels/Sources/config.fbs)

## Model-family baselines

| Model | Start here | Notes |
|---|---|---|
| `qwen_image_2512_bf16_q8p.ckpt` | 30-40 steps, CFG 4.0, Euler A Trailing (10), `shift: 1.0`, `resolutionDependentShift: true` | Strong general-purpose prompt following and book/cover concept art. Keep exact labels/text in layout software. |
| FLUX.2 Klein distilled 4B/9B | 4 steps, CFG 1.0, Euler A Trailing (10) | Distilled variants are designed around 4 steps and CFG 1.0. Do not boost steps/CFG as if it were a regular SDXL model. |
| FLUX.2 Klein Base | 30-50 steps, CFG about 4.0; start Euler A Trailing (10) and compare UniPC Trailing (17) | Base is not the distilled model. Verify exact local filename. |
| `juggernaut_xl_v9_f16.ckpt` | 30-40 steps, CFG 3-6, DPM++ 2M Karras (0) | Good for photorealism; lower CFG often looks more natural. The model card recommends 832x1216 portrait / 1216x832 landscape and advises starting with no negative prompt. |
| `juggernaut_xl_x_f16.ckpt` | 28-38 steps, CFG 4-6, DPM++ 2M Karras (0) | Treat as an empirical starting point; calibrate separately from v9. |
| `colorfulxl_v6.0_f16.ckpt` | 26-36 steps, CFG 5-6.2, Euler A (1) or DPM++ 2M Karras (0) | First try for vivid storybook/painterly illustration; these are calibration defaults rather than a verified official preset. |
| `animagine_xl_v3.1_f16.ckpt` | 22-29 steps, CFG 5-7, Euler A (1) | Anime-focused; good first try around 26 steps and CFG 6. Keep CLIP skip at default unless checkpoint-specific instructions say otherwise. |

FLUX.2's official repository differentiates distilled Klein (4-step, guidance-distilled) from Base (undistilled). [Official model overview](https://github.com/black-forest-labs/flux2). Juggernaut v9 and Animagine settings are based on their model cards ([Juggernaut](https://huggingface.co/KillerBohne420/Juggernaut-XL-v9), [Animagine](https://huggingface.co/cagliostrolab/animagine-xl-3.1)).

## Profiles by book genre and audience

| Use case | Preferred model | Steps / CFG / sampler | Prompt strategy | Critical checks |
|---|---|---|---|---|
| Preschool picture books (2-5) | Qwen 2512 or ColorfulXL | Qwen: 28-36 / 3.8-4.8 / Euler A Trailing (10). ColorfulXL: 26-34 / 5-6 / Euler A (1). | One large focal subject, rounded forms, simple palette, warm mood, uncluttered background. | Make the action instantly readable; reserve negative space for text. |
| Children’s storybooks (6-9) | ColorfulXL or Qwen | ColorfulXL: 26-36 / 5-6.5 / Euler A (1). Qwen: 32-40 / 4-4.8 / Euler A Trailing (10). | Describe foreground/midground/background, action, mood and palette. | Maintain character design/seed/ratio across pages; seed alone does not guarantee identity. |
| Non-fiction and educational books (8-16) | Qwen 2512 | 32-44 / 3.8-5 / Euler A Trailing (10) | Request label-free, clean, separated parts with space for callouts. | Add labels/arrows with layout software; independently fact-check anatomy/science. |
| Kids/teen coloring pages | Qwen 2512 | 28-38 / 3.8-5 / Euler A Trailing (10); test DPM++ 2M AYS (12) | Pure black closed outlines on pure white; uniform stroke; big colourable regions. | Reject gray fills, shadows, gradients, hatching, broken lines and stray marks. |
| Adult mandala coloring | Qwen 2512 | 30-42 / 4-5.2 / DPM++ 2M AYS (12); compare 10 or 17 | Radial symmetry, concentric rings, repeating motifs, closed compartments. | For perfect geometry use SVG/vector tooling; diffusion may break symmetry or line closure. |
| Pencil/engraving/architectural sketch | Juggernaut v9 or XL X | 28-38 / 3.8-5.5 / DPM++ 2M Karras (0); compare 12 | Name the medium and stroke behavior (graphite, cross-hatching, etching, paper grain). | Sketches intentionally contain tone; use the coloring-page profile if white fill is required. |
| Watercolor/oil/gouache | ColorfulXL or Qwen | 28-40 / 4.8-6.2 / Euler A (1) or DPM++ 2M Karras (0) | Watercolor: transparent washes, granulation, soft lost edges. Oil: impasto, glazing, visible brush marks. | State one medium clearly; avoid aggressive sharpening on upscale. |
| 2D anime/manga | Animagine XL 3.1 | 22-29 / 5-7 / Euler A (1) | Use quality tags, pose, camera angle, expression, clothes, setting and lighting. | Short, defect-focused negative prompt; leave CLIP skip at default initially. |
| Digital cartoon / stylized 3D | ColorfulXL or Juggernaut XL X | 26-36 / 4.8-6.5 / Euler A (1) or DPM++ 2M Karras (0) | Explicitly choose 2D graphic vs 3D; specify material, key/fill/rim lighting and camera. | For young audiences keep silhouette, face and action readable; control background clutter. |
| Photorealism / photography | Juggernaut XL v9 | 30-40 / 3-6 / DPM++ 2M Karras (0) | Describe shot type, focal-length feel, light, focus plane, realistic textures and colour science. | Start with no negative prompt; lower CFG for natural skin/contrast. |
| Book cover / title art | Qwen 2512 | 32-44 / 3.8-5.2 / Euler A Trailing (10) | State title safe zone, focal-point placement, reading direction and trim ratio; ask for no words. | Add title/author/type after generation; check bleed/safe margins at exact trim. |

Audience age changes subject complexity, mood and visual density—not CFG by itself.

## Executable example commands

The examples below use filenames from your stated model list. FLUX.2 Klein's filename varies by quantization; the example uses a common Draw Things 4B quantized filename. If your local file is named differently, replace only that filename with the exact installed file. The command syntax/config structure stays the same.

### 1. Preschool picture-book illustration — Qwen

```bash
draw-things-cli generate \
  --model qwen_image_2512_bf16_q8p.ckpt \
  --output "$HOME/Dev/tmp/preschool_fox.png" \
  --prompt "A charming picture-book illustration for preschool children: a small orange fox in blue overalls carefully waters a sunflower in a little garden, rounded friendly shapes, expressive face, warm pastel palette, simple clear composition, soft gouache texture, generous open space, no lettering." \
  --negative-prompt "scary expression, cluttered background, text, watermark, blurry, malformed hands" \
  --width 1024 --height 1024 --steps 32 --cfg 4.0 \
  --config-json '{"sampler":10,"shift":1.0,"resolutionDependentShift":true,"loras":[]}'
```
**Why:** Qwen’s CFG 4 baseline and Euler A Trailing (10) are a good starting point for narrative prompt adherence; 32 steps adds detail without overcommitting compute.

### 2. Teen science-book illustration — label-free, Qwen

```bash
draw-things-cli generate \
  --model qwen_image_2512_bf16_q8p.ckpt \
  --output "$HOME/Dev/tmp/plant_science.png" \
  --prompt "A clean educational illustration for a teen science book showing a large cutaway model of a flowering plant, roots, stem, leaves and flower clearly separated and anatomically plausible, simple light background, crisp colors, textbook-style clarity, leave open spaces for later labels, no text or arrows." \
  --negative-prompt "illegible text, random letters, watermark, decorative clutter, incorrect extra parts, blurry" \
  --width 1024 --height 768 --steps 38 --cfg 4.0 \
  --config-json '{"sampler":10,"shift":1.0,"resolutionDependentShift":true,"loras":[]}'
```
**Why:** More steps than a quick draft improve separation/detail; labels are deliberately added later for factual and typographic control.

### 3. Children’s coloring page — clear closed outlines

```bash
draw-things-cli generate \
  --model qwen_image_2512_bf16_q8p.ckpt \
  --output "$HOME/Dev/tmp/kids_coloring_dragon.png" \
  --prompt "A printable children's coloring-book page of a cheerful baby dragon reading a book under a tree, pure black clean uniform outlines on a pure white background, closed shapes, simple bold contours, large open spaces to colour, minimal background details, no gray, no shading, no hatching, no text." \
  --negative-prompt "colour, gray fill, grayscale shading, gradients, shadows, hatching, crosshatching, stippling, pencil texture, sketch, gray background, text, watermark, broken outlines, messy lines" \
  --width 768 --height 1024 --steps 32 --cfg 4.2 \
  --config-json '{"sampler":10,"shift":1.0,"resolutionDependentShift":true,"loras":[]}'
```
**Why:** Portrait page ratio; line-art constraints are explicit. Inspect closed regions; diffusion output may still need cleanup/vectorization.

### 4. Adult mandala — intricate monochrome line art

```bash
draw-things-cli generate \
  --model qwen_image_2512_bf16_q8p.ckpt \
  --output "$HOME/Dev/tmp/adult_mandala.png" \
  --prompt "Intricate adult mandala coloring page, centered radial composition with eight concentric rings of repeating lotus petals, paisley leaves, tiny geometric rosettes and balanced ornamental filigree, clean uniform black outlines, pure white background, every region closed and colourable, no gray, no fill, no shading, no text." \
  --negative-prompt "color, gray fill, grayscale, shadows, gradients, pencil shading, crosshatching, stippling, open line ends, asymmetry, lettering, watermark, dirty paper texture" \
  --width 1024 --height 1024 --steps 36 --cfg 4.5 \
  --config-json '{"sampler":12,"shift":1.0,"resolutionDependentShift":true,"loras":[]}'
```
**Why:** DPM++ 2M AYS (12) is an alternative line-detail schedule worth comparing with Euler A Trailing (10). Exact radial symmetry still needs inspection.

### 5. 2D anime character — Animagine XL 3.1

```bash
draw-things-cli generate \
  --model animagine_xl_v3.1_f16.ckpt \
  --output "$HOME/Dev/tmp/anime_cartographer.png" \
  --prompt "masterpiece, best quality, very aesthetic, 1girl, teen fantasy cartographer, full body, holding an open star map, expressive eyes, flowing navy cloak with gold constellations, clean 2D anime illustration, crisp line art, cel shading, moonlit observatory, vertical composition" \
  --negative-prompt "lowres, worst quality, low quality, jpeg artifacts, watermark, signature, extra digits, missing fingers, bad anatomy, text" \
  --width 832 --height 1216 --steps 26 --cfg 6.0 \
  --config-json '{"sampler":1,"loras":[]}'
```
**Why:** Animagine’s model card supports low-to-mid CFG around 5-7, fewer than 30 steps and Euler A (1).

### 6. Watercolor storybook scene — ColorfulXL

```bash
draw-things-cli generate \
  --model colorfulxl_v6.0_f16.ckpt \
  --output "$HOME/Dev/tmp/watercolor_fox.png" \
  --prompt "A luminous watercolor illustration for a nature storybook, a red fox standing in a misty meadow at dawn, transparent pigment washes, granulated greens, soft wet-on-wet background, a few crisp dry-brush details on the fox, warm paper-white highlights, restrained natural palette, no lettering." \
  --negative-prompt "plastic 3d look, vector flatness, text, watermark, overly smooth airbrush, oversharpened edges" \
  --width 1024 --height 1024 --steps 32 --cfg 5.6 \
  --config-json '{"sampler":1,"loras":[]}'
```
**Why:** ColorfulXL is a good experimental choice for vivid illustration; CFG 5.6 balances style and prompt adherence. Compare DPM++ 2M Karras (0) if textures look too chaotic.

### 7. Photorealistic wildlife image — Juggernaut XL v9

```bash
draw-things-cli generate \
  --model juggernaut_xl_v9_f16.ckpt \
  --output "$HOME/Dev/tmp/kookaburra_photo.png" \
  --prompt "Editorial wildlife photograph of a kookaburra perched on a weathered eucalyptus branch after rain, 200mm telephoto look, natural overcast light, lifelike feather detail, soft out-of-focus Australian bush background, accurate proportions, gentle contrast, natural colour science." \
  --width 832 --height 1216 --steps 35 --cfg 4.5 \
  --config-json '{"sampler":0,"loras":[]}'
```
**Why:** DPM++ 2M Karras (0), 35 steps and CFG 4.5 align with a realism-first SDXL baseline. No negative prompt is intentional for the first pass.

### 8. Quick FLUX.2 Klein distilled draft

```bash
draw-things-cli generate \
  --model flux_2_klein_4b_q6p.ckpt \
  --output "$HOME/Dev/tmp/klein_robot_librarian.png" \
  --prompt "A tiny friendly robot librarian carries an oversized stack of books through a sunlit children's library, rounded shapes, felt and painted-metal materials, warm morning light, clear central composition, colourful storybook mood, no text." \
  --width 1024 --height 1024 --steps 4 --cfg 1.0 \
  --config-json '{"sampler":10,"loras":[]}'
```
**Why:** Distilled FLUX.2 Klein is designed around 4 steps and guidance 1.0. If your model filename includes `base`, do not use these settings; start with the Base profile instead.

### 9. Pencil sketch — Juggernaut XL v9

```bash
draw-things-cli generate \
  --model juggernaut_xl_v9_f16.ckpt \
  --output "$HOME/Dev/tmp/graphite_reading_chair.png" \
  --prompt "A finely observed graphite pencil drawing for an art book: an old reading chair beside a tall window, confident contour lines, subtle cross-hatched shadows, visible paper grain, delicate value range, museum-study sketch, monochrome graphite only." \
  --negative-prompt "full colour, glossy 3d render, neon colours, text, watermark, blurry" \
  --width 832 --height 1216 --steps 32 --cfg 4.5 \
  --config-json '{"sampler":0,"loras":[]}'
```
**Why:** The prompt deliberately asks for graphite tone and cross-hatching; do not reuse this negative/positive prompt pair for a coloring page.

## Upscaling and print workflow

1. Generate at the target composition/aspect ratio. For the M4/48 GB system, start around 1024 square or a 832x1216 portrait and inspect before raising resolution.
2. Once a seed/composition is approved, try `--hires-fix` or the installed upscaler. For photo/paint workflows, aim for roughly 1.5x and second-pass denoise around 0.25-0.35. Lower denoise preserves geometry.
3. For coloring pages/mandalas, avoid creative upscalers that add gray texture. Use non-generative resampling, threshold cleanup or vectorization and verify closed line regions.
4. Use the exact upscaler filename listed by your installed `draw-things-cli generate --help`. Names differ by install/version; possible candidates to check include `4x_NMKD-Siax_200k` and `4x_foolhardy_Remacri`.
5. Add all page typography, scientific labels, arrows, folios, trim/bleed and safe margins in a layout/vector tool. For an 8x10-inch final at 300 DPI, target 2400x3000 pixels after upscaling/layout.

## AI-agent tuning and validation rules

- **Never pick a model by prompt style alone if the user explicitly requests a checkpoint.** Model preference should be ranked, not silently substituted.
- **Do not transfer CFG/step defaults across model families.** Distilled FLUX.2 Klein (4 steps/CFG 1), Qwen 2512 (about 30-40/CFG 4), SDXL Juggernaut (30-40/CFG 3-6) and Animagine (22-29/CFG 5-7) have different operating zones.
- **Compare settings at a fixed seed.** First try same seed/prompt/resolution, then sweep CFG by ±0.7 or steps by ±4. Change one dimension at a time.
- **If prompt fidelity is weak, improve spatial language before raising CFG.** If output looks plasticky/overcooked, lower CFG by 0.5-1 and shorten negative prompt.
- **Use LoRAs only if available and compatible with the checkpoint family/version.** Keep `"loras": []` when none is selected; don't invent LoRA filenames.
- **Educational illustrations are not a source of truth.** Verify factual anatomy/science; overlay exact text/labels in a design tool.
- **Print readiness is a production stage.** Check pixel dimensions, DPI at trim size, bleed, safe margins, and grayscale/line cleanliness outside the generation step.

## Sources for core settings

- [Draw Things sampler enum/config schema](https://raw.githubusercontent.com/drawthingsai/draw-things-community/main/Libraries/DataModels/Sources/config.fbs)
- [Draw Things configuration parameters](https://raw.githubusercontent.com/drawthingsai/draw-things-community/main/Libraries/Invocation/Sources/Parameters.swift)
- [Official FLUX.2 repository: distilled vs Base](https://github.com/black-forest-labs/flux2)
- [FLUX.2 Klein 4B model card](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B)
- [Juggernaut XL v9 model card](https://huggingface.co/KillerBohne420/Juggernaut-XL-v9)
- [Animagine XL v3.1 model card](https://huggingface.co/cagliostrolab/animagine-xl-3.1)
- [Draw Things community Qwen defaults reference](https://github.com/wysie/drawthings-grpc-hermes-plugin)
