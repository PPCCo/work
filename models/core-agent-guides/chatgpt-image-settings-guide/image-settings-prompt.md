# Prompt for image-settings (Same promot given to ChatGPT and Claude)

Settings like cfg, upscalers and schedules are extremely important for generating the best results for different types and styles of images.

On my Macbook Pro M4 (12-core, 48 GB Unified Memory), I'm using "draw-things-cli" with qwen_image_2512_bf16_q8p.ckpt (Qwen BF16 8-bit S) and Flux.2-Klein and SDXL (juggernaut_xl_v9_f16, juggernaut_xl_x_f16, colorfulxl_v6.0_f16, and animagine_xl_v3.1_f16) to create images for Kids Reading Books, Illustrations books, Kids and adults Coloring Books & Line Art, Storybooks and Non-fiction Informative books for kids and teens, Adults Mandala Coloring Books, Pencil & Artistic Sketch books, oil and watercolor paintings, 2D/3D anime illustrations, digital drawings, photography, oil painting, Photorealism, and other types of books.

For each groups (could be based on categories, genres, and age groups, etc), give comprehensive but concise (not too verbose) tips, strategies and suggestions on how and what cfg, samplers, etc to set. Also include (in brackets) numberic value for sampler.

Give example prompts and a brief explanation of why the specific values were used. An AI recommendation engine will be the consumer of this info, so keep the explanations very brief and not verbose. Think hard and add any other info that will help AI Agent in evaulation and making recommendations based on certain undeterministic user requirements.

All example commands should be executable and should use `--config-json` in this format:

```bash
draw-things-cli generate \
--model qwen_image_2512_bf16_q8p.ckpt \
--output '~/Dev/tmp/sdxl_coloring_adult_owl.png' \
--prompt "intricate adult coloring book page, mystical owl on a crescent moon, complex mandala patterns..." \
--negative-prompt "3d render, shading, gray shadows, sketch, charcoal, messy lines, text, bg color..." \
--width 768 --height 768 --steps 28 --cfg 5.5 \
--config-json '{
"sampler": 0,
"loras": ''
}'
```

# Files Generated

- `./image-recommendation-rules-chatgpt.json` - AI recommendation rules JSON - Structured profiles, candidate ranges, model-selection rules, constraints, confidence, and validation requirements.
- `./image-settings-playbook-chatgpt.md` - Settings playbook - Category-by-category recommendations, prompts, explanations, and nine complete CLI examples.
- `./image-settings-guide-claude.md` - Claude recommendations for Agent/Skill

# ChatGPT Response

Draw Things CLI Settings Playbook: Books & Illustration (Apple M4, 48 GB)

I’ve prepared a model-aware settings guide and machine-readable recommendation rules for your Draw Things CLI setup. They cover all six of your checkpoint types, 11 image-generation profiles, all 20 current sampler IDs, LoRA selection, upscaling, confidence levels, validation rules, and runnable command examples.

- `image-recommendation-rules-chatgpt.json` - AI recommendation rules JSON - Structured profiles, candidate ranges, model-selection rules, constraints, confidence, and validation requirements.
- `image-settings-playbook-chatgpt.md` - Settings playbook - Category-by-category recommendations, prompts, explanations, and nine complete CLI examples.

## 1. The most important model-specific defaults

These are starting points, not universal optimums. Sampler behaviour and the useful CFG range vary between model families.

| Model / family         | Steps | CFG     | Sampler (numeric ID)                               | Main use                                                       |
| ---------------------- | ----- | ------- | -------------------------------------------------- | -------------------------------------------------------------- |
| Qwen Image 2512        | 30–40 | 4.0     | Euler A Trailing (10)                              | Story illustrations, covers, educational art, prompt adherence |
| FLUX.2 Klein distilled | 4     | 1.0     | Euler A Trailing (10)                              | Fast drafts and efficient generation                           |
| FLUX.2 Klein Base      | 30–50 | \~4.0   | Euler A Trailing (10); compare UniPC Trailing (17) | Undistilled generation and experimentation                     |
| Juggernaut XL v9       | 30–40 | 3.0–6.0 | DPM++ 2M Karras (0)                                | Photorealism, realistic illustrations, pencil studies          |
| Juggernaut XL X        | 28–38 | 4.0–6.0 | DPM++ 2M Karras (0)                                | General-purpose SDXL-style artwork; calibrate separately       |
| ColorfulXL v6.0        | 26–36 | 5.0–6.2 | Euler A (1) or DPM++ 2M Karras (0)                 | Vivid storybooks, paintings, colorful digital illustrations    |
| Animagine XL v3.1      | 22–29 | 5.0–7.0 | Euler A (1)                                        | 2D anime, manga-style characters, stylized illustrations       |

