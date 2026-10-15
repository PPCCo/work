# Draw Things CLI + SDXL: Illustration Recommendation Guide

**Purpose:** machine-readable decision support and practical recipes for children's books, educational/non-fiction illustrations, coloring pages, mandalas, anime, sketches, painterly art, digital illustration, analog photography and photorealism, using only the user-supplied assets.

## 0. Compatibility and executable-command notes

- `--config-json` is a **partial override** merged with the model's recommended configuration. Explicit CLI flags (`--steps`, `--cfg`, `--width`, `--height`, `--seed`) override their corresponding config defaults.
- Use exact filenames, including case and extension, as Draw Things registers them. Models/LoRAs/upscalers must be present in the model directory used by this CLI.
- Current Draw Things `SamplerType` numeric mapping is included below. These numbers are Draw Things enum values, not universal sampler IDs. Validate against your installed CLI after upgrades.
- `JSGenerationConfiguration` has `upscaler`, `upscalerScaleFactor`, `hiresFix`, `hiresFixWidth`, `hiresFixHeight`, and `hiresFixStrength`. In recipes, base generation is usually 768 px and hires-fix target is 1024 px. This is a second diffusion pass, not a guarantee of a literal 4x final image. `upscalerScaleFactor` describes the selected upscaler's scale factor; target output dimensions are set by the hires-fix dimensions.
- Draw Things CLI documents `loras[].version` for local LoRAs not registered in `custom_lora.json`. The recipes omit `version` to match a typical registered-LoRA config. If a LoRA is ignored/rejected or the CLI reports missing custom LoRA metadata, add the version required by your local metadata (normally the SDXL-base version label used by your installed catalog) to each relevant LoRA object, or import/register it through your Draw Things workflow. Do not assume that an arbitrary `.safetensors` is active merely because the filename is accepted.
- Create the output directory before running commands. The examples do this with `mkdir -p "$HOME/Dev/tmp"`. These commands assume the `draw-things-cli` executable is on `PATH` and assets resolve in the default Draw Things models directory.
- If exact clean linework is more important than fine surface detail, render directly at the intended resolution and omit hires fix; an additional diffusion pass can introduce unwanted texture or alter contours. For print, inspect at 100%, especially tiny enclosed coloring areas.

## 1. Sampler values (numeric IDs)

| ID | Sampler name | Suggested role for SDXL |
|---:|---|---|
| 0 | DPM++ 2M Karras | Main baseline for most tasks: realistic, illustrated, painterly and detailed work |
| 1 | Euler A | More stochastic/expressive variation; try for sketches and organic painterly forms |
| 2 | DDIM | Controlled comparisons and simple, clear compositions |
| 3 | PLMS | Legacy; not the default recommendation |
| 4 | DPM++ SDE Karras | Stochastic detail experiment; often slower |
| 5 | UniPC | Alternative general-purpose solver |
| 6 | LCM | Not a default for these standard SDXL checkpoints; intended for compatible consistency workflows |
| 7 | Euler A Substep | Alternative for organic detail experiments |
| 8 | DPM++ SDE Substep | Specialized; test only if needed |
| 9 | TCD | Not a default for these checkpoints |
| 10 | Euler A Trailing | Alternative schedule; validate on each model |
| 11 | DPM++ SDE Trailing | Stochastic alternative |
| 12 | DPM++ 2M AYS | Alternative step placement; test at fewer steps |
| 13 | Euler A AYS | Alternative for efficient tests |
| 14 | DPM++ SDE AYS | Specialized alternative |
| 15 | DPM++ 2M Trailing | Alternative DPM++ schedule |
| 16 | DDIM Trailing | Controlled alternative schedule |
| 17 | UniPC Trailing | Available; not the first pick for ordinary SDXL |
| 18 | UniPC AYS | Alternative step-placement experiment |

**Default:** sampler `0`. Keep the seed and all generation settings fixed when comparing prompts, LoRA weights, or model checkpoints. Only change one variable at a time.

## 2. Model routing

| Model | Prefer for | Caveat / steering |
|---|---|---|
| `juggernaut_xl_x_f16.ckpt` | Photorealism, editorial images, realistic objects/animals, mature digital illustration, cinematic scenes | Prompt concrete camera/lighting/material details for photos; limit stylistic LoRAs for realism |
| `juggernaut_xl_v9_f16.ckpt` | Versatile painterly work, classic storybook art, oil/watercolor-like illustration, general illustration | Good alternate when X becomes too slick/photographic; still control style with medium terms |
| `colorfulxl_v6.0_f16.ckpt` | Bright children's art, friendly cartoons, vivid digital illustration, colorful fantasy/mascot scenes | Reduce saturation tokens when colors become garish; not the first choice for neutral photography |
| `animagine_xl_v3.1_f16.ckpt` | 2D anime, manga-inspired character illustrations, chibi, anime cover art | Use concise anime/tag-style prompts and style/quality tags; not ideal for photorealistic or pure coloring pages |

## 3. LoRA routing and starting weights

Weights below are **empirical starting points**, not guarantees. Increase by 0.05–0.10 per iteration only when the style is too weak; reduce if content collapses, edges get noisy, colors become muddy, or the model loses subject control.

