# SDXL illustration recommendation engine for Draw Things CLI

The best approach is to choose the model for the subject and rendering domain, the LoRA for the intended visual style, the sampler and steps for image formation, and the upscaler for the final output requirements. Keep those decisions separate so your agent can adapt to mixed requests such as “a preschool storybook illustration with watercolor textures” or “an intricate adult coloring page with botanical mandalas.”

Your supplied LoRAs support distinct visual workflows: children's books, clean coloring-book line art, anime line art, oil painting, sketching, analog photography, 3D rendering, and detail enhancement. The StoryBookRedmond and ColoringBookRedmond families have documented trigger words—`KidsRedmAF, Kids Book` and `ColoringBookAF, Coloring Book`, respectively.

## 1. Important CLI conventions

The sampler number in your `--config-json` example is a Draw Things `SamplerType` enum value, not a universal Stable Diffusion sampler ID. The Draw Things configuration source maps `sampler` to that enum, and the current source-backed mapping is:

| `sampler` | Draw Things sampler | Recommended use with your SDXL models                                   |
| --------- | ------------------- | ----------------------------------------------------------------------- |
| `0`       | DPM++ 2M Karras     | General-purpose baseline; photorealism, painting, detailed illustration |
| `1`       | Euler A             | Expressive, organic, sketch-like or painterly variation                 |
| `2`       | DDIM                | Controlled, repeatable comparisons and simple illustrations             |
| `3`       | PLMS                | Legacy option; not my default for new SDXL workflows                    |
| `4`       | DPM++ SDE Karras    | Stochastic detail; experiment for organic textures                      |
| `5`       | UniPC               | Alternative general-purpose solver                                      |
| `6`       | LCM                 | Not a default for these standard SDXL checkpoints                       |
| `7`       | Euler A Substep     | Alternative for testing fine, organic details                           |
| `8`       | DPM++ SDE Substep   | Specialized alternative; usually not necessary                          |
| `9`       | TCD                 | Not a default for these checkpoints                                     |
| `10`      | Euler A Trailing    | Compatibility-oriented alternative; validate output                     |
| `11`      | DPM++ SDE Trailing  | Alternative stochastic sampler                                          |
| `12`      | DPM++ 2M AYS        | Efficient step-placement experiment                                     |
| `13`      | Euler A AYS         | Efficient alternative for testing                                       |
| `14`      | DPM++ SDE AYS       | Specialized alternative                                                 |
| `15`      | DPM++ 2M Trailing   | Alternative DPM++ schedule                                              |
| `16`      | DDIM Trailing       | Alternative for controlled outputs                                      |
| `17`      | UniPC Trailing      | Not my default for classic SDXL                                         |
| `18`      | UniPC AYS           | Efficient alternative for testing                                       |

Baseline recommendation: start with sampler `0`, around 25–30 steps and CFG 5–6. That is a practical starting point, not a universal optimum. Keep the same seed, sampler, resolution, steps, CFG and LoRA weights when comparing models or prompts.

## Deliverables

I’ve prepared two files: a practical configuration guide and a structured recommendation ruleset for your AI agent.

- `sdxl-configuration-guide-recipes.md` - Detailed recommendations, prompt examples and 17 command recipes. Covers all four models, ten LoRAs and six upscalers; age-group and genre recommendations; numeric sampler IDs; steps, CFG and resolution; negative-prompt strategies; troubleshooting; and brief explanations of each recipe.

- `sdxl-recommendation-rules.json` - Machine-readable settings and selection rules. Designed for an agent to map a request to a model, LoRA combination, sampler, CFG, steps, dimensions, upscaler and prompt constraints.

## Recommended starting rules

| User intent                  | Starting configuration                                                                                             |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Young children's storybooks  | `redmondv2_kids_storybook_lora_f16.ckpt`, weight `0.70–0.85`; CFG `5.0–5.5`                            |
| Clean coloring-book line art | `redmond_coloringbook_lora_f16.ckpt`, weight `0.80–0.95`; CFG `5–7`                       |
| Adult mandalas               | ColoringBook LoRA `0.80–0.95`; 28–34 steps; emphasize enclosed shapes and consistent outlines                      |
| Anime illustrations          | `animagine_xl_v3.1_f16.ckpt`; optionally `redmondv2_lineart_lineani_lora_f16.ckpt` at `0.45–0.70`           |
| Oil painting                 | `juggernaut_xl_x_f16.ckpt` or v9; `oil_painting_slider_lora_f16.ckpt` at `0.50–0.75`                                 |
| Pencil sketches              | `sketch_style_lora_f16.ckpt` at `0.60–0.85`; suppress color and glossy rendering                                  |
| 3D or family-animation style | `3d_render_style_xl_lora_f16.ckpt` or `pixar_style_lora_f16.ckpt`; use one as the main style control                   |
| Photorealism                 | Juggernaut v9 or X; optional `redmondv2_analog_lora_f16.ckpt` at `0.25–0.45` for a film-like feel |

For most initial tests, sampler `0` (DPM++ 2M Karras), CFG around `5.5`, and 25–30 steps are sensible baselines. Upscalers should be chosen by the desired finish: smoother edges for children's illustrations, line-preserving choices for coloring pages, and detail-oriented choices for realistic images.

Compatibility note: the recipes use the Draw Things `--config-json` field names, but they have not been run against your local CLI installation. Verify the installed CLI's sampler enum and LoRA registration—especially if a local LoRA requires a version entry—before treating the recipes as production-ready.
