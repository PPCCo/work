I'm using Flux Klein and SDXL (juggernaut_xl_v9_f16, juggernaut_xl_x_f16, colorfulxl_v6.0_f16, and animagine_xl_v3.1_f16) to create Kids Reading Book Illustrations, Kids and adults Coloring Books & Line Art, Adults Mandala Coloring Books, Pencil & Artistic Sketches, 2D/3D anime illustrations, digital drawings, photography, oil painting, Photorealism, etc.

For each genre, can you create a markdown table with recommendations on which models, loras (multi-loras are okay if needed), along with other settings like steps, guidanceScale, sampler.

---
On my Macbook Pro M4 (12-core, 48 GB Unified Memory), I'm using "draw-things-cli" with flux_2_klein_4b_f16.ckpt.

I wanted to use WikiQwen-Illustrator for how-to illustration books for kids but the license doesn't allow Commercial Use. What are the alternatives that are compatible with draw-things-cli and free for Commercial Use

---

For each genre and age group, can you think hard and come up with good examples that would illustrate good use of models, loras, as well as prompting (prompt and --negative-prompt), sampler (if needed), steps, cfg, etc etc with a brief explanation of why the specific values and prompts were used. An AI Agent and recommendation engine will be the consumer of this info, so keep the explanations very brief and not verbose. Think hard and add any other info that will help AI Agent in evaulation and making recommendations based on certain undeterministic user requirements.

All commands should be executable in and should use `--config-json` in this format:

```json
draw-things-cli generate \
--model juggernaut_xl_x_f16.ckpt \
--output '~/Dev/tmp/sdxl_coloring_adult_owl.png' \
--prompt "intricate adult coloring book page, mystical owl on a crescent moon, complex mandala patterns..." \
--negative-prompt "3d render, shading, gray shadows, sketch, charcoal, messy lines, text, bg color..." \
--width 768 --height 768 --steps 28 --cfg 5.5 \
--config-json '{
"sampler": 0,
"loras": [
    {"file": "LORA_1.ckpt", "weight": 0.85, "mode": "all"},
    {"file": "LORA_2.ckpt", "weight": 0.50, "mode": "all"}
  ]
}'
```

---

# FINAL PROMPT

I'm using "draw-things-cli" with Flux-2-Klein and SDXL (juggernaut_xl_v9_f16, juggernaut_xl_x_f16, colorfulxl_v6.0_f16, and animagine_xl_v3.1_f16) to create Kids Reading Book Illustrations, Kids and adults Coloring Books & Line Art, Adults Mandala Coloring Books, Pencil & Artistic Sketches, 2D/3D anime illustrations, digital drawings, photography, oil painting, Photorealism, etc.

I can only use these Models, LoRAs, and Upscalers:

## Models

flux_2_klein_4b_f16.ckpt
flux_2_klein_base_4b_f16.ckpt

flux_2_klein_4b_q8p.ckpt
flux_2_klein_base_4b_q8p.ckpt

juggernaut_xl_v9_f16.ckpt
juggernaut_xl_x_f16.ckpt
colorfulxl_v6.0_f16.ckpt
animagine_xl_v3.1_f16.ckpt

## SDXL LoRAs - Original Names

- 3d_render_style_xl.safetensors
- add-detail-xl.safetensors
- AnalogRedmondV2-Analog-AnalogRedmAF.safetensors
- ColoringBookRedmond-ColoringBook-ColoringBookAF.safetensors
- epic-oil-painting-slider.safetensors
- oil-painting-slider.safetensors
- LineAniRedmondV2-Lineart-LineAniAF.safetensors
- pixar-style.safetensors
- sketch-style-xl.safetensors
- StorybookRedmondV2-KidsBook-KidsRedmAF.safetensors

## SDXL LoRAs - New Names

3d_render_style_xl_lora_f16.ckpt
add_detail_xl_lora_f16.ckpt
redmondv2_analog_lora_f16.ckpt
redmond_coloringbook_lora_f16.ckpt
oil_painting_slider_epic_lora_f16.ckpt
oil_painting_slider_lora_f16.ckpt
redmondv2_lineart_lineani_lora_f16.ckpt
pixar_style_lora_f16.ckpt
sketch_style_lora_f16.ckpt
redmondv2_kids_storybook_lora_f16.ckpt

klein_4b_colorize_3500k_lora_f16.ckpt
klein_4b_outpaint_lora_f16.ckpt
klein_4b_zoom_red_lora_f16.ckpt

## Klein LoRAs - Original Names

dutchbaroqueflux_klein_lora_f16.ckpt
light_fantasy_klein_lora_f16.ckpt
numzoo_klein_lora_f16.ckpt
ohiseeflux_klein_lora_f16.ckpt
klein4b_yarn_art_lora_v1_lora_f16.ckpt
wikiqwen_illustrator_lora_f16.ckpt

