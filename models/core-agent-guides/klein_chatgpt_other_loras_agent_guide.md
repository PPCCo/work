# FLUX.2 Klein 4B LoRA selection and prompt guide

**Target environment:** macOS Apple Silicon, `draw-things-cli`, `flux_2_klein_4b_q8p.ckpt`  
**Purpose:** concise rules for an AI agent to select one of four image-editing LoRAs, choose prompt/parameters, select one of four allowed upscalers, and reject mismatched combinations.

## 1. Fast routing rules

| User intent | Best route | Use one of these LoRAs? | Required input | Agent confidence |
|---|---|---:|---|---|
| Colourise an existing grayscale photograph | HaaDeej colorization | Yes: `Flux2-3500K` | Original grayscale image | Medium-high for grayscale photos; medium/low for line art and paintings |
| Extend a photo, illustration, or painting beyond its current edges | FLUX.2 Klein outpaint | Yes: use **one** of the two outpaint repos | Image canvas containing pure-green `#00FF00` added border/regions | High if border is prepared correctly |
| Enlarge a particular detail/region | Red Zoom | Yes: `fal/flux-2-klein-4B-zoom-lora` | Image with a clearly defined **red rectangle/region** | High if highlight is obvious and not confused with real red objects |
| Generate a new image from text only | Normal Klein generation | **No** | None | High that these LoRAs are not the right tool |
| Generate a new coloring-book page, line-art page, mandala, pencil sketch, watercolor, oil painting, 2D/3D anime image, or photorealistic image from scratch | Normal Klein generation, optionally a separate compatible style LoRA | **No**, unless editing an existing image with a task matching the LoRA | None for text-to-image; marked source image for edits | High |
| Add style to an existing image | Use positive edit instructions; optionally test a separate FLUX.2 Klein-compatible style LoRA | Not by themselves | Source image | Medium; depends on the other LoRA |

**Priority rule:** select a LoRA by *operation* (colourise / outpaint / zoom), not by the target genre alone. These are not dedicated coloring-book, mandala, anime, oil-painting, watercolor, or photorealism style LoRAs.

## 2. LoRA comparison and candidate settings

Ranges below are **initial search ranges, not guaranteed optima**. Start with one LoRA, one fixed seed, and one matched input. Change only one variable per comparison.

