# FLUX.2 Klein 4B: LoRAs, upscalers and generation profiles for Draw Things CLI

For your MacBook Pro M4 with 48 GB unified memory, I'd build a profile-based image-generation recommendation engine rather than one configuration for every genre. Children's illustrations, adult coloring pages, photorealistic images and anime have different priorities, and a LoRA that helps one style can damage another.

The recommendations below are designed around `flux_2_klein_4b_f16.ckpt`, your `draw-things-cli` workflow, and your preferred `--config-json` format.

A few important distinctions:

- Model compatibility: prefer LoRAs explicitly trained for FLUX.2 Klein 4B. A FLUX.1, SDXL or SD 1.5 LoRA is not automatically compatible.
- Upscaling: distinguish a supported Draw Things upscaler from a standalone ESRGAN or Real-ESRGAN model. A downloadable upscaler is useful only if your installed CLI can load it.
- Resolution: use moderate initial dimensions, then upscale selectively. For coloring books, clean contours matter more than photographic texture; for storybooks, composition and consistent characters matter more than maximum sharpness.
- Reproducibility: keep the seed, prompt, LoRA weights, model version and configuration together for each generated page.

The Draw Things configuration model exposes LoRA weights, sampler IDs, upscaler selection and scale factor. That makes it possible to encode these preferences in an automated recommendation engine.&#x20;

## 1. Recommended LoRAs to download

Start with these three candidates. The first two have explicit Klein 4B support; the third is a useful illustration-style candidate for testing.

### Anime illustration

Sawata97/flux2_4b_koni_animestyle

File: `Flux_klein_4b_anime_Koni.safetensors`

Trigger: `anime_style`

Use for 2D anime, manga-inspired storybooks, stylized teen characters and cel-shaded digital illustrations. Begin at weight `0.65`; test `0.45–0.85`.