Flux_klein_4b_anime_Koni.safetensors
minoteflux-klein.safetensors
pixelart_lora.safetensors

pytorch_lora_weights.safetensors
flux2_klein_4b_colorize_3500k_lora_f16.ckpt
flux-outpaint-lora.safetensors
flux-red-zoom-lora.safetensors

## Klein LoRAs - New Names

klein_dutchbaroqueflux_lora_f16.ckpt
klein_light_fantasy_lora_f16.ckpt
klein_numzoo_lora_f16.ckpt
klein_ohiseeflux_lora_f16.ckpt
klein_wikiqwen_illustrator_lora_f16.ckpt
klein_yarn_art_lora_f16.ckpt

klein_anime_koni_lora_f16.ckpt
klein_minoteflux_lora_f16.ckpt
klein_pixelart_lora_f16.ckpt

## Upscalers - Original Names

4x_foolhardy_Remacri_ExtraSmoother.safetensors
4x_NMKD-Superscale-SP_178000_G.safetensors
RealESRGAN_x4plus.safetensors
RealESRGAN_x4plus_anime_6B.safetensors
4x-UltraSharpV2.safetensors
SwinIR-L_x4_PSNR.safetensors

## Upscalers

4x_foolhardy_remacri_extrasmoother_f16.ckpt
4x_nmkd_superscale_sp_178000_g_f16.ckpt
realesrgan_x4plus_f16.ckpt
realesrgan_x4plus_anime_6b_f16.ckpt

SwinIR Alternative:

rrdb_psnr_x4_f16.ckpt

## Upscalers (DT App)

esrgan_4x_universal_upscaler_v2_sharp_f16. ckpt
realesrgan_x2plus_f16.ckpt

## Non-Commercial

4x_ultrasharp_f16.ckpt
remacri_4x_f16.ckpt

## TASK

For each genre and age group, can you create a markdown table with recommendations on which models, loras (multi-loras are okay if needed), along with other settings like steps, guidanceScale, upscaler, and sampler. Also include (in brackets) numberic value for sampler.

For each genre and age group, can you think hard and come up with good examples that would illustrate good use of models, loras, as well as prompting (prompt and --negative-prompt), sampler (if needed), steps, cfg, etc etc with a brief explanation of why the specific values and prompts were used. An AI Agent and recommendation engine will be the consumer of this info, so keep the explanations very brief and not verbose. Think hard and add any other info that will help AI Agent in evaulation and making recommendations based on certain undeterministic user requirements.

All commands should be executable in and should use `--config-json` in this format:

```json
draw-things-cli generate \
--model juggernaut_xl_x_f16.ckpt \
--output '~/Dev/tmp/sdxl_coloring_adult_owl.png' \
--prompt "intricate adult coloring book page, mystical owl on a crescent moon, complex mandala patterns..." \
--negative-prompt "3d render, shading, gray shadows, sketch, charcoal, messy lines, text, bg color..." \
--width 768 --height 768 --steps 28 --cfg 5.5 \
--config-json '{
"sampler": 0,
"loras": [
    {"file": "LORA_1.ckpt", "weight": 0.85, "mode": "all"},
    {"file": "LORA_2.ckpt", "weight": 0.50, "mode": "all"}
  ]
}'
```

---

## RESPONSE

I'll build this as a single markdown reference file for your agent, starting with the Klein skill and a check of the draw-things-cli config fields.

The recipe book is ready as `draw-things-recipes.md`: 30 recipes across kids illustration, coloring, mandalas, sketches, anime, 3D, digital, photo and oil painting, each with an executable command in your `--config-json` format. I haven't run any of them through `draw-things-cli`. I checked every command's shell syntax, JSON, and file names against your allowed lists, and confirmed each recipe matches its row in the index table.

Each recipe has the keywords it should match, a brief reason for its settings, and its sampler and `schedule_sampler` values with the number in brackets. The file also has an asset registry (model, LoRA and upscaler traits and weight ranges), rules for routing a user request to a recipe, adjustments for vague requirements, a troubleshooting table, and safety rules for the agent.

A few things are assumptions or deviations, all flagged in section 0 of the file:

- **Sampler numbers:** I took them from a published copy of the Draw Things `SamplerType` list (0 = DPM++ 2M Karras, 1 = Euler A, 4 = DPM++ SDE Karras, 10 = Euler A Trailing, and so on). Newer builds may add values, so nothing above 18 should be used without checking.
- **Upscaler:** I pass `"upscaler"` in the config JSON and left out any scale-factor key because I couldn't confirm its name.
- **Klein:** Klein recipes have no `--negative-prompt` and no LoRAs, since Klein ignores negatives.
- **Output path:** commands use `"$HOME/Dev/tmp/..."` instead of `'~/Dev/tmp/...'`, because the shell won't expand `~` inside quotes.

