# recommendations

## Prompt

I'm using Flux Klein and SDXL (juggernaut_xl_v9_f16, juggernaut_xl_x_f16, colorfulxl_v6.0_f16, and animagine_xl_v3.1_f16) to create Kids Reading Book Illustrations, Kids and adults Coloring Books & Line Art, Adults Mandala Coloring Books, Pencil & Artistic Sketches, 2D/3D anime illustrations, digital drawings, photography, oil painting, Photorealism, etc.

For each genre, can you create a markdown table with recommendations on which models, loras (multi-loras are okay if needed), along with other settings like steps, guidanceScale, sampler, schedule_sampler.

---

Here are my recommendations. SDXL is a different ecosystem from Flux Klein: SDXL LoRAs won't load on Klein, and Flux.1 LoRAs generally won't either. So each genre has SDXL rows (checkpoint + LoRAs) and a Klein row that relies on prompting.

## Baseline settings

| Model                  | Steps | guidanceScale | Sampler      | schedule_sampler | Notes                                                                                  |
| ---------------------- | ----- | ------------- | ------------ | ---------------- | -------------------------------------------------------------------------------------- |
| Flux Klein (distilled) | 4     | 1.0           | Euler        | Simple           | Ignores negative prompts, so phrase everything positively                              |
| Flux Klein (base)      | 28–40 | 3.5–4.5       | Euler        | Simple           | Slower but more variety; negative prompts work                                         |
| Juggernaut XL v9 / X   | 30–40 | 4–6           | DPM++ 2M SDE | Karras           | CFG above 7 gets harsh and "fried"                                                     |
| ColorfulXL v6          | 28–35 | 5–7           | DPM++ 2M     | Karras           | Saturated, illustrative default                                                        |
| Animagine XL v3.1      | 25–28 | 5–7           | Euler a      | Normal/Simple    | Danbooru-style tags; start with `masterpiece, best quality, very aesthetic, absurdres` |

## Kids reading book illustrations

| Option                | Model             | LoRA(s)                       | Steps | guidanceScale | sampler  | schedule_sampler |
| --------------------- | ----------------- | ----------------------------- | ----- | ------------- | -------- | ---------------- |
| Primary               | ColorfulXL v6     | StorybookRedmond 0.7–0.9      | 30    | 6             | DPM++ 2M | Karras           |
| Cartoon/anime-leaning | Animagine XL v3.1 | LineAniRedmond 0.5 (optional) | 28    | 6             | Euler a  | Normal           |
| Flux Klein            | Klein distilled   | none                          | 4     | 1.0           | Euler    | Simple           |

Klein's multi-reference editing helps keep characters consistent from page to page. Feed it your approved character image.

## Kids coloring books and line art

| Option      | Model            | LoRA(s)                     | Steps | guidanceScale | sampler  | schedule_sampler |
| ----------- | ---------------- | --------------------------- | ----- | ------------- | -------- | ---------------- |
| Primary     | ColorfulXL v6    | ColoringBookRedmond 0.8–1.0 | 28    | 7             | DPM++ 2M | Karras           |
| Alternative | Juggernaut XL v9 | ColoringBookRedmond 0.8     | 30    | 6.5           | DPM++ 2M | Karras           |
| Flux Klein  | Klein distilled  | none                        | 4     | 1.0           | Euler    | Simple           |

For SDXL, use the negative prompt `color, shading, gray, gradient, filled areas, photo, text`. For Klein, prompt "bold clean black outlines, thick uniform line weight, pure white background, no shading, no fill".

## Adult coloring books and line art

| Option      | Model           | LoRA(s)                                         | Steps | guidanceScale | Sampler      | schedule_sampler |
| ----------- | --------------- | ----------------------------------------------- | ----- | ------------- | ------------ | ---------------- |
| Primary     | Juggernaut XL X | ColoringBookRedmond 0.6 + Detail Tweaker XL 0.4 | 35    | 6.5           | DPM++ 2M SDE | Karras           |
| Alternative | ColorfulXL v6   | ColoringBookRedmond 0.8                         | 32    | 7             | DPM++ 2M     | Karras           |
| Flux Klein  | Klein base      | none                                            | 30    | 4             | Euler        | Simple           |