| LoRA file | Main task | Start weight | Prompt activation / usage |
|---|---|---:|---|
| `StorybookRedmondV2-KidsBook-KidsRedmAF.safetensors` | Children's picture books, gentle story illustrations, narrative vignettes | 0.70–0.90 | Include `KidsRedmAF, Kids Book`; steer with `colorful`, `minimalist`, or `detailed` |
| `ColoringBookRedmond-ColoringBook-ColoringBookAF.safetensors` | Black-and-white printable coloring pages, kids/adult coloring books, mandala pages | 0.85–1.00 | Include `ColoringBookAF, Coloring Book`; explicitly request black outlines and white background |
| `LineAniRedmondV2-Lineart-LineAniAF.safetensors` | Manga/anime line art, inked character illustrations | 0.35–0.65 | Include `LineAniAF, lineart`; pair with Animagine for 2D anime work |
| `AnalogRedmondV2-Analog-AnalogRedmAF.safetensors` | Filmic/analog-looking photography, vintage editorial images | 0.40–0.70 | Include `AnalogRedmAF, Analog`; pair with Juggernaut X for photographs |
| `3d_render_style_xl.safetensors` | 3D-rendered character/product/scene illustration | 0.50–0.75 | Include `3D style`, `3D render`, smooth materials and coherent studio lighting |
| `pixar-style.safetensors` | Feature-animation-like 3D characters and family-friendly cinematic cartoons | 0.35–0.65 | Include `pixar-style`; treat as a style slider, not a substitute for clear scene description |
| `add-detail-xl.safetensors` | Small details, texture and micro-detail support | 0.15–0.35 | Usually no special trigger; optional and easy to overdo, especially on line art |
| `sketch-style-xl.safetensors` | Pencil sketch, grayscale drawing, loose artistic sketch | 0.45–0.75 | Prompt `pencil sketch`, `graphite`, `visible pencil strokes`, or `gesture drawing` |
| `oil-painting-slider.safetensors` | Oil-painting look | 0.35–0.65 | Describe brushwork, paint thickness, canvas and palette; test positive weight only |
| `epic-oil-painting-slider.safetensors` | Stronger / more dramatic oil-painting stylization | 0.30–0.60 | Use as an **alternative** to `oil-painting-slider`, not automatically stacked with it |

**LoRA stacking policy:** use one dominant style LoRA; add at most one supporting LoRA. Do not stack Storybook + ColoringBook for the same image unless a deliberately hybrid outcome is wanted. Avoid `add-detail-xl` on coloring pages unless it demonstrably improves line integrity.

## 4. Upscaler routing

These recommendations describe the likely visual tendencies implied by each model family; verify against your exact installed versions and inspect at 100%.

| Upscaler file | Best first test | Main risk |
|---|---|---|
| `4x_foolhardy_Remacri_ExtraSmoother.safetensors` | Smooth children's illustration, clean linework, softer painterly textures | Can soften fine hatch marks or tiny details |
| `4x_NMKD-Superscale-SP_178000_G.safetensors` | General illustration, mixed texture, painterly work, general-purpose backup | May emphasize invented surface texture; inspect faces and small objects |
| `4x-UltraSharpV2.safetensors` | Crisp digital drawing, bold outlines, graphic illustration | May oversharpen/halo edges and make coloring contours harsh |
| `RealESRGAN_x4plus_anime_6B.safetensors` | Anime, manga-color illustrations, cel-shaded cartoon work | Can oversharpen gradients and line joins |
| `RealESRGAN_x4plus.safetensors` | Photorealism, natural textures, realistic objects/animals | May add crunchy microtexture or alter smooth paint transitions |
| `RealESRGAN_x2plus.safetensors` | Conservative 2x enlargement, quality proofing, images where 4x enhancement is too strong | Less size gain; won't fix composition or anatomy |

Use upscaling late, after composition and anatomy are already good. Upscalers cannot repair bad hands, fused coloring shapes, invented text, or incorrect educational facts. For print, upscale once, not repeatedly.

## 5. Resolution, steps, CFG and sampler defaults

| Output intent | Base render | Steps | CFG | Sampler ID | Practical rule |
|---|---|---:|---:|---:|---|
| Quick layout / prompt test | 640–768 square or aspect-matched | 18–24 | 4.5–5.5 | 0 | Make composition decisions fast; don't judge final line quality yet |
| Children's picture-book art | 768×1024 or 832×1024 | 24–30 | 4.5–6.0 | 0 | Keep silhouettes readable and focal points few |
| Educational illustration | 768–1024 on long edge | 26–32 | 4.5–6.0 | 0 | Prioritize object count and spatial correctness over decorative complexity |
| Kids coloring page 3–5 | 768–1024 square/portrait | 24–30 | 4.5–5.8 | 0 or 2 | Few large closed shapes; avoid shading and overly thin lines |
| Kids coloring page 6–12 | 768–1024 square/portrait | 25–32 | 4.5–6.0 | 0 | Increase object and pattern count with age, not stroke density alone |
| Adult mandala coloring | 768–1024 square | 28–34 | 4.5–6.0 | 0 | Many enclosed, non-overlapping cells; pure black linework |
| Anime / manga | 768–1024 | 25–32 | 4.5–6.5 | 0 | Animagine works best with concise tagged descriptors plus composition |
| 3D / family animation | 768–1024 | 24–30 | 4.5–6.0 | 0 | Name material, camera angle, lighting and character expression |
| Pencil / charcoal sketch | 768–1024 | 26–34 | 4.5–6.0 | 0; try 1 | Define paper, pencil medium and mark density explicitly |
| Oil / watercolor | 768–1024 | 28–36 | 4.5–6.0 | 0; try 1 | Describe brushwork and pigment; don't ask for both photorealism and painterly edges |
| Photorealism / analog film | 768–1024 | 28–36 | 4.5–6.5 | 0 | Describe lighting, lens/framing, subject materials and natural detail |

SDXL typically benefits from dimensions divisible by 64; use resolution as a composition decision. Square is useful for mandalas and icons, portrait for page art, landscape for spreads and explanatory scenes. Stay near native SDXL working resolutions unless testing higher memory loads.

## 6. Prompt-building recipe

Use this order and keep the prompt focused:

1. **Subject + action:** one clear subject and verb.
2. **Scene + composition:** background, camera/viewpoint, foreground/midground/background, subject placement, negative space.
3. **Medium/style:** storybook watercolor, clean coloring-book line art, graphite pencil, oil impasto, analog film, cel-shaded anime, 3D render, or photorealistic photography.
4. **Lighting + palette:** only when relevant (soft morning light, warm limited palette, neutral daylight, monochrome).
5. **Craft constraints:** closed contours, broad shapes, simple background, accurate anatomy, legible margins, no text, high edge clarity.
6. **LoRA trigger words:** include exact documented trigger words early in the prompt.

Prefer observable specifics to adjectives alone. Better: “a red fox kits curled under fern fronds, eye-level view, a clear silhouette, soft watercolor washes, cream paper, gentle morning light.” Weaker: “cute, amazing, best, beautiful, masterpiece, ultra-detailed.” Avoid unnecessary quality-token piles on Juggernaut/ColorfulXL; Animagine can benefit from its familiar quality and anime tagging conventions.

### Complexity budget by age group

| Target age | Detail density | Composition rules | Avoid |
|---|---|---|---|
| Preschool (3–5) | Very low; 1–3 main forms | Big silhouette, few props, simple background, generous whitespace | Tiny texture, thin lines, crowded scenes, subtle value contrast |
| Early readers (5–7) | Low–medium | 1 main action, clear emotion, 2–4 supporting objects | Too many competing focal points, complex perspective |
| Children (8–12) | Medium | More environmental clues, layered setting, narrative action | High texture over the focal subject, confusing overlap |
| Teens (13–18) | Medium–high | More accurate educational detail, nuanced mood, clear visual hierarchy | Overly childish proportions unless requested, invented diagram labels |
| Adult coloring | High but organized | Repeating logic, many closed regions, deliberate symmetry and line-weight hierarchy | Gray shading, open gaps, large accidental solid-black fills |

Age is a **visual-complexity preference**, not a model change by itself. Interpret “for teens” as a publication audience and content-complexity instruction; don't automatically switch to photorealism or anime without style cues.

## 7. Negative-prompt strategy

Construct negatives from task-specific failure modes rather than pasting every possible negative token into every prompt.

**General artifact suffix:** `blurry, low detail, jpeg artifacts, text, watermark, logo, signature, cropped subject, malformed anatomy, extra fingers, fused fingers`.

**Coloring-book suffix:** `color, grayscale shading, gray shadows, gradients, halftone, crosshatching, filled black areas, sketchy construction lines, broken outlines, open contours, cluttered background, text, watermark`.

**Storybook suffix:** `photorealistic, harsh flash, uncanny skin, excessive microtexture, gritty horror, cluttered composition, text, watermark, malformed anatomy`.

**Anime suffix:** `photorealistic, live action, western comic rendering` (only if those are not intended), plus `bad anatomy, extra digits, broken linework, text, watermark`.

**Photo suffix:** `illustration, cartoon, anime, 3d render, plastic skin, oversmoothed skin, overprocessed HDR, fake bokeh, text, watermark, malformed hands`.

**Sketch suffix:** `full color, glossy 3d, photorealistic color photo, plastic surfaces, clean vector fill` when the intended output is monochrome graphite.

**Pinting suffix:** use only when the style drifts: `photographic sharpness, vector outlines, plastic 3d surfaces, text, watermark`. Don't negate “brushstroke”, “texture”, “wash”, or “canvas” when those are the goal.

Rules:
- Don't place intended style words in the negative prompt (e.g. don't negate “watercolor” for a watercolor request).
- Negative prompts are not a substitute for a precise positive prompt. If subject, count, pose or composition fails, simplify/rewrite the positive prompt first.
- For nonfiction book art, add “no text, no labels, no numbers” and typeset labels in page-layout software afterward. Generated text and scientific labels should not be trusted.
- For print line art, inspect tiny spaces at actual print size. Add `closed contours, no hatching, pure black outlines, white background` to the positive prompt rather than relying on negatives alone.

## 8. Recipes with complete CLI commands

All commands use `--config-json`. They assume the selected model and exact LoRA/upscaler files are recognized by your installation. The commands use hires fix from a 768 px base to a 1024 px target when the chosen upscaler is part of the render. Set `--seed` for reproducible comparison; `--seed 0` may be random depending on CLI version, so recipes omit it for normal use. Add `--seed 31415` to all compared runs when evaluating.

### A. Preschool picture-book illustration (ages 3–5)
**Recommendation:** ColorfulXL + Storybook LoRA 0.82; sampler 0; 26 steps; CFG 5.2. Large readable shapes, saturated but gentle palette, simple background. Remacri ExtraSmoother keeps soft contours.

```bash
mkdir -p "$HOME/Dev/tmp" && draw-things-cli generate \
  --model colorfulxl_v6.0_f16.ckpt \
  --output "$HOME/Dev/tmp/preschool_fox_storybook.png" \
  --prompt "KidsRedmAF, Kids Book, colorful, a friendly red fox kit carrying a tiny blue umbrella through a puddle, full-body clear silhouette, eye-level view, one main character, simple garden path and two oversized flowers, cheerful picture-book watercolor and gouache, warm soft daylight, limited harmonious palette, generous whitespace around the character, simple child-friendly shapes, no text" \
  --negative-prompt "photorealistic, gritty texture, busy background, tiny repeated details, scary expression, excessive microtexture, text, watermark, malformed paws, extra limbs, blurry" \
  --width 768 --height 768 --steps 26 --cfg 5.2 \
  --config-json '{"sampler":0,"loras":[{"file":"StorybookRedmondV2-KidsBook-KidsRedmAF.safetensors","weight":0.82,"mode":"all"}],"hiresFix":true,"hiresFixWidth":1024,"hiresFixHeight":1024,"hiresFixStrength":0.28,"upscaler":"4x_foolhardy_Remacri_ExtraSmoother.safetensors","upscalerScaleFactor":4}'
```