The agent should smoke-test once before batch runs: `draw-things-cli generate --help`, then a small 4-step render per recipe family.

---

---

---

# SDXL Strategy

I'm using "draw-things-cli" with SDXL to create Kids Reading Book Illustrations, Kids and adults Coloring Books & Line Art, Storybooks and Non-fiction Informative books for kids and teens, Adults Mandala Coloring Books, Pencil & Artistic Sketches, oil and watercolor paintings, 2D/3D anime illustrations, digital drawings, photography, oil painting, Photorealism, etc.

I can only use these Models, LoRAs, and Upscalers:

## Models

- juggernaut_xl_v9_f16.ckpt
- juggernaut_xl_x_f16.ckpt
- colorfulxl_v6.0_f16.ckpt
- animagine_xl_v3.1_f16.ckpt

## LoRAs

- 3d_render_style_xl.safetensors
- add-detail-xl.safetensors
- AnalogRedmondV2-Analog-AnalogRedmAF.safetensors
- ColoringBookRedmond-ColoringBook-ColoringBookAF.safetensors
- epic-oil-painting-slider.safetensors
- LineAniRedmondV2-Lineart-LineAniAF.safetensors
- oil-painting-slider.safetensors
- pixar-style.safetensors
- sketch-style-xl.safetensors
- StorybookRedmondV2-KidsBook-KidsRedmAF.safetensors

## Upscalers

- 4x_foolhardy_Remacri_ExtraSmoother.safetensors
- 4x_NMKD-Superscale-SP_178000_G.safetensors
- 4x-UltraSharpV2.safetensors
- RealESRGAN_x4plus_anime_6B.safetensors
- RealESRGAN_x4plus.safetensors
- RealESRGAN_x2plus.safetensors

For each categories, genres, and age groups, can you suggest which LoRAs and upscalers I should use, and the different tips and configuration to use for example, which steps, cfg, upscaler, sampler, etc to use. Also include (in brackets) numberic value for sampler.

Also, can you suggest strategies on how to create good prompts, and strategies for good negtive prompts. For each genre and age group, can you think hard and come up with good examples that would illustrate good use of loras, as well as prompt, upscaler, sampler (if needed), steps, cfg, etc etc with a brief explanation of why the specific values and prompts were used. An AI Agent and recommendation engine will be the consumer of this info, so keep the explanations very brief and not verbose. Think hard and add any other info that will help AI Agent in evaulation and making recommendations based on certain undeterministic user requirements.

All example commands should be executable in and should use `--config-json` in this format:

```json
draw-things-cli generate \
--model juggernaut_xl_x_f16.ckpt \
--output '~/Dev/tmp/sdxl_coloring_adult_owl.png' \
--prompt "intricate adult coloring book page, mystical owl on a crescent moon, complex mandala patterns..." \
--negative-prompt "3d render, shading, gray shadows, sketch, charcoal, messy lines, text, bg color..." \
--width 768 --height 768 --steps 28 --cfg 5.5 \
--config-json '{
"sampler": 0,
"loras": [
    {"file": "LORA_1.ckpt", "weight": 0.85, "mode": "all"},
    {"file": "LORA_2.ckpt", "weight": 0.50, "mode": "all"}
  ]
}'
```

---

# Flux-2-Klein Strategy

On my Macbook Pro M4 (12-core, 48 GB Unified Memory), I'm using "draw-things-cli" with flux_2_klein_4b_q8p.ckpt to create Kids Reading Book Illustrations, Kids and adults Coloring Books & Line Art, Storybooks and Non-fiction Informative books for kids and teens, Adults Mandala Coloring Books, Pencil & Artistic Sketches, oil and watercolor paintings, 2D/3D anime illustrations, digital drawings, photography, oil painting, Photorealism, etc.

Can you suggest which LoRAs and upscalers I should use that are compatible with "draw-things-cli", and the different tips and configuration to use for the different categories, genres, and age groups, for example, which steps, cfg, upscaler, sampler, etc to use. Also include (in brackets) numberic value for sampler.

Also give exact HF download commands to download the suggested LoRAs and upscalers. `.safetensor` or `.ckpt` files are preferred.

Also, since Klein doesn't support negative-prompt, can you suggest strategies on how to create good prompts, and strategies to generate good positive prompts. For each genre and age group, can you think hard and come up with good examples that would illustrate good use of loras, as well as prompt, upscaler, sampler (if needed), steps, cfg, etc etc with a brief explanation of why the specific values and prompts were used. An AI Agent and recommendation engine will be the consumer of this info, so keep the explanations very brief and not verbose. Think hard and add any other info that will help AI Agent in evaulation and making recommendations based on certain undeterministic user requirements.