Generate at 1024, then upscale 1.5× with a 0.3–0.4 denoise to keep lines fine without redrawing the image. Klein base is good for intricate detail because it follows "fine hairline strokes, dense detail" prompts well.

## Adult mandala coloring books

| Option      | Model           | LoRA(s)                                    | Steps | guidanceScale | Sampler      | schedule_sampler |
| ----------- | --------------- | ------------------------------------------ | ----- | ------------- | ------------ | ---------------- |
| Primary     | Juggernaut XL X | Mandala LoRA 0.7 + ColoringBookRedmond 0.5 | 35    | 7             | DPM++ 2M SDE | Karras           |
| Alternative | ColorfulXL v6   | Mandala LoRA 0.8                           | 30    | 7             | DPM++ 2M     | Karras           |
| Flux Klein  | Klein base      | none                                       | 30–40 | 4             | Euler        | Simple           |

Use a 1024×1024 canvas and prompt for "radially symmetric, centered, black and white line art". If symmetry drifts, generate a quarter or half and mirror it in post.

## Pencil and artistic sketches

| Option             | Model            | LoRA(s)                             | Steps | guidanceScale | sampler  | schedule_sampler |
| ------------------ | ---------------- | ----------------------------------- | ----- | ------------- | -------- | ---------------- |
| Graphite/pencil    | Juggernaut XL v9 | Pencil/graphite sketch LoRA 0.6–0.8 | 30    | 5.5           | DPM++ 2M | Karras           |
| Ink/charcoal/loose | ColorfulXL v6    | Sketch or ink LoRA 0.7              | 30    | 6             | DPM++ 2M | Karras           |
| Flux Klein         | Klein distilled  | none                                | 4     | 1.0           | Euler    | Simple           |

Keep the pencil LoRA at or below 0.8, since higher weights flatten the paper texture. Prompt for "cross-hatching, visible paper grain, graphite smudges".

## 2D anime illustrations

| Option     | Model             | LoRA(s)                       | Steps | guidanceScale | Sampler | schedule_sampler |
| ---------- | ----------------- | ----------------------------- | ----- | ------------- | ------- | ---------------- |
| Primary    | Animagine XL v3.1 | none (or a style LoRA at 0.6) | 28    | 6             | Euler a | Normal           |
| Flux Klein | Klein distilled   | none                          | 4     | 1.0           | Euler   | Simple           |

Animagine works best with tag prompts like `1girl, solo, ... , masterpiece, best quality`, at 832×1216 or 1024×1024.

## 3D anime illustrations

| Option      | Model             | LoRA(s)                              | Steps | guidanceScale | sampler  | schedule_sampler |
| ----------- | ----------------- | ------------------------------------ | ----- | ------------- | -------- | ---------------- |
| Primary     | Animagine XL v3.1 | 3D render/"Pixar-style" LoRA 0.6–0.8 | 28    | 6             | Euler a  | Normal           |
| Alternative | ColorfulXL v6     | 3D character LoRA 0.7                | 30    | 6             | DPM++ 2M | Karras           |
| Flux Klein  | Klein distilled   | none                                 | 4     | 1.0           | Euler    | Simple           |

## Digital drawings and illustration

| Option      | Model           | LoRA(s)               | Steps | guidanceScale | Sampler      | schedule_sampler |
| ----------- | --------------- | --------------------- | ----- | ------------- | ------------ | ---------------- |
| Primary     | ColorfulXL v6   | Detail Tweaker XL 0.3 | 30    | 6             | DPM++ 2M     | Karras           |
| Alternative | Juggernaut XL X | style LoRA as needed  | 32    | 5.5           | DPM++ 2M SDE | Karras           |
| Flux Klein  | Klein base      | none                  | 30    | 4             | Euler        | Simple           |

## Photography

| Option      | Model            | LoRA(s)                          | Steps | guidanceScale | Sampler      | schedule_sampler |
| ----------- | ---------------- | -------------------------------- | ----- | ------------- | ------------ | ---------------- |
| Primary     | Juggernaut XL X  | Detail Tweaker XL 0.3 (optional) | 35    | 4.5           | DPM++ 2M SDE | Karras           |
| Alternative | Juggernaut XL v9 | film/grain LoRA 0.4 (optional)   | 35    | 5             | DPM++ 2M SDE | Karras           |
| Flux Klein  | Klein base       | none                             | 30    | 4             | Euler        | Simple           |

