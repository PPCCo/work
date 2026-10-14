# Stage Qwen-Image-2512 via gh release (Mac → other machine)

## Downloads

### Upscalers

- 4x_foolhardy_Remacri_ExtraSmoother.safetensors
- 4x_NMKD-Superscale-SP_178000_G.safetensors
- 4x-UltraSharpV2.safetensors
- RealESRGAN_x4plus_anime_6B.safetensors
- RealESRGAN_x4plus.safetensors
- SwinIR-L_x4_PSNR.safetensors

### LoRAs

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

## 1. Create the mirror repo

gh repo create PPCCo/loras-upscalers-mirror --public --confirm
echo "# loras-upscalers-mirror" > README.md
git init
git add README.md
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/PPCCo/loras-upscalers-mirror.git
git push -u origin main

`caffeinate -i`

## 2. Create the release, upload everything

```bash
gh release create v1 README.md \
--repo PPCCo/loras-upscalers-mirror \
--title "Release v1" \
--notes "loras and upscalers"

# batch 2 - the big fp8 diffusion checkpoint
caffeinate -i gh release upload v1 *.safetensors --repo PPCCo/loras-upscalers-mirror --clobber
```

## 3. Then, download on the other machine

`mkdir -p ~/Dev/loras-upscalers && cd ~/Dev/loras-upscalers`

`caffeinate -i gh release download v1 --repo PPCCo/loras-upscalers-mirror --pattern '*'`
