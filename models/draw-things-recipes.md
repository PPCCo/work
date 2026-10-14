# Draw Things CLI Recipe Book (agent-consumable)

Scope: genre x age-group recipes for `draw-things-cli generate` using ONLY the allowed models, LoRAs and upscalers below.
Audience: an AI agent / recommendation engine. Terse by design.

---

## 0. Read first: verified vs assumed

| Item                                       | Status                                                                                                                                                                                                                                                                                                                                                                        |
| ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `sampler` numeric values (section 1)       | Verified against a Draw Things `config.fbs` `SamplerType` enum snapshot. Newer builds may append values; never use a number above 18 without checking the app.                                                                                                                                                                                                                |
| `loras` array shape `{file, weight, mode}` | Verified (config.fbs `LoRA` table; mode = All/Base/Refiner). Use `"mode": "all"`.                                                                                                                                                                                                                                                                                             |
| `upscaler` key inside `--config-json`      | Documented as supported by community tooling. Value = upscaler filename.                                                                                                                                                                                                                                                                                                      |
| `upscaler_scale_factor`                    | NOT verified. Omitted from all commands. 4x models default to 4x; if output is too large, downscale after.                                                                                                                                                                                                                                                                    |
| `schedule_sampler` key                     | NOT verified as a native key. Kept because the user's template requires it. Treated as the **fallback sampler** (the schedule-variant sibling: Karras / AYS / Trailing). Operational rule: if the primary sampler gives noise, mush or banding, rerun with `sampler` = the `schedule_sampler` value. If the CLI rejects the key, delete it; `sampler` alone is authoritative. |
| Klein file is the distilled build          | ASSUMED (filename has no "base"). If 4 steps looks under-cooked and CFG > 1 works, it is base: use 20-28 steps, CFG ~4.                                                                                                                                                                                                                                                       |
| LoRA trigger words                         | From memory of LoRA cards. Verify on each LoRA's card; they are cheap to add and harmless if redundant.                                                                                                                                                                                                                                                                       |

Smoke test before any batch (agent runs once): `draw-things-cli generate --help`, then one 512x512, 4-step render per recipe family to confirm keys are accepted.

Path note: commands use `"$HOME/Dev/tmp/..."` not `'~/Dev/tmp/...'` because `~` is not expanded inside quotes.

---

## 1. Conventions

### Sampler enum (`"sampler": n`)

| n   | Name              | n   | Name               |
| --- | ----------------- | --- | ------------------ |
| 0   | DPM++ 2M Karras   | 10  | Euler A Trailing   |
| 1   | Euler A           | 11  | DPM++ SDE Trailing |
| 2   | DDIM              | 12  | DPM++ 2M AYS       |
| 3   | PLMS              | 13  | Euler A AYS        |
| 4   | DPM++ SDE Karras  | 14  | DPM++ SDE AYS      |
| 5   | UniPC             | 15  | DPM++ 2M Trailing  |
| 6   | LCM               | 16  | DDIM Trailing      |
| 7   | Euler A Substep   | 17  | UniPC Trailing     |
| 8   | DPM++ SDE Substep | 18  | UniPC AYS          |
| 9   | TCD               |     |                    |

Use guide: 0 = clean, stable default for SDXL. 4 = richer texture/detail, ~2x slower per step. 12/14 (AYS) = same look in fewer steps (can drop ~8 steps). 1 = Euler A: soft, loose, Animagine's native sampler. 10/15 = Trailing: for few-step/flow models (Klein). Avoid 6/9 (LCM/TCD) unless a matching LCM/TCD LoRA is loaded (none allowed here).

### Pairing used in this file (sampler -> schedule_sampler fallback)

`0 -> 12` · `4 -> 14` · `1 -> 10` · Klein `10 -> 15`

### Sizes

- SDXL: multiples of 64, ~1 MP. Square 1024x1024 · portrait/print 832x1216 · tall 896x1152 · landscape/spread 1216x832.
- Klein: multiples of 16, <= ~2 MP. 1024x1024 · 1360x1024 · printable page 1216x1600.
- Do not request 2K+ natively on SDXL (duplicate subjects). Upscale instead.

### Prompt styles

- SDXL models: comma-separated phrases; `--negative-prompt` is real and effective. Do NOT use `masterpiece/8k` spam except Animagine's own quality tags.
- Animagine: Danbooru tags, subject first, quality tags last.
- Klein: natural sentences, 45-90 words, important things first, **NO negative prompt, NO negations ("no", "without")**, no `(word:1.3)` weights, no quality tags, hex colors attached to named objects (`the scarf is color #5B8E7D`), max one short quoted text string.

### Seeds / reproducibility

Add `"seed": 12345` inside `--config-json` to lock. Generate 4 candidates per idea; judge composition, then re-render the winner with higher steps. A seed is only valid for its exact prompt.

---

## 2. Asset registry

### Models

| File                         | Type                                            | Best for                                                                        | Avoid for                                                            | Typical                             |
| ---------------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------- | -------------------------------------------------------------------- | ----------------------------------- |
| `flux_2_klein_4b_f16.ckpt`   | Klein 4B flow model (assumed distilled)         | Fast drafts, flat vector, text-in-image, photoreal (non-child), simple kids art | Dense line art, painterly texture, 4+ subjects, hands, any SDXL LoRA | 4-8 steps, CFG 1.0, sampler 10      |
| `juggernaut_xl_v9_f16.ckpt`  | SDXL, photoreal-leaning all-rounder             | Photo, sketch, line art base, 3D, oil                                           | Anime                                                                | 30-35 steps, CFG 4-6, sampler 0/4   |
| `juggernaut_xl_x_f16.ckpt`   | SDXL, newer Juggernaut, better adherence/detail | Complex scenes, intricate line art, detailed photo/painting                     | Anime                                                                | 30-36 steps, CFG 3.5-6, sampler 0/4 |
| `colorfulxl_v6.0_f16.ckpt`   | SDXL, vivid saturated illustration              | Kids books, digital painting, fantasy, bright 3D                                | Muted photoreal, B/W line art (color leaks)                          | 28-32 steps, CFG 5-7, sampler 0     |
| `animagine_xl_v3.1_f16.ckpt` | SDXL anime (Danbooru tags)                      | 2D anime, chibi, manga line art                                                 | Photo, western realism                                               | 28 steps, CFG 5-7, sampler 1        |

### LoRAs (all SDXL-family; **never load with Klein**)