### B. Early-reader story scene (ages 5–7)
**Recommendation:** Juggernaut v9 + Storybook LoRA 0.72; sampler 0; 28 steps; CFG 5.4. A single obvious action and background cues support sequencing.

```bash
mkdir -p "$HOME/Dev/tmp" && draw-things-cli generate \
  --model juggernaut_xl_v9_f16.ckpt \
  --output "$HOME/Dev/tmp/early_reader_garden.png" \
  --prompt "KidsRedmAF, Kids Book, colorful, two children planting a sunflower seed in a small garden bed, three-quarter view, clearly visible hands and watering can, friendly expressions, simple cottage garden, storybook gouache with soft paper texture, rounded shapes, bright warm palette, balanced composition, clean focus on the planting action, no text" \
  --negative-prompt "photorealistic, ominous mood, crowded background, tiny intricate foliage, confusing overlapping hands, text, watermark, malformed fingers, blur" \
  --width 768 --height 768 --steps 28 --cfg 5.4 \
  --config-json '{"sampler":0,"loras":[{"file":"StorybookRedmondV2-KidsBook-KidsRedmAF.safetensors","weight":0.72,"mode":"all"}],"hiresFix":true,"hiresFixWidth":1024,"hiresFixHeight":1024,"hiresFixStrength":0.26,"upscaler":"4x_foolhardy_Remacri_ExtraSmoother.safetensors","upscalerScaleFactor":4}'
```

### C. Middle-grade fantasy illustration (ages 8–12)
**Recommendation:** Juggernaut X + Storybook 0.60; optional Detail LoRA 0.20; sampler 0; 30 steps; CFG 5.6. Richer environmental storytelling while protecting focal clarity.

```bash
mkdir -p "$HOME/Dev/tmp" && draw-things-cli generate \
  --model juggernaut_xl_x_f16.ckpt \
  --output "$HOME/Dev/tmp/middle_grade_fantasy.png" \
  --prompt "KidsRedmAF, Kids Book, detailed, a young explorer discovering a glowing library hidden inside an ancient tree, full figure on the lower left, winding roots, tiny warm lanterns, readable arch-shaped doorway, layered forest depth, adventurous but gentle mood, painterly digital storybook illustration, rich teal and amber palette, cinematic rim light, clear focal hierarchy, no text" \
  --negative-prompt "photorealistic, horror, gore, chaotic composition, excessive foliage covering the doorway, extreme grunge, text, watermark, extra limbs, deformed hands" \
  --width 768 --height 768 --steps 30 --cfg 5.6 \
  --config-json '{"sampler":0,"loras":[{"file":"StorybookRedmondV2-KidsBook-KidsRedmAF.safetensors","weight":0.60,"mode":"all"},{"file":"add-detail-xl.safetensors","weight":0.20,"mode":"all"}],"hiresFix":true,"hiresFixWidth":1024,"hiresFixHeight":1024,"hiresFixStrength":0.30,"upscaler":"4x_NMKD-Superscale-SP_178000_G.safetensors","upscalerScaleFactor":4}'
```

### D. Teen nonfiction: rainforest ecology illustration (ages 13–18)
**Recommendation:** Juggernaut X, no style LoRA; optional Detail 0.18; sampler 0; 30 steps; CFG 5.0. Accurate visual hierarchy beats decorative styling; add callout labels later in layout.

```bash
mkdir -p "$HOME/Dev/tmp" && draw-things-cli generate \
  --model juggernaut_xl_x_f16.ckpt \
  --output "$HOME/Dev/tmp/teen_nonfiction_rainforest.png" \
  --prompt "educational natural-history illustration of a rainforest canopy cross-section, emergent trees above the canopy, understory, forest floor, vines, epiphytes, a toucan perched on a branch and a tree frog on a leaf, visually separated ecological layers, scientifically plausible plant forms, clean editorial illustration, natural greens with restrained earth tones, soft daylight, uncluttered shapes, no labels or text" \
  --negative-prompt "fantasy plants, impossible anatomy, repeated identical animals, overcrowded leaves, cartoon eyes, text, labels, numbers, watermark, blur, oversaturated colors" \
  --width 768 --height 768 --steps 30 --cfg 5.0 \
  --config-json '{"sampler":0,"loras":[{"file":"add-detail-xl.safetensors","weight":0.18,"mode":"all"}],"hiresFix":true,"hiresFixWidth":1024,"hiresFixHeight":1024,"hiresFixStrength":0.24,"upscaler":"RealESRGAN_x4plus.safetensors","upscalerScaleFactor":4}'
```

### E. Children's coloring page (ages 3–5)
**Recommendation:** ColoringBook LoRA 0.96; sampler 0; 26 steps; CFG 5.0. Use 3–5 large closed shapes, bold lines, and large open coloring areas. Do not add Detail LoRA.

```bash
mkdir -p "$HOME/Dev/tmp" && draw-things-cli generate \
  --model juggernaut_xl_v9_f16.ckpt \
  --output "$HOME/Dev/tmp/coloring_toddler_dinosaur.png" \
  --prompt "ColoringBookAF, Coloring Book, black and white printable coloring page for preschool children, one smiling baby dinosaur standing beside one large fern and a round sun, very bold smooth uniform black outlines, large simple closed shapes, few details, pure white background, no gray tones, no filled black areas, centered composition, wide white margins, no text" \
  --negative-prompt "color, colored fills, grayscale shading, gray shadows, gradients, halftone, crosshatching, solid black areas, thin scratchy lines, broken outlines, open contours, crowded background, text, watermark, blurry edges" \
  --width 768 --height 768 --steps 26 --cfg 5.0 \
  --config-json '{"sampler":0,"loras":[{"file":"ColoringBookRedmond-ColoringBook-ColoringBookAF.safetensors","weight":0.96,"mode":"all"}],"hiresFix":true,"hiresFixWidth":1024,"hiresFixHeight":1024,"hiresFixStrength":0.20,"upscaler":"4x_foolhardy_Remacri_ExtraSmoother.safetensors","upscalerScaleFactor":4}'
```

