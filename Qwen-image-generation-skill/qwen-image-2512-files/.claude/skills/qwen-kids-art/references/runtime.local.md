# Local runtime notes

Fill this in as you go. Once it has a few rows, the defaults in
`scripts/build_prompt.py` become irrelevant and this file is the source of truth
for your install. This is the single highest-value habit in the whole skill:
inconsistency stops being a model problem the moment you have a record of what
actually worked.

## Install

- ComfyUI version:
- ComfyUI-GGUF custom node installed (required for the Q8_0 diffusion model): y/n
- GPU / VRAM:
- Full model file (Q8_0 GGUF, ~20 GB): `Qwen-Image-2512-Q8_0.gguf`
- Lightning LoRA file, if used:
- Text encoder: `qwen_2.5_vl_7b_fp8_scaled.safetensors` (or the Q8_0 GGUF text
  encoder, if you chose to match precision - see comfyui-runtime.md #2)
- VAE: `qwen_image_vae.safetensors`
- Workflow (API format) used by `batch_generate.py`:
- Node ids — positive text encode: ___ · negative text encode: ___ ·
  latent: ___ · sampler: ___

## Measured settings

| Pack | Variant | Steps | CFG | Sampler / scheduler | Resolution | Verdict |
|---|---|---|---|---|---|---|
| | | | | | | |

## Known-good seeds

Only ever record a seed together with its exact prompt — the same seed on a
changed prompt is a different picture.

| Set / character | Prompt file or id | Seed | Why it was kept |
|---|---|---|---|
| | | | |

## Things that failed here

| Symptom | What fixed it |
|---|---|
| | |
