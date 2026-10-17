# Stage Qwen-Image-2512 via gh release (Mac → other machine)

## Downloads

### Upscalers

- 4x_foolhardy_remacri_extrasmoother_f16.ckpt
- 4x_nmkd_superscale_sp_178000_g_f16.ckpt
- 4x_ultrasharp_f16.ckpt
- realesrgan_x4plus_anime_6b_f16.ckpt
- realesrgan_x4plus_f16.ckpt
- rrdb_psnr_x4_f16.ckpt

### LoRAs

- 3d_render_style_xl_lora_f16.ckpt
- add_detail_xl_lora_f16.ckpt
- redmondv2_analog_lora_f16.ckpt
- redmond_coloringbook_lora_f16.ckpt
- oil_painting_slider_epic_lora_f16.ckpt
- redmondv2_lineart_lineani_lora_f16.ckpt
- oil_painting_slider_lora_f16.ckpt
- pixar_style_lora_f16.ckpt
- sketch_style_lora_f16.ckpt
- redmondv2_kids_storybook_lora_f16.ckpt

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
gh release create v2 README.md \
--repo PPCCo/loras-upscalers-mirror \
--title "Release v2 - Klein loras" \
--notes "Klein loras and upscalers"

# batch 2 - the big fp8 diffusion checkpoint
caffeinate -i gh release upload v1 *.safetensors --repo PPCCo/loras-upscalers-mirror --clobber
caffeinate -i gh release upload v1 rrdb_psnr_x4.pth --repo PPCCo/loras-upscalers-mirror --clobber

caffeinate -i gh release upload v2 *.safetensors --repo PPCCo/loras-upscalers-mirror --clobber

caffeinate -i gh release create v3 * \
--repo PPCCo/loras-upscalers-mirror \
--title "Release v3 - More Klein loras" \
--notes "Klein loras and upscalers"

```

## 3. Then, download on the other machine

`mkdir -p ~/Dev/loras-upscalers && cd ~/Dev/loras-upscalers`
`caffeinate -i gh release download v1 --repo PPCCo/loras-upscalers-mirror --pattern '*'`

`mkdir -p ~/Dev/loras-klein && cd ~/Dev/loras-klein`
`caffeinate -i gh release download v2 --repo PPCCo/loras-upscalers-mirror --pattern '*'`
