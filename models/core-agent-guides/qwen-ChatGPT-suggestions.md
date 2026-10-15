# Qwen Image 2512: book-cover recommendation engine system

For your MacBook Pro M4 with 12 CPU cores and 48 GB unified memory, I recommend building the system around Qwen Image 2512 as the primary model, a category-specific generation profile, and a separate upscaling decision. The recommendation engine should optimise for the intended audience, illustration style, typography, print dimensions, and visual complexity rather than using one configuration for every book.

Qwen Image 2512 is designed for text-and-image generation, making it a sensible starting point for covers that combine artwork with a title, series name, and publisher name. Its reference workflows commonly use approximately 50 steps, CFG 4, and Euler sampling; these are starting points, not guaranteed optimal settings for every cover.&#x20;

## 1. Recommendation rules and command guide

I created two files for your agent workflow.

- `qwen-book-cover-settings-rules.json` - Recommendation rules JSON - 15 profiles, 6 permitted upscalers, 8 selection rules, constraints, confidence levels, scoring weights, and validation requirements.

- `qwen-settings-and-command-guide.md` - Executable generation examples, positive and negative prompts, parameter recommendations, and operational caveats.

The JSON covers early readers, children's storybooks, tweens, young-adult fantasy, children's colouring books, adult mandalas, pencil sketches, watercolour, oil painting, 2D anime, stylised 3D, photorealism, editorial nonfiction, landscape photography, and text-priority covers.

## 2. Core recommendation principles

**Children's reading books and storybooks**:

Prioritise readable silhouettes, warm colours, expressive characters, simplified backgrounds, and generous title space.

Starting profile: 30–40 steps, CFG 3.5–4.5, `realesrgan_x4plus_f16.ckpt` if available in your installed upscaler list.

**Colouring books and line art**:

Prioritise closed contours, clean white negative space, printable line thickness, and minimal accidental shading.

Starting profile: 35–45 steps, CFG 3.5–4.5, `4x_foolhardy_remacri_extrasmoother_f16.ckpt` for testing smooth contours.

**Fantasy, adult fiction, and painterly covers**:

Prioritise atmosphere, controlled contrast, clear focal points, and enough quiet space for typography.

Starting profile: 40–50 steps, CFG 3.5–4.5, `4x_nmkd_superscale_sp_178000_g_f16.ckpt` for a detail-oriented upscale trial.

**Non-fiction, photography, and informative books**:

Prioritise subject accuracy, clear visual hierarchy, restrained backgrounds, and a professional editorial look.

Starting profile: 40–50 steps, CFG 3.5–4.5, `realesrgan_x4plus_f16.ckpt` or `realesrgan_x2plus_f16.ckpt` depending on final print size.

These are initial hypotheses for controlled testing, not benchmark results. The rules should be calibrated against your actual `draw-things-cli` build and the six upscalers you have installed.

## 3. Executable command examples

All examples use your Qwen checkpoint and `--config-json`. The sampler ID `[0]` below means numeric ID `0`; its exact mapping must be verified against your installed CLI version.

### A. Children's storybook

```
draw-things-cli generate \
  --model qwen_image_2512_bf16_q8p.ckpt \
  --output "$HOME/Dev/tmp/kids_storybook_cover.png" \
  --prompt 'Portrait picture-book cover for early readers, a curious little red fox holding a yellow umbrella in a friendly rainy woodland, rounded shapes, expressive gentle face, warm storybook watercolor and gouache, uncluttered background, strong silhouette, upper title area reserved, exact title "FOX AND THE RAINY DAY", series name "LITTLE WOODLAND READERS", publisher name "ACORN HOUSE", readable child-friendly lettering, safe margins.' \
  --negative-prompt 'misspelled words, extra letters, duplicate title, watermark, cropped title, text touching edges, frightening expression, horror, cluttered background, tiny busy details, muddy colours, distorted face, extra limbs, blurry subject' \
  --width 1024 --height 1536 --steps 36 --cfg 4.0 \
  --config-json '{"sampler":0}'
```

- Steps: 36 — efficient first-pass quality.
- CFG: 4.0 — balanced prompt adherence.
- Sampler: [0] — provisional numeric ID.
- Upscaler candidate: `realesrgan_x4plus_f16.ckpt`.

### B. Adult mandala colouring cover