### F. Children's coloring page (ages 6–8)
**Recommendation:** ColoringBook LoRA 0.92; sampler 0; 28 steps; CFG 5.2. Add a few patterned objects and background structure while preserving large coloring cells.

```bash
mkdir -p "$HOME/Dev/tmp" && draw-things-cli generate \
  --model juggernaut_xl_v9_f16.ckpt \
  --output "$HOME/Dev/tmp/coloring_kids_camping.png" \
  --prompt "ColoringBookAF, Coloring Book, black and white kids coloring book page for ages 6 to 8, two friendly raccoons roasting marshmallows beside a small tent, a few stars and pine trees, bold consistent black line art, distinct closed contours, simple decorative patterns on the tent, medium-large areas to color, white background, clean spacing, no gray shading, no text" \
  --negative-prompt "color, grayscale, shadows, gradients, crosshatching, scratchy sketch lines, dense micro-patterns, large filled black shapes, tangled outlines, open contours, text, watermark, gray paper" \
  --width 768 --height 768 --steps 28 --cfg 5.2 \
  --config-json '{"sampler":0,"loras":[{"file":"ColoringBookRedmond-ColoringBook-ColoringBookAF.safetensors","weight":0.92,"mode":"all"}],"hiresFix":true,"hiresFixWidth":1024,"hiresFixHeight":1024,"hiresFixStrength":0.18,"upscaler":"4x-UltraSharpV2.safetensors","upscalerScaleFactor":4}'
```

### G. Teen coloring page (ages 9–12)
**Recommendation:** ColoringBook 0.95; sampler 0; 30 steps; CFG 5.3. Higher pattern density is appropriate but each region must remain closed and printable.

```bash
mkdir -p "$HOME/Dev/tmp" && draw-things-cli generate \
  --model juggernaut_xl_v9_f16.ckpt \
  --output "$HOME/Dev/tmp/coloring_teen_moon_garden.png" \
  --prompt "ColoringBookAF, Coloring Book, intricate but readable coloring book page for older children, moonlit botanical garden with a moth, layered leaves, winding stems, berries, tiny stars and a decorative gate, crisp black outlines, several levels of detail, all shapes enclosed, balanced negative space, white background, no solid fills, no grayscale, no text" \
  --negative-prompt "color, gradients, gray shadows, grayscale, halftone, photographic texture, charcoal smudges, broken contours, overlapping unreadable patterns, huge black filled areas, text, watermark" \
  --width 768 --height 768 --steps 30 --cfg 5.3 \
  --config-json '{"sampler":0,"loras":[{"file":"ColoringBookRedmond-ColoringBook-ColoringBookAF.safetensors","weight":0.95,"mode":"all"}],"hiresFix":true,"hiresFixWidth":1024,"hiresFixHeight":1024,"hiresFixStrength":0.18,"upscaler":"4x-UltraSharpV2.safetensors","upscalerScaleFactor":4}'
```

### H. Adult mandala coloring page
**Recommendation:** ColoringBook 0.98; sampler 0; 32 steps; CFG 5.0. Explicit radial symmetry and closed cells matter more than extra surface detail.

```bash
mkdir -p "$HOME/Dev/tmp" && draw-things-cli generate \
  --model juggernaut_xl_x_f16.ckpt \
  --output "$HOME/Dev/tmp/adult_mandala_owl.png" \
  --prompt "ColoringBookAF, Coloring Book, intricate adult coloring book page, perfectly centered radial mandala formed from a wise owl, crescent moon, feathers, leaves and repeating geometric petals, precise symmetrical rings, intricate closed regions of varied sizes, pure black outlines on pure white background, uniform clean line weight with fine interior details, no grayscale, no shading, no solid black fills, generous outer margin, no text" \
  --negative-prompt "color, colored fills, gray shadows, grayscale, gradients, halftone, crosshatching, pencil smudges, sketch lines, asymmetrical rings, open shapes, broken linework, large black filled areas, text, signature, watermark" \
  --width 768 --height 768 --steps 32 --cfg 5.0 \
  --config-json '{"sampler":0,"loras":[{"file":"ColoringBookRedmond-ColoringBook-ColoringBookAF.safetensors","weight":0.98,"mode":"all"}],"hiresFix":true,"hiresFixWidth":1024,"hiresFixHeight":1024,"hiresFixStrength":0.16,"upscaler":"4x-UltraSharpV2.safetensors","upscalerScaleFactor":4}'
```

### I. 2D anime illustration
**Recommendation:** Animagine XL v3.1 + LineAni 0.48; sampler 0; 28 steps; CFG 5.5. Anime model provides character priors; line-art LoRA strengthens ink structure without overwhelming color.

```bash
mkdir -p "$HOME/Dev/tmp" && draw-things-cli generate \
  --model animagine_xl_v3.1_f16.ckpt \
  --output "$HOME/Dev/tmp/anime_girl_reading.png" \
  --prompt "masterpiece, best quality, very aesthetic, absurdres, LineAniAF, lineart, 1girl, a teen anime student reading a thick astronomy book by a dormitory window, thoughtful expression, waist-up three-quarter view, clear hands holding the book, midnight blue hair, warm desk lamp and cool moonlight, clean cel shading, precise expressive outlines, star map pinned to the wall, detailed but uncluttered anime illustration, no text" \
  --negative-prompt "photorealistic, live action, 3d render, malformed hands, extra fingers, fused fingers, broken linework, muddy colors, text, watermark, logo, low contrast, blurry" \
  --width 768 --height 768 --steps 28 --cfg 5.5 \
  --config-json '{"sampler":0,"loras":[{"file":"LineAniRedmondV2-Lineart-LineAniAF.safetensors","weight":0.48,"mode":"all"}],"hiresFix":true,"hiresFixWidth":1024,"hiresFixHeight":1024,"hiresFixStrength":0.24,"upscaler":"RealESRGAN_x4plus_anime_6B.safetensors","upscalerScaleFactor":4}'
```

