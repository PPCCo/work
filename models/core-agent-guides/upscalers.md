# Upscalers

## Available upscaler list and the licenses on each model before giving you downloads.

- 4x_foolhardy_remacri_extrasmoother_f16.ckpt
- 4x_nmkd_superscale_sp_178000_g_f16.ckpt
- 4x_ultrasharp_f16.ckpt
- realesrgan_x4plus_anime_6b_f16.ckpt
- realesrgan_x4plus_anime_6b_f16.ckpt

## Upscaler and strength by use case

An upscaler has no strength setting of its own. `--upscaler-scale` accepts 2 or 4, and a pure upscale is deterministic. The strength column applies only if you add a hires-fix or img2img refine pass afterwards, and those values are my starting points to tune, not official numbers.

| Use case                                          | `--upscaler` value                    |
| ------------------------------------------------- | ------------------------------------- |
| Kids illustrations, flat or cartoon storybook art | `realesrgan_x4plus_anime_6b_f16.ckpt` |
| Painterly or watercolor storybook pages           | `realesrgan_x4plus_anime_6b_f16.ckpt` |
| Adult non-fiction (photos, diagrams, charts)      | `realesrgan_x4plus_anime_6b_f16.ckpt` |
| Sketching books (pencil or ink line art)          | `realesrgan_x4plus_anime_6b_f16.ckpt` |
| Coloring books (outline pages)                    | `realesrgan_x4plus_anime_6b_f16.ckpt` |
| Adult mandala coloring books                      | `realesrgan_x4plus_anime_6b_f16.ckpt` |
| Light 2× pass on anything                         | `realesrgan_x2plus_f16.ckpt`          |

For line art, keep strength near zero so the refine pass doesn't add grey shading or invent detail. After upscaling, threshold the line art to pure black and white for clean print edges.

```bash
draw-things-cli generate \
  --model <your_model>.ckpt \
  --prompt "..." \
  --upscaler realesrgan_x4plus_anime_6b_f16.ckpt \
  --upscaler-scale 4
```