[Model and files](https://huggingface.co/Sawata97/flux2_4b_koni_animestyle)

#### Anime Example prompt 1

`The palette is dominated by dark tones. The texture is pronounced, with brushstrokes and traces of paint visible, imitating the process of painting using multi-layered tones. The composition is centered around the figures, and the background flows smoothly in color and tone. The style is abstract, almost sculptural. The style is abstract, almost sculptural. Free, gestural brushstrokes create a sense of movement and action. The muted color palette includes subtle variations in tone. The sense of depth is achieved through different densities of brushstrokes. The light source is diffused, giving the image a slightly cool and mysterious shade. The style of painting is reminiscent of abstract realism and expressionism. Soft shadows that reflect every detail and add volume to the scene. In a field bathed in soft, natural light, stands a 21-year-old young woman of East Asian descent. She wears a light blue short-sleeved shirt, a short khaki skirt, and a vibrant red backpack, suggesting a casual, energetic, and adventurous spirit. Her dark hair is long-cut. The young woman stands with her back to the viewer, her head tilted up as she gazes with wonder into the distance. Her focus is on a colossal, ring-shaped structure dominating the skyline. The gigantic construct, composed of metallic and industrial elements, is positioned in the mid-ground, creating a stark contrast with the idyllic landscape. The surrounding landscape features a golden field in the foreground, transitioning to a winding path that leads toward rolling hills. A small town is nestled on the hillsides. The sky above is a bright blue canvas dotted with puffy white clouds, further emphasizing the vivid contrast with the mechanical monolith. The overall mood is one of discovery, awe, and quiet contemplation. Rendered in a detailed anime style with a strong emphasis on environmental storytelling.`

#### Anime Example prompt 2

`anime_style, masterpiece, best quality, ultra-detailed, dynamic composition, very awa, very aesthetic, incredibly_absurdres, breathtaking, 8k, (surreal:1.5), 1girl, solo, fantasy illustration, limited palette, pastel explosion, white background, profile portrait, looking right, pale skin, soft blush, pink eyes, glowing pupils, very long hair, braided strand, hair transforming into butterflies, rainbow butterflies, paint splash hair, color burst, flowing motion, light particles, painterly texture, soft lighting, dreamlike atmosphere, anime illustration, clean lineart, flat color shading, soft cel shading, pastel palette, high-key lighting, minimal gradients, smooth skin, graphic color blocking, fashion illustration style, modern anime aesthetic, editorial portrait, lo-fi pop art, contemporary japanese digital art, (too many butterflies:1.3), visual poetry theme: "thoughts escape her mind as wings instead of words`

### Pixel art and retro game illustrations

adirik/pixel-art-lora-flux.2-klein-4B

File: `pixelart_lora.safetensors`

Trigger: `PXART4`

Use for pixel-art storybook inserts, game-like creatures and retro illustrations. Start at weight `0.8`. The published training resolution is 512 × 512, so test at that size first.&#x20;

Hugging Face [Model and files](https://huggingface.co/adirik/pixel-art-lora-flux.2-klein-4B)

### Whimsical hand-drawn illustration

noema-art/minoteflux-klein

Trigger: `minote`

Worth evaluating for whimsical children's stories, notebook-like drawings and watercolor-inspired illustrations. Start at `0.65–0.8`; compare against the base model because a style LoRA can impose its own aesthetic.&#x20;

Hugging Face [Model and files](https://huggingface.co/noema-art/minoteflux-klein)

#### minote Example prompts

See `minoteflux-prompts.md`

## 2. Sampler IDs, steps and CFG

These are the numeric sampler IDs exposed by the Draw Things configuration enum.

| Numeric value | Sampler           | Suggested use                                       |
| ------------- | ----------------- | --------------------------------------------------- |
| `0`           | DPM++ 2M Karras   | Comparative test; don't assume it is best for Klein |
| `1`           | Euler A           | Alternative for stylized illustrations              |
| `2`           | DDIM              | Comparison baseline                                 |
| `4`           | DPM++ SDE Karras  | Alternative if supported and tested                 |
| `5`           | UniPC             | General comparison                                  |
| `9`           | TCD               | Specialized; test first                             |
| `10`          | Euler A Trailing  | Alternative for fast sampling                       |
| `12`          | DPM++ 2M AYS      | Alternative sampling schedule                       |
| `13`          | Euler A AYS       | Alternative for stylized art                        |
| `15`          | DPM++ 2M Trailing | Alternative                                         |
| `16`          | DDIM Trailing     | Alternative                                         |
| `17`          | UniPC Trailing    | First sampler to test                               |
| `18`          | UniPC AYS         | Alternative                                         |

These IDs identify the sampler, not a quality ranking. The sampler enum is shared by Draw Things; support and quality can differ by model family and CLI version.

### Starting settings for your distilled Klein model

The 4B distilled model is designed for very few sampling steps. The official model ecosystem demonstrates four-step generation, while its LoRA training guide recommends running trained adapters on the distilled model for inference.

| Profile              | Steps | CFG | Sampler    |
| -------------------- | ----- | --- | ---------- |
| Fast draft           | 4     | 1.0 | `17`       |
| General illustration | 4     | 1.0 | `17`       |
| Style LoRA test      | 4     | 1.0 | `17`       |
| Quality experiment   | 4     | 1.0 | `1` or `0` |

Treat these as initial tests, not a universal optimum. Increasing the step count to 20–30 does not automatically improve a distilled model; benchmark it against the four-step baseline. Similarly, your example's CFG of `5.5` should not be the default for this distilled checkpoint.

If a LoRA's author publishes different settings, record them as a separate profile and compare outputs using the same seed.

## 3. Upscaling strategy

For the native Draw Things workflow, I recommend generating clean images first and upscaling only when the output requires it.

| Use case                   | Preferred approach                                       | Reason                                             |
| -------------------------- | -------------------------------------------------------- | -------------------------------------------------- |
| Children's storybook       | 768–1024 px initial dimension; upscale if needed         | Preserve composition and soft texture              |
| Early-reader illustrations | 768–1024 px; selective 2× upscale                        | Keep simple shapes clean                           |
| Coloring books             | 768–1024 px; inspect contours before enlargement         | Avoid inventing gray shading or closing small gaps |
| Adult mandalas             | 1024 px; selective 2× upscale                            | Preserve fine radial detail                        |
| Informative diagrams       | Generate with ample space around labels; verify all text | Upscaling cannot fix incorrect labels              |
| Photorealism               | 1024 px; modest upscale                                  | Retain natural texture                             |
| Pencil sketches            | 768–1024 px; avoid excessive sharpening                  | Preserve fine graphite-like strokes                |
| Oil and watercolor         | 768–1024 px; modest upscale                              | Preserve brushwork and paper texture               |

### Which upscaler should you use?

There are two different cases:

1. Native Draw Things upscaler: choose a model that is already installed and explicitly recognized by your CLI. The configuration accepts an `upscaler` name and `upscalerScaleFactor`, but the source code alone does not establish which model names your installation supports.

2. External upscaler: a standalone Real-ESRGAN or other super-resolution checkpoint can be used in a separate post-processing pipeline, but it is not automatically a valid value for the Draw Things `upscaler` field.

I would not prescribe an arbitrary Hugging Face upscaler filename as a native Draw Things configuration value without verifying its format and your installed model registry. There is no universal `.safetensors` upscaler that can safely be assumed to work in this field.

For your recommendation engine, use this policy:

- Default: no upscaler.
- If the installed upscaler registry is available: select a supported model by image type and scale factor.
- If the registry is unknown: generate the base image and return an external-upscaling recommendation instead of an unverified model name.
- For line art: reject any upscaling result that introduces gray fills, extra contours, or closed gaps.

## 4. Positive prompting without negative prompts

Since your Klein workflow does not support a conventional negative prompt, use positive specification and explicit exclusions phrased as desired outcomes.

Instead of relying on:

`bad anatomy, blurry, extra fingers, text, watermark`

describe what the image should contain and how it should be constructed:

- Anatomy: “two hands, five clearly separated fingers on each visible hand, natural relaxed pose.”
- Composition: “one central subject, full body visible, generous clean margin on all sides.”
- Coloring pages: “pure white background, bold continuous black outlines, enclosed regions, no gray shading, no filled black areas.”
- Text-free illustrations: “no lettering or labels, visual storytelling only.”
- Clean backgrounds: “uncluttered background with only three supporting objects.”
- Photorealism: “natural skin texture, anatomically plausible hands, realistic lens perspective, physically consistent shadows.”

These are not guaranteed exclusions; they are instructions that improve the probability of the desired result.

### Prompt construction template

Use a stable ordering so the AI agent can build prompts systematically.

1. Subject and action

Who or what is depicted, what they are doing, and the number of subjects.

2. Age group and intended use

Toddler picture book, early reader, middle-grade story, teen graphic novel or adult coloring page.

3. Style and medium

Watercolor, ink line art, colored pencil, oil painting, anime cel shading, photorealistic photography.

4. Composition

Close-up, full body, bird's-eye view, centered subject, clear foreground and background, aspect ratio.

5. Technical quality requirements

Clean edges, coherent perspective, legible silhouettes, continuous outlines, consistent lighting.

6. Desired exclusions expressed positively

White background, no lettering, no extra subjects, no gray shading, generous whitespace.

Prompt rules for the agent

- Prefer concrete visual nouns over long lists of aesthetic adjectives.
- State exact subject counts when they matter.
- Describe foreground, background and layout separately.
- For book series, maintain a character description and palette across prompts.
- For informative books, generate the illustration separately from labels and explanatory text. Add typography during page layout.
- Use LoRA trigger words exactly as documented, near the beginning of the prompt.
- Avoid piling on conflicting styles such as “photorealistic watercolor anime oil painting.”
- If the result fails, change one variable at a time: prompt, LoRA weight, resolution, or sampler.

## 5. Genre-specific examples and CLI profiles

The examples below use four-step sampling and CFG 1.0 as the baseline for the distilled model. LoRA filenames assume the adapters have been imported or otherwise made accessible to your Draw Things installation. If your installation cannot load a particular adapter directly, remove the `loras` entry and use the base-model prompt as a fallback.

### A. Toddler and preschool picture books (ages 2–5)

[Draw your unique and whimsical watercolor children book illustration by Gaelageiros | Fiverr](https://images.openai.com/static-rsc-4/PpW5X9G_bNDvOHOJc6Czovj-wbgT6sRQRuR15ld9eVYIYgufbGpHwb4Lo1WcPKd6xmij21BzMAintbw7gAJcc-BhaCdzG4sn9Qu0kaniY59DMtyz32wMvb7fnB4NxZGeniphv-yQfhQu27IOhVgKQnY-pDRNR0_kpSBCZhwoqso?purpose=inline)

https://au.pinterest.com/pin/1094937728178738767/

Goal: instantly recognizable characters, friendly expressions, simple silhouettes and soft color.

Suggested size: 768 × 1024 · LoRA: none initially · Upscaler: none

```
draw-things-cli generate \
  --model flux_2_klein_4b_f16.ckpt \
  --output "$HOME/Dev/t2/preschool_fox.png" \
  --prompt "A warm children's picture book illustration for ages 2 to 5, one friendly baby fox sitting beside a tiny rabbit in a sunny meadow, rounded simple shapes, large expressive eyes, soft watercolor washes, pastel orange green and sky blue palette, clear silhouettes, gentle daylight, minimal flowers and grass, uncluttered pale cream background, both characters fully visible, ample whitespace around the scene, no lettering, polished traditional picture-book artwork" \
  --width 768 --height 1024 --steps 4 --cfg 1.0 \
  --config-json '{
    "sampler": 17,
    "schedule_sampler": 1,
    "loras": []
  }'
```

Why: low visual complexity and a small palette make the scene easy for young children to parse. Avoid highly detailed backgrounds and excessive contrast.

### B. Early readers (ages 5–8)

[The Enchanted Treehouse | Story.com](https://images.openai.com/static-rsc-4/s_LibnO_Kv3TqLc9ZUnx1zxILsgK9WLZSCXkqzzaUD8kF9Fq4TMTdU114yZM6eg77-16xMHDAz5cIJ3lZR2MEYkbXLFC-0dHLd_OVcCq3Eju2WDsRN2tq2sq5w63rXhiAQ5AG216mY-zd2JfQ-tiyqMf4pgledxSos_EY4GOM60?purpose=inline)

Goal: clear action, expressive faces and repeatable characters.

Suggested size: 768 × 1024 · LoRA: optional `minote` · Weight: 0.7

```
draw-things-cli generate \
  --model flux_2_klein_4b_f16.ckpt \
  --output "$HOME/Dev/t2/early_reader_owl.png" \
  --prompt "minote, an illustrated early-reader storybook scene for ages 5 to 8, a curious young child wearing a yellow raincoat discovers a friendly owl in a wooden treehouse, clear storytelling action, expressive faces, soft hand-painted watercolor and colored pencil texture, warm greens and golden yellow, three simple background props, coherent perspective, clear separation between characters and background, full figures visible, charming and reassuring mood, no text, polished children's book illustration" \
  --width 768 --height 1024 --steps 4 --cfg 1.0 \
  --config-json '{
    "sampler": 17,
    "schedule_sampler": 1,
    "loras": [
      {"file": "minoteflux-klein.safetensors", "weight": 0.7, "mode": "all"}
    ]
  }'
```

Why: a restrained style LoRA can create a hand-drawn look; the moderate weight leaves room for the prompt to determine the scene. Verify the actual filename in the downloaded repository before running.

### C. Middle-grade and teen storybooks (ages 9–17)

[To save a dying kingdom, five strangers must brave a land where legends were buried for a reason | Fiction](https://images.openai.com/static-rsc-4/0z0pdEtk7vM0R8j-EvUpgnXweRdOCXRvrNAfUMrl6yapBAdSzbvPGzKbTy1w3vQqYBHlhTF3InlCBw9WCMx0gJXrYFmbwaW89nKYbjpTNu0fJnwE16z8sRvK3VT62lxElcfCLGnKgbYHa93run_UiKvie5zcom081PZSydH0gaU?purpose=inline)

Goal: richer environments, atmosphere, character design and stronger composition.

Suggested size: 832 × 1216 · Anime option: `anime_style` · Weight: 0.65

```
draw-things-cli generate \
  --model flux_2_klein_4b_f16.ckpt \
  --output "$HOME/Dev/t2/teen_fantasy.png" \
  --prompt "anime_style, a polished fantasy storybook illustration for readers aged 12 to 17, two teenage adventurers crossing an ancient stone bridge above a misty mountain valley, one carrying a lantern and the other holding a folded map, dynamic but readable silhouettes, layered mountains, cinematic morning light, intricate clothing details, rich teal and amber palette, controlled atmospheric depth, consistent facial proportions, coherent hands and fingers, wide environmental composition, professional anime background painting, no lettering" \
  --width 832 --height 1216 --steps 4 --cfg 1.0 \
  --config-json '{
    "sampler": 17,
    "schedule_sampler": 1,
    "loras": [
      {"file": "Flux_klein_4b_anime_Koni.safetensors", "weight": 0.65, "mode": "all"}
    ]
  }'
```

Why: anime styling reinforces linework and character design. If the result becomes overly stylized, reduce the weight to `0.45–0.55`. For painterly fantasy, omit the LoRA and explicitly describe brushwork and lighting.

### D. Children's coloring books (ages 4–8)

[Dinossauro Bebê Fofo Saindo do Ovo - Pintar e Colorir](https://images.openai.com/static-rsc-4/DWhuEaT_gRjxcQ-te2voJQP4PuL0tQtvFcU3L-OxfuSVEiDwgC37INKuKryCL8HsydlUTuU90wqjNlwYsmiflgs3vUIjE-Iv37cnFjnXVfhjL8UxLDgDum3-Y0Klp84Ncu4TwlVKyOAb23WVM7WY-LrYFwMvLDNkCT61QT9JXNk?purpose=inline)

Goal: large enclosed regions, thick outlines, very low detail density.

Suggested size: 768 × 768 · LoRA: none initially · Upscaler: optional

```
draw-things-cli generate \
  --model flux_2_klein_4b_f16.ckpt \
  --output "$HOME/Dev/t2/kids_coloring_dinosaur.png" \
  --prompt "Printable black and white coloring book page for children ages 4 to 8, one cute baby dinosaur hatching from a large egg, bold smooth continuous black outlines of uniform thickness, pure white background, closed clearly separated shapes, large easy-to-color areas, simple rounded cartoon anatomy, a few large clouds and flowers, centered composition, generous white margins, crisp vector-like line art, black outlines only, no gray, no gradients, no shadows, no crosshatching, no filled black regions, no lettering" \
  --width 768 --height 768 --steps 4 --cfg 1.0 \
  --config-json '{
    "sampler": 17,
    "schedule_sampler": 1,
    "loras": []
  }'
```

Why: the prompt explicitly prioritizes enclosed shapes and thick outlines rather than merely saying “coloring book.” Inspect the image at actual print size; thin gaps and disconnected contours can make a page difficult to color.

### E. Adult mandala coloring books

[Owl or eagle-owl bird sketch vector isolated icon. Wild forest feathered predatory bird of prey sitting on branch. Wildlife fauna and zoology symbol for zoo nature adventure club. Ethnic doodle motifs](https://images.openai.com/static-rsc-4/6e3zf5x42EFcQhJt4m8OUDolx6dQPLwSoxV51QOpZA4m4gJIPMo2YSgdNLdqOi86h1Qy_uSIUyMDhqPE6EVzXMHlJ0bBs-E-gEoQnGr8gxrFl02LE_BxxisXRMCciMQpin6n9oxurDrNCqiUj4Un2ZZKq0x-46FytLpJBo6Wm3FZPhfCuEQ6v8cKUcLgD69N?purpose=inline)

Goal: radial symmetry, fine line detail and many closed regions.

Suggested size: 1024 × 1024 · LoRA: none initially · Upscaler: selective 2×

```
draw-things-cli generate \
  --model flux_2_klein_4b_f16.ckpt \
  --output "$HOME/Dev/t2/adult_mandala_owl.png" \
  --prompt "Intricate adult coloring book page, a majestic owl centered inside a perfectly radial circular mandala, layered symmetrical feather motifs, repeating botanical ornaments, balanced geometric rings, fine consistent black contour lines, many distinct enclosed coloring regions, elegant symmetrical composition, pure white background, uniform line weight, crisp monochrome vector-like ink drawing, full circular design inside a generous white margin, no grayscale, no gradients, no shadows, no crosshatching, no solid black background, no lettering" \
  --width 1024 --height 1024 --steps 4 --cfg 1.0 \
  --config-json '{
    "sampler": 17,
    "schedule_sampler": 1,
    "loras": []
  }'
```

Why: the mandala's symmetry and enclosure requirements are specified directly. For print publication, validate line thickness and symmetry after generation; upscale only if it preserves contours.

### F. Non-fiction and informative books for kids and teens

[Arm And Hammer Volcano at Ester Gordan blog](https://images.openai.com/static-rsc-4/a4o3Z5-IsaeA_S2COzn9fdM4r98zq3Z1nE5Bl1ninNEoNCWic1uIQBBf93whe3gaQy8D4qYg4pX1lzB8XplKFwcFdjD1OfrwPu8Mas198C8XOtgUtEK1LreVc3fd04yhisJrjVoBvM8Wd-Ro_0gZTc1_mpuuq5ILMTveVjA1a5s?purpose=inline)

Goal: correct structure, clear visual hierarchy and space for labels.

Suggested size: 1024 × 768 · LoRA: none · Add typography separately

```
draw-things-cli generate \
  --model flux_2_klein_4b_f16.ckpt \
  --output "$HOME/Dev/t2/volcano_education.png" \
  --prompt "A scientifically grounded educational textbook illustration for readers aged 9 to 14, a clear cutaway cross-section of a volcano showing the cone, central vent, magma chamber, branching side vent and ash plume, distinct layers with clean boundaries, accurate spatial relationships, clear uncluttered composition, professional museum educational illustration, restrained orange red brown and blue palette, plain light background, leave empty callout spaces around the diagram for later labels, no text, no letters, no numbers, no decorative clutter" \
  --width 1024 --height 768 --steps 4 --cfg 1.0 \
  --config-json '{
    "sampler": 17,
    "schedule_sampler": 1,
    "loras": []
  }'
```

Why: labels, scientific claims and diagram accuracy should be validated separately. Generate the visual structure, then add real labels in a vector or page-layout tool. For anatomy, machinery or other high-precision topics, use a verified reference image or diagram as a guide rather than relying on prompt-only generation.

### G. Pencil and artistic sketches

[Pencil Study of a Bird Perched on a Branch](https://images.openai.com/static-rsc-4/cqF-1Qrv6daxAwPG8fjSDXT8ujvoFxHpwIwlYctmXKcg6wSlb6jcFh_8YfwgzQFBmgDv2IMQFgIxRkWBjQ5saqvabr_lA9--7c5xeB-WGCa58gUhvRWEbmbPJMpcTi1fV7KGc_MG9n4IcTUabAHHAz8r1_Vngf3T4eEpis1IsBQ?purpose=inline)

Goal: natural graphite marks, tonal variation and visible paper texture.

Suggested size: 768 × 1024 · LoRA: none · Upscaler: optional

```
draw-things-cli generate \
  --model flux_2_klein_4b_f16.ckpt \
  --output "$HOME/Dev/t2/pencil_bird.png" \
  --prompt "Traditional graphite pencil study of a small bird perched on a natural branch, realistic bird anatomy and feather layering, confident pencil contours, delicate hatching, varied graphite pressure, subtle paper grain, carefully observed proportions, soft natural daylight, white sketchbook paper, elegant hand-drawn fine-art study, visible pencil strokes, restrained tonal shading, no ink outlines, no color, no digital airbrush, no lettering" \
  --width 768 --height 1024 --steps 4 --cfg 1.0 \
  --config-json '{
    "sampler": 17,
    "schedule_sampler": 1,
    "loras": []
  }'
```

Why: specifying the drawing medium, mark-making and paper helps avoid a generic digital illustration. If the result looks too smooth, change the prompt before increasing resolution.

### H. Oil painting and watercolor

[イラスト生成プロンプト配布：クラシックな児童書の挿絵風｜ミライ｜学び続けるデザイナー🐰](https://images.openai.com/static-rsc-4/jzNzCjhRAruuCteZv1Jfp_yxE3uIvK6AGpAOQQugDQh3ipFMIPogjnk0b6FchEMKk1-bj3ikCHWVZHNG_cCVXsxlR2zvS-qCe0UdlmLZBxHYZU1goT8i1q-wdnhrptBIUfvhDKsEQ7qe1E4v6IrP-57J0HhUVUuAip6-jsYkHRw?purpose=inline)

Goal: preserve the characteristic medium rather than produce a generic digital painting.

Suggested size: 832 × 1024 · LoRA: optional `minote` for whimsical watercolor

```
draw-things-cli generate \
  --model flux_2_klein_4b_f16.ckpt \
  --output "$HOME/Dev/t2/watercolor_cottage.png" \
  --prompt "A traditional watercolor landscape painting of a small stone cottage surrounded by wildflowers, translucent pigment washes, soft wet-on-wet transitions, visible cold-pressed paper texture, delicate granulation, loose natural brushwork, subtle edges, fresh spring palette, atmospheric depth, gentle morning light, carefully composed foreground and background, authentic watercolor medium, no glossy digital finish, no lettering" \
  --width 832 --height 1024 --steps 4 --cfg 1.0 \
  --config-json '{
    "sampler": 17,
    "schedule_sampler": 1,
    "loras": []
  }'
```

Oil variation: replace the medium description with “traditional oil painting, visible impasto brushstrokes, layered opaque pigments, rich pigment mixing, canvas texture, deliberate painterly edges.” Use a separate profile for oil; do not combine both media in one prompt.

### I. Photorealism and realistic photography

[Red Fox ( Vulpes vulpes ) close up](https://images.openai.com/static-rsc-4/zqtPqkabM8FA78H4yn5NPax6VL8pkC419exSYaD51xW7pty4_A3rboHc3ntmsioEZdT0EXNKOfpXaNZhNoELN_xaAa2E9n6FjVL07u5wHbnDTBuMBMwZLk6ADC8nvm9SAnTVXXrkPg_NBUYCGe9IMJZit1VEvqSdeC4tGh72tLDSDO8IDQBAYJjdB8AV2S0l?purpose=inline)

Goal: natural lighting, credible anatomy, lens perspective and realistic texture.

Suggested size: 1024 × 768 · LoRA: none initially

```
draw-things-cli generate \
  --model flux_2_klein_4b_f16.ckpt \
  --output "$HOME/Dev/t2/photorealistic_fox.png" \
  --prompt "Photorealistic wildlife photograph of a red fox standing on a mossy forest path, natural fur texture, anatomically plausible body and paws, alert but relaxed posture, soft morning sunlight filtered through trees, physically consistent shadows, realistic depth of field, natural woodland colors, professional wildlife photography, credible lens perspective, sharp focus on the fox's eyes, restrained background bokeh, no painterly texture, no illustration, no lettering" \
  --width 1024 --height 768 --steps 4 --cfg 1.0 \
  --config-json '{
    "sampler": 17,
    "schedule_sampler": 1,
    "loras": []
  }'
```

Why: photographic cues are specified as camera, lighting and material properties rather than a long list of quality buzzwords. For commercial photography-like output, compare the base model before introducing any style LoRA.

### J. 2D anime and digital illustrations

```
draw-things-cli generate \
  --model flux_2_klein_4b_f16.ckpt \
  --output "$HOME/Dev/t2/anime_character.png" \
  --prompt "anime_style, polished 2D anime character illustration, a young adult fantasy cartographer with short silver hair and a deep blue travel coat, holding an antique compass, expressive but natural face, clean confident linework, controlled cel shading, carefully designed clothing folds, limited navy teal and gold palette, three-quarter view, attractive readable silhouette, softly painted fantasy library background, professional anime concept art, coherent hands, no lettering" \
  --width 832 --height 1024 --steps 4 --cfg 1.0 \
  --config-json '{
    "sampler": 17,
    "loras": [
      {"file": "Flux_klein_4b_anime_Koni.safetensors", "weight": 0.65, "mode": "all"}
    ]
  }'
```

Why: explicit cel shading and linework make this a more useful 2D profile than “anime, high quality.” The documented `anime_style` trigger activates the candidate LoRA.

### K. 3D-style characters and scenes

```
draw-things-cli generate \
  --model flux_2_klein_4b_f16.ckpt \
  --output "$HOME/Dev/t2/3d_fantasy_scene.png" \
  --prompt "A polished stylized 3D render of a small friendly robot exploring a miniature greenhouse, appealing rounded geometry, physically based materials, subtle surface roughness, coherent perspective, soft global illumination, realistic contact shadows, glass panels with controlled reflections, colorful plants, cinematic three-point lighting, carefully modeled proportions, clean studio-quality rendering, clear foreground and background separation, no text, no watermark" \
  --width 1024 --height 768 --steps 4 --cfg 1.0 \
  --config-json '{
    "sampler": 17,
    "loras": []
  }'
```

Why: the prompt requests rendering properties, material response and lighting. This is a 3D-rendered look, not a guarantee of a true 3D model or exportable geometry.

## 6. Correcting and extending the example configuration

Your preferred JSON format is suitable, with two caveats:

- The configuration schema exposes `sampler`, `upscaler`, `upscalerScaleFactor` and `loras`. The schema I checked does not establish `schedule_sampler` as a supported property, so omit it unless your installed CLI version confirms that it is accepted.&#x20;

- A LoRA's `file` must resolve to a recognized adapter. An arbitrary downloaded filename or path is not enough to guarantee compatibility.

A conservative reusable template is:

```bash
draw-things-cli generate \
  --model flux_2_klein_4b_f16.ckpt \
  --output "$HOME/Dev/t2/example.png" \
  --prompt "A clearly described subject, action, medium, composition and lighting, with explicit visual requirements" \
  --width 768 --height 768 --steps 4 --cfg 1.0 \
  --config-json '{
    "sampler": 17,
    "loras": []
  }'
```

For a native upscaler that you have verified is available, extend the JSON using the exact registered name:

```bash
{
  "sampler": 17,
  "upscaler": "EXACT_INSTALLED_UPSCALER_NAME",
  "upscalerScaleFactor": 2,
  "loras": []
}
```

The placeholder is intentional; replace it with an actual supported model name. Do not run this version unchanged.

## 7. Recommendations for your AI agent

I would store recommendations as data, not just prose. Each profile should identify the goal, candidate settings, constraints, confidence and validation requirements.

```json
{
  "profile": "adult_coloring_mandala",
  "model": "flux_2_klein_4b_f16.ckpt",
  "purpose": "printable monochrome line art",
  "age_group": "adult",
  "style": ["mandala", "botanical", "geometric"],
  "prompt_requirements": [
    "radial symmetry",
    "continuous black contours",
    "enclosed coloring regions",
    "pure white background",
    "generous white margin"
  ],
  "avoid_by_positive_specification": [
    "gray shading",
    "gradients",
    "crosshatching",
    "solid black background",
    "lettering"
  ],
  "resolution": [1024, 1024],
  "steps": 4,
  "cfg": 1.0,
  "sampler": 17,
  "loras": [],
  "upscaler": null,
  "upscaler_scale_factor": 1,
  "validation": [
    "line continuity",
    "closed regions",
    "symmetry",
    "print-size readability"
  ],
  "confidence": "starting heuristic; benchmark locally"
}
```

### Decision rules

| User requirement                          | Recommendation-engine action                                         |
| ----------------------------------------- | -------------------------------------------------------------------- |
| Simple art for ages 2–5                   | Favor simple shapes, few objects, broad color regions                |
| Detailed teen fantasy                     | Increase composition and environment detail; consider anime LoRA     |
| Printable children's coloring             | Require bold outlines, large enclosed regions and white background   |
| Adult mandala                             | Require radial symmetry, repeated motifs and fine contours           |
| Informative nonfiction                    | Reserve space for labels; require factual review                     |
| Pencil sketch                             | Specify graphite marks, paper and tonal hatching                     |
| Watercolor or oil                         | Specify the medium's physical texture and characteristic edges       |
| Photorealism                              | Emphasize lighting, material realism and plausible anatomy           |
| User requests consistency across a series | Fix character descriptions, palette, seed policy and LoRA weights    |
| Output must be print-ready                | Validate final dimensions, margins, line thickness and image quality |

### Evaluation and optimization loop

For each profile, generate a small comparison set using the same prompt and seed:

1. Base model, sampler `17`, four steps, CFG `1.0`.
2. Same configuration with the candidate LoRA.
3. Same LoRA at a lower weight.
4. Alternative sampler `1`, holding all other settings constant.
5. Upscale only the best candidate, if needed.

Score the outputs for prompt adherence, anatomy, composition, style fidelity, artifact rate and downstream print suitability. Keep per-genre scores separate: a highly detailed image is not necessarily a better coloring page, and a beautiful illustration is not necessarily a correct science diagram.

My recommended first implementation: start with the anime LoRA and pixel-art LoRA, maintain a no-LoRA baseline for every genre, and treat watercolor, pencil, oil and photorealism as prompt-driven profiles until you have verified a suitable Klein 4B-specific adapter. This gives your agent a defensible starting point without depending on unverified LoRAs or upscalers.

# Comprehensive JSON recommendation rules

Created and validated a comprehensive JSON recommendation Draw Things FLUX.2 Klein 4B Recommendation Rules JSON in `klein-recommendation-rules.json`

The file contains 13 generation profiles, 3 LoRA candidates, and 10 selection rules, with machine-readable settings and validation requirements.

Included:

- Profiles: preschool picture books, early readers, teen fantasy, anime, pixel art, children's coloring pages, adult mandalas, educational nonfiction, pencil sketches, watercolor, oil painting, photorealism and 3D-style renders.
- Generation settings: model, dimensions, steps, CFG, numeric sampler ID, LoRA weights and upscaling policy.
- Prompt rules: positive-prompt construction, desired exclusions, style triggers and genre-specific constraints.
- Selection logic: prioritized rules for choosing profiles, handling unsupported LoRAs and avoiding unverified upscalers.
- Evaluation: baseline comparisons, controlled experiments, scoring criteria and genre-specific validation.
- CLI integration: configuration fields, command-generation template and compatibility safeguards.

The JSON was parsed after writing to verify its syntax.

Important implementation detail: sampler IDs, LoRA loading and native upscaler names remain subject to verification against your installed CLI. The file explicitly records these uncertainties so the agent can fall back safely instead of treating candidate settings as guaranteed compatibility.