| File                                      | Effect                              | Trigger (verify)                     | Weight range | Notes                                                             |
| ----------------------------------------- | ----------------------------------- | ------------------------------------ | ------------ | ----------------------------------------------------------------- |
| `redmondv2_kids_storybook_lora_f16.ckpt`  | Children's picture-book look        | `KidsRedmAF, kids book illustration` | 0.5-0.95     | Strongest on colorfulxl. Lower to blend with oil/3D.              |
| `redmond_coloringbook_lora_f16.ckpt`      | Black-on-white coloring pages       | `ColoringBookAF, Coloring Book`      | 0.8-1.0      | Pair with strong color/shading negatives.                         |
| `redmondv2_lineart_lineani_lora_f16.ckpt` | Clean line art / ink                | `LineAniAF, lineart`                 | 0.3-0.8      | Secondary LoRA for coloring/sketch/anime lineart.                 |
| `sketch_style_lora_f16.ckpt`              | Pencil / ink sketch                 | `sketch style`                       | 0.7-0.9      | Add `monochrome` + paper words.                                   |
| `add_detail_xl_lora_f16.ckpt`             | Detail slider                       | none                                 | -1.0 to +1.0 | **Negative = simpler** (toddler art). Positive = intricate.       |
| `pixar_style_lora_f16.ckpt`               | Rounded animated-film 3D characters | per LoRA card                        | 0.6-0.8      | Describe qualities in the prompt, do not name studios/franchises. |
| `3d_render_style_xl_lora_f16.ckpt`        | Soft 3D render material look        | per LoRA card                        | 0.4-0.8      | Stack under pixar-style at 0.3-0.5.                               |
| `redmondv2_analog_lora_f16.ckpt`          | Analog film photo look              | `AnalogRedmAF, analog style photo`   | 0.5-0.8      | Photo only.                                                       |
| `oil_painting_slider_lora_f16.ckpt`       | Oil paint slider                    | none                                 | 0.7-1.2      | Realistic-leaning oil. Negative reverses.                         |
| `oil_painting_slider_epic_lora_f16.ckpt`  | Dramatic impasto                    | per LoRA card                        | 0.8-1.0      | Do not stack with oil-painting-slider above 1.0 combined.         |

Stacking rule: sum of style-LoRA weights (excluding add-detail) <= ~1.5. More than 3 LoRAs raises artifact risk.

### Upscalers (set via `"upscaler"` in config-json)

| File                                          | Short        | Character                                 | Use for                                      |
| --------------------------------------------- | ------------ | ----------------------------------------- | -------------------------------------------- |
| `4x_foolhardy_remacri_extrasmoother_f16.ckpt` | Remacri      | Smooth, painterly, forgiving              | Painted illustration, oil, 3D, portraits     |
| `4x_nmkd_superscale_sp_178000_g_f16.ckpt`     | NMKD         | Clean edges, low halo                     | Line art, coloring pages, mixed content      |
| `4x_ultrasharp_f16.ckpt`                      | UltraSharpV2 | Crisp, high micro-contrast (can halo)     | Detailed photo, mandalas, hatching, product  |
| `realesrgan_x4plus_anime_6b_f16.ckpt`         | ESRGAN-anime | Flat color, solid black lines             | Anime, flat vector, kids coloring, cartoon   |
| `realesrgan_x4plus_f16.ckpt`                  | ESRGAN       | General photo, keeps grain                | Photo, analog film                           |
| `rrdb_psnr_x4.ckpt`.                          | RRDB-PSNR    | Faithful, no hallucination, slightly soft | Pencil/ink sketch, when fidelity > sharpness |

---

## 3. Recipe index

| ID    | Genre                             | Age         | Model             | LoRAs (weight)                                 | Size      | Steps | CFG | Sampler [n]           | schedule_sampler [n]   | Upscaler     |
| ----- | --------------------------------- | ----------- | ----------------- | ---------------------------------------------- | --------- | ----- | --- | --------------------- | ---------------------- | ------------ |
| ILL-A | Kids book illustration            | 2-4         | colorfulxl_v6.0   | Storybook 0.9, add-detail -0.6                 | 1024x1024 | 28    | 6.0 | DPM++ 2M Karras [0]   | DPM++ 2M AYS [12]      | Remacri      |
| ILL-B | Kids book illustration            | 5-7         | colorfulxl_v6.0   | Storybook 0.85                                 | 1216x832  | 30    | 6.0 | DPM++ 2M Karras [0]   | DPM++ 2M AYS [12]      | Remacri      |
| ILL-C | Kids book illustration            | 8-10        | juggernaut_xl_x   | Storybook 0.7, add-detail 0.4                  | 1216x832  | 32    | 5.5 | DPM++ SDE Karras [4]  | DPM++ SDE AYS [14]     | Remacri      |
| ILL-K | Kids illustration (fast flat)     | 2-7         | flux_2_klein_4b   | none                                           | 1024x1024 | 4     | 1.0 | Euler A Trailing [10] | DPM++ 2M Trailing [15] | ESRGAN-anime |
| COL-A | Kids coloring/line art            | 2-4         | juggernaut_xl_v9  | ColoringBook 1.0, add-detail -1.0              | 832x1216  | 30    | 6.0 | DPM++ 2M Karras [0]   | DPM++ 2M AYS [12]      | ESRGAN-anime |
| COL-B | Kids coloring/line art            | 5-7         | juggernaut_xl_v9  | ColoringBook 0.95                              | 832x1216  | 30    | 6.0 | DPM++ 2M Karras [0]   | DPM++ 2M AYS [12]      | ESRGAN-anime |
| COL-C | Kids coloring/line art            | 8-10        | juggernaut_xl_x   | ColoringBook 0.9, add-detail 0.6               | 832x1216  | 32    | 6.0 | DPM++ SDE Karras [4]  | DPM++ SDE AYS [14]     | NMKD         |
| COL-K | Kids coloring (fast draft)        | 2-4         | flux_2_klein_4b   | none                                           | 1216x1600 | 8     | 1.0 | Euler A Trailing [10] | DPM++ 2M Trailing [15] | ESRGAN-anime |
| ADC-A | Adult coloring/line art           | teen, adult | juggernaut_xl_x   | ColoringBook 0.8, LineAni 0.4, add-detail 0.9  | 832x1216  | 34    | 6.0 | DPM++ SDE Karras [4]  | DPM++ SDE AYS [14]     | NMKD         |
| ADC-B | Adult mandala                     | teen, adult | juggernaut_xl_v9  | ColoringBook 0.85, add-detail 1.0              | 1024x1024 | 32    | 7.0 | DPM++ 2M Karras [0]   | DPM++ 2M AYS [12]      | UltraSharpV2 |
| ADC-C | Adult mandala (subject)           | teen, adult | juggernaut_xl_x   | ColoringBook 0.8, LineAni 0.35, add-detail 0.9 | 1024x1024 | 30    | 6.0 | DPM++ 2M Karras [0]   | DPM++ 2M AYS [12]      | NMKD         |
| SKT-A | Pencil/graphite sketch            | teen, adult | juggernaut_xl_v9  | sketch-style 0.85, add-detail 0.3              | 896x1152  | 30    | 5.0 | DPM++ 2M Karras [0]   | DPM++ 2M AYS [12]      | UltraSharpV2 |
| SKT-B | Ink/travel sketch                 | teen, adult | juggernaut_xl_x   | sketch-style 0.7, LineAni 0.5                  | 1216x832  | 30    | 5.5 | Euler A [1]           | Euler A Trailing [10]  | RRDB-PSNR    |
| SKT-C | Simple pencil drawing             | 8-10        | juggernaut_xl_v9  | sketch-style 0.7, add-detail -0.3              | 1024x1024 | 28    | 5.0 | DPM++ 2M Karras [0]   | DPM++ 2M AYS [12]      | RRDB-PSNR    |
| ANI-A | 2D anime chibi/mascot             | 5-10        | animagine_xl_v3.1 | none                                           | 1024x1024 | 28    | 6.0 | Euler A [1]           | Euler A Trailing [10]  | ESRGAN-anime |
| ANI-B | 2D anime illustration (SFW)       | teen, adult | animagine_xl_v3.1 | add-detail 0.5                                 | 832x1216  | 28    | 7.0 | Euler A [1]           | Euler A Trailing [10]  | ESRGAN-anime |
| ANI-C | Anime line art (coloring)         | teen, adult | animagine_xl_v3.1 | LineAni 0.8, ColoringBook 0.4                  | 832x1216  | 28    | 6.0 | Euler A [1]           | Euler A Trailing [10]  | ESRGAN-anime |
| 3D-A  | 3D cute character                 | 2-7         | colorfulxl_v6.0   | pixar-style 0.8, 3d_render 0.4                 | 1024x1024 | 30    | 5.5 | DPM++ 2M Karras [0]   | DPM++ 2M AYS [12]      | Remacri      |
| 3D-B  | 3D character in scene             | 8-10, teen  | juggernaut_xl_x   | pixar-style 0.7, 3d_render 0.5, add-detail 0.5 | 1216x832  | 32    | 5.0 | DPM++ SDE Karras [4]  | DPM++ SDE AYS [14]     | UltraSharpV2 |
| 3D-C  | 3D isometric/object render        | teen, adult | juggernaut_xl_v9  | 3d_render 0.8                                  | 1024x1024 | 30    | 5.0 | DPM++ 2M Karras [0]   | DPM++ 2M AYS [12]      | UltraSharpV2 |
| DIG-A | Digital flat vector/sticker       | all ages    | flux_2_klein_4b   | none                                           | 1024x1024 | 4     | 1.0 | Euler A Trailing [10] | DPM++ 2M Trailing [15] | ESRGAN-anime |
| DIG-B | Digital painting/concept art      | teen, adult | colorfulxl_v6.0   | add-detail 0.6                                 | 1216x832  | 30    | 6.0 | DPM++ 2M Karras [0]   | DPM++ 2M AYS [12]      | Remacri      |
| PHO-A | Photography: landscape            | all ages    | juggernaut_xl_x   | add-detail 0.5                                 | 1216x832  | 34    | 4.5 | DPM++ SDE Karras [4]  | DPM++ SDE AYS [14]     | ESRGAN       |
| PHO-B | Photorealism: adult portrait      | adult       | juggernaut_xl_v9  | add-detail 0.4                                 | 896x1152  | 35    | 4.5 | DPM++ SDE Karras [4]  | DPM++ SDE AYS [14]     | Remacri      |
| PHO-C | Photography: analog film          | teen, adult | juggernaut_xl_x   | Analog 0.7, add-detail 0.2                     | 1216x832  | 32    | 5.0 | DPM++ 2M Karras [0]   | DPM++ 2M AYS [12]      | ESRGAN       |
| PHO-D | Photography: product/macro        | all ages    | juggernaut_xl_v9  | add-detail 0.8                                 | 1024x1024 | 32    | 5.0 | DPM++ SDE Karras [4]  | DPM++ SDE AYS [14]     | UltraSharpV2 |
| PHO-K | Photography (fast)                | teen, adult | flux_2_klein_4b   | none                                           | 1360x1024 | 4     | 1.0 | Euler A Trailing [10] | DPM++ 2M Trailing [15] | ESRGAN       |
| OIL-A | Oil painting: classical landscape | all ages    | juggernaut_xl_x   | oil-painting-slider 1.0, add-detail 0.3        | 1216x832  | 32    | 5.5 | DPM++ 2M Karras [0]   | DPM++ 2M AYS [12]      | Remacri      |
| OIL-B | Oil painting: impasto/dramatic    | teen, adult | juggernaut_xl_v9  | epic-oil-painting-slider 1.0                   | 896x1152  | 32    | 6.0 | DPM++ SDE Karras [4]  | DPM++ SDE AYS [14]     | Remacri      |
| OIL-C | Oil-painted storybook             | 8-10        | colorfulxl_v6.0   | Storybook 0.5, oil-painting-slider 0.7         | 1216x832  | 30    | 6.0 | DPM++ 2M Karras [0]   | DPM++ 2M AYS [12]      | Remacri      |