| LoRA | Benefit / best use | Input and prompt requirements | Candidate LoRA weight | Steps | CFG (`--cfg`) | Sampler | Upscaler choices from the allowed list | Confidence / validation |
|---|---|---|---:|---:|---:|---|---|---|
| [HaaDeej/Flux2-3500K](https://huggingface.co/HaaDeej/Flux2-3500K) | Adds plausible colour to a grayscale image while retaining its content. Best for old/faded photographs and monochrome portraits. | Pass the grayscale source via `--image`. Prompt should explicitly say to colourise and preserve identity, age, expression, geometry, clothing and lighting. | **0.75–1.0**; start **1.0** | Start **4**; test **4–8** only if required | Start **1.0**; test **1.0–1.5** | Use the model-recommended sampler; avoid pinning a raw integer until verified against the installed CLI build. | `RealESRGAN_x4plus` for general photos; `4x_foolhardy_Remacri_ExtraSmoother` for gentler skin/painterly texture; `RealESRGAN_x4plus_anime_6B` for clean anime/line-art input. | Card recipe is 4 steps, guidance 1.0, grayscale image conditioning. Commercial-use license needs review: HF currently labels it `other`. Test whether the trained photo colourizer handles line art/paintings acceptably. |
| [fal/flux-2-klein-4B-outpaint-lora](https://huggingface.co/fal/flux-2-klein-4B-outpaint-lora) | Extends canvas into green border regions. Best for reframing, adding sky/landscape/background, and changing aspect ratio. | Input must contain **pure RGB(0,255,0) / `#00FF00`** in areas to fill. Suggested border thickness: **5–25%** of each dimension. Prompt may start with the card's phrase, then describe the desired continuation. | **0.8–1.1**; start **1.0**; provider example uses 1.1 | Start **4**; test **4–8** | Start **1.0** for the distilled q8p workflow; test **1.0–2.0** only if guidance improves results | Model-recommended sampler; don't hard-code without checking local enum mapping. | Photo: `RealESRGAN_x4plus`; painted/painterly: `4x_foolhardy_Remacri_ExtraSmoother`; detailed architecture/ornament: `4x_NMKD-Superscale-SP_178000_G`; cel-shaded art: `RealESRGAN_x4plus_anime_6B`. | High for correct green-border input. Outpainting quality can decline with very large fill areas; prefer multiple moderate extensions. Apache-2.0 on the fal card. |
| [xocialize/outpaint-FLUX.2-klein-4B-lora](https://huggingface.co/xocialize/outpaint-FLUX.2-klein-4B-lora) | Same outpaint capability as the fal LoRA; this is a mirror, not a separate style/capability. | Same green-border workflow. Prompt: `Fill the green spaces according to the image`, optionally followed by desired scene continuity. | **0.8–1.1**; start **1.0** | Start **4**; test **4–8** | Start **1.0**; test **1.0–2.0** | Model-recommended sampler. | Choose according to source type as above. | Do not load together with the fal outpaint LoRA. The mirror states it is byte-for-byte identical to the canonical fal file; verify the local file you downloaded. Apache-2.0 is stated on the mirror page. |
| [fal/flux-2-klein-4B-zoom-lora](https://huggingface.co/fal/flux-2-klein-4B-zoom-lora) | Produces a close-up of the highlighted region. Best for a face/accessory detail, artwork detail, product feature, architectural feature or pattern detail. | Input must show the desired region in **red**, preferably as a clear rectangle. Prompt begins `Zoom into the red highlighted area`. Avoid red objects near the selection that could be mistaken for the annotation. | **0.8–1.1**; start **1.0**; provider example uses 1.1 | Start **4**; test **4–8** | Start **1.0**; test **1.0–2.0** | Model-recommended sampler. | Photo: `RealESRGAN_x4plus`; smooth portrait/painting: `4x_foolhardy_Remacri_ExtraSmoother`; line-art/anime: `RealESRGAN_x4plus_anime_6B`; fine hard-surface details: `4x_NMKD-Superscale-SP_178000_G`. | High when the red ROI is clearly marked. Very small regions may lose fidelity; prompt cannot replace the red input annotation. Apache-2.0 on the fal card. |

### Important weight caveat

The `1.1` values documented by fal are provider-side LoRA scales, not a guarantee that Draw Things' local LoRA weight is numerically identical. Treat them as an initial reference. Run a small weight sweep such as **0.8 / 1.0 / 1.1** on the same input and seed; keep the lowest weight that performs the operation reliably without unwanted changes.

### Avoid stacking task LoRAs

- **Do not** load both outpaint LoRAs; they represent the same adapter.
- **Do not** stack zoom and outpaint in one pass as a default. If both are needed, run two passes: outpaint first, then mark a region on the result and zoom.
- For a grayscale image that also needs more canvas, use two passes: colourise first, then create the green border and outpaint.
- Add a separate style LoRA only if it is explicitly compatible with FLUX.2 Klein 4B and solves a distinct requirement. Start at a low weight (candidate **0.25–0.5**, low confidence) and validate structure/colour preservation. Never presume FLUX.1 or SDXL LoRAs are compatible.

## 3. Positive-prompt construction when negative prompting is unavailable or ineffective

Build prompts as:

`[operation] + [subject/age/genre] + [properties to preserve] + [desired finish] + [composition/lighting]`

Use explicit positive constraints instead of depending on a negative prompt. Examples: `single centered subject`, `plain white background`, `crisp closed black contours`, `uniform thin linework`, `natural skin colour`, `preserved original facial identity`, `continuous background matching the source`, `consistent perspective`, `clean cel shading`.

For editing, distinguish **what must remain unchanged** from **what should change**. Do not ask the model to redesign a face or outfit when the goal is colourisation. For outpainting, describe the continuation, not an entirely new scene. For zoom, identify the detail inside the red selection and state its desired close-up treatment.

## 4. Upscaler selection rules

Use only the four requested names. In Draw Things, the JSON keys are `upscaler` and `upscalerScaleFactor` (camelCase for the latter).

| Upscaler | Preferred source/output | Agent rule |
|---|---|---|
| `RealESRGAN_x4plus` | General photographic images, realistic textures, landscapes, architecture | Default for photo/photorealistic source images. |
| `4x_foolhardy_Remacri_ExtraSmoother` | Softer portraits, smooth skin, soft/painterly images | Choose when smoother tonal transitions matter more than maximum micro-contrast. Inspect for lost fine texture. |
| `4x_NMKD-Superscale-SP_178000_G` | Fine surface detail, ornate patterns, objects, architecture, illustration texture | Choose when stronger detail definition is valuable; inspect for oversharpening or invented texture. |
| `RealESRGAN_x4plus_anime_6B` | Anime, cel-shaded art, crisp illustration and line-art-like images | Preferred among these four for anime/illustration contours and clean linework; not a substitute for a dedicated line-art generator. |

`upscalerScaleFactor: 4` asks for a 4× upscale when the chosen model is installed and supported. If a task prioritises predictable geometry or fine black linework, compare the generated image before and after upscaling; an upscaler can alter small lines and texture. For print assets, inspect the final image at 100% before publishing.

## 5. CLI and asset preparation rules

1. Use a current CLI build and check its actual options with `draw-things-cli generate --help`.
2. Download/import each LoRA through a Draw Things-supported workflow and use the **actual local filename** in `loras[].file`. The Hugging Face filename is a source filename, not proof the file has already been registered or converted correctly for Draw Things.
3. The examples include `"version":"flux2_4b"` for custom LoRAs not registered in `custom_lora.json`. This matches the Draw Things community model version identifier used for Klein 4B. If the LoRA is already registered, follow the local metadata; don't create conflicting duplicate registration.
4. `mode: "all"` is a valid LoRA mode. The command-line `--cfg` flag is clearer than placing guidance inside JSON because explicit CLI flags take precedence over JSON overrides.
5. The current generation JSON schema includes `sampler` as an integer raw value, but sampler indices are implementation identifiers, not portable names. These examples intentionally leave `sampler` out so Draw Things can retain its model-recommended setting. Pin a numeric sampler only after confirming its mapping in your installed build.
6. Do not add `schedule_sampler` to `--config-json`; it is not a field in the current `JSGenerationConfiguration` schema.
7. Image inputs are resized to the target dimensions with aspect-preserving scale and centre crop. Prepare input canvases with the **same aspect ratio** as `--width`/`--height`; this is especially important for red zoom marks and green outpaint borders. Make both dimensions multiples of 64 in this Draw Things configuration.
8. The paths below assume your input images and output directory already exist. Shell `$HOME` is used instead of quoted `~`, because a tilde inside single quotes does not expand.
9. These examples target the distilled-style `flux_2_klein_4b_q8p.ckpt` workflow: begin around **4 steps / CFG 1.0**. If the installed checkpoint actually resolves to a base variant, validate that first; the base model commonly uses a much higher step count and guidance. Do not copy base-model settings to the distilled checkpoint without checking.

## 6. Runnable command examples

**Precondition for all commands:** the named LoRA has been installed/registered in Draw Things, and the `--image` input exists at the stated path. Output dimensions match the input aspect ratio. The upscaler is installed under the name supplied. If your local installation uses another filename, replace only `loras[].file` with that exact local name.

### A. Colourise a family photo with children and adults

Use for a grayscale source photo containing people of mixed ages. Explicitly preserve identities and ages instead of asking for a style transformation.

```bash
draw-things-cli generate \
  --model flux_2_klein_4b_q8p.ckpt \
  --image "$HOME/Dev/tmp/input_grayscale_family.png" \
  --output "$HOME/Dev/tmp/colorized_family.png" \
  --prompt "Colorize this black-and-white family photograph with natural, realistic colours. Preserve the original identities, ages, expressions, facial features, hairstyles, clothing, poses, lighting and composition. Give each person plausible natural skin tones and age-appropriate hair and clothing colours. Use a gentle, authentic colour-film look with consistent daylight and subtle photographic grain." \
  --width 768 --height 1024 --steps 4 --cfg 1.0 \
  --config-json '{
    "loras": [
      {"file": "klein_4b_colorize_3500k_lora_f16.ckpt", "weight": 1.0, "mode": "all", "version": "flux2_4b"}
    ],
    "upscaler": "RealESRGAN_x4plus",
    "upscalerScaleFactor": 4
  }'
```

**Why:** the operation and identity-preservation requirements are explicit; four steps and CFG 1.0 follow the colourizer author's baseline. Use `RealESRGAN_x4plus` for a general photographic source.

### B. Colourise a child's outdoor portrait

Use an existing grayscale photo of a child. The age reference is part of the prompt; it is not a separate LoRA trigger.

```bash
draw-things-cli generate \
  --model flux_2_klein_4b_q8p.ckpt \
  --image "$HOME/Dev/tmp/input_grayscale_child.png" \
  --output "$HOME/Dev/tmp/colorized_child.png" \
  --prompt "Colourise the existing black-and-white outdoor portrait as a natural, realistic photograph of the same young child. Preserve the child's identity, apparent age, expression, pose, facial proportions, hairstyle, clothing folds and original background. Use believable skin colour, natural hair colour, soft green foliage, realistic sky colour and gentle daylight. Keep the original camera perspective and photographic texture." \
  --width 768 --height 1024 --steps 4 --cfg 1.0 \
  --config-json '{
    "loras": [
      {"file": "klein_4b_colorize_3500k_lora_f16.ckpt", "weight": 1.0, "mode": "all", "version": "flux2_4b"}
    ],
    "upscaler": "RealESRGAN_x4plus",
    "upscalerScaleFactor": 4
  }'
```

**Why:** natural colour and age preservation are higher priority than creative restyling. Validate skin and background hues against the grayscale source; the model cannot infer historically accurate colour from luminance alone.

### C. Colourise an adult or senior portrait

Use the prompt for an existing grayscale portrait; alter the age descriptor to match the actual input rather than changing a person's apparent age.

```bash
draw-things-cli generate \
  --model flux_2_klein_4b_q8p.ckpt \
  --image "$HOME/Dev/tmp/input_grayscale_senior.png" \
  --output "$HOME/Dev/tmp/colorized_senior.png" \
  --prompt "Colourise this black-and-white portrait as a realistic photograph of the same older adult. Preserve identity, age, natural wrinkles, facial proportions, expression, hairstyle, clothing, pose, lighting and framing. Use plausible natural skin colour with realistic age-related variation, natural hair tones, restrained clothing colours, soft directional window light and subtle film texture. Keep the source photograph's mood and composition." \
  --width 768 --height 1024 --steps 4 --cfg 1.0 \
  --config-json '{
    "loras": [
      {"file": "klein_4b_colorize_3500k_lora_f16.ckpt", "weight": 0.9, "mode": "all", "version": "flux2_4b"}
    ],
    "upscaler": "4x_foolhardy_Remacri_ExtraSmoother",
    "upscalerScaleFactor": 4
  }'
```

**Why:** `0.9` is a cautious candidate if the full weight changes too much; compare against `1.0`. Remacri ExtraSmoother is a candidate for a gentler portrait finish, but inspect for loss of wrinkles and skin texture.

### D. Zoom into an adult portrait detail

Prepare `input_portrait_red_roi.png` with a clear red rectangle around the eye/accessory detail. The image should already have the annotation; writing “red highlighted area” in the text is not enough by itself.

```bash
draw-things-cli generate \
  --model flux_2_klein_4b_q8p.ckpt \
  --image "$HOME/Dev/tmp/input_portrait_red_roi.png" \
  --output "$HOME/Dev/tmp/portrait_detail_zoom.png" \
  --prompt "Zoom into the red highlighted area. Create a clear, detailed close-up of the selected eye and accessory region from the same adult portrait. Preserve the person's identity, natural skin texture, original lighting, colour palette and photographic realism. Render fine eyelashes, fabric and accessory details with believable optical focus and a coherent close-up composition." \
  --width 768 --height 768 --steps 4 --cfg 1.0 \
  --config-json '{
    "loras": [
      {"file": "klein_4b_zoom_red_lora_f16.ckpt", "weight": 1.0, "mode": "all", "version": "flux2_4b"}
    ],
    "upscaler": "RealESRGAN_x4plus",
    "upscalerScaleFactor": 4
  }'
```

**Why:** the model card's required instruction is retained; the extra words describe the desired content and style. Keep real red objects away from the marked region where possible.

### E. Zoom into an anime illustration detail

Prepare a red rectangle around the intended eye, hair ornament, clothing motif or prop in the input illustration.

```bash
draw-things-cli generate \
  --model flux_2_klein_4b_q8p.ckpt \
  --image "$HOME/Dev/tmp/input_anime_red_roi.png" \
  --output "$HOME/Dev/tmp/anime_detail_zoom.png" \
  --prompt "Zoom into the red highlighted area. Produce a polished close-up of the selected anime eye and hair ornament. Preserve the original character design, apparent age, line style, colour palette, cel shading and light direction. Use crisp contour lines, controlled highlights, clean colour boundaries and a well-defined illustration detail." \
  --width 768 --height 768 --steps 4 --cfg 1.0 \
  --config-json '{
    "loras": [
      {"file": "klein_4b_zoom_red_lora_f16.ckpt", "weight": 1.0, "mode": "all", "version": "flux2_4b"}
    ],
    "upscaler": "RealESRGAN_x4plus_anime_6B",
    "upscalerScaleFactor": 4
  }'
```

**Why:** only use the anime upscaler because the input/output is cel-shaded art. The zoom LoRA enlarges a region; it does not itself convert a photograph into anime.

### F. Outpaint a landscape photograph

Prepare `input_landscape_green_border.png` with pure `#00FF00` in the areas to extend. Preserve the original centre image and include the green margin in the input file.

```bash
draw-things-cli generate \
  --model flux_2_klein_4b_q8p.ckpt \
  --image "$HOME/Dev/tmp/input_landscape_green_border.png" \
  --output "$HOME/Dev/tmp/landscape_outpainted.png" \
  --prompt "Fill the green spaces according to the image. Continue the same coastal landscape naturally, extending the distant shoreline, sea, sky and foreground with consistent perspective, horizon height, weather, daylight, colour grading and photographic detail. Make the new areas blend seamlessly with the existing photograph." \
  --width 1024 --height 768 --steps 4 --cfg 1.0 \
  --config-json '{
    "loras": [
      {"file": "klein_4b_outpaint_lora_f16.ckpt", "weight": 1.0, "mode": "all", "version": "flux2_4b"}
    ],
    "upscaler": "RealESRGAN_x4plus",
    "upscalerScaleFactor": 4
  }'
```

**Why:** the required green-fill instruction comes first, followed by scene-continuity constraints. Keep the input canvas ratio at 4:3 to match `1024×768`; do not centre-crop away any green areas.

### G. Outpaint a watercolor or oil painting

Use an existing painting already surrounded by green extension regions. This LoRA extends an existing style; it does not reliably convert a photo into a painting.

```bash
draw-things-cli generate \
  --model flux_2_klein_4b_q8p.ckpt \
  --image "$HOME/Dev/tmp/input_watercolor_green_border.png" \
  --output "$HOME/Dev/tmp/watercolor_outpainted.png" \
  --prompt "Fill the green spaces according to the image. Extend the existing watercolor landscape with the same loose brushwork, transparent pigment washes, soft-edged clouds, muted greens and blues, paper texture and atmospheric perspective. Continue the existing shapes and lighting smoothly across the border so the additions feel painted as part of the original work." \
  --width 1024 --height 768 --steps 4 --cfg 1.0 \
  --config-json '{
    "loras": [
      {"file": "klein_4b_outpaint_lora_f16.ckpt", "weight": 1.0, "mode": "all", "version": "flux2_4b"}
    ],
    "upscaler": "4x_foolhardy_Remacri_ExtraSmoother",
    "upscalerScaleFactor": 4
  }'
```

**Why:** style-continuity language encourages the border to match the original brushwork. Treat painterly performance as medium-confidence; compare the upscaled result for texture smearing.

### H. Outpaint a 2D anime scene

Use the fal outpaint LoRA once; do not also load the xocialize mirror. The input should be an anime image with green borders where the scene needs extending.

```bash
draw-things-cli generate \
  --model flux_2_klein_4b_q8p.ckpt \
  --image "$HOME/Dev/tmp/input_anime_city_green_border.png" \
  --output "$HOME/Dev/tmp/anime_city_outpainted.png" \
  --prompt "Fill the green spaces according to the image. Extend this 2D anime city scene with matching perspective, architectural shapes, clean linework, cel shading, sky colour, light direction and palette. Continue rooftops, windows, street details and background atmosphere in the same illustration style with crisp, consistent contours." \
  --width 1024 --height 768 --steps 4 --cfg 1.0 \
  --config-json '{
    "loras": [
      {"file": "klein_4b_outpaint_lora_f16.ckpt", "weight": 1.0, "mode": "all", "version": "flux2_4b"}
    ],
    "upscaler": "RealESRGAN_x4plus_anime_6B",
    "upscalerScaleFactor": 4
  }'
```

**Why:** prompts continuity of the input's line and shade language; the anime upscaler is a post-process choice, not the outpainting control.

### I. Text-to-image: adult mandala coloring page (do not apply these LoRAs)

This is a deliberate **no-LoRA** example. These four adapters do not generate mandalas from scratch. Use the model's normal text-to-image settings or a dedicated compatible line-art LoRA if available.

```bash
draw-things-cli generate \
  --model flux_2_klein_4b_q8p.ckpt \
  --output "$HOME/Dev/tmp/adult_mandala_coloring_page.png" \
  --prompt "A square black-and-white adult mandala coloring-book page, perfectly centered radial symmetry, intricate repeating lotus petals, interlocking geometric rings, balanced negative space, clean closed outlines of consistent medium thickness, pure white paper and crisp black linework suitable for printing and hand colouring. Every region is enclosed and clearly separated; no shading, gradients or filled colour." \
  --width 768 --height 768 --steps 4 --cfg 1.0 \
  --config-json '{
    "loras": [],
    "upscaler": "RealESRGAN_x4plus_anime_6B",
    "upscalerScaleFactor": 4
  }'
```

**Why:** correct LoRA routing is more important than forcing a LoRA onto an unrelated goal. Expect to inspect closed contours and symmetry; a dedicated coloring-book model/LoRA may work better.

### J. Text-to-image: child-friendly animal coloring page (do not apply these LoRAs)

```bash
draw-things-cli generate \
  --model flux_2_klein_4b_q8p.ckpt \
  --output "$HOME/Dev/tmp/kids_animal_coloring_page.png" \
  --prompt "A child-friendly black-and-white coloring page for ages 5–8, one happy young elephant standing beside three large flowers, simple rounded forms, thick smooth closed outlines, large easy-to-colour regions, balanced centered composition, plain white background, consistent black line weight, minimal background details, clean printable page." \
  --width 768 --height 768 --steps 4 --cfg 1.0 \
  --config-json '{
    "loras": [],
    "upscaler": "RealESRGAN_x4plus_anime_6B",
    "upscalerScaleFactor": 4
  }'
```

**Why:** age range, subject simplicity, contour thickness and fill-region size are stated positively. These requirements belong in the prompt; the listed LoRAs do not specialise in children's coloring pages.

### K. Text-to-image: photorealistic adult portrait (do not apply these LoRAs)

```bash
draw-things-cli generate \
  --model flux_2_klein_4b_q8p.ckpt \
  --output "$HOME/Dev/tmp/photorealistic_adult_portrait.png" \
  --prompt "A photorealistic editorial head-and-shoulders portrait of an adult in their early forties, natural skin texture and age-appropriate facial detail, relaxed expression, simple neutral clothing, soft window light from camera left, realistic catchlights, neutral studio background, 85mm portrait-lens perspective, subtle depth of field, accurate anatomy and natural colour grading." \
  --width 768 --height 1024 --steps 4 --cfg 1.0 \
  --config-json '{
    "loras": [],
    "upscaler": "RealESRGAN_x4plus",
    "upscalerScaleFactor": 4
  }'
```

**Why:** the goal is text-to-image, so none of the four edit LoRAs adds its intended function. If a source image needs colourisation instead, reroute to HaaDeej and provide `--image`.

## 7. Small deterministic validation plan for the agent

For each task/input, use a repeatable mini-grid. Fix the seed, dimensions, prompt, and upscaler during each LoRA-weight comparison.

| Test | Candidate values | Pass criteria |
|---|---|---|
| LoRA weight | `0.8`, `1.0`, `1.1` | Target operation works; subject identity/geometry and unaffected areas are preserved. |
| Steps (distilled Klein) | `4`, then `6` or `8` if justified | Additional steps visibly improve consistency/detail without excessive drift. |
| CFG | `1.0` baseline; `1.5` or `2.0` only as a controlled trial | More instruction adherence without unwanted stylisation or source-image changes. |
| Upscaler | One genre-matched choice; compare to un-upscaled output | No broken outlines, altered faces, false texture or loss of small detail. |
| Task input | correct grayscale / red ROI / pure-green border | Correct conditioning signal is present and survives resizing/cropping. |

### Machine-oriented selection record

Use a record like this in the agent's own decision log. Replace measured fields only after generating and inspecting a sample.

```json
{
  "goal": "outpaint_existing_image",
  "selected_lora": "fal/flux-2-klein-4B-outpaint-lora",
  "lora_weight_candidate": 1.0,
  "input_requirements": ["source canvas includes pure #00FF00 extension regions", "input/output aspect ratios match"],
  "steps_candidate": 4,
  "cfg_candidate": 1.0,
  "sampler": "model_recommended_unpinned",
  "upscaler_candidate": "RealESRGAN_x4plus",
  "confidence": "high_if_input_contract_passes",
  "validation_required": true,
  "failure_routes": ["if there is no green border, ask for/preprocess a marked canvas", "if text_to_image_only, do not select this LoRA", "if fill area is very large, recommend staged outpainting"]
}
```

## 8. Sources and validation notes

- [HaaDeej FLUX.2-Klein colorization LoRA](https://huggingface.co/HaaDeej/Flux2-3500K): grayscale-to-colour image conditioning; card recipe states 4 steps and guidance 1.0; HF currently displays license `other`.
- [fal Red Zoom LoRA](https://huggingface.co/fal/flux-2-klein-4B-zoom-lora): requires a red highlight and prompt `Zoom into the red highlighted area`; provider example uses scale 1.1; lists photo, architecture, art, object and pattern detail use cases.
- [fal Green Screen Outpainting LoRA](https://huggingface.co/fal/flux-2-klein-4B-outpaint-lora): requires RGB(0,255,0) green spaces; border suggestion 5–25%; provider example uses scale 1.1; Apache-2.0.
- [xocialize outpaint mirror](https://huggingface.co/xocialize/outpaint-FLUX.2-klein-4B-lora): identifies itself as a mirror of fal's outpaint LoRA and describes the mirrored weight file/hash.
- [Draw Things CLI repository](https://github.com/drawthingsai/draw-things-community): check local CLI help for the installed version.
- [Draw Things `JSGenerationConfiguration` fields](https://github.com/drawthingsai/draw-things-community/blob/main/Libraries/Scripting/Sources/ScriptModels.swift): current schema shows fields including `sampler`, `upscaler`, `upscalerScaleFactor`, and `loras`.

**Version sensitivity:** the CLI and configuration schema can change. Before production/batch generation, run one smoke test for each adapter, confirm that the LoRA is actually applied (compare with the same seed and no LoRA), and confirm that the selected upscaler is resolved by the installed build.
