# FLUX.2 Klein 4B — Edit-LoRA Reference (draw-things-cli)

Audience: AI agent / recommendation engine. Compiled 2026-10-17 from the four Hugging Face model cards.
Base: `flux_2_klein_4b_q8p.ckpt` · Hardware: MacBook Pro M4, 12-core, 48 GB.

---

## 0. Agent TL;DR

1. **All four LoRAs are instruction/edit LoRAs, not style LoRAs.** Each needs an input image, a fixed trigger sentence, and (outpaint, zoom) a colour marker painted into the input. Attaching one to plain txt2img gives nothing useful. Genre/style comes from the **stage-1 prompt**; the LoRA runs in a separate **transformation stage**.
2. **`xocialize/outpaint-FLUX.2-klein-4B-lora` is a byte-identical mirror of `fal/flux-2-klein-4B-outpaint-lora`.** Load one, never both.
3. **Licence:** three are Apache-2.0. `HaaDeej/Flux2-3500K` is licence "other" with no licence text in the repo → treat as **not cleared for commercial use** until the author confirms.
4. **Default settings (distilled Klein):** steps 4–6, cfg 1.0, sampler 10, edit-pass strength 1.0, LoRA weight 1.0–1.1.
5. **One edit LoRA per pass.** Chain passes; do not stack edit LoRAs.
6. Klein has no negative prompt: write constraints as positives (section 3).

---

## 1. LoRA comparison

| Attribute | Colorize 3500K | Outpaint (fal / xocialize mirror) | Zoom (fal) |
|---|---|---|---|---|
| HF repo | `HaaDeej/Flux2-3500K` | `fal/flux-2-klein-4B-outpaint-lora` | `xocialize/outpaint-FLUX.2-klein-4B-lora` | `fal/flux-2-klein-4B-zoom-lora` |
| Task | Grayscale → colour | Fill green border regions | Zoom into red-boxed region |
| Benefit | Plausible natural colour, very fast (card: ~4 steps) | Seamless extension; per-side borders; trained on 1,000 pairs | Reframes and re-synthesises detail (not a plain crop); 86 training pairs |
| Best for | Vintage-photo colourisation/restoration | Aspect-ratio change, panoramic/double-page spreads, extra background | Detail callouts: face, eye, hands, product, brushwork, texture studies |
| Avoid | Stylised art when exact flat colours matter (untested) | Radial/symmetric line art (mandala), text, borders >25% per side | Tiny regions, red subjects in scene, anything needing factual fidelity |
| Input prep | Grayscale image saved as RGB | Pad with pure `#00FF00`, 5–25% per side, canvas = target size | Draw pure `#FF0000` rectangle outline around region |
| Trigger prompt (verbatim) | `colorize this black and white photograph with natural, realistic colors` | `Fill the green spaces according to the image` | `Zoom into the red highlighted area` |
| Weight | 1.0 (0.8–1.1) | 1.1 (1.0–1.2) | 1.1 (1.0–1.2) |
| Steps, distilled | 4 (4–6) | 4–8 | 4–8 (start 6) |
| Steps, base | n/a (trained at guidance 1.0 → use distilled settings) | 20–28 | 20–28 |
| CFG, distilled / base | 1.0 (1.0–1.2) / n/a | 1.0 / 3.5–4.5 | 1.0 / 3.5–4.5 |
| Sampler (DT id) | 10 | 10 (base: 15) | 10 (base: 15) |
| Img2img `strength` | 1.0 | 1.0 | 1.0 |
| Resolution | Trained at 512; run 512–1024 | ≤ ~1.5 MP canvas | 1024-class works well |
| Output size | = input size | = input size (canvas) | = input size |
| Limits | Photo-pair training; other media untested | Complex scenes may need 2 passes; very large borders go incoherent | Small regions lose detail; red objects confuse it |
| Licence | "other" (unspecified) | Apache-2.0 | Apache-2.0 |
| File / size | `klein_4b_colorize_3500k_lora_f16.ckpt`, 66.9 MB, rank 32 | `klein_4b_outpaint_lora_f16.ckpt`, ~76 MB, rank 16 | `klein_4b_zoom_red_lora_f16.ckpt` |
| Pairs with | Upscaler only | Style LoRA in stage 1 only | — | Upscaler (zoom output is synthesised, then sharpen) |