Use real camera language in the prompt ("85mm f/1.8, natural window light, shallow depth of field"). Keep CFG at 5 or below to avoid the oversharpened look.

## Oil painting

| Option      | Model            | LoRA(s)                   | Steps | guidanceScale | Sampler      | schedule_sampler |
| ----------- | ---------------- | ------------------------- | ----- | ------------- | ------------ | ---------------- |
| Primary     | ColorfulXL v6    | Oil painting LoRA 0.7–0.9 | 32    | 6             | DPM++ 2M     | Karras           |
| Alternative | Juggernaut XL v9 | Oil painting LoRA 0.7     | 35    | 5.5           | DPM++ 2M SDE | Karras           |
| Flux Klein  | Klein base       | none                      | 30–40 | 4             | Euler        | Simple           |

Prompt for "visible impasto brushstrokes, canvas texture, palette-knife highlights".

## Photorealism (hyper-detailed)

| Option          | Model            | LoRA(s)                   | Steps | guidanceScale | Sampler      | schedule_sampler |
| --------------- | ---------------- | ------------------------- | ----- | ------------- | ------------ | ---------------- |
| Primary         | Juggernaut XL X  | Detail Tweaker XL 0.4–0.6 | 40    | 4–5           | DPM++ 2M SDE | Karras           |
| Faces/portraits | Juggernaut XL v9 | none                      | 35    | 4.5           | DPM++ 2M SDE | Karras           |
| Flux Klein      | Klein base       | none                      | 35–40 | 4–4.5         | Euler        | Simple           |

For the primary row, add a hires pass: 1.5× upscale, 0.3–0.35 denoise, 20 steps.

## Caveats

- **LoRA names:** StorybookRedmond, ColoringBookRedmond, LineAniRedmond, and Detail Tweaker XL are real SDXL LoRAs. The rows that say "mandala," "pencil," "oil painting," or "3D" are categories, so pick whichever SDXL LoRA you like on Civitai and check it was trained for SDXL, not SD1.5.
- **Klein variants:** The Klein settings assume the 4-step distilled and base variants. If you're running a different size or quant, check its model card for step and CFG ranges.
- **Sampler names:** If your tool uses different labels, "DPM++ 2M Karras" and "DPM++ 2M SDE Karras" map to the sampler plus scheduler pair above.

---

#

## Trigger words and weights

- **Coloring book:** The tags are ColoringBookAF and Coloring Book.
- **Storybook:** The trigger is KidsRedmAF, Kids Book.
- **LineAni:** The trigger is LineAniAF, lineart.
- **Analog:** The trigger is AnalogRedmAF, Analog. I haven't read this one's model card, so I'm inferring the film-grain look from the name and trigger.
- **3D (goofyai):** The triggers are 3d style, 3d, and 3d render.
- **Pixar and oil painting sliders:** The triggers are `pixar-style`, `oil painting` and `epic oil painting`. The Pixar slider's own example loads it at strength 2.0.
- **Pencil:** The Osipova LoRA is triggered by "sketch pencil drawing OSI style".

## Corrections to above table

- **Slider weights:** The ntc-ai LoRAs (Pixar, both oil paintings) are sliders that work on a wider scale than normal LoRAs. Their example applies the oil painting slider at 2.0. Use roughly 1.5–3 for them, not the 0.7–0.9 I listed.
- **Detail Tweaker XL:** Its description says it works from -3 to 3, with a suggested starting weight of 1.5. My 0.3–0.6 was a conservative guess, so tune it by eye. The Hugging Face copy is an unofficial re-upload. The original lives on Civitai (model 122359).
- **Mandala:** I found no dedicated SDXL mandala LoRA on Hugging Face, so I won't invent a repo. The coloring-book LoRA plus a prompt like "radially symmetric mandala, black and white line art" is the safest HF-only setup. Dedicated mandala LoRAs exist on Civitai if you want one.
- **Pencil and sketch:** Linaqruf's LoRA was built for Animagine XL 2.0 and targets monochrome sketch looks, so test it with Animagine 3.1 rather than Juggernaut.