The Qwen figures reflect practical Draw Things defaults; FLUX.2 Klein's official documentation distinguishes its distilled 4-step, guidance-1.0 models from the Base variants. Juggernaut XL v9 recommends DPM++ 2M Karras, 30–40 steps and CFG 3–7; Animagine recommends Euler Ancestral with CFG around 5–7 and fewer than 30 steps.&#x20;

Important: Never apply FLUX.2 Klein's 4-step settings to Qwen or a regular SDXL checkpoint. Conversely, increasing distilled Klein to 30–40 steps is not the normal quality-improvement path.

## 2. Profiles by book genre and image style

Use the ranges below as candidate settings for your AI agent. The prompt constraints are often as important as CFG and sampler selection.

| Category                            | Recommended starting settings                                                         | Key prompt strategy                                                                             |
| ----------------------------------- | ------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Preschool picture books (ages 2–5)  | Qwen: 28–36 steps, CFG 3.8–4.8, Euler A Trailing (10)                                 | One dominant subject, round shapes, warm palette, simple background, friendly expressions       |
| Children's storybooks (ages 6–9)    | ColorfulXL: 26–36, CFG 5–6.5, Euler A (1)                                             | Clear foreground/background, expressive characters, narrative action, consistent style          |
| Educational/non-fiction (ages 8–16) | Qwen: 32–44, CFG 3.8–5, Euler A Trailing (10)                                         | Clear components, precise spatial relationships, uncluttered composition, space for labels      |
| Kids' and teens' coloring pages     | Qwen: 28–38, CFG 3.8–5, Euler A Trailing (10); compare DPM++ 2M AYS (12)              | Pure black closed outlines, white background, consistent strokes, large colourable areas        |
| Adult mandala coloring              | Qwen: 30–42, CFG 4–5.2, DPM++ 2M AYS (12)                                             | Radial symmetry, repeating motifs, concentric rings, no shading or gray fills                   |
| Pencil/graphite/artistic sketch     | Juggernaut v9: 28–38, CFG 3.8–5.5, DPM++ 2M Karras (0)                                | Specify medium, stroke character, hatching, paper texture and tonal range                       |
| Watercolor/oil/gouache              | ColorfulXL: 28–40, CFG 4.8–6.2, Euler A (1) or DPM++ 2M Karras (0)                    | Watercolor washes and granulation, or oil impasto, glazing and visible brush marks              |
| 2D anime/manga                      | Animagine: 22–29, CFG 5–7, Euler A (1)                                                | Use anime quality tags, pose, expression, clothing, camera angle and lighting                   |
| Digital cartoon/stylized 3D         | ColorfulXL or Juggernaut XL X: 26–36, CFG 4.8–6.5, Euler A (1) or DPM++ 2M Karras (0) | Specify 2D versus 3D, materials, lighting, camera angle and shape language                      |
| Photorealistic photography          | Juggernaut v9: 30–40, CFG 3–6, DPM++ 2M Karras (0)                                    | Shot type, lens feel, natural lighting, focus plane, realistic textures and restrained contrast |
| Book covers/editorial artwork       | Qwen: 32–44, CFG 3.8–5.2, Euler A Trailing (10)                                       | Specify focal-point placement, title-safe space, visual hierarchy and final trim ratio          |

These are category-level heuristics. Your JSON file assigns confidence per profile and tells the agent which settings to validate rather than assuming every combination will work equally well.

## 3. Executable command example

This example generates a children's coloring page. The full playbook contains nine runnable examples covering the main use cases.

```
mkdir -p "$HOME/Dev/tmp"

draw-things-cli generate \
  --model qwen_image_2512_bf16_q8p.ckpt \
  --output "$HOME/Dev/tmp/kids_coloring_dragon.png" \
  --prompt "A printable children's coloring-book page of a cheerful baby dragon reading a book under a tree, pure black clean uniform outlines on a pure white background, closed shapes, simple bold contours, large open spaces to colour, minimal background details, no gray, no shading, no hatching, no text." \
  --negative-prompt "colour, gray fill, grayscale shading, gradients, shadows, hatching, crosshatching, stippling, pencil texture, sketch, gray background, text, watermark, broken outlines, messy lines" \
  --width 768 --height 1024 --steps 32 --cfg 4.2 \
  --config-json '{"sampler":10,"shift":1.0,"resolutionDependentShift":true,"loras":[]}'
```

Why these settings? The portrait dimensions suit a coloring-book page. CFG 4.2 is a moderate prompt-guidance starting point for Qwen; 32 steps allows detail refinement. Euler A Trailing (10) follows the Qwen starting profile, while the negative prompt discourages gray texture and shading.