---

## 2. Klein baseline settings

| | Distilled (`flux_2_klein_4b_*`, no "base" in name) | Base (`flux_2_klein_base_4b_*`) |
|---|---|---|
| Steps | 4–6 (never >8; more steps give waxy/over-cooked output) | 20–28 |
| CFG | 1.0 (1.0–1.5) | 3.5–5.0 |
| Negative prompt | none | supported but keep empty for consistency |
| Resolution | 1–2 MP, width/height multiples of 64 | same |

**Detection rule:** if the filename contains `base` use the Base column, otherwise Distilled. `q8p` filename implies distilled (assumption). The fal LoRAs were trained on the base model but run on distilled Klein.

Sampler ids (confirmed enum order from the Draw Things config schema): `0` DPM++ 2M Karras, `1` Euler A, `10` Euler A Trailing, `15` DPM++ 2M Trailing, `17` UniPC Trailing. Which one is best for Klein is unverified: default to `10`, A/B against `15`.

---

## 3. Prompting without negative prompts

Structure: **subject + action + scene + style + lighting + camera + quality**. Klein does no prompt upsampling, so be explicit.

| Instead of (negative) | Write (positive) |
|---|---|
| no shading / no gray | `pure white background, flat black outlines only, empty white fills` |
| no clutter | `single centered subject, simple uncluttered background, generous margin` |
| no text | `unlabeled, blank signs` |
| no blur | `crisp focus, sharp edges, fine detail` |
| no extra fingers | `hands resting naturally, five clearly drawn fingers` |
| not photoreal | `flat gouache colors, visible brush texture` |

**Age-group modifiers (apply in stage-1 prompts):**

| Group | Prompt phrases | Parameter shift |
|---|---|---|
| Kids 3–8 | `thick uniform outlines, large simple shapes, friendly rounded characters, bright cheerful palette, minimal background` | Lower detail; upscaler `4x_foolhardy_Remacri_ExtraSmoother` (painterly) or `RealESRGAN_x4plus_anime_6B` (flat cartoon) |
| Tween/Teen 9–17 | `dynamic pose, expressive, bold colour contrast, clean line art` | Medium detail |
| Adult 18+ | `intricate, fine detail, nuanced lighting, subtle colour grading` | High detail; fine-line upscaler `4x_NMKD-Superscale-SP_178000_G` |

**Edit-pass prompts:** keep the trigger sentence verbatim as the first sentence. Optionally append one style-continuity sentence (e.g. `Continue the same watercolor washes and paper grain.`). Untested; fall back to the verbatim prompt if the result drifts.

---

## 4. Upscaler selection (allowed four only)

| Upscaler | Use for | Avoid for |
|---|---|---|
| `RealESRGAN_x4plus` | Photography, photorealism, neutral general use | Fine hatching (smooths), anime flats |
| `4x_foolhardy_Remacri_ExtraSmoother` | Oil/watercolor, painterly kids' art, 3D/CG renders, skin | Ultra-crisp line art |
| `4x_NMKD-Superscale-SP_178000_G` | Mandalas, line art, pencil sketches, digital drawings (keeps crisp lines/grain) | Soft painterly textures (can look brittle) |
| `RealESRGAN_x4plus_anime_6B` | 2D anime, cel shading, bold-outline kids' coloring pages | Photos, pencil hatching |

Upscale only on the **final** stage; mid-pipeline upscaling compounds artefacts. Use `upscalerScaleFactor` 2 for ≥1.5 MP outputs, 4 for ≤1 MP.
Assumed DT filenames (verify): `realesrgan_x4plus_f16.ckpt`, `4x_foolhardy_remacri_extrasmoother_f16.ckpt`, `4x_nmkd_superscale_sp_178000_g_f16.ckpt`, `realesrgan_x4plus_anime_6b_f16.ckpt`.

---

## 5. Coverage matrix (genre × age × LoRA)

C = Colorize · O = Outpaint · Z = Zoom. ✓✓ strong · ✓ good · ⚠ experimental · ✗ avoid.