All example commands should be executable in and should use `--config-json` in this format:

```json
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--output '~/Dev/t2/klein_coloring_adult_owl.png' \
--prompt "intricate adult coloring book page, mystical owl on a crescent moon, complex mandala patterns..." \
--width 768 --height 768 --steps 28 --cfg 5.5 \
--config-json '{
"sampler": 0,
"loras": [
    {"file": "LORA_1.ckpt", "weight": 0.85, "mode": "all"},
    {"file": "LORA_2.ckpt", "weight": 0.50, "mode": "all"}
  ]
}'
```

---

## Claude Response (klein_drawthings_guide_claude.md)

I'll start by loading the Klein skill and researching what actually works with Draw Things CLI: Klein-compatible LoRAs, upscalers, sampler numeric values, and the config schema. Then I'll build the guide as a file.

Research is done. I'm now writing the guide as a markdown file with runnable examples, then I'll validate every JSON block and command before sending it. Key finding so far: only 4B-compatible LoRAs work, and they must be converted to Draw Things' own `_lora_f16.ckpt` format first, or they're silently ignored.

Those three flagged items are the variant-test and LoRA-verify snippets, which are intentional (short test prompts or variable prompts). Everything else passed. Delivering.

The guide is `klein_drawthings_guide.md`. It has LoRA and upscaler picks, settings per category and age group, the positive-only prompt method, 18 runnable commands and a JSON preset layer for your agent. I validated all 20 `--config-json` blocks (they parse, sampler values are in range, upscaler names are valid) and every example prompt. I haven't run any of it on a Mac.

Things to know before running it:

- **Your template has three problems.**
  - `schedule_sampler` isn't a valid field, so I dropped it.
  - cfg 5.5 is too high for Klein. I use 4.0 for the base model and 1.0 for the distilled one.
  - Your `.ckpt` file name isn't an official Draw Things file. The guide includes a quick test to identify which variant it really is.
- **LoRAs need converting.** Draw Things wants a `_lora_f16.ckpt` registered in `custom_lora.json`, and the CLI doesn't convert for you. Import through the app, or use the converter script (the guide has the steps).
- **9B LoRAs are silently ignored on the 4B model.** The guide lists the ones that work and a same-seed check to confirm a LoRA is actually applied.
- **Several genres are prompt-only.** I found no 4B LoRA for coloring pages, mandalas, watercolor or photorealism, so those examples use prompt wording alone.
- **Upscalers aren't on Hugging Face.** They come from Draw Things' own CDN or the app's built-in download. I couldn't reach the CDN from my sandbox, so that URL pattern is inferred and needs a test on your Mac. UltraSharp and Remacri are non-commercial, as is the WikiQwen-Illustrator LoRA.
- **Unverified items** are listed in §8.3 of the guide. They include flag names beyond your template, whether the CLI applies `upscaler`, and M4 speed. The `hf download` commands are untested too, since my sandbox has no `hf` CLI.

Sources are in §9 of the guide.

---

## Claude Response 2

I'll check the Draw Things CLI's config schema and sampler IDs, then look for FLUX.2 Klein 4B LoRAs and upscalers that work with it. After that I'll write the reference guide.

Still researching. I've confirmed the sampler numeric IDs from the Draw Things source and I'm now reading the CLI's generate options and config-JSON keys. Next up are Klein 4B LoRAs and upscalers.

Found something that changes the commands. The JSON keys must be camelCase, and `schedule_sampler` isn't a real key, so the CLI silently ignores it. I'm now checking how LoRAs and upscalers load, including the `version` field that Klein 4B LoRAs need.

Source check done: Klein 4B's LoRA version tag is `flux2_4b`, and the built-in upscaler filenames are confirmed. One thing to flag: the plain 4B model is step-distilled, so it wants few steps and low CFG. Only the Base variant suits 28 steps at CFG 5.5. I'm now searching Hugging Face for real Klein 4B LoRAs.

Early finding: very few LoRAs exist for Klein 4B. The Redmond coloring-book, lineart and storybook LoRAs are 9B-only and won't load on 4B. I'm now checking how a `.safetensors` LoRA gets into Draw Things format, since the CLI may not load it directly.

I've confirmed upscalers are set with `upscaler` and `upscalerScaleFactor`, and that the CLI expands `~` in output paths. I'm now looking for Draw Things' own recommended Klein settings, so the sampler and shift advice has a source behind it.

Research is done. Verified so far:
- The sampler IDs.
- The JSON key names.
- Draw Things' own Klein defaults. The plain 4B runs at 4 steps and CFG 1, and the Base variant at 30 steps and CFG 4.
- The LoRA conversion path.

I'm doing one last check on whether any Hugging Face repo hosts upscalers in Draw Things' `.ckpt` format. Then I'll write the guide.

