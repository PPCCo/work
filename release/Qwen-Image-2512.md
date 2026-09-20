# Stage Qwen-Image-2512 via gh release (Mac → other machine)

Highest practical quant here is `Q8_0` — it's the top standard GGUF tier (near-lossless vs BF16) and the numbers still clear your budget with room to spare: ~21GB diffusion model + ~8GB text encoder + ~1.4GB mmproj + ~0.25GB VAE ≈ 30GB, well under your 40GB target out of 48GB total. Full BF16 (~40GB+ for the diffusion model alone) would blow that budget once the encoder's added, so Q8_0 is the ceiling, not a compromise.

## 1. Create the mirror repo

mkdir -p ~/qwen-stage && cd ~/qwen-stage
gh repo create PPCCo/qwen-image-2512-mirror --public --confirm
echo "# qwen-image-2512-mirror" > README.md
git init
git add README.md
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/PPCCo/qwen-image-2512-mirror.git
git push -u origin main

## 2. Download the model files

cd ~/qwen-stage
`caffeinate -i curl -L -C - -o qwen-image-2512-Q8_0.gguf https://huggingface.co/unsloth/Qwen-Image-2512-GGUF/resolve/main/qwen-image-2512-Q8_0.gguf`
`caffeinate -i curl -L -C - -o Qwen2.5-VL-7B-Instruct-Q8_0.gguf https://huggingface.co/unsloth/Qwen2.5-VL-7B-Instruct-GGUF/resolve/main/Qwen2.5-VL-7B-Instruct-Q8_0.gguf`
`caffeinate -i curl -L -C - -o mmproj-BF16.gguf https://huggingface.co/unsloth/Qwen2.5-VL-7B-Instruct-GGUF/resolve/main/mmproj-BF16.gguf`
`caffeinate -i curl -L -C - -o qwen_image_vae.safetensors https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/vae/qwen_image_vae.safetensors`

`ls -la _.gguf _.safetensors`

## 3. Checksum the originals, then split anything over 2GB

`caffeinate -i sha256sum qwen-image-2512-Q8_0.gguf > qwen-image-2512-Q8_0.gguf.sha256`
`caffeinate -i sha256sum Qwen2.5-VL-7B-Instruct-Q8_0.gguf > Qwen2.5-VL-7B-Instruct-Q8_0.gguf.sha256`
`sha256sum mmproj-BF16.gguf > mmproj-BF16.gguf.sha256`
`sha256sum qwen_image_vae.safetensors > qwen_image_vae.safetensors.sha256`

`caffeinate -i split -b 1800M qwen-image-2512-Q8_0.gguf qwen-image-2512-Q8_0.gguf.part_`
`caffeinate -i split -b 1800M Qwen2.5-VL-7B-Instruct-Q8_0.gguf Qwen2.5-VL-7B-Instruct-Q8_0.gguf.part_`

`ls -la \_.part\_\_ mmproj-BF16.gguf qwen_image_vae.safetensors`

## 4. Create the release, upload everything

```text
cd ~/qwen-stage

caffeinate -i gh release create v1 Qwen2.5-VL-7B-Instruct-Q8_0.gguf.part_* \
  --repo PPCCo/qwen-image-2512-mirror \
  --title "Release v1" \
  --notes "Qwen-Image-2512 Q8_0 + Qwen2.5-VL-7B Q8_0 text encoder + VAE for ComfyUI. Large files split with 'split -b 1800M'; reassemble with cat, verify with the .sha256 files."
```

`caffeinate -i gh release upload v1 * --repo PPCCo/qwen-image-2512-mirror --clobber`
`caffeinate -i gh release upload v1 qwen-image-2512-Q8_0.gguf.part_* --repo PPCCo/qwen-image-2512-mirror --clobber`

`caffeinate -i gh release upload v1 mmproj-BF16.gguf qwen_image_vae.safetensors *.sha256 --repo PPCCo/qwen-image-2512-mirror --clobber`

## 3. Then, download on the other machine

`mkdir -p ~/qwen-download && cd ~/qwen-download`
`caffeinate -i gh release download v1 --repo PPCCo/qwen-image-2512-mirror --pattern '*'`

`caffeinate -i gh release download v1 --repo PPCCo/qwen-image-2512-mirror --pattern 'Qwen2.5-VL-7B-Instruct-Q8_0.gguf.part_*' --clobber`
`caffeinate -i gh release download v1 --repo PPCCo/qwen-image-2512-mirror --pattern 'qwen-image-2512-Q8_0.gguf.part_*' --clobber`

`caffeinate -i gh release download v1 --repo PPCCo/qwen-image-2512-mirror --pattern 'mmproj-BF16.gguf qwen_image_vae.safetensors *.sha256' --clobber`
`caffeinate -i gh release download v1 --repo PPCCo/qwen-image-2512-mirror --pattern 'xxxx' --clobber`

`caffeinate -i bash -c 'cat qwen-image-2512-Q8_0.gguf.part_* > qwen-image-2512-Q8_0.gguf'`
`caffeinate -i bash -c 'cat Qwen2.5-VL-7B-Instruct-Q8_0.gguf.part_* > Qwen2.5-VL-7B-Instruct-Q8_0.gguf'`

`caffeinate -i sha256sum -c qwen-image-2512-Q8_0.gguf.sha256`
`caffeinate -i sha256sum -c Qwen2.5-VL-7B-Instruct-Q8_0.gguf.sha256`
`sha256sum -c mmproj-BF16.gguf.sha256`
`sha256sum -c qwen_image_vae.safetensors.sha256`

`mkdir -p ~/ComfyUI/models/diffusion_models ~/ComfyUI/models/text_encoders ~/ComfyUI/models/vae`
`mv qwen-image-2512-Q8_0.gguf ~/ComfyUI/models/diffusion_models/`
`mv Qwen2.5-VL-7B-Instruct-Q8_0.gguf mmproj-BF16.gguf ~/ComfyUI/models/text_encoders/`
`mv qwen_image_vae.safetensors ~/ComfyUI/models/vae/`