| Genre | Kids 3–8 | Teen 9–17 | Adult 18+ |
|---|---|---|---|
| Photography / photorealism | O ✓, Z ✓ (animals, nature) | O ✓✓, Z ✓ | C ✓✓ (restoration), O ✓✓, Z ✓✓ |
| Coloring book / line art | C ⚠ (coloured sample page), Z ✓, O ✗ | C ⚠, Z ✓ | Z ✓, C ⚠ |
| Mandala coloring | Z ✓ (simple motif) | Z ✓ | Z ✓✓ (detail page), O ✗, C ⚠ |
| Pencil / artistic sketch | C ⚠ | C ⚠, Z ✓ | C ⚠, O ✓, Z ✓ |
| Oil painting | — | O ✓, Z ✓ | O ✓✓, Z ✓✓, C ⚠ (underpainting) |
| Watercolor | O ✓✓ (storybook) | O ✓ | O ✓✓, Z ✓ |
| 2D anime | O ✓✓ (backgrounds) | O ✓✓, Z ✓, C ⚠ (manga) | O ✓, Z ✓ |
| 3D anime / CG | Z ✓✓, O ✓ | Z ✓, O ✓ | Z ✓ |
| Digital drawing | O ✓, Z ✓ | O ✓✓, Z ✓✓ | O ✓, Z ✓ |
| Kids storybook | O ✓✓ (double-page spread), Z ✓ (spot illustrations) | — | — |

---

## 6. Input-prep recipes (ImageMagick 7: `brew install imagemagick`)

```bash
# Grayscale for Colorize
magick in.png -colorspace Gray -colorspace sRGB in_gray.png

# Green border for Outpaint: adds 192 px left+right (768x768 -> 1152x768)
magick in.png -bordercolor '#00FF00' -border 192x0 in_green.png

# Red zoom box (adjust coordinates to your image)
magick in.png -fill none -stroke '#FF0000' -strokewidth 10 -draw 'rectangle 300,420 740,800' in_red.png
```

Rules: `--width/--height` of the edit pass must equal the prepared image size (multiples of 64). Border sizes: 5–25% of the canvas per side. Never leave natural pure-green (`#00FF00`) or pure-red (`#FF0000`) areas in the source image.

---

## 7. Worked examples

Common: `--model flux_2_klein_4b_q8p.ckpt`, distilled profile, `"sampler": 10`. Edit passes add `--image` and `"strength": 1.0`. Replace LoRA/upscaler filenames with your real ones.

### A. Colorize

**A1 · Photography · Adult/All · restore a vintage photo** (user-supplied input; prep with the grayscale recipe)

```bash
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--image "$HOME/Dev/tmp/old_photo_gray.png" \
--output "$HOME/Dev/tmp/klein_colorize_photo_adult.png" \
--prompt "colorize this black and white photograph with natural, realistic colors" \
--width 768 --height 768 --steps 4 --cfg 1.0 \
--config-json '{
"sampler": 10,
"strength": 1.0,
"loras": [
  {"file": "klein_4b_colorize_3500k_lora_f16.ckpt", "weight": 1.0, "mode": "all"}
],
"upscaler": "realesrgan_x4plus_f16.ckpt",
"upscalerScaleFactor": 2
}'
```
Why: trigger is verbatim as trained; 4 steps/cfg 1.0 match its training (guidance 1.0); x4plus keeps photo texture neutral. If skin looks plastic after upscale, switch to Remacri ExtraSmoother. Match width/height to the photo (multiples of 64).

**A2 · Coloring book · Kids · coloured sample page (experimental, two stages)**

```bash
# Stage 1: line art (no LoRA)
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--output "$HOME/Dev/tmp/klein_lineart_kids_elephant.png" \
--prompt "children's coloring book page, a smiling baby elephant holding a balloon, thick uniform black outlines, large simple shapes, pure white background, flat black outlines only, empty white fills, centered composition with generous white margin" \
--width 768 --height 768 --steps 4 --cfg 1.0 \
--config-json '{"sampler": 10}'

# Stage 2: colourise for cover/sample
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--image "$HOME/Dev/tmp/klein_lineart_kids_elephant.png" \
--output "$HOME/Dev/tmp/klein_colorize_kids_elephant.png" \
--prompt "colorize this black and white drawing with bright, natural colors" \
--width 768 --height 768 --steps 4 --cfg 1.0 \
--config-json '{
"sampler": 10,
"strength": 1.0,
"loras": [
  {"file": "klein_4b_colorize_3500k_lora_f16.ckpt", "weight": 0.9, "mode": "all"}
],
"upscaler": "realesrgan_x4plus_anime_6b_f16.ckpt",
"upscalerScaleFactor": 2
}'
```
Why: stage-1 prompt turns every "no X" into a positive; kids' flat bold outlines suit anime_6B. LoRA trained on photos, so "photograph" is swapped to "drawing" (untested; fall back to the verbatim sentence if colours bleed over lines) and weight is lowered to 0.9.