The JSON syntax in your example needed one correction: use `"loras":[]` when no LoRAs are selected. An empty string is not a valid LoRA array.

## 4. Sampler and schedule rules for the agent

Draw Things' published schema represents its samplers as numeric enum values. Useful IDs include DPM++ 2M Karras (0), Euler A (1), Euler A Trailing (10), DPM++ 2M AYS (12) and UniPC Trailing (17). The complete 20-item mapping is included in the playbook and JSON.&#x20;

Do not treat the sampler ID as a ComfyUI sampler ID or assume a separate `scheduler` field works. Draw Things has variants such as Karras, AYS and Trailing represented by sampler choices. Since numeric values depend on the current schema, have the agent revalidate them whenever the CLI version changes.

For comparison testing, start with the recommended sampler, then compare one alternative using the same seed, prompt, resolution, steps and CFG. That makes it easier to tell whether the sampler actually improved the result.

## 5. Upscaling and print quality

Upscaling should happen after you select a good composition—not as a substitute for generating the right image.

- Photorealism: Try a supported detail-oriented upscaler, such as `4x_NMKD-Siax_200k` or `4x_foolhardy_Remacri` if available in your installation. For a second generation pass, start around 0.25–0.35 denoising strength to limit composition drift.
- Storybooks and digital illustrations: Start with a modest 1.25–1.5× upscale; inspect facial features, brush texture and contour sharpness.
- Coloring pages and mandalas: Prefer ordinary high-quality resampling, threshold cleanup or vectorization. Generative upscaling can introduce gray fills, stray marks and broken outlines.
- Print production: For an 8 × 10 inch page at 300 DPI, the final layout needs 2400 × 3000 pixels. Create the illustration, upscale it, and then verify trim, bleed and safe margins in your publishing software.

Use the exact upscaler filename shown by your installed `draw-things-cli generate --help`; available filenames can vary by version and installation.

## 6. What makes the JSON useful to an AI agent

The rules file is designed to support more than static presets. It includes model-selection priorities, candidate parameter ranges, prompt constraints, confidence, upscaling strategies and validation requirements.

A good recommendation flow should:

1. Respect the requested checkpoint and distinguish FLUX.2 Klein distilled from Klein Base.
2. Select a category profile, then adjust composition and visual complexity to the requested audience.
3. Validate model/LoRA/upscaler compatibility before constructing the command.
4. Change one setting at a time during comparisons and preserve the seed and complete configuration.
5. Require visual checks for broken coloring outlines, anatomy, illegible text, repeated motifs and educational accuracy.

For educational books, the agent should recommend generating clean, label-free artwork and adding verified labels in layout software. For mandalas, it should explicitly warn that AI-generated geometry may need manual correction even with the best-looking sampler.

# Claude Response

I'll check the current Draw Things CLI config options and sampler IDs first, then write this up as a single reference file for your recommendation engine.

I've written the playbook as one markdown file for your recommendation agent. All 12 example commands passed a check for valid JSON, sampler IDs in range and quoting. I haven't run any of them through `draw-things-cli`, so the settings themselves are untested.

It covers 14 categories, from kids and adult coloring pages and mandalas to storybooks, non-fiction diagrams, sketch, watercolor, oil, anime, 3D, photoreal and covers. Each has a recommended model, steps, cfg, sampler ID, resolution, upscaler and negative prompt. It also has an agent quick-start, age-group modifiers, print sizing, a troubleshooting table and an A/B test routine.

- **Sampler IDs:** these come from Draw Things' own enum, e.g. UniPC Trailing is 17, Euler A is 1, DPM++ 2M Karras is 0.
- **JSON in the commands:** I used `"loras": []` rather than `''` from your template, because `''` isn't valid JSON.
- **Output paths:** I used `"$HOME/Dev/tmp/..."`, since `'~/...'` in single quotes doesn't expand in the shell.
- **Verified vs. guessed:** the guide marks which numbers come from model cards or Draw Things sources and which are my starting points to confirm with a fixed-seed A/B test. ColorfulXL, Juggernaut X and Klein settings are mostly the latter.
- **Klein variant:** I assumed `flux_2_klein_base_4b_f16.ckpt` is the distilled version (4–8 steps, cfg 1). If it behaves like the Base version, use the Base row (20+ steps, cfg 3.5–4).
- **Licences:** a licence table is included because you plan commercial books. Remacri and UltraSharp upscalers are non-commercial, so the guide defaults to the BSD-licensed RealESRGAN files. Check the Klein, Juggernaut and ColorfulXL terms yourself.

I also saved your model list and the categories you want covered to your memory notes in `./image-settings-guide-claude.md`

Sources are listed at the end of the file.