The guide draft is written: 24 example commands, the sampler ID table, the LoRA and upscaler catalogs, and the prompting rules. I'm running a validation pass now on every command's bash syntax and `--config-json`, plus the sampler IDs and size rules.

I've written the agent reference as `klein4b_draw-things_reference.md`, with 24 example commands in your `--config-json` format. I couldn't run `draw-things-cli` or reach Hugging Face from here, so the commands are checked for bash syntax and JSON validity but haven't been run on your Mac.

**Fixes to your template command**
- **`schedule_sampler` isn't a real key.** The CLI silently ignores it. The sampler variants are their own IDs instead, such as DDIM Trailing `[16]`, Euler A Trailing `[10]` and DPM++ 2M Trailing `[15]`.
- **JSON keys must be camelCase.** For example `upscalerScaleFactor`, not snake_case. Unknown keys are dropped without an error.
- **Your file is the step-distilled model.** `flux_2_klein_4b_q8p.ckpt` has no "base" in its name, so use 4–8 steps and CFG 1.0. Draw Things' own defaults for it are 4 steps, CFG 1 and sampler `[16]`. Your `--steps 28 --cfg 5.5` only suits `flux_2_klein_base_4b_*`, which defaults to 30 steps and CFG 4.
- **`sampler 0` (DPM++ 2M Karras) is a legacy SD-era choice.** Use `[16]` for this model.

**LoRAs are the weak spot.** Almost nothing exists for Klein 4B in your genres.
- **Incompatible LoRAs:** the popular coloring-book, lineart-anime and storybook LoRAs are 9B-only and won't load on 4B.
- **4B LoRAs I found:**
  - A painterly-fantasy LoRA.
  - A vintage-book-cover LoRA.
  - A sprite-sheet LoRA for pose consistency.
  - A pixel-art LoRA.
- **Conversion needed:** the CLI ignores raw `.safetensors` LoRAs, so each one must be converted to Draw Things' `.ckpt` format first. The guide gives two routes.
- **Self-training:** for a locked coloring-book or mandala style, `draw-things-cli train lora` is the better route. The guide includes a `--dry-run` command.

**Upscalers:** the six built-in Draw Things upscalers auto-download on first use. I found no Hugging Face repo with them in a format the CLI can load. The guide has a pre-fetch command instead of `hf download` for these.

**Still unconfirmed**
- The LoRA download filenames are unconfirmed for two LoRAs (use `--include "*.safetensors"`). The Klein conversion path in the third-party script is also unconfirmed.
- The sampler and step choices beyond the verified defaults are heuristics. They're tagged `[H]`, meaning A/B test them on a fixed seed.
- The photo-to-coloring-page example (E22) is untested.

The file also has the negative-to-positive prompt rewrite table, age-group specs, a preset matrix per genre and age, and the agent's decision order, pre-flight checklist and troubleshooting table.