**A3 · Pencil sketch · Adult · gentle colour wash (experimental)**

```bash
# Stage 1
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--output "$HOME/Dev/tmp/klein_pencil_adult_fisherman.png" \
--prompt "detailed graphite pencil portrait sketch of an elderly fisherman with a weathered face and a woolen cap, soft cross-hatching, visible pencil strokes, smudged shading, cream-white sketchbook paper, dramatic side lighting, monochrome" \
--width 768 --height 1024 --steps 4 --cfg 1.0 \
--config-json '{"sampler": 10}'

# Stage 2
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--image "$HOME/Dev/tmp/klein_pencil_adult_fisherman.png" \
--output "$HOME/Dev/tmp/klein_colorize_adult_fisherman.png" \
--prompt "colorize this black and white pencil sketch with natural, realistic colors" \
--width 768 --height 1024 --steps 4 --cfg 1.0 \
--config-json '{
"sampler": 10,
"strength": 1.0,
"loras": [
  {"file": "klein_4b_colorize_3500k_lora_f16.ckpt", "weight": 0.7, "mode": "all"}
],
"upscaler": "4x_nmkd_superscale_sp_178000_g_f16.ckpt",
"upscalerScaleFactor": 2
}'
```
Why: weight 0.7 keeps pencil grain visible; NMKD preserves strokes.

### B. Outpaint (fal)

**B1 · Photorealism · Adult · square → 3:2**

```bash
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--output "$HOME/Dev/tmp/klein_photo_valley_base.png" \
--prompt "photorealistic Tuscan valley at golden hour, a gravel road lined with cypress trees winding toward a stone farmhouse, soft haze over distant hills, warm low sun raking across the fields, shot on a 35mm full-frame camera at f/8, natural color grading, crisp detail" \
--width 768 --height 768 --steps 4 --cfg 1.0 \
--config-json '{"sampler": 10}'

magick "$HOME/Dev/tmp/klein_photo_valley_base.png" -bordercolor '#00FF00' -border 192x0 "$HOME/Dev/tmp/klein_photo_valley_green.png"

draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--image "$HOME/Dev/tmp/klein_photo_valley_green.png" \
--output "$HOME/Dev/tmp/klein_outpaint_photo_adult_valley.png" \
--prompt "Fill the green spaces according to the image" \
--width 1152 --height 768 --steps 6 --cfg 1.0 \
--config-json '{
"sampler": 10,
"strength": 1.0,
"loras": [
  {"file": "klein_4b_outpaint_lora_f16.ckpt", "weight": 1.1, "mode": "all"}
],
"upscaler": "realesrgan_x4plus_f16.ckpt",
"upscalerScaleFactor": 2
}'
```
Why: 192/1152 ≈ 17% per side sits inside the trained 5–25% band; weight 1.1 is the author's scale; 6 steps help seam blending on distilled Klein.

**B2 · Watercolor · Adult/Teen**

```bash
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--output "$HOME/Dev/tmp/klein_watercolor_lake_base.png" \
--prompt "loose watercolor landscape of a misty lake at dawn with a small wooden rowboat, pine-covered hills fading into pale blue, wet-on-wet washes, soft bleeding edges, visible cold-press paper grain, white paper showing at the edges, muted teal and ochre palette" \
--width 768 --height 768 --steps 4 --cfg 1.0 \
--config-json '{"sampler": 10}'

magick "$HOME/Dev/tmp/klein_watercolor_lake_base.png" -bordercolor '#00FF00' -border 192x0 "$HOME/Dev/tmp/klein_watercolor_lake_green.png"

draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--image "$HOME/Dev/tmp/klein_watercolor_lake_green.png" \
--output "$HOME/Dev/tmp/klein_outpaint_watercolor_adult_lake.png" \
--prompt "Fill the green spaces according to the image. Continue the same watercolor washes, paper grain and muted palette." \
--width 1152 --height 768 --steps 6 --cfg 1.0 \
--config-json '{
"sampler": 10,
"strength": 1.0,
"loras": [
  {"file": "klein_4b_outpaint_lora_f16.ckpt", "weight": 1.1, "mode": "all"}
],
"upscaler": "4x_foolhardy_remacri_extrasmoother_f16.ckpt",
"upscalerScaleFactor": 2
}'
```
Why: the appended continuity sentence guards against hard-edged fills in a wash medium; Remacri preserves soft pigment edges.

