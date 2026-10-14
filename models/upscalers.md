I'll check Draw Things' current upscaler list and the licenses on each model before giving you downloads.

`https://huggingface.co/easygoing0114/AI_upscalers/tree/main`

4x_foolhardy_Remacri_ExtraSmoother.safetensors
4x_NMKD-Superscale-SP_178000_G.safetensors
4x-UltraSharpV2.safetensors
RealESRGAN_x4plus_anime_6B.safetensors
RealESRGAN_x4plus.safetensors
SwinIR-L_x4_PSNR.safetensors

Draw Things can't use Hugging Face upscaler files directly, so I can't give you exact HF downloads for it. `--upscaler` expects Draw Things' own converted `.ckpt` files, which come from its own CDN (static.libnnc.org). I tried those URLs from my sandbox and got 403s, so I couldn't confirm the direct links or hashes. The CLI shares the app's models folder, so the safest route is to select each upscaler once in the Draw Things app so it downloads itself. You can then confirm it's installed with `draw-things-cli models list --downloaded-only`.

**Commercial use cuts the list down to three.** The Real-ESRGAN models (x4plus and x4plus anime 6B) are BSD 3-Clause, while 4x-UltraSharp and 4x_foolhardy_Remacri are CC-BY-NC-SA-4.0, so they're non-commercial. Remacri's listing on OpenModelDB also shows CC-BY-NC-SA-4.0. Draw Things bundles both, so **don't use `remacri_4x_f16.ckpt` or `4x_ultrasharp_f16.ckpt` for books you sell.**

The Draw Things filenames I found for the Real-ESRGAN set are realesrgan_x2plus_f16.ckpt, realesrgan_x4plus_f16.ckpt and realesrgan_x4plus_anime_6b_f16.ckpt. That list comes from a third-party skill file, not Draw Things' own docs, so check it against `draw-things-cli generate --help` and the app's upscaler dropdown.

## Upscaler and strength by use case

An upscaler has no strength setting of its own. `--upscaler-scale` accepts 2 or 4, and a pure upscale is deterministic. The strength column applies only if you add a hires-fix or img2img refine pass afterwards, and those values are my starting points to tune, not official numbers.

| Use case                                          | `--upscaler` value                    | `--upscaler-scale`                        | Refine `--strength` (optional) |
| ------------------------------------------------- | ------------------------------------- | ----------------------------------------- | ------------------------------ |
| Kids illustrations, flat or cartoon storybook art | `realesrgan_x4plus_anime_6b_f16.ckpt` | 4 (use 2 if the image is already ≥2048px) | 0.15–0.25                      |
| Painterly or watercolor storybook pages           | `realesrgan_x4plus_f16.ckpt`          | 4                                         | 0.10–0.20                      |
| Adult non-fiction (photos, diagrams, charts)      | `realesrgan_x4plus_f16.ckpt`          | 2 for large sources, 4 for small          | 0.05–0.15                      |
| Sketching books (pencil or ink line art)          | `realesrgan_x4plus_anime_6b_f16.ckpt` | 4                                         | 0.0–0.10                       |
| Coloring books (outline pages)                    | `realesrgan_x4plus_anime_6b_f16.ckpt` | 4                                         | 0.0–0.10                       |
| Adult mandala coloring books                      | `realesrgan_x4plus_anime_6b_f16.ckpt` | 4                                         | 0.0–0.08                       |
| Light 2× pass on anything                         | `realesrgan_x2plus_f16.ckpt`          | 2                                         | 0.0–0.10                       |

For line art, keep strength near zero so the refine pass doesn't add grey shading or invent detail. After upscaling, threshold the line art to pure black and white for clean print edges.

```bash
draw-things-cli generate \
  --model <your_model>.ckpt \
  --prompt "..." \
  --upscaler realesrgan_x4plus_anime_6b_f16.ckpt \
  --upscaler-scale 4
```

## Original weights, if you want them for reference

The original BSD-3 weights are on GitHub (not Hugging Face), and these are the release URLs:

```bash
wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth
wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth
wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth
```

Other commercial-friendly upscalers exist (WTFPL ones like NMKD Superscale and RealisticRescaler), but they're in `.pth` format. Draw Things can't load them without a conversion I haven't verified, so I left them out. This is licensing information, not legal advice. Check the license text yourself before committing to a print run.

Sources:

- [easygoing0114/AI_upscalers (license table)](https://huggingface.co/easygoing0114/AI_upscalers)
- [OpenModelDB: 4x Remacri](https://openmodeldb.info/models/4x-Remacri)
- [draw-thing skill (CLI flags and filenames)](https://skills.sh/wyattowalsh/agents/draw-thing)
- [Real-ESRGAN weight URLs](https://docsearch.algolia.com/mcp/docs/repo/xinntao/real-esrgan)