---

## 4. Recipes (executable)

Each block: match keywords, command, why.

### ILL-A · Kids book illustration · age 2-4

Match: toddler, board book, nursery, very simple, huge eyes, one character.

```bash
draw-things-cli generate \
--model colorfulxl_v6.0_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_illustration_2-4_duckling.png" \
--prompt "KidsRedmAF, kids book illustration, a big round yellow duckling smiling in a puddle, huge friendly eyes, very simple shapes, thick soft outlines, flat bright colors, plain pale blue background with a few simple clouds, lots of empty space, cute, cheerful" \
--negative-prompt "scary, dark, creepy, realistic, photo, complex background, tiny details, busy, text, watermark, extra limbs, deformed, sharp teeth" \
--width 1024 --height 1024 --steps 28 --cfg 6.0 \
--config-json '{
"sampler": 0,
"schedule_sampler": 12,
"upscaler": "4x_foolhardy_remacri_extrasmoother_f16.ckpt",
"loras": [
    {"file": "redmondv2_kids_storybook_lora_f16.ckpt", "weight": 0.9, "mode": "all"},
    {"file": "add_detail_xl_lora_f16.ckpt", "weight": -0.6, "mode": "all"}
  ]
}'
```

Why: negative add-detail strips clutter; one subject; empty space; colorfulxl gives flat saturated toddler palette.

### ILL-B · Kids book illustration · age 5-7

Match: picture book spread, two characters, gentle story, space for text.

```bash
draw-things-cli generate \
--model colorfulxl_v6.0_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_illustration_5-7_fox_hedgehog.png" \
--prompt "KidsRedmAF, kids book illustration, a young fox and a hedgehog sharing a red umbrella on a rainy forest path, curious happy faces, soft watercolor and gouache texture, warm muted palette, simple clear shapes with a few playful details, wide picture book spread, empty space on the left for text" \
--negative-prompt "scary, dark, photo, realistic, text, watermark, extra limbs, deformed hands, blurry, cluttered" \
--width 1216 --height 832 --steps 30 --cfg 6.0 \
--config-json '{
"sampler": 0,
"schedule_sampler": 12,
"upscaler": "4x_foolhardy_remacri_extrasmoother_f16.ckpt",
"loras": [
    {"file": "redmondv2_kids_storybook_lora_f16.ckpt", "weight": 0.85, "mode": "all"}
  ]
}'
```

Why: landscape size = spread; two subjects max; "empty space for text" reserves layout room.

### ILL-C · Kids book illustration · age 8-10

Match: adventure, richer detail, atmosphere, 2-3 subjects, middle grade.

```bash
draw-things-cli generate \
--model juggernaut_xl_x_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_illustration_8-10_cave_dragon.png" \
--prompt "KidsRedmAF, kids book illustration, two young explorers with a lantern entering a glowing crystal cave, a small friendly dragon peeking from behind a rock, detailed painted storybook art, rich colors, warm dramatic light, depth and atmosphere, adventure mood, wide spread" \
--negative-prompt "gore, horror, scary, photo, text, watermark, deformed, extra limbs, blurry, lowres" \
--width 1216 --height 832 --steps 32 --cfg 5.5 \
--config-json '{
"sampler": 4,
"schedule_sampler": 14,
"upscaler": "4x_foolhardy_remacri_extrasmoother_f16.ckpt",
"loras": [
    {"file": "redmondv2_kids_storybook_lora_f16.ckpt", "weight": 0.7, "mode": "all"},
    {"file": "add_detail_xl_lora_f16.ckpt", "weight": 0.4, "mode": "all"}
  ]
}'
```