**B3 · Kids storybook · double-page spread**

```bash
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--output "$HOME/Dev/tmp/klein_storybook_fox_base.png" \
--prompt "children's picture-book illustration, a small round red fox in a yellow raincoat splashing through a puddle in a sunny meadow, big friendly eyes, soft rounded shapes, flat gouache colors with gentle texture, bright cheerful palette of sky blue and warm yellow, simple uncluttered background, warm even lighting" \
--width 768 --height 768 --steps 4 --cfg 1.0 \
--config-json '{"sampler": 10}'

magick "$HOME/Dev/tmp/klein_storybook_fox_base.png" -bordercolor '#00FF00' -border 256x0 "$HOME/Dev/tmp/klein_storybook_fox_green.png"

draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--image "$HOME/Dev/tmp/klein_storybook_fox_green.png" \
--output "$HOME/Dev/tmp/klein_outpaint_kids_fox_spread.png" \
--prompt "Fill the green spaces according to the image. Continue the sunny meadow in the same flat gouache style." \
--width 1280 --height 768 --steps 6 --cfg 1.0 \
--config-json '{
"sampler": 10,
"strength": 1.0,
"loras": [
  {"file": "klein_4b_outpaint_lora_f16.ckpt", "weight": 1.1, "mode": "all"}
],
"upscaler": "4x_foolhardy_remacri_extrasmoother_f16.ckpt",
"upscalerScaleFactor": 2
}'
```
Why: 256/1280 = 20% per side (upper end of trained band); prompt avoids saturated green so the source image cannot be mistaken for fill. For a true 2:1 spread run a second pass rather than a bigger border.

**B4 · 2D anime · Teen · wallpaper extension**

```bash
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--output "$HOME/Dev/tmp/klein_anime_rooftop_base.png" \
--prompt "2D anime key visual, a teenage girl with short silver hair and a navy school uniform standing on a rooftop at sunset, wind in her hair, city skyline in the distance, clean cel shading, crisp line art, warm orange and violet sky gradient, cinematic composition, high detail" \
--width 768 --height 768 --steps 4 --cfg 1.0 \
--config-json '{"sampler": 10}'

magick "$HOME/Dev/tmp/klein_anime_rooftop_base.png" -bordercolor '#00FF00' -border 288x0 "$HOME/Dev/tmp/klein_anime_rooftop_green.png"

draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--image "$HOME/Dev/tmp/klein_anime_rooftop_green.png" \
--output "$HOME/Dev/tmp/klein_outpaint_anime_teen_rooftop.png" \
--prompt "Fill the green spaces according to the image. Extend the city skyline and sunset sky in the same cel-shaded anime style." \
--width 1344 --height 768 --steps 6 --cfg 1.0 \
--config-json '{
"sampler": 10,
"strength": 1.0,
"loras": [
  {"file": "klein_4b_outpaint_lora_f16.ckpt", "weight": 1.1, "mode": "all"}
],
"upscaler": "realesrgan_x4plus_anime_6b_f16.ckpt",
"upscalerScaleFactor": 2
}'
```
Why: 16:9 wallpaper from a square key visual; anime_6B keeps cel edges clean.

### C. Zoom (fal)

**C1 · Photography · Adult · detail callout**

