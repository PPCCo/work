# Stage Qwen-Image-2512 via gh release (Mac → other machine)

Highest practical quant here is `Q8_0` — it's the top standard GGUF tier (near-lossless vs BF16) and the numbers still clear your budget with room to spare: ~21GB diffusion model + ~8GB text encoder + ~1.4GB mmproj + ~0.25GB VAE ≈ 30GB, well under your 40GB target out of 48GB total. Full BF16 (~40GB+ for the diffusion model alone) would blow that budget once the encoder's added, so Q8_0 is the ceiling, not a compromise.

## 1. Create the mirror repo

mkdir -p ~/qwen-safetensors-stage && cd ~/qwen-safetensors-stage
gh repo create PPCCo/qwen-image-2512-safetensors-mirror --public --confirm
echo "# qwen-image-2512-safetensors-mirror" > README.md
git init
git add README.md
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/PPCCo/qwen-image-2512-safetensors-mirror.git
git push -u origin main

## 2. Download the safetensors files, checksum, split

```bash
cd ~/qwen-safetensors-stage
pip install -U huggingface_hub
```

- no 'hf auth login' needed - the Comfy-Org mirror is public/ungated

`caffeinate -i hf download Comfy-Org/Qwen-Image_ComfyUI split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors --local-dir .`
`mv split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors .`
`sha256sum qwen_2.5_vl_7b_fp8_scaled.safetensors > qwen_2.5_vl_7b_fp8_scaled.safetensors.sha256`
`split -b 1900M -d qwen_2.5_vl_7b_fp8_scaled.safetensors qwen_2.5_vl_7b_fp8_scaled.safetensors.part`

**qwen_image_fp8_e4m3fn.safetensors** ~20 GB

`caffeinate -i hf download Comfy-Org/Qwen-Image_ComfyUI split_files/diffusion_models/qwen_image_fp8_e4m3fn.safetensors --local-dir .`
`mv split_files/diffusion_models/qwen_image_fp8_e4m3fn.safetensors .`
`sha256sum qwen_image_fp8_e4m3fn.safetensors > qwen_image_fp8_e4m3fn.safetensors.sha256`
`split -b 1900M -d qwen_image_fp8_e4m3fn.safetensors qwen_image_fp8_e4m3fn.safetensors.part`

rm -rf split_files

### ONLY FOR fp16

`caffeinate -i hf download Comfy-Org/Qwen-Image_ComfyUI split_files/diffusion_models/qwen_image_bf16.safetensors --local-dir .`
`mv split_files/diffusion_models/qwen_image_bf16.safetensors .`
`shasum -a 256 qwen_image_bf16.safetensors > SHA256SUMS.txt`
`split -b 1900M -d qwen_image_bf16.safetensors qwen_image_bf16.safetensors.part`

## 4. Create the release, upload everything

```bash
caffeinate -i gh release create v1 qwen_2.5_vl_7b_fp8_scaled.safetensors* \
--repo PPCCo/qwen-image-2512-safetensors-mirror \
--title "Release v1" \
--notes "Qwen-Image-2512 Q8_0 + Qwen2.5-VL-7B Q8_0 text encoder + VAE for ComfyUI. Large files split with 'split -b 1800M'; reassemble with cat, verify with the .sha256 files."

# batch 2 - the big fp8 diffusion checkpoint
caffeinate -i gh release upload v1 qwen_image_fp8_e4m3fn.safetensors* --repo PPCCo/qwen-image-2512-safetensors-mirror --clobber
caffeinate -i gh release upload v1 * --repo PPCCo/qwen-image-2512-safetensors-mirror --clobber
```

## 3. Then, download on the other machine

`mkdir -p ~/qwen-safetensors-download && cd ~/qwen-safetensors-download`

`caffeinate -i gh release download v1 --repo PPCCo/qwen-image-2512-mirror --pattern '*'`

`caffeinate -i gh release download v1 --repo PPCCo/qwen-image-2512-mirror --pattern 'qwen_2.5_vl_7b_fp8_scaled.safetensors.part*' --clobber`
`caffeinate -i bash -c 'cat qwen_2.5_vl_7b_fp8_scaled.safetensors.part* > qwen_2.5_vl_7b_fp8_scaled.safetensors'`
`caffeinate -i sha256sum -c qwen_2.5_vl_7b_fp8_scaled.safetensors.sha256`

`caffeinate -i gh release download v1 --repo PPCCo/qwen-image-2512-mirror --pattern 'qwen_image_fp8_e4m3fn.safetensors.part*' --clobber`
`caffeinate -i bash -c 'cat qwen_image_fp8_e4m3fn.safetensors.part* > qwen_image_fp8_e4m3fn.safetensors'`
`sha256sum -c qwen_image_fp8_e4m3fn.safetensors.sha256`