Why: juggernaut_x adds depth; lower Storybook weight keeps detail; SDE sampler for texture; "friendly" in prompt pins mood.

### ILL-K · Kids illustration, fast flat · age 2-7 (Klein)

Match: quick draft, flat vector, bold outlines, flashcards, app art. No negative prompt, no LoRA.

```bash
draw-things-cli generate \
--model flux_2_klein_4b_f16.ckpt \
--output "$HOME/Dev/tmp/klein_illustration_2-7_cat_ball.png" \
--prompt "A round orange cat balancing on a beach ball, joyful with a wide smile, chunky flat vector children's illustration with bold thick outlines and simple rounded shapes, bright cheerful palette, a sunny garden with two daisies and a red bucket, soft even light, the cat is color #E8913A and the ball is color #3FA7D6, single centred subject with generous space around it" \
--width 1024 --height 1024 --steps 4 --cfg 1.0 \
--config-json '{
"sampler": 10,
"schedule_sampler": 15,
"upscaler": "realesrgan_x4plus_anime_6b_f16.ckpt",
"loras": []
}'
```

Why: distilled Klein excels at flat shapes; 11-slot sentence prompt (subject, action, expression, style, scene, light, hex colors, framing); ~1 s per image, so run 4 seeds.

### COL-A · Kids coloring · age 2-4

Match: toddler coloring page, one big shape, thick lines, huge open areas.

```bash
draw-things-cli generate \
--model juggernaut_xl_v9_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_coloring_2-4_elephant.png" \
--prompt "ColoringBookAF, Coloring Book, coloring page for toddlers, one big friendly elephant holding a balloon, very thick bold black outlines, extremely simple shapes, huge open areas, pure white background, black and white line art, centered, whole subject in frame" \
--negative-prompt "color, colour, shading, gray, grayscale fill, gradient, shadows, hatching, small details, patterns, texture, sketch, messy lines, broken lines, text, watermark, background, border, 3d, photo" \
--width 832 --height 1216 --steps 30 --cfg 6.0 \
--config-json '{
"sampler": 0,
"schedule_sampler": 12,
"upscaler": "realesrgan_x4plus_anime_6b_f16.ckpt",
"loras": [
    {"file": "redmond_coloringbook_lora_f16.ckpt", "weight": 1.0, "mode": "all"},
    {"file": "add_detail_xl_lora_f16.ckpt", "weight": -1.0, "mode": "all"}
  ]
}'
```

Why: add-detail -1.0 deletes tiny areas; long negative blocks color/shading leak; 832x1216 ~ A4 ratio; ESRGAN-anime keeps lines solid black.

### COL-B · Kids coloring · age 5-7

Match: kids coloring page, simple scene, a few playful details.

```bash
draw-things-cli generate \
--model juggernaut_xl_v9_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_coloring_5-7_dino_bird.png" \
--prompt "ColoringBookAF, Coloring Book, coloring page for kids, a smiling dinosaur and a small bird in a jungle, thick black outlines, simple shapes with a few playful details like leaves and spots, large open areas easy to color, pure white background, black and white line art, whole scene inside the frame" \
--negative-prompt "color, colour, shading, gray, grayscale fill, gradient, shadows, hatching, tiny details, texture, sketch, messy lines, broken lines, text, watermark, border, 3d, photo" \
--width 832 --height 1216 --steps 30 --cfg 6.0 \
--config-json '{
"sampler": 0,
"schedule_sampler": 12,
"upscaler": "realesrgan_x4plus_anime_6b_f16.ckpt",
"loras": [
    {"file": "redmond_coloringbook_lora_f16.ckpt", "weight": 0.95, "mode": "all"}
  ]
}'
```

Why: LoRA alone gives default medium detail; two subjects max; "easy to color" steers area size.

### COL-C · Kids coloring · age 8-10

Match: detailed kids coloring, patterns, many small areas, challenge.

```bash
draw-things-cli generate \
--model juggernaut_xl_x_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_coloring_8-10_sea_turtle.png" \
--prompt "ColoringBookAF, Coloring Book, coloring page for kids age 8 to 10, a detailed underwater scene with a sea turtle, coral and a school of fish, medium weight clean black outlines, decorative patterns on the shell and fins, many small areas to color, pure white background, black and white line art" \
--negative-prompt "color, colour, shading, gray, grayscale fill, gradient, shadows, sketch, messy lines, broken lines, blurry, text, watermark, border, 3d, photo" \
--width 832 --height 1216 --steps 32 --cfg 6.0 \
--config-json '{
"sampler": 4,
"schedule_sampler": 14,
"upscaler": "4x_nmkd_superscale_sp_178000_g_f16.ckpt",
"loras": [
    {"file": "redmond_coloringbook_lora_f16.ckpt", "weight": 0.9, "mode": "all"},
    {"file": "add_detail_xl_lora_f16.ckpt", "weight": 0.6, "mode": "all"}
  ]
}'
```

Why: positive add-detail + "decorative patterns" = pattern-rich areas older kids enjoy; NMKD keeps thin lines clean.

### COL-K · Kids coloring, fast draft · age 2-4 (Klein)

Match: instant coloring-page draft. Expect occasional broken outlines; if so use COL-A.

```bash
draw-things-cli generate \
--model flux_2_klein_4b_f16.ckpt \
--output "$HOME/Dev/tmp/klein_coloring_2-4_bear.png" \
--prompt "A big friendly bear waving hello, a coloring book page with thick uniform black outlines, every shape fully closed, flat pure white background, large open areas left blank ready for coloring, simple clear shapes, even flat lighting, single centred subject, whole bear inside the frame, wide white margin around the edges" \
--width 1216 --height 1600 --steps 8 --cfg 1.0 \
--config-json '{
"sampler": 10,
"schedule_sampler": 15,
"upscaler": "realesrgan_x4plus_anime_6b_f16.ckpt",
"loras": []
}'
```

Why: positive-only wording ("flat pure white background") replaces the unusable negative prompt; 8 steps for edge stability; no color or shadow words anywhere.

### ADC-A · Adult coloring / line art · teen, adult

Match: intricate coloring page, animals, botanical, scenes, fine line work. Teen: lower add-detail to 0.5.

```bash
draw-things-cli generate \
--model juggernaut_xl_x_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_coloring_adult_fox_forest.png" \
--prompt "ColoringBookAF, Coloring Book, intricate adult coloring page, a fox curled up in a forest of ferns and wildflowers, fine clean black linework, detailed botanical patterns in the fur and leaves, varied line weight, pure white background, black and white line art, balanced composition" \
--negative-prompt "color, shading, gray fill, gradient, shadows, sketch, smudges, messy lines, broken lines, blurry, text, watermark, signature, border, photo, 3d render, low contrast" \
--width 832 --height 1216 --steps 34 --cfg 6.0 \
--config-json '{
"sampler": 4,
"schedule_sampler": 14,
"upscaler": "4x_nmkd_superscale_sp_178000_g_f16.ckpt",
"loras": [
    {"file": "redmond_coloringbook_lora_f16.ckpt", "weight": 0.8, "mode": "all"},
    {"file": "redmondv2_lineart_lineani_lora_f16.ckpt", "weight": 0.4, "mode": "all"},
    {"file": "add_detail_xl_lora_f16.ckpt", "weight": 0.9, "mode": "all"}
  ]
}'
```