```bash
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--output "$HOME/Dev/tmp/klein_photo_potter_base.png" \
--prompt "photorealistic ceramic workshop, a potter's hands trimming a blue-glazed bowl on a spinning wheel, shelves of glazed ceramics behind, soft window light, 50mm lens at f/2.8, shallow depth of field, natural color, crisp detail" \
--width 1024 --height 1024 --steps 4 --cfg 1.0 \
--config-json '{"sampler": 10}'

magick "$HOME/Dev/tmp/klein_photo_potter_base.png" -fill none -stroke '#FF0000' -strokewidth 10 -draw 'rectangle 300,420 740,800' "$HOME/Dev/tmp/klein_photo_potter_red.png"

draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--image "$HOME/Dev/tmp/klein_photo_potter_red.png" \
--output "$HOME/Dev/tmp/klein_zoom_photo_adult_potter.png" \
--prompt "Zoom into the red highlighted area" \
--width 1024 --height 1024 --steps 6 --cfg 1.0 \
--config-json '{
"sampler": 10,
"strength": 1.0,
"loras": [
  {"file": "klein_4b_zoom_red_lora_f16.ckpt", "weight": 1.1, "mode": "all"}
],
"upscaler": "realesrgan_x4plus_f16.ckpt",
"upscalerScaleFactor": 2
}'
```
Why: scene deliberately has no red so the marker is unambiguous; the zoomed view is re-synthesised, so the upscaler is applied after it.

**C2 · Oil painting · Adult · brushwork study**

```bash
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--output "$HOME/Dev/tmp/klein_oil_sea_base.png" \
--prompt "impasto oil painting of a stormy sea crashing against dark cliffs, thick palette-knife strokes, visible bristle marks, cobalt and slate-grey water with white foam highlights, a distant lighthouse glowing amber, dramatic chiaroscuro, canvas weave texture" \
--width 1024 --height 768 --steps 4 --cfg 1.0 \
--config-json '{"sampler": 10}'

magick "$HOME/Dev/tmp/klein_oil_sea_base.png" -fill none -stroke '#FF0000' -strokewidth 10 -draw 'rectangle 280,260 700,560' "$HOME/Dev/tmp/klein_oil_sea_red.png"

draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--image "$HOME/Dev/tmp/klein_oil_sea_red.png" \
--output "$HOME/Dev/tmp/klein_zoom_oil_adult_sea.png" \
--prompt "Zoom into the red highlighted area" \
--width 1024 --height 768 --steps 6 --cfg 1.0 \
--config-json '{
"sampler": 10,
"strength": 1.0,
"loras": [
  {"file": "klein_4b_zoom_red_lora_f16.ckpt", "weight": 1.1, "mode": "all"}
],
"upscaler": "4x_foolhardy_remacri_extrasmoother_f16.ckpt",
"upscalerScaleFactor": 2
}'
```

**C3 · 3D anime / CG · Kids · character face spot illustration**

```bash
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--output "$HOME/Dev/tmp/klein_cg_inventor_base.png" \
--prompt "3D animated feature-film character render, a cheerful young inventor girl with curly brown hair and round yellow goggles holding a small glowing robot, soft subsurface skin shading, expressive large eyes, pastel workshop interior, warm rim light, polished stylized CG look, shallow depth of field" \
--width 1024 --height 1024 --steps 4 --cfg 1.0 \
--config-json '{"sampler": 10}'

magick "$HOME/Dev/tmp/klein_cg_inventor_base.png" -fill none -stroke '#FF0000' -strokewidth 10 -draw 'rectangle 340,140 700,520' "$HOME/Dev/tmp/klein_cg_inventor_red.png"

draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--image "$HOME/Dev/tmp/klein_cg_inventor_red.png" \
--output "$HOME/Dev/tmp/klein_zoom_cg_kids_inventor.png" \
--prompt "Zoom into the red highlighted area" \
--width 1024 --height 1024 --steps 6 --cfg 1.0 \
--config-json '{
"sampler": 10,
"strength": 1.0,
"loras": [
  {"file": "klein_4b_zoom_red_lora_f16.ckpt", "weight": 1.0, "mode": "all"}
],
"upscaler": "4x_foolhardy_remacri_extrasmoother_f16.ckpt",
"upscalerScaleFactor": 2
}'
```
Why: weight 1.0 (not 1.1) keeps faces from over-sharpening; Remacri suits soft CG skin. Inspect for identity drift versus the full figure.

**C4 · Mandala coloring · Adult · enlarged detail page**