```
draw-things-cli generate \
  --model qwen_image_2512_bf16_q8p.ckpt \
  --output "$HOME/Dev/tmp/adult_mandala_cover.png" \
  --prompt 'Square adult mandala coloring-book cover, perfectly centered intricate radial mandala with botanical petals, paisley, fine geometric rosettes and repeating symmetrical ornaments, clean black contour lines on pure white background, consistent printable line weight, closed shapes with ample spaces for colouring, no grey fill, no gradients, no shadows, crisp vector-like line art, leave a clear top title band, exact title "MINDFUL MANDALAS", subtitle "A CALMING COLOURING COLLECTION", publisher "PAPER FERN PRESS", high-contrast typography, safe margins.' \
  --negative-prompt 'colour inside line-art, gray fill, grayscale shading, gradients, drop shadows, pencil texture, crosshatching, sketchy strokes, broken contours, open gaps, fuzzy edges, dense black blobs, asymmetry, misspelled text, extra text, watermark, cropped border' \
  --width 1024 --height 1024 --steps 42 --cfg 4.0 \
  --config-json '{"sampler":0}'
```

- Steps: 42 — prioritises intricate contour development.
- CFG: 4.0 — a baseline for following the detailed pattern instructions.
- Sampler: [0] — provisional numeric ID.
- Upscaler candidates: `4x_ultrasharp_f16.ckpt`, `4x_foolhardy_remacri_extrasmoother_f16.ckpt`, and `realesrgan_x2plus_f16.ckpt`.

The most important validation is whether the upscaled image retains closed shapes and printable line thickness.

### C. Photorealistic nonfiction cover

```
draw-things-cli generate \
  --model qwen_image_2512_bf16_q8p.ckpt \
  --output "$HOME/Dev/tmp/nonfiction_photo_cover.png" \
  --prompt 'Portrait photorealistic editorial book cover, a weathered red canoe beside a still alpine lake at dawn, natural atmospheric haze, physically plausible reflections, fine wood grain, restrained editorial colour grading, realistic exposure, one clear focal subject, calm upper third for title, exact title "WHERE THE WATER WAITS", series name "FIELD NOTES", publisher name "NORTHSTAR BOOKS", refined high-contrast typography, safe margins.' \
  --negative-prompt 'illustration, cartoon, anime, CGI sheen, impossible reflections, warped objects, oversaturated HDR, excessive clarity, unnatural fog, duplicate canoe, misspelled words, random text, watermark, cropped title, illegible typography' \
  --width 1024 --height 1536 --steps 48 --cfg 4.0 \
  --config-json '{"sampler":0}'
```

- Steps: 48 — a higher-quality candidate for fine textures.
- CFG: 4.0 — avoids assuming that aggressive guidance improves realism.
- Sampler: [0] — provisional numeric ID.
- Upscaler candidates: `realesrgan_x4plus_f16.ckpt` and `realesrgan_x2plus_f16.ckpt`.

Prefer the 2× candidate if 4× enlargement introduces harsh edges or artificial texture.

Important upscaler limitation: I have not invented an upscaler command-line flag. The generation examples are executable generation commands, but selecting an upscaler must use the option or workflow supported by your installed `draw-things-cli` version. The filenames in the JSON are recommendations, not proof that an upscaler can be selected through `--config-json`.

## 4. Rules your AI agent should enforce

Typography takes priority when exact wording is mandatory.

Reduce background complexity, reserve a title zone, and validate title, series, and publisher names with OCR or manual proofreading. Upscaling does not correct misspellings.

Select upscalers by image characteristics.

Choose anime-oriented upscaling for cel-shaded art, conservative smoothing for delicate washes, and a detail-oriented candidate for complex painterly art. Require visual inspection.

Keep model compatibility explicit.

Your other permitted checkpoints are SDXL-family models. Do not assume their SDXL LoRAs work with Qwen Image 2512; keep LoRA selection disabled for Qwen until compatibility is verified.

Evaluate the actual deliverable, not just generation success.

Score text accuracy, composition, genre fit, visual quality, print readiness, and upscaler artifacts separately. Reject outputs with critical text errors or cropped typography.

## 5. Recommended calibration procedure

Before using the JSON for automatic production, run a small benchmark:

1. Fix the prompt and seed.
2. Compare 32, 40, and 50 steps at CFG 4.0.
3. Verify the sampler ID mapping for your CLI build.
4. Compare two or three relevant upscalers on the same output.
5. Inspect the cover at thumbnail size and at 100% zoom.
6. Validate text spelling and the final print dimensions.

The official Qwen Image 2512 model references and Draw Things CLI documentation provide a useful baseline, but runtime support and sampler mappings should be confirmed locally.

The resulting JSON is designed as a recommendation policy with explicit uncertainty, rather than a collection of universal settings. Its confidence levels should be raised only after repeatable testing on your actual MacBook and installed CLI build.