### J. Family-friendly 3D / animation still
**Recommendation:** ColorfulXL + 3D Render Style 0.62; sampler 0; 28 steps; CFG 5.4. Choose this over the Pixar slider when the user asks broadly for 3D-rendered illustration.

```bash
mkdir -p "$HOME/Dev/tmp" && draw-things-cli generate \
  --model colorfulxl_v6.0_f16.ckpt \
  --output "$HOME/Dev/tmp/3d_cartoon_turtle.png" \
  --prompt "3D style, 3D render, a cheerful small turtle inventor showing a cardboard rocket to a friend, appealing stylized proportions, smooth clay-like shell, large readable eyes, soft studio key light, gentle contact shadows, colorful family animation still, simple pastel workshop background, medium shot, clear silhouette, polished materials, no text" \
  --negative-prompt "flat black-and-white line art, horror, photorealistic reptile, gritty pores, overly glossy plastic, harsh specular highlights, clutter, text, watermark, malformed limbs" \
  --width 768 --height 768 --steps 28 --cfg 5.4 \
  --config-json '{"sampler":0,"loras":[{"file":"3d_render_style_xl.safetensors","weight":0.62,"mode":"all"}],"hiresFix":true,"hiresFixWidth":1024,"hiresFixHeight":1024,"hiresFixStrength":0.28,"upscaler":"4x_NMKD-Superscale-SP_178000_G.safetensors","upscalerScaleFactor":4}'
```

### K. Pixar-style family character
**Recommendation:** ColorfulXL + Pixar Style 0.50; sampler 0; 26 steps; CFG 5.0. Use as an alternative to recipe J, not together by default.

```bash
mkdir -p "$HOME/Dev/tmp" && draw-things-cli generate \
  --model colorfulxl_v6.0_f16.ckpt \
  --output "$HOME/Dev/tmp/pixar_style_lost_penguin.png" \
  --prompt "pixar-style, a tiny penguin wearing an oversized yellow scarf, standing at a snowy train platform and looking hopeful, expressive eyes, appealing rounded silhouette, polished stylized 3D animation, soft global illumination, teal and amber color contrast, medium-wide shot, simple snow-covered station, cinematic family-film composition, no text" \
  --negative-prompt "flat coloring-book line art, realistic wildlife photo, horror, uncanny face, plastic glare, busy background, text, watermark, malformed wings" \
  --width 768 --height 768 --steps 26 --cfg 5.0 \
  --config-json '{"sampler":0,"loras":[{"file":"pixar-style.safetensors","weight":0.50,"mode":"all"}],"hiresFix":true,"hiresFixWidth":1024,"hiresFixHeight":1024,"hiresFixStrength":0.28,"upscaler":"4x_NMKD-Superscale-SP_178000_G.safetensors","upscalerScaleFactor":4}'
```

### L. Pencil / artistic sketch
**Recommendation:** Juggernaut v9 + Sketch Style 0.62; sampler 0 or 1; 30 steps; CFG 5.0. Specify paper, pencil grade, mark density and whether the sketch should stay unfinished.

```bash
mkdir -p "$HOME/Dev/tmp" && draw-things-cli generate \
  --model juggernaut_xl_v9_f16.ckpt \
  --output "$HOME/Dev/tmp/pencil_sketch_barn_owl.png" \
  --prompt "graphite pencil sketch of a barn owl perched on a weathered branch, three-quarter profile, anatomical feather structure, varied pencil pressure, fine cross-contours, visible graphite strokes on warm white drawing paper, delicate hatching concentrated under the wings, lightly suggested background, observational natural-history sketch, no color" \
  --negative-prompt "full color, glossy 3d, polished vector art, photorealistic color photograph, plastic texture, heavy charcoal smears, messy construction lines obscuring the subject, text, watermark" \
  --width 768 --height 768 --steps 30 --cfg 5.0 \
  --config-json '{"sampler":0,"loras":[{"file":"sketch-style-xl.safetensors","weight":0.62,"mode":"all"}],"hiresFix":true,"hiresFixWidth":1024,"hiresFixHeight":1024,"hiresFixStrength":0.22,"upscaler":"RealESRGAN_x2plus.safetensors","upscalerScaleFactor":2}'
```

### M. Oil painting
**Recommendation:** Juggernaut v9 + Oil Painting Slider 0.52; sampler 0; 32 steps; CFG 5.2. Use only one oil slider initially; increase weight if the result is too photographic.

```bash
mkdir -p "$HOME/Dev/tmp" && draw-things-cli generate \
  --model juggernaut_xl_v9_f16.ckpt \
  --output "$HOME/Dev/tmp/oil_painting_harbor.png" \
  --prompt "oil painting of a small fishing harbor at dawn, wet boats and reflections, broad confident brush strokes, visible impasto highlights on the water, canvas tooth, layered pigments, muted cobalt blue and warm ochre palette, painterly edges, balanced fine-art composition, believable perspective, soft overcast light, no lettering" \
  --negative-prompt "photographic sharpness, vector outlines, flat digital gradients, glossy 3d surfaces, oversmoothed texture, text, watermark, malformed boats, distorted horizon" \
  --width 768 --height 768 --steps 32 --cfg 5.2 \
  --config-json '{"sampler":0,"loras":[{"file":"oil-painting-slider.safetensors","weight":0.52,"mode":"all"}],"hiresFix":true,"hiresFixWidth":1024,"hiresFixHeight":1024,"hiresFixStrength":0.26,"upscaler":"4x_NMKD-Superscale-SP_178000_G.safetensors","upscalerScaleFactor":4}'
```