```bash
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--output "$HOME/Dev/tmp/klein_mandala_adult_base.png" \
--prompt "intricate mandala coloring book page, concentric rings of lotus petals, paisley teardrops and fine geometric lattice, perfectly symmetrical, crisp thin black lines on a pure white background, high contrast, empty white fills" \
--width 1024 --height 1024 --steps 4 --cfg 1.0 \
--config-json '{"sampler": 10}'

magick "$HOME/Dev/tmp/klein_mandala_adult_base.png" -fill none -stroke '#FF0000' -strokewidth 8 -draw 'rectangle 380,100 640,360' "$HOME/Dev/tmp/klein_mandala_adult_red.png"

draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--image "$HOME/Dev/tmp/klein_mandala_adult_red.png" \
--output "$HOME/Dev/tmp/klein_zoom_mandala_adult_detail.png" \
--prompt "Zoom into the red highlighted area" \
--width 1024 --height 1024 --steps 6 --cfg 1.0 \
--config-json '{
"sampler": 10,
"strength": 1.0,
"loras": [
  {"file": "klein_4b_zoom_red_lora_f16.ckpt", "weight": 1.0, "mode": "all"}
],
"upscaler": "4x_nmkd_superscale_sp_178000_g_f16.ckpt",
"upscalerScaleFactor": 2
}'
```
Why: red outline is highly visible on black/white art; NMKD keeps thin lines crisp. Check the result for grey fills and re-run with a different seed if lines soften. Experimental on line art.

**C5 · Digital drawing · Teen · hands/gear detail**

```bash
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--output "$HOME/Dev/tmp/klein_digital_musician_base.png" \
--prompt "digital illustration of a cyberpunk street musician, teenage boy with glowing teal headphones and a patched denim jacket playing an electric guitar, neon signs reflected in rain puddles, painterly digital brush strokes, teal and amber rim lighting, dynamic low angle" \
--width 1024 --height 1024 --steps 4 --cfg 1.0 \
--config-json '{"sampler": 10}'

magick "$HOME/Dev/tmp/klein_digital_musician_base.png" -fill none -stroke '#FF0000' -strokewidth 10 -draw 'rectangle 360,560 760,900' "$HOME/Dev/tmp/klein_digital_musician_red.png"

draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--image "$HOME/Dev/tmp/klein_digital_musician_red.png" \
--output "$HOME/Dev/tmp/klein_zoom_digital_teen_musician.png" \
--prompt "Zoom into the red highlighted area" \
--width 1024 --height 1024 --steps 6 --cfg 1.0 \
--config-json '{
"sampler": 10,
"strength": 1.0,
"loras": [
  {"file": "klein_4b_zoom_red_lora_f16.ckpt", "weight": 1.1, "mode": "all"}
],
"upscaler": "4x_nmkd_superscale_sp_178000_g_f16.ckpt",
"upscalerScaleFactor": 2
}'
```
Why: palette avoids red/magenta so the marker stays unambiguous.

---

## 8. Combining LoRAs and pipelines

| Question | Guidance |
|---|---|
| Stack two of these four? | No. Different markers and trigger prompts conflict. Chain passes (e.g. outpaint → zoom). Never load both outpaint files. |
| Stack with a style/genre LoRA? | Prefer **stage 1 only** (style LoRA during generation, none during the edit pass). If you must stack in the edit pass, hold the style LoRA ≤0.4 and keep the edit LoRA at its normal weight; untested, check instruction-following. |
| Best pipeline order | stage 1 generate (style LoRA allowed) → edit pass (one LoRA) → optional second edit pass → upscaler on the last pass only |
| Seeds | Fix `--seed` while tuning weight/steps, then vary |
| Fidelity-critical work (product labels, text, likeness) | Use plain crop + upscaler instead of Zoom; Zoom invents detail |

---

## 9. Request → recommendation rules

| User intent | Recommend |
|---|---|
| "Make it wider / 16:9 / extend / more background" | Outpaint (not for mandalas) |
| "Zoom in / closeup of part / detail view" | Zoom; offer crop + upscaler if accuracy matters |
| "Colorize / add colour to B&W" | Colorize (photos strong; art experimental; flag licence for commercial use) |
| "Make a coloring page / mandala / line art" | No LoRA: txt2img with positive-only constraints (section 3) |
| "Change style / genre" | None of these four; use plain prompting or a style LoRA |
| "Just higher resolution" | Upscaler only |
| "Commercial book/product" | Exclude Colorize until licence confirmed; the other three are Apache-2.0 |
| "Add or fix text in image" | None of these |
| Low-quality input | Run upscaler first only if the input is <512 px; edit passes expect clean inputs |

