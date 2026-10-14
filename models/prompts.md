I'm using Flux Klein and SDXL (juggernaut_xl_v9_f16, juggernaut_xl_x_f16, colorfulxl_v6.0_f16, and animagine_xl_v3.1_f16) to create Kids Reading Book Illustrations, Kids and adults Coloring Books & Line Art, Adults Mandala Coloring Books, Pencil & Artistic Sketches, 2D/3D anime illustrations, digital drawings, photography, oil painting, Photorealism, etc.

For each genre, can you create a markdown table with recommendations on which models, loras (multi-loras are okay if needed), along with other settings like steps, guidanceScale, sampler, schedule_sampler.

---

For each genre and age group, can you think hard and come up with good examples that would illustrate good use of models, loras, as well as prompting (prompt and --negative-prompt), sampler, schedule_sampler (if needed), steps, cfg, etc etc with a brief explanation of why the specific values and prompts were used. An AI Agent and recommendation engine will be the consumer of this info, so keep the explanations very brief and not verbose. Think hard and add any other info that will help AI Agent in evaulation and making recommendations based on certain undeterministic user requirements.

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
"schedule_sampler": 1,
"loras": [
    {"file": "LORA_1.safetensors", "weight": 0.85, "mode": "all"},
    {"file": "LORA_2.safetensors", "weight": 0.50, "mode": "all"}
  ]
}'
```

---

# FINAL PROMPT

I'm using "draw-things-cli" with Flux-2-Klein and SDXL (juggernaut_xl_v9_f16, juggernaut_xl_x_f16, colorfulxl_v6.0_f16, and animagine_xl_v3.1_f16) to create Kids Reading Book Illustrations, Kids and adults Coloring Books & Line Art, Adults Mandala Coloring Books, Pencil & Artistic Sketches, 2D/3D anime illustrations, digital drawings, photography, oil painting, Photorealism, etc.

I can only use these Models, LoRAs, and Upscalers:

## Models

- flux_2_klein_4b_f16.ckpt
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
- SwinIR-L_x4_PSNR.safetensors

## TASK

For each genre and age group, can you create a markdown table with recommendations on which models, loras (multi-loras are okay if needed), along with other settings like steps, guidanceScale, upscaler, sampler, and schedule_sampler. Also include (in brackets) numberic value for sampler and schedule_sampler.

For each genre and age group, can you think hard and come up with good examples that would illustrate good use of models, loras, as well as prompting (prompt and --negative-prompt), sampler, schedule_sampler (if needed), steps, cfg, etc etc with a brief explanation of why the specific values and prompts were used. An AI Agent and recommendation engine will be the consumer of this info, so keep the explanations very brief and not verbose. Think hard and add any other info that will help AI Agent in evaulation and making recommendations based on certain undeterministic user requirements.

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
"schedule_sampler": 1,
"loras": [
    {"file": "LORA_1.safetensors", "weight": 0.85, "mode": "all"},
    {"file": "LORA_2.safetensors", "weight": 0.50, "mode": "all"}
  ]
}'
```

---

## RESPONSE

I'll build this as a single markdown reference file for your agent, starting with the Klein skill and a check of the draw-things-cli config fields.

The recipe book is ready as `draw-things-recipes.md`: 30 recipes across kids illustration, coloring, mandalas, sketches, anime, 3D, digital, photo and oil painting, each with an executable command in your `--config-json` format. I haven't run any of them through `draw-things-cli`. I checked every command's shell syntax, JSON, and file names against your allowed lists, and confirmed each recipe matches its row in the index table.

Each recipe has the keywords it should match, a brief reason for its settings, and its sampler and `schedule_sampler` values with the number in brackets. The file also has an asset registry (model, LoRA and upscaler traits and weight ranges), rules for routing a user request to a recipe, adjustments for vague requirements, a troubleshooting table, and safety rules for the agent.

A few things are assumptions or deviations, all flagged in section 0 of the file:

- **`schedule_sampler`:** I couldn't find this as a native key in the Draw Things config, so I kept it from your template and treated it as the fallback sampler (the Karras, AYS or Trailing sibling of the main one). The agent is told to drop the key if the CLI rejects it. Is it meant to be something else?
- **Sampler numbers:** I took them from a published copy of the Draw Things `SamplerType` list (0 = DPM++ 2M Karras, 1 = Euler A, 4 = DPM++ SDE Karras, 10 = Euler A Trailing, and so on). Newer builds may add values, so nothing above 18 should be used without checking.
- **Upscaler:** I pass `"upscaler"` in the config JSON and left out any scale-factor key because I couldn't confirm its name.
- **Klein:** I assumed `flux_2_klein_4b_f16.ckpt` is the distilled build (4 steps, CFG 1.0). Klein recipes have no `--negative-prompt` and no LoRAs, since Klein ignores negatives and your LoRAs are all SDXL-family.
- **Output path:** commands use `"$HOME/Dev/tmp/..."` instead of `'~/Dev/tmp/...'`, because the shell won't expand `~` inside quotes.

The agent should smoke-test once before batch runs: `draw-things-cli generate --help`, then a small 4-step render per recipe family.