Why: LineAni sharpens/steadies strokes; add-detail adds fine patterning; 34 steps + SDE for edge fidelity.

### ADC-B · Adult mandala (classic) · teen, adult

Match: mandala, radial, symmetrical, meditation, geometric.

```bash
draw-things-cli generate \
--model juggernaut_xl_v9_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_mandala_adult_classic.png" \
--prompt "ColoringBookAF, Coloring Book, adult mandala coloring page, perfectly symmetrical circular mandala with layered petals, geometric rings, paisley and dotwork borders, fine crisp black lines, centered radial composition, pure white background, black and white line art" \
--negative-prompt "color, shading, gray, gradient, shadows, asymmetry, off-center, sketch, blurry, broken lines, filled black areas, text, watermark, background texture, photo" \
--width 1024 --height 1024 --steps 32 --cfg 7.0 \
--config-json '{
"sampler": 0,
"schedule_sampler": 12,
"upscaler": "4x_ultrasharp_f16.ckpt",
"loras": [
    {"file": "redmond_coloringbook_lora_f16.ckpt", "weight": 0.85, "mode": "all"},
    {"file": "add_detail_xl_lora_f16.ckpt", "weight": 1.0, "mode": "all"}
  ]
}'
```

Why: higher CFG 7 enforces symmetry words; square canvas suits radial; UltraSharpV2 maximizes hairline crispness (if halos appear, swap to NMKD).

### ADC-C · Adult mandala with subject · teen, adult

Match: animal mandala, owl, lion, butterfly, moon, zentangle hybrid.

```bash
draw-things-cli generate \
--model juggernaut_xl_x_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_mandala_adult_owl.png" \
--prompt "ColoringBookAF, Coloring Book, intricate adult coloring page, mystical owl perched on a crescent moon, wings and body built from complex mandala patterns, stars and leaves, fine clean black linework, pure white background, black and white line art, centered" \
--negative-prompt "color, shading, gray, gradient, shadows, sketch, blurry, broken lines, filled black areas, messy lines, text, watermark, background texture, photo, 3d render" \
--width 1024 --height 1024 --steps 30 --cfg 6.0 \
--config-json '{
"sampler": 0,
"schedule_sampler": 12,
"upscaler": "4x_nmkd_superscale_sp_178000_g_f16.ckpt",
"loras": [
    {"file": "redmond_coloringbook_lora_f16.ckpt", "weight": 0.8, "mode": "all"},
    {"file": "redmondv2_lineart_lineani_lora_f16.ckpt", "weight": 0.35, "mode": "all"},
    {"file": "add_detail_xl_lora_f16.ckpt", "weight": 0.9, "mode": "all"}
  ]
}'
```

Why: CFG 6 balances a recognizable subject against pattern fill; juggernaut_x follows "built from mandala patterns" better than v9.

### SKT-A · Pencil / graphite sketch · teen, adult

Match: pencil drawing, graphite, cross-hatching, charcoal-like, sketchbook.

```bash
draw-things-cli generate \
--model juggernaut_xl_v9_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_sketch_adult_lighthouse.png" \
--prompt "sketch style, graphite pencil drawing of an old lighthouse on a rocky cliff, detailed cross-hatching, soft shading, visible paper grain, artist sketchbook page, monochrome" \
--negative-prompt "color, photo, 3d render, digital painting, blurry, smooth airbrush, text, watermark, signature, frame" \
--width 896 --height 1152 --steps 30 --cfg 5.0 \
--config-json '{
"sampler": 0,
"schedule_sampler": 12,
"upscaler": "4x_ultrasharp_f16.ckpt",
"loras": [
    {"file": "sketch_style_lora_f16.ckpt", "weight": 0.85, "mode": "all"},
    {"file": "add_detail_xl_lora_f16.ckpt", "weight": 0.3, "mode": "all"}
  ]
}'
```

Why: low CFG keeps natural, uneven pencil tone; "paper grain" + monochrome prevent painted look; UltraSharpV2 preserves hatching.

### SKT-B · Ink / travel sketch · teen, adult

Match: pen and ink, urban sketch, loose lines, architecture.

```bash
draw-things-cli generate \
--model juggernaut_xl_x_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_sketch_adult_ink_street.png" \
--prompt "sketch style, LineAniAF, lineart, pen and ink travel sketch of a narrow cobblestone street with old buildings and a bicycle, loose confident linework, monochrome ink on white paper, sketchbook page" \
--negative-prompt "color, photo, 3d render, painting, blurry, heavy shading, text, watermark, signature, frame" \
--width 1216 --height 832 --steps 30 --cfg 5.5 \
--config-json '{
"sampler": 1,
"schedule_sampler": 10,
"upscaler": "rrdb_psnr_x4_f16.ckpt",
"loras": [
    {"file": "sketch_style_lora_f16.ckpt", "weight": 0.7, "mode": "all"},
    {"file": "redmondv2_lineart_lineani_lora_f16.ckpt", "weight": 0.5, "mode": "all"}
  ]
}'
```

safetensors
Why: Euler A gives looser, hand-drawn strokes; RRDB-PSNR upscales without inventing texture.

### SKT-C · Simple pencil drawing · age 8-10

Match: kids drawing practice, simple pencil animal, tutorial reference, kid-safe.

```bash
draw-things-cli generate \
--model juggernaut_xl_v9_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_sketch_8-10_sleeping_fox.png" \
--prompt "sketch style, simple pencil drawing of a sleeping fox curled in a circle, clean soft graphite lines, light shading, white paper, drawing practice reference, monochrome" \
--negative-prompt "color, photo, 3d render, painting, cluttered, complex background, blurry, text, watermark, signature, frame, scary" \
--width 1024 --height 1024 --steps 28 --cfg 5.0 \
--config-json '{
"sampler": 0,
"schedule_sampler": 12,
"upscaler": "rrdb_psnr_x4_f16.ckpt",
"loras": [
    {"file": "sketch_style_lora_f16.ckpt", "weight": 0.7, "mode": "all"},
    {"file": "add_detail_xl_lora_f16.ckpt", "weight": -0.3, "mode": "all"}
  ]
}'
```

Why: slight negative detail = fewer, copyable shapes; one simple subject. (RRDB-PSNR)

### ANI-A · 2D anime chibi / mascot · age 5-10

Match: cute mascot, chibi, kawaii, sticker, kid-friendly anime. No humans keeps it age-safe.

```bash
draw-things-cli generate \
--model animagine_xl_v3.1_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_anime_5-10_chibi_fox.png" \
--prompt "no humans, chibi, cute fox mascot, big sparkling eyes, smiling, holding a small star, simple pastel background, masterpiece, high score, great score, absurdres" \
--negative-prompt "nsfw, lowres, bad anatomy, bad hands, text, error, missing finger, extra digits, fewer digits, cropped, worst quality, low quality, low score, bad score, average score, signature, watermark, username, blurry" \
--width 1024 --height 1024 --steps 28 --cfg 6.0 \
--config-json '{
"sampler": 1,
"schedule_sampler": 10,
"upscaler": "realesrgan_x4plus_anime_6b_f16.ckpt",
"loras": []
}'
```

Why: Animagine's documented tag order (subject, then quality tags) and Euler A; no LoRA needed; "nsfw" always in negative.