### N. Watercolor storybook illustration
**Recommendation:** Juggernaut v9 + Storybook 0.38 (supporting use only); sampler 0 or 1; 30 steps; CFG 5.0. No watercolor-specific LoRA is in the allowed list, so use medium language and a low Storybook weight for a storybook sensibility.

```bash
mkdir -p "$HOME/Dev/tmp" && draw-things-cli generate \
  --model juggernaut_xl_v9_f16.ckpt \
  --output "$HOME/Dev/tmp/watercolor_seaside.png" \
  --prompt "KidsRedmAF, Kids Book, a small sailboat crossing a calm seaside bay, translucent watercolor washes, pigment blooms, soft wet-on-wet edges, visible cold-press paper grain, pale cerulean and coral palette, distant headland and a few seabirds, airy book illustration, simple readable shapes, gentle afternoon light, no text" \
  --negative-prompt "hard vector edges, glossy 3d, photorealistic camera rendering, oil impasto, muddy overworked pigment, heavy black outlines, clutter, text, watermark" \
  --width 768 --height 768 --steps 30 --cfg 5.0 \
  --config-json '{"sampler":0,"loras":[{"file":"StorybookRedmondV2-KidsBook-KidsRedmAF.safetensors","weight":0.38,"mode":"all"}],"hiresFix":true,"hiresFixWidth":1024,"hiresFixHeight":1024,"hiresFixStrength":0.22,"upscaler":"4x_foolhardy_Remacri_ExtraSmoother.safetensors","upscalerScaleFactor":4}'
```

### O. Analog film / editorial photography
**Recommendation:** Juggernaut X + AnalogRedmond 0.58; sampler 0; 32 steps; CFG 5.2. Trigger explicitly activates the analog style; specify lens and light, not only film grain.

```bash
mkdir -p "$HOME/Dev/tmp" && draw-things-cli generate \
  --model juggernaut_xl_x_f16.ckpt \
  --output "$HOME/Dev/tmp/analog_film_bicycle.png" \
  --prompt "AnalogRedmAF, Analog, candid analog film photograph of a young adult riding a bicycle along a quiet tree-lined street after rain, 35mm lens, eye-level documentary framing, natural skin texture, subtle halation around highlights, fine organic film grain, soft overcast daylight, restrained warm color response, realistic wet pavement reflections, authentic imperfect film exposure, no text" \
  --negative-prompt "illustration, anime, cartoon, 3d render, plastic skin, excessive clarity, overprocessed HDR, fake bokeh, oversaturated colors, text, logo, watermark, malformed hands, blur" \
  --width 768 --height 768 --steps 32 --cfg 5.2 \
  --config-json '{"sampler":0,"loras":[{"file":"AnalogRedmondV2-Analog-AnalogRedmAF.safetensors","weight":0.58,"mode":"all"}],"hiresFix":true,"hiresFixWidth":1024,"hiresFixHeight":1024,"hiresFixStrength":0.20,"upscaler":"RealESRGAN_x4plus.safetensors","upscalerScaleFactor":4}'
```

### P. Photorealistic wildlife / non-fiction photo
**Recommendation:** Juggernaut X, optional Detail LoRA 0.20; sampler 0; 34 steps; CFG 5.0. Skip analog and painterly LoRAs unless explicitly requested.

```bash
mkdir -p "$HOME/Dev/tmp" && draw-things-cli generate \
  --model juggernaut_xl_x_f16.ckpt \
  --output "$HOME/Dev/tmp/photorealistic_kingfisher.png" \
  --prompt "photorealistic wildlife photograph of a sacred kingfisher perched on a weathered mangrove branch, sharp natural feather structure, small water droplets on the bark, bird at eye level, 400mm telephoto lens, soft morning side light, distant creamy natural bokeh, accurate bird proportions, realistic color and exposure, documentary natural-history photography, no text" \
  --negative-prompt "painting, drawing, illustration, anime, cartoon, 3d render, plastic feathers, oversaturated color, crunchy HDR, fake bokeh, duplicated bird, malformed beak, text, watermark, blur" \
  --width 768 --height 768 --steps 34 --cfg 5.0 \
  --config-json '{"sampler":0,"loras":[{"file":"add-detail-xl.safetensors","weight":0.20,"mode":"all"}],"hiresFix":true,"hiresFixWidth":1024,"hiresFixHeight":1024,"hiresFixStrength":0.18,"upscaler":"RealESRGAN_x4plus.safetensors","upscalerScaleFactor":4}'
```

### Q. Informative black-and-white biology line art
**Recommendation:** ColoringBook LoRA 0.70–0.85 if printable worksheet line art is desired; otherwise omit that LoRA for clean editorial diagrams. Sampler 2 or 0; 28 steps; CFG 4.8. Keep labels out of the generated art.

```bash
mkdir -p "$HOME/Dev/tmp" && draw-things-cli generate \
  --model juggernaut_xl_v9_f16.ckpt \
  --output "$HOME/Dev/tmp/biology_butterfly_line_art.png" \
  --prompt "ColoringBookAF, Coloring Book, clean educational black-and-white line illustration of a butterfly in dorsal view with symmetrical wings, anatomically plausible wing veins, head thorax and abdomen clearly separated, a few host plant leaves below, thin consistent black contour lines, no labels, no arrows, no text, white background, uncluttered textbook figure" \
  --negative-prompt "color, gradients, gray shading, decorative mandala, excessive patterning, inaccurate wing anatomy, overlapping body parts, broken contours, text, numbers, watermark, solid black background" \
  --width 768 --height 768 --steps 28 --cfg 4.8 \
  --config-json '{"sampler":2,"loras":[{"file":"ColoringBookRedmond-ColoringBook-ColoringBookAF.safetensors","weight":0.78,"mode":"all"}],"hiresFix":true,"hiresFixWidth":1024,"hiresFixHeight":1024,"hiresFixStrength":0.16,"upscaler":"4x_foolhardy_Remacri_ExtraSmoother.safetensors","upscalerScaleFactor":4}'
```