```json
{
  "base": {"model": "flux_2_klein_4b_q8p.ckpt", "variant_assumed": "distilled"},
  "profiles": {
    "distilled": {"steps": [4, 6], "cfg": [1.0, 1.5], "sampler": 10},
    "base": {"steps": [20, 28], "cfg": [3.5, 5.0], "sampler": 15}
  },
  "loras": [
    {"id": "colorize_3500k", "hf": "HaaDeej/Flux2-3500K", "task": "gray_to_color",
     "trigger": "colorize this black and white photograph with natural, realistic colors",
     "input_marker": null, "weight": {"default": 1.0, "range": [0.8, 1.1]},
     "strength": 1.0, "license": "other-unspecified", "commercial_ok": "unknown",
     "genre_fit": {"photography": "strong", "line_art": "experimental", "pencil": "experimental", "anime": "experimental"}},
    {"id": "outpaint_fal", "hf": "fal/flux-2-klein-4B-outpaint-lora", "task": "outpaint",
     "trigger": "Fill the green spaces according to the image",
     "input_marker": {"color": "#00FF00", "border_pct_per_side": [5, 25]},
     "weight": {"default": 1.1, "range": [1.0, 1.2]}, "strength": 1.0,
     "license": "Apache-2.0", "commercial_ok": true, "duplicate_of": null,
     "genre_fit": {"photography": "strong", "painting": "strong", "anime": "strong", "storybook": "strong", "mandala": "avoid"}},
    {"id": "outpaint_xocialize_mirror", "hf": "xocialize/outpaint-FLUX.2-klein-4B-lora",
     "duplicate_of": "outpaint_fal", "recommended": false},
    {"id": "zoom_red_fal", "hf": "fal/flux-2-klein-4B-zoom-lora", "task": "zoom_region",
     "trigger": "Zoom into the red highlighted area",
     "input_marker": {"color": "#FF0000", "shape": "rectangle_outline"},
     "weight": {"default": 1.1, "range": [1.0, 1.2]}, "strength": 1.0,
     "license": "Apache-2.0", "commercial_ok": true,
     "genre_fit": {"photography": "strong", "painting": "strong", "cg": "strong", "digital": "strong", "mandala": "experimental"}}
  ],
  "rules": {"max_edit_loras_per_pass": 1, "upscale_final_stage_only": true, "negative_prompt": "unsupported_use_positive_phrasing"}
}
```

---

## 10. Unverified items: check on first run

- **Distilled vs base:** assumed distilled from the `q8p` filename. If outputs look under-cooked at 4 steps, check whether the file is a base model and switch profile.
- **`--image` + `"strength": 1.0` as an edit/reference pass:** documented by third-party Draw Things CLI wrappers; confirm with `draw-things-cli generate --help`. If the original content is repainted instead of preserved, try strength 0.9–1.0 or the reference-image/moodboard route in the Draw Things app.
- **`upscalerScaleFactor`** key name and the **upscaler/LoRA `.ckpt` filenames** are assumptions. List the real names in the Models folder.
- **`"schedule_sampler": 1`** from your template is not in the Draw Things config schema I could verify, so these commands omit it. Add it back if your build uses it.
- **Paths:** single-quoted `'~/Dev/t2/...'` does not expand in zsh (it can create a literal `~` folder). These commands use `"$HOME/Dev/tmp/..."`.
- **Sampler choice** (10 vs 15) is an A/B test, not a documented recommendation.
- **Colorize on non-photo art, and extra continuity sentences in edit prompts,** are untested extrapolations.

Sources: HF model cards for `HaaDeej/Flux2-3500K`, `fal/flux-2-klein-4B-outpaint-lora`, `xocialize/outpaint-FLUX.2-klein-4B-lora`, `fal/flux-2-klein-4B-zoom-lora`; Draw Things config schema (`config.fbs`); NeuroCanvas FLUX.2 Klein ComfyUI guide (steps/cfg); draw-things-cli wrapper docs.