### ANI-B · 2D anime illustration (SFW) · teen, adult

Match: anime character scene, key visual, cinematic anime, wallpaper. Always SFW, adult-appearing characters.

```bash
draw-things-cli generate \
--model animagine_xl_v3.1_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_anime_adult_rooftop.png" \
--prompt "1girl, adult, solo, silver hair, long coat, standing on a rooftop at sunset, city skyline, wind blowing, looking at viewer, soft smile, detailed background, cinematic lighting, masterpiece, high score, great score, absurdres" \
--negative-prompt "nsfw, lowres, bad anatomy, bad hands, text, error, missing finger, extra digits, fewer digits, cropped, worst quality, low quality, low score, bad score, average score, signature, watermark, username, blurry" \
--width 832 --height 1216 --steps 28 --cfg 7.0 \
--config-json '{
"sampler": 1,
"schedule_sampler": 10,
"upscaler": "realesrgan_x4plus_anime_6b_f16.ckpt",
"loras": [
    {"file": "add_detail_xl_lora_f16.ckpt", "weight": 0.5, "mode": "all"}
  ]
}'
```

Why: portrait size for a full-body character plus skyline; CFG 7 for tag adherence; mild add-detail enriches background.

### ANI-C · Anime line art for coloring · teen, adult

Match: manga line art, anime coloring page, inking, B/W character.

```bash
draw-things-cli generate \
--model animagine_xl_v3.1_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_anime_lineart_samurai.png" \
--prompt "LineAniAF, lineart, 1boy, adult, solo, samurai standing under cherry blossoms, katana sheathed at the hip, clean black lineart, monochrome, flat white background, coloring page, masterpiece, high score, great score, absurdres" \
--negative-prompt "nsfw, color, shading, gray fill, gradient, shadows, lowres, bad anatomy, bad hands, text, watermark, signature, blurry, worst quality, low quality, low score" \
--width 832 --height 1216 --steps 28 --cfg 6.0 \
--config-json '{
"sampler": 1,
"schedule_sampler": 10,
"upscaler": "realesrgan_x4plus_anime_6b_f16.ckpt",
"loras": [
    {"file": "redmondv2_lineart_lineani_lora_f16.ckpt", "weight": 0.8, "mode": "all"},
    {"file": "redmond_coloringbook_lora_f16.ckpt", "weight": 0.4, "mode": "all"}
  ]
}'
```

Why: LineAni dominant for ink quality, ColoringBook low to force white fills without degrading anime anatomy.

### 3D-A · 3D cute character · age 2-7

Match: toy-like 3D animal, cute plush render, nursery 3D, bright.

```bash
draw-things-cli generate \
--model colorfulxl_v6.0_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_3d_2-7_baby_penguin.png" \
--prompt "cute 3d animated character, a round baby penguin with huge shiny eyes wearing a tiny red scarf, soft rounded toy-like shapes, smooth clay-like material, soft studio lighting, pastel background, shallow depth of field, high quality render" \
--negative-prompt "scary, creepy, realistic fur, photo, 2d, flat, lowres, deformed, extra limbs, text, watermark, dark" \
--width 1024 --height 1024 --steps 30 --cfg 5.5 \
--config-json '{
"sampler": 0,
"schedule_sampler": 12,
"upscaler": "4x_foolhardy_remacri_extrasmoother_f16.ckpt",
"loras": [
    {"file": "pixar_style_lora_f16.ckpt", "weight": 0.8, "mode": "all"},
    {"file": "3d_render_style_xl_lora_f16.ckpt", "weight": 0.4, "mode": "all"}
  ]
}'
```

Why: colorfulxl keeps pastel saturation; "toy-like, clay-like" describes the look without naming a studio; Remacri keeps surfaces smooth.

### 3D-B · 3D character in scene · age 8-10, teen

Match: animated-film still, character + environment, cinematic 3D.

```bash
draw-things-cli generate \
--model juggernaut_xl_x_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_3d_8-10_inventor_robot.png" \
--prompt "3d animated film still, a young inventor and her small robot companion exploring a neon-lit greenhouse, expressive faces, detailed fabric and plant textures, warm rim lighting, cinematic depth of field, wide shot" \
--negative-prompt "photo, realistic skin, 2d, flat, lowres, deformed, extra limbs, text, watermark, scary, dark, blurry" \
--width 1216 --height 832 --steps 32 --cfg 5.0 \
--config-json '{
"sampler": 4,
"schedule_sampler": 14,
"upscaler": "4x_ultrasharp_f16.ckpt",
"loras": [
    {"file": "pixar_style_lora_f16.ckpt", "weight": 0.7, "mode": "all"},
    {"file": "3d_render_style_xl_lora_f16.ckpt", "weight": 0.5, "mode": "all"},
    {"file": "add_detail_xl_lora_f16.ckpt", "weight": 0.5, "mode": "all"}
  ]
}'
```

Why: juggernaut_x handles multi-element scenes; "realistic skin" in negative keeps characters stylized (never photoreal children).

### 3D-C · 3D isometric / object render · teen, adult

Match: isometric room, product-like 3D, diorama, icon render.

```bash
draw-things-cli generate \
--model juggernaut_xl_v9_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_3d_adult_isometric_bookstore.png" \
--prompt "isometric 3d render of a cozy tiny bookstore room, soft global illumination, smooth plastic and wood materials, pastel palette, clean studio backdrop, high detail" \
--negative-prompt "photo, lowres, text, watermark, noisy, dark, flat 2d, blurry" \
--width 1024 --height 1024 --steps 30 --cfg 5.0 \
--config-json '{
"sampler": 0,
"schedule_sampler": 12,
"upscaler": "4x_ultrasharp_f16.ckpt",
"loras": [
    {"file": "3d_render_style_xl_lora_f16.ckpt", "weight": 0.8, "mode": "all"}
  ]
}'
```

Why: no character LoRA (object, not character); single LoRA at 0.8 keeps materials consistent.

### DIG-A · Digital flat vector / sticker · all ages (Klein)

Match: sticker, icon, logo-like illustration, flat vector, app art, set of assets.

```bash
draw-things-cli generate \
--model flux_2_klein_4b_f16.ckpt \
--output "$HOME/Dev/tmp/klein_digital_vector_rocket.png" \
--prompt "A flat vector sticker of a smiling rocket ship launching between two stars, bold clean shapes with a thick white sticker border, limited bright palette, the rocket body is color #F4F1DE and the fins are color #E07A5F, soft even light, centred on a plain pale background" \
--width 1024 --height 1024 --steps 4 --cfg 1.0 \
--config-json '{
"sampler": 10,
"schedule_sampler": 15,
"upscaler": "realesrgan_x4plus_anime_6b_f16.ckpt",
"loras": []
}'
```

Why: Klein's strength is clean shapes and exact hex colors; fixed palette hexes make a coherent multi-image set.

### DIG-B · Digital painting / concept art · teen, adult

Match: fantasy landscape, concept art, painterly digital, wallpaper.