Sources:
- [draw-things-community source](https://github.com/drawthingsai/draw-things-community)
- [drawthings-lora-convert](https://github.com/vcspr/drawthings-lora-convert)
- [BFL FLUX.2-klein-4B](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B)
- [BFL FLUX.2-klein-base-4B](https://huggingface.co/black-forest-labs/FLUX.2-klein-base-4B)
- [BFL Klein LoRA guide](https://huggingface.co/blog/black-forest-labs/flux-2-klein-lora)
- [BFL FLUX.2 prompting docs](https://docs.bfl.ml/flux_2/flux2_overview)
- [giannisan/light-fantasy-flux2-klein-base-lora](https://huggingface.co/giannisan/light-fantasy-flux2-klein-base-lora)
- [Norod78/flux2-klein-4b-base-lora-vintage-book-cover](https://huggingface.co/Norod78/flux2-klein-4b-base-lora-vintage-book-cover)
- [fal/flux-2-klein-4b-spritesheet-lora](https://huggingface.co/fal/flux-2-klein-4b-spritesheet-lora)
- [adirik/pixel-art-lora-flux.2-klein-4B](https://huggingface.co/adirik/pixel-art-lora-flux.2-klein-4B)
- [easygoing0114/FLUX.2-klein-4B_clear](https://huggingface.co/easygoing0114/FLUX.2-klein-4B_clear)

---

---
---
---

---

# More Flux-2-Klein LoRAs

On my Macbook Pro M4 (12-core, 48 GB Unified Memory), I'm using "draw-things-cli" with flux_2_klein_4b_q8p.ckpt to creating photographs, Coloring Books, Line Art, Mandala Coloring Books, Pencil & Artistic Sketches, oil and watercolor paintings, 2D/3D anime illustrations, digital drawings, photography, oil painting, Photorealism, etc.

With my flux_2_klein_4b_q8p, I want to use these LoRAs:

- https://huggingface.co/HaaDeej/Flux2-3500K
- https://huggingface.co/xocialize/outpaint-FLUX.2-klein-4B-lora
- https://huggingface.co/fal/flux-2-klein-4B-zoom-lora
- https://huggingface.co/fal/flux-2-klein-4B-outpaint-lora

Can you create a markdown table with columns containing information on each , including LoRA strength/benefit, best used for, and the ideal confiuguration ranges for each LoRA, for example, sampler (if needed), steps, cfg, etc.

Also, since Klein doesn't support negative-prompt, can you give examples of good positive prompts, specifically for the above LoRAs that show good use of these LoRAs. For each genre and age group, can you think hard and come up with good examples that would illustrate good use of loras, as well as good prompting, and appropriate values for upscaler, sampler, steps, cfg, etc etc with a brief explanation of why the specific values and prompts were used. Also suggest if it's better to use these LoRAs with other LoRAs.

An AI Agent and recommendation engine will be the consumer of this info, so keep the explanations very brief and not verbose. Think hard and add any other info that will help AI Agent in evaulation and making recommendations based on certain undeterministic user requirements.

For the upscalers examples, use appropriate upscalers only out of these four:

- 4x_foolhardy_Remacri_ExtraSmoother
- 4x_NMKD-Superscale-SP_178000_G
- RealESRGAN_x4plus
- RealESRGAN_x4plus_anime_6B

All example commands should be executable in and should use `--config-json` in this format:

```json
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--output '~/Dev/t2/klein_coloring_adult_owl.png' \
--prompt "intricate adult coloring book page, mystical owl on a crescent moon, complex mandala patterns..." \
--width 768 --height 768 --steps 28 --cfg 5.5 \
--config-json '{
"sampler": 0,
"loras": [
    {"file": "LORA_1.ckpt", "weight": 0.85, "mode": "all"},
    {"file": "LORA_2.ckpt", "weight": 0.50, "mode": "all"}
  ]
}'
```


---
---
---
qqq

# Sprites Flux-2-Klein LoRAs

I'm using Flux Klein and SDXL (juggernaut_xl_v9_f16, juggernaut_xl_x_f16, colorfulxl_v6.0_f16, and animagine_xl_v3.1_f16) to create Kids Reading Book Illustrations, Kids and adults Coloring Books & Line Art, Adults Mandala Coloring Books, Pencil & Artistic Sketches, 2D/3D anime illustrations, digital drawings, photography, oil painting, Photorealism, etc.

For each genre, can you create a markdown table with recommendations on which models, loras (multi-loras are okay if needed), along with other settings like steps, guidanceScale, sampler.

I'm using "draw-things-cli" with SDXL to create Kids Reading Book Illustrations, Kids and adults Coloring Books & Line Art, Storybooks and Non-fiction Informative books for kids and teens, Adults Mandala Coloring Books, Pencil & Artistic Sketches, oil and watercolor paintings, 2D/3D anime illustrations, digital drawings, photography, oil painting, Photorealism, etc.

I can only use these Models, LoRAs, and Upscalers:

## Models

- juggernaut_xl_v9_f16.ckpt
- juggernaut_xl_x_f16.ckpt
- colorfulxl_v6.0_f16.ckpt
- animagine_xl_v3.1_f16.ckpt

On my Macbook Pro M4 (12-core, 48 GB Unified Memory), I'm using "draw-things-cli" with flux_2_klein_4b_q8p.ckpt to creating photographs, Coloring Books, Line Art, Mandala Coloring Books, Pencil & Artistic Sketches, oil and watercolor paintings, 2D/3D anime illustrations, digital drawings, photography, oil painting, Photorealism, etc.

With my flux_2_klein_4b_q8p, I want to use these LoRAs:

- https://huggingface.co/HaaDeej/Flux2-3500K
- https://huggingface.co/xocialize/outpaint-FLUX.2-klein-4B-lora
- https://huggingface.co/fal/flux-2-klein-4B-zoom-lora
- https://huggingface.co/fal/flux-2-klein-4B-outpaint-lora

Can you create a markdown table with columns containing information on each , including LoRA strength/benefit, best used for, and the ideal confiuguration ranges for each LoRA, for example, sampler (if needed), steps, cfg, etc.

Also, since Klein doesn't support negative-prompt, can you give examples of good positive prompts, specifically for the above LoRAs that show good use of these LoRAs. For each genre and age group, can you think hard and come up with good examples that would illustrate good use of loras, as well as good prompting, and appropriate values for upscaler, sampler, steps, cfg, etc etc with a brief explanation of why the specific values and prompts were used. Also suggest if it's better to use these LoRAs with other LoRAs.

An AI Agent and recommendation engine will be the consumer of this info, so keep the explanations very brief and not verbose. Think hard and add any other info that will help AI Agent in evaulation and making recommendations based on certain undeterministic user requirements.

For the upscalers examples, use appropriate upscalers only out of these four:

- 4x_foolhardy_Remacri_ExtraSmoother
- 4x_NMKD-Superscale-SP_178000_G
- RealESRGAN_x4plus
- RealESRGAN_x4plus_anime_6B

All example commands should be executable in and should use `--config-json` in this format:

```json
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--output '~/Dev/t2/klein_coloring_adult_owl.png' \
--prompt "intricate adult coloring book page, mystical owl on a crescent moon, complex mandala patterns..." \
--width 768 --height 768 --steps 28 --cfg 5.5 \
--config-json '{
"sampler": 0,
"loras": [
    {"file": "LORA_1.ckpt", "weight": 0.85, "mode": "all"},
    {"file": "LORA_2.ckpt", "weight": 0.50, "mode": "all"}
  ]
}'
```


---
---
---


---
---
---
# ChatGPT Klein Response

Created and validated a comprehensive JSON recommendation Draw Things FLUX.2 Klein 4B Recommendation Rules JSON in

The file `klein-recommendation-rules.json` contains 13 generation profiles, 3 LoRA candidates, and 10 selection rules, with machine-readable settings and validation requirements.

- `sdxl-recommendation-rules.json` - Machine-readable settings and selection rules. Designed for an agent to map a request to a model, LoRA combination, sampler, CFG, steps, dimensions, upscaler and prompt constraints.

Can you create a comprehensive recommendation rules JSON, with the recommendations you suggested stored as data for the AI agent. Each profile should identify the goal, candidate settings, constraints, confidence and validation requirements. A Machine-readable settings and selection rules designed for an agent to map a request to a model, LoRA combination, sampler, CFG, steps, dimensions, upscaler and prompt constraints. JSON syntax has been validated.


---
---
---
---


# Qwen Prompt Strategy

On my Macbook Pro M4 (12-core, 48 GB Unified Memory), I'm using "draw-things-cli" with qwen_image_2512_bf16_q8p.ckpt (Qwen BF16 8-bit S) to create book cover images with embedded book title, series name, and publisher name on different types of books, like Kids Reading Books, Illustrations books, Kids and adults Coloring Books & Line Art, Storybooks and Non-fiction Informative books for kids and teens, Adults Mandala Coloring Books, Pencil & Artistic Sketch books, oil and watercolor paintings, 2D/3D anime illustrations, digital drawings, photography, oil painting, Photorealism, and other types of books.

For each categories, genres, and age groups, also suggest which upscalers I should use that are compatible with "draw-things-cli", and give different tips and configuration to use for the different categories, genres, and age groups, for example, which steps, cfg, upscaler, sampler, etc to use. Also include (in brackets) numberic value for sampler.

Also, can you suggest strategies on how to create good prompts, and strategies for good negtive prompts. For each genre and age group, think hard and come up with good examples that would illustrate good use of prompts and negtive prompts, and different settings for upscaler, sampler (if needed), steps, cfg, etc etc with a brief explanation of why the specific values and prompts were used. An AI Agent and recommendation engine will be the consumer of this info, so keep the explanations very brief and not verbose. Think hard and add any other info that will help AI Agent in evaulation and making recommendations based on certain undeterministic user requirements.

All example commands should be executable in and should use `--config-json` in this format:

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

Can you also create a comprehensive recommendation rules JSON, that will store recommendation as data for the AI agent. Each profile should identify the goal, candidate settings, constraints, confidence and validation requirements. A Machine-readable settings and selection rules designed for an agent to map a request to a model, sampler, CFG, steps, dimensions, upscaler and prompt constraints.


## cfg, samplers and schedules

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

---
---
---
---

On my Macbook Pro M4 (12-core, 48 GB Unified Memory), I'm using "draw-things-cli" with qwen_image_2512_bf16_q8p.ckpt (Qwen BF16 8-bit S) to create book cover images with embedded book title, series name, and publisher name

do an extensive research on how the different ways I can specify coordinates for positioning the book title, etc. Validate and test to see if it's working


---
---
---
---

I'm using "draw-things-cli" on my Macbook Pro M4 (12-core, 48 GB Unified Memory) for image generating and editing book cover images with embedded book title, series name, and publisher name. In earlier version "Qwen image 2512", I had to use a different "edit" model version for editing the generated images, but I've recently downloaded `qwen_image_2.1_q8p.ckpt`. I have discovered that Qwen-Image-2.1 model natively supports both text-to-image generation and image editing in a single unified architecture.

I also found that Image Editing in Qwen-Image-2.1 comes with these features:

- Unified Model: You do not need a separate "edit version" checkpoint; the core 7 billion parameter model handles both tasks.
- Multiple Reference Images: It supports up to 10–16 reference images in a single pipeline to guide character identity, clothing, style, or products.
- Local and Regional Edits: You can specify where changes happen using circles, painted annotations, or separate masks.
- Transparency Support: It can handle native RGBA transparency and product cutout compositing.

Can you generate a single document that explains these features with good examples that show how best to use these features?

Note that I will be creating book covers for different types of books, like Kids Reading Books, Illustrations books, Kids and adults Coloring Books & Line Art, Storybooks and Non-fiction Informative books for kids and teens, Adults Mandala Coloring Books, Pencil & Artistic Sketch books, oil and watercolor paintings, 2D/3D anime illustrations, digital drawings, photography, oil painting, Photorealism, and other types of books.

These are the only upscalers I can use:

- 4x_foolhardy_Remacri_ExtraSmoother.safetensors
- 4x_NMKD-Superscale-SP_178000_G.safetensors
- RealESRGAN_x4plus.safetensors
- RealESRGAN_x4plus_anime_6B.safetensors

For each categories, genres, and age groups, can you suggest which upscalers I should use, and the different tips and configuration to use for example, which steps, cfg, upscaler, sampler, etc to use. Also include (in brackets) numberic value for sampler.

Can you also briefly explain the features as well as suggest tips and tricks for this new models, strategies on how to create good prompts, and negtive prompts. For each genre and age group, can you think hard and come up with good examples that would illustrate good use of loras, as well as prompt, upscaler, sampler (if needed), steps, cfg, etc. An AI Agent and recommendation engine will be the consumer of this info, so keep the explanations very brief and not verbose. Think hard and add any other info that will help AI Agent in evaulation and making recommendations based on certain undeterministic user requirements.

All example commands should be executable in and should use `--config-json` in this format:

```json
draw-things-cli generate \
--model qwen_image_2.1_q8p.ckpt \
--output '~/Dev/tmp/sdxl_coloring_adult_owl.png' \
--prompt "intricate adult coloring book page, mystical owl on a crescent moon, complex mandala patterns..." \
--negative-prompt "3d render, shading, gray shadows, sketch, charcoal, messy lines, text, bg color..." \
--width 1024 --height 1024 --steps 28 --cfg 4.0
```

## RESPONSE

I'll verify the Qwen-Image-2.1 claims and the `draw-things-cli` flag syntax first, then write the guide as a single Markdown file for your agent.

I've written the playbook as one Markdown file for your agent. It covers the unified generate/edit model, prompt and negative-prompt rules, sampler IDs, and upscaler picks. It also has settings and runnable commands for 17 genres, plus recipes for edits, transparency and multi-reference work. I couldn't run `draw-things-cli` here, so I only checked that all 22 commands parse as shell, the `--config-json` payloads are valid JSON, and sizes are multiples of 64.

Things that change how you use it:

- **Licence:** Qwen-Image-2.1 is released under the Qwen Research License, which allows non-commercial research and evaluation only. Commercial use needs a separate licence from Qwen. If these covers are for sale, the playbook flags this first and suggests `qwen_image_2512` and `qwen_image_edit_2511` (Apache 2.0 per published reports; confirm on their model cards) or asking Qwen for a licence. The licence text doesn't say whether the images it produces are covered.
- **Reference images:** the limit is 10, not 10–16.
- **Negative prompts:** the official recipe is 40 steps at CFG 1.0 with no negative prompt. At CFG 1.0 a negative prompt does nothing, so my examples use CFG 2.0–3.5 with negatives, and the playbook tells the agent to compare against CFG 1.0 on the same seed.
- **Sampler numbers:** these come from the Draw Things enum, where 15 is DPM++ 2M Trailing and 10 is Euler A Trailing. Karras and AYS samplers are marked as ones to avoid.
- **Command format:** I used `"$HOME/Dev/tmp/..."` instead of `'~/...'`, because a tilde inside quotes isn't expanded by the shell. I also kept your flag style and put sampler, upscaler and LoRAs in `--config-json`.

The playbook tags each value so your agent knows how far to trust it. `[V]` means checked in published sources, `[R]` means my starting default, and `[P]` means probe your local CLI first. Steps, CFG, sampler and upscaler choices are all `[R]`, so run a fixed-seed A/B test before relying on them. These are still unconfirmed and need a probe: whether `--image` acts as an edit reference, how to pass multiple references or a mask, and whether `upscalerScaleFactor` and your upscaler filenames are accepted. The probe commands are in section 3.3. The LoRA section shows how to use them but names no specific files, since I couldn't confirm which 2.1-trained LoRAs work in Draw Things.

Files are in /home/claude:
- qwen-image-2.1-draw-things-cover-playbook.md

Sources are listed at the end of the file.