## 9. Decision rules for an agent

Apply constraints in this order:

1. **Hard output constraint:** coloring page / pure line art overrides ordinary style choice; use ColoringBook LoRA, white background, closed outlines, no shading. If “manga line art” is requested, use LineAni instead or as a low-weight support.
2. **Explicit medium/style:** anime → Animagine; analog film/photography → Juggernaut X + AnalogRedmond; broad 3D render → ColorfulXL + 3d_render_style; Pixar-like family animation → ColorfulXL + pixar-style; sketch → Sketch Style; oil painting → one oil slider; watercolor → prompt medium words and optionally low Storybook LoRA for book-like softness.
3. **Audience / age:** use age to set count of objects, edge thickness, detail density, negative space and contrast—not to automatically switch the model.
4. **Visual complexity:** use one primary LoRA. Add Detail LoRA only where detail is desired and not harmful to the intended medium.
5. **Upscaler:** linework/simple illustration → Remacri ExtraSmoother; bold graphic lines → UltraSharpV2 only if no halos; anime → RealESRGAN anime 6B; photos → RealESRGAN x4plus; mixed painterly texture → NMKD; conservative 2x → RealESRGAN x2plus.
6. **Prompt completeness check:** subject, action, composition, style, lighting/palette, output constraints and LoRA trigger are all accounted for.
7. **Negative check:** ensure no desired style term appears in negative prompt. Add media-specific and task-specific failures, not a universal mega-list.
8. **Quality evaluation:** score subject correctness, composition, line closure (if coloring), readability at print size, style adherence, unwanted text, hand/face defects, and overprocessing. If anatomy/composition fails, regenerate rather than trying to fix it with an upscaler.

### Lightweight scoring rubric (0–5 each)

- `subject_match`: requested objects/actions/count are present.
- `composition_readability`: focal point and spacing suit intended age/format.
- `style_match`: chosen model/LoRA/medium is visible but not overpowering.
- `technical_cleanliness`: edges, hands, faces, and textures have no obvious defects.
- `print_suitability`: sufficient resolution, safe margins, no tiny broken contours or unreadable black fills.
- `content_accuracy`: anatomy/ecology/diagram relationships are plausible; all generated text removed or separately typeset.

Total score is a useful ranking heuristic, not a calibrated probability. Use genre-specific weights: print/coloring should weight `print_suitability` and line closure highest; nonfiction should weight `content_accuracy` and `subject_match`; photography should weight `technical_cleanliness` and realistic materials; picture books should weight `composition_readability` and `style_match`.

## 10. Troubleshooting / tuning

- **Style too weak:** verify exact trigger token; raise dominant LoRA +0.05–0.10; do not immediately raise CFG.
- **Style overpowering subject:** reduce dominant LoRA by 0.10–0.20; remove the secondary LoRA.
- **Coloring page turns gray/shaded:** remove Detail LoRA; increase ColoringBook weight slightly; add `pure black outlines, pure white background, no gray tones, no solid fills`; reduce hires-fix strength or skip hires fix.
- **Linework overly sharp / halos:** switch UltraSharpV2 → Remacri ExtraSmoother or render without hires fix.
- **Oil/watercolor looks photographic:** reduce CFG slightly, strengthen medium words, adjust oil slider modestly; avoid AnalogRedmond and Detail LoRA.
- **Photo looks painterly/plastic:** remove painting/3D/storybook LoRAs; lower Detail LoRA; use specific camera/lighting language and RealESRGAN x4plus or x2plus.
- **Anime linework too thick:** lower LineAni weight; omit add-detail; increase `lineart` specificity only if needed.
- **Too many objects / visual chaos:** state object count, simplify background, limit patterns and set focal placement.
- **Text gibberish:** prompt for blank signs/pages/labels and add `text, letters, watermark` to negative prompt; add typography during layout.
- **LoRA appears not to work:** check model/LoRA compatibility, exact filename and registered metadata; CLI documentation notes unregistered local LoRAs may require `loras[].version`.
- **Comparisons are noisy:** fix seed, dimensions, sampler, steps, CFG and all other LoRA weights; vary just one setting at a time.

## 11. Sources and version notes

- Draw Things CLI release / general setup: https://releases.drawthings.ai/p/draw-things-cli-local-media-generation
- Draw Things community CLI source and current `JSGenerationConfiguration`: https://github.com/drawthingsai/draw-things-community/blob/main/Apps/DrawThingsCLI/DrawThingsCLI.swift and https://github.com/drawthingsai/draw-things-community/blob/main/Libraries/Scripting/Sources/ScriptModels.swift
- Current numeric sampler mapping in source-based notes: https://github.com/stainboy/drawthings-cli/blob/main/CLAUDE.md (cross-check against your installed version)
- StoryBookRedmond trigger/settings: https://artificialguy.com/blog/storybookredmond-v2-sdxl-childrens-book-lora/
- ColoringBookRedmond trigger/settings: https://artificialguy.com/blog/coloringbook-redmond-sdxl-lora-coloring-book/
- LineAniRedmond trigger/settings: https://artificialguy.com/blog/linearmangasdxl-v2-manga-lineart-lora-sdxl/
- AnalogRedmond V2 card: https://huggingface.co/artificialguybr/analogredmond-v2

Treat weights and recipes as starting points; model merges, LoRA copies, quantization, and CLI versions can change results. Always inspect outputs and retain seeds/metadata for accepted images.