```bash
draw-things-cli generate \
--model colorfulxl_v6.0_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_digital_adult_floating_island.png" \
--prompt "epic digital painting of a floating island village at dawn, waterfalls spilling into clouds, glowing lanterns, rich saturated colors, volumetric light, painterly brush strokes, concept art, wide landscape" \
--negative-prompt "photo, lowres, blurry, text, watermark, deformed, ugly, cropped, jpeg artifacts" \
--width 1216 --height 832 --steps 30 --cfg 6.0 \
--config-json '{
"sampler": 0,
"schedule_sampler": 12,
"upscaler": "4x_foolhardy_remacri_extrasmoother_f16.ckpt",
"loras": [
    {"file": "add_detail_xl_lora_f16.ckpt", "weight": 0.6, "mode": "all"}
  ]
}'
```

Why: colorfulxl's saturation suits fantasy; add-detail enriches small architecture; Remacri keeps brushwork smooth.

### PHO-A · Photography: landscape · all ages

Match: landscape photo, nature, golden hour, scenery.

```bash
draw-things-cli generate \
--model juggernaut_xl_x_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_photo_landscape_mountain_lake.png" \
--prompt "photo of a misty mountain lake at sunrise, pine forest on the shore, golden light on the peaks, calm reflection, landscape photography, 24mm wide angle, sharp focus, natural colors" \
--negative-prompt "illustration, painting, cartoon, oversaturated, hdr, lowres, blurry, noise, text, watermark, people, oversharpened" \
--width 1216 --height 832 --steps 34 --cfg 4.5 \
--config-json '{
"sampler": 4,
"schedule_sampler": 14,
"upscaler": "realesrgan_x4plus_f16.ckpt",
"loras": [
    {"file": "add_detail_xl_lora_f16.ckpt", "weight": 0.5, "mode": "all"}
  ]
}'
```

Why: low CFG = natural color; "hdr/oversaturated" in negative; camera terms are valid for photoreal only.

### PHO-B · Photorealism: adult portrait · adult

Match: portrait photo, headshot, character study. Invented adults only; never a real person's likeness, never a child.

```bash
draw-things-cli generate \
--model juggernaut_xl_v9_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_photo_adult_portrait_fisherman.png" \
--prompt "portrait photo of an adult fisherman with weathered skin and a gray beard, wool cap, soft window light, 85mm lens, shallow depth of field, natural skin texture, candid expression" \
--negative-prompt "illustration, cartoon, plastic skin, airbrushed, deformed, extra fingers, lowres, blurry, text, watermark, child" \
--width 896 --height 1152 --steps 35 --cfg 4.5 \
--config-json '{
"sampler": 4,
"schedule_sampler": 14,
"upscaler": "4x_foolhardy_remacri_extrasmoother_f16.ckpt",
"loras": [
    {"file": "add_detail_xl_lora_f16.ckpt", "weight": 0.4, "mode": "all"}
  ]
}'
```

Why: juggernaut_v9 is the strongest skin model here; add-detail kept low to avoid waxy over-texture; Remacri is kind to faces.

### PHO-C · Photography: analog film · teen, adult

Match: vintage, film grain, 35mm, street, nostalgic.

```bash
draw-things-cli generate \
--model juggernaut_xl_x_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_photo_analog_rainy_street.png" \
--prompt "AnalogRedmAF, analog style photo, a rainy city street at night with neon signs and reflections on wet asphalt, a lone cyclist, film grain, soft halation, muted colors, 35mm" \
--negative-prompt "digital, hdr, oversharpened, clean, plastic, cartoon, lowres, text, watermark" \
--width 1216 --height 832 --steps 32 --cfg 5.0 \
--config-json '{
"sampler": 0,
"schedule_sampler": 12,
"upscaler": "realesrgan_x4plus_f16.ckpt",
"loras": [
    {"file": "redmondv2_analog_lora_f16.ckpt", "weight": 0.7, "mode": "all"},
    {"file": "add_detail_xl_lora_f16.ckpt", "weight": 0.2, "mode": "all"}
  ]
}'
```

Why: ESRGAN (non-anime) preserves grain; "clean/oversharpened" negatives fight the digital look.

### PHO-D · Photography: product / macro · all ages

Match: product shot, still life, macro, catalog.

```bash
draw-things-cli generate \
--model juggernaut_xl_v9_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_photo_product_mug.png" \
--prompt "product photo of a ceramic coffee mug with steam on a walnut table, soft window light, macro, shallow depth of field, crisp texture, clean minimal background" \
--negative-prompt "illustration, cartoon, lowres, blurry, noise, text, watermark, logo, harsh shadows" \
--width 1024 --height 1024 --steps 32 --cfg 5.0 \
--config-json '{
"sampler": 4,
"schedule_sampler": 14,
"upscaler": "4x_ultrasharp_f16.ckpt",
"loras": [
    {"file": "add_detail_xl_lora_f16.ckpt", "weight": 0.8, "mode": "all"}
  ]
}'
```

Why: high add-detail + UltraSharpV2 = surface micro-texture; "logo" in negative avoids garbled brand text.

### PHO-K · Photography, fast (Klein) · teen, adult

Match: quick photoreal draft, candid scene, adult subjects, text-in-scene. No negative prompt.

```bash
draw-things-cli generate \
--model flux_2_klein_4b_f16.ckpt \
--output "$HOME/Dev/tmp/klein_photo_baker_dawn.png" \
--prompt "A candid street photograph of an elderly baker sliding loaves from a wooden oven at dawn, warm light spilling from the doorway, shot on a 50mm lens at f/2, shallow depth of field, natural film-like colors, flour dust in the air" \
--width 1360 --height 1024 --steps 4 --cfg 1.0 \
--config-json '{
"sampler": 10,
"schedule_sampler": 15,
"upscaler": "realesrgan_x4plus_f16.ckpt",
"loras": []
}'
```

Why: Klein responds to camera/lens language and long scene sentences; ~1 s per draft; promote keepers to PHO-B/A for texture.

### OIL-A · Oil painting: classical landscape · all ages

Match: oil painting, landscape, impressionist, canvas, traditional art.

```bash
draw-things-cli generate \
--model juggernaut_xl_x_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_oil_landscape_tuscany.png" \
--prompt "oil painting, a rolling Tuscan valley at golden hour, cypress trees and a stone farmhouse, visible brushstrokes, rich impasto texture, warm earthy palette, canvas texture, classical landscape painting" \
--negative-prompt "photo, digital, 3d render, smooth, airbrushed, cartoon, lowres, text, watermark, signature, frame" \
--width 1216 --height 832 --steps 32 --cfg 5.5 \
--config-json '{
"sampler": 0,
"schedule_sampler": 12,
"upscaler": "4x_foolhardy_remacri_extrasmoother_f16.ckpt",
"loras": [
    {"file": "oil_painting_slider_lora_f16.ckpt", "weight": 1.0, "mode": "all"},
    {"file": "add_detail_xl_lora_f16.ckpt", "weight": 0.3, "mode": "all"}
  ]
}'
```

Why: slider at 1.0 gives a realistic-oil blend; "smooth, airbrushed" negatives remove digital sheen.

### OIL-B · Oil painting: impasto / dramatic · teen, adult

Match: expressive, palette knife, dramatic, moody, gallery.

```bash
draw-things-cli generate \
--model juggernaut_xl_v9_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_oil_impasto_red_fox.png" \
--prompt "expressive oil painting of a red fox in snow, thick impasto brushwork, bold palette knife strokes, dramatic light, dark moody background" \
--negative-prompt "photo, digital, 3d render, smooth, airbrushed, cartoon, lowres, text, watermark, signature, frame" \
--width 896 --height 1152 --steps 32 --cfg 6.0 \
--config-json '{
"sampler": 4,
"schedule_sampler": 14,
"upscaler": "4x_foolhardy_remacri_extrasmoother_f16.ckpt",
"loras": [
    {"file": "oil_painting_slider_epic_lora_f16.ckpt", "weight": 1.0, "mode": "all"}
  ]
}'
```

Why: epic slider alone for strong impasto; SDE sampler adds chunky texture; do not stack both oil sliders above 1.0 combined.

### OIL-C · Oil-painted storybook · age 8-10

Match: painterly children's scene, dreamy, gift art, keepsake.

```bash
draw-things-cli generate \
--model colorfulxl_v6.0_f16.ckpt \
--output "$HOME/Dev/tmp/sdxl_oil_storybook_8-10_moon_boat.png" \
--prompt "KidsRedmAF, oil painted children's storybook scene, a small boat with a lantern sailing across a calm moonlit sea, whales surfacing in the distance, soft impasto brushstrokes, warm glowing colors, gentle and dreamy" \
--negative-prompt "scary, dark, photo, text, watermark, deformed, blurry, lowres" \
--width 1216 --height 832 --steps 30 --cfg 6.0 \
--config-json '{
"sampler": 0,
"schedule_sampler": 12,
"upscaler": "4x_foolhardy_remacri_extrasmoother_f16.ckpt",
"loras": [
    {"file": "redmondv2_kids_storybook_lora_f16.ckpt", "weight": 0.5, "mode": "all"},
    {"file": "oil_painting_slider_lora_f16.ckpt", "weight": 0.7, "mode": "all"}
  ]
}'
```

Why: two style LoRAs each under 0.75 (sum ~1.2) blend instead of fighting; colorfulxl keeps it warm.

---

## 5. Agent decision rules

### 5.1 Routing (first match wins)

| User signal                                                                           | Recipe family                                               |
| ------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| "fast", "draft", "quick", "sticker", "flat vector", "text in image", hex colors given | Klein: ILL-K, COL-K, DIG-A, PHO-K                           |
| coloring page + age <= 10                                                             | COL-A/B/C (Klein COL-K only if speed > quality)             |
| coloring page + teen/adult, "intricate"                                               | ADC-A                                                       |
| "mandala", "zentangle", "radial", "symmetrical"                                       | ADC-B (pure pattern) or ADC-C (subject + mandala)           |
| children's book, picture book, nursery, bedtime                                       | ILL-A/B/C by age; OIL-C if painterly                        |
| pencil, graphite, charcoal, pen and ink, sketchbook                                   | SKT-A/B (SKT-C for kids)                                    |
| anime, manga, chibi, kawaii, waifu-style character                                    | ANI-A (kids/mascot), ANI-B (illustration), ANI-C (line art) |
| 3D, render, clay, toy-like, animated film look                                        | 3D-A (young), 3D-B (character scene), 3D-C (object/room)    |
| oil painting, impasto, canvas, brushstrokes                                           | OIL-A/B/C                                                   |
| digital painting, concept art, fantasy wallpaper                                      | DIG-B                                                       |
| photo, photoreal, camera/lens words, product, portrait                                | PHO-A/B/C/D (PHO-K for speed)                               |

### 5.2 Age band mapping

| Age   | Subjects | Detail                        | Line weight | Palette             |
| ----- | -------- | ----------------------------- | ----------- | ------------------- |
| 2-4   | 1        | minimal (add-detail negative) | very thick  | bright, flat        |
| 5-7   | up to 2  | simple + few playful details  | thick       | warm, bright        |
| 8-10  | up to 3  | richer, patterns              | medium      | richer, atmospheric |
| teen  | any      | high                          | fine        | any                 |
| adult | any      | high to extreme               | fine        | any                 |

### 5.3 Knobs for under-specified requests

| Requirement                   | Change                                                                                             |
| ----------------------------- | -------------------------------------------------------------------------------------------------- |
| "more detail / intricate"     | add-detail +0.2 to +0.4 (max 1.0), steps +4, sampler 4                                             |
| "simpler / cleaner / younger" | add-detail -0.3 to -1.0, cut subjects and props, thicker-line words                                |
| "faster / cheaper"            | sampler -> schedule_sampler value (AYS) and steps -8; or switch to Klein recipe                    |
| "print quality"               | keep native size, use the recipe's upscaler; coloring pages 832x1216 (SDXL) or 1216x1600 (Klein)   |
| "more vivid / saturated"      | swap model to colorfulxl; CFG +0.5                                                                 |
| "more realistic / natural"    | juggernaut_xl_x, CFG -0.5 to -1, drop style LoRAs                                                  |
| "consistent across a set"     | fixed seed + identical prompt skeleton + identical LoRA weights; Klein: reuse hex palette verbatim |
| "text in the image"           | Klein only, one quoted string, <= 3 words; else leave space and typeset afterwards                 |
| "landscape / spread"          | 1216x832 (SDXL) or 1360x1024 (Klein)                                                               |
| "portrait / poster / page"    | 832x1216 or 896x1152 (SDXL); 1216x1600 (Klein)                                                     |

### 5.4 Troubleshooting

| Symptom                                      | Fix                                                                                                      |
| -------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| Color or gray fills in coloring page         | Strengthen negative (color, shading, gradient); raise ColoringBook to 1.0; use juggernaut not colorfulxl |
| Broken / doubled outlines                    | More steps (+6), sampler 4, LineAni +0.3; Klein: move to SDXL recipe                                     |
| Over-smooth plastic skin                     | add-detail <= 0.4, lower CFG, Remacri -> ESRGAN                                                          |
| Burnt / oversaturated                        | CFG -1, drop Analog or slider LoRAs to 0.5                                                               |
| Muddy or noisy                               | Use `schedule_sampler` value as `sampler`, steps -4                                                      |
| Fused subjects, extra limbs                  | Fewer subjects (see age table); size back to native; negative "extra limbs, deformed"                    |
| LoRA has no effect                           | Missing trigger word; or SDXL LoRA loaded on Klein (remove)                                              |
| Klein ignores a "no X"                       | Rewrite as positive statement; negatives do nothing on Klein                                             |
| Klein looks soft/plastic on painterly styles | Switch to SDXL recipe (OIL, ILL, 3D)                                                                     |
| Output too large after upscale               | Downscale 50% with an image tool; do not retry                                                           |

### 5.5 Safety guardrails (apply before recommending)

- Never produce a likeness of a real child or real person, and never photoreal children. Use invented characters; kids content stays illustrated.
- Kids age bands: nothing frightening, sexualized, or showing distress. Add "scary, dark" to negatives.
- Anime: always SFW, adult-appearing characters outside ANI-A; always include `nsfw` in the negative prompt.
- No franchise, studio, or artist names in prompts. Describe qualities (rounded, clay-like, gouache) instead.
- Klein: never pass `--negative-prompt` or SDXL LoRAs.

### 5.6 Recipe-selection checklist

1. Identify genre, age band, speed vs quality.
2. Pick the recipe via 5.1; if two match, prefer the one whose Match keywords overlap most.
3. Copy command; change only `--prompt` subject, `--output`, size (if orientation differs), and optional `seed`.
4. Smoke-test once (section 0); generate 4 seeds; keep winner; apply 5.3/5.4 adjustments one at a time.
