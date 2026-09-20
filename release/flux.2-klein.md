# Stage FLUX.2 Klein 4B via gh release, then install into ComfyUI

Same steps-only pattern as `gh-release-argos-translate.md`. Reason to mirror through a release
here: the two BFL fp8 checkpoints are **gated** (must click "Agree" on the HF model page once,
in a browser, before `hf download` will work), and each checkpoint is well over GitHub's 2GB
per-asset limit — so every file gets split before upload and `cat`-rejoined on the local side.

Before step 2: visit these two pages once and accept the license (can't be scripted):
`https://huggingface.co/black-forest-labs/FLUX.2-klein-base-4b-fp8`
`https://huggingface.co/black-forest-labs/FLUX.2-klein-4b-fp8`

## 1. Create repo + push README

```
mkdir -p ~/flux-klein-stage && cd ~/flux-klein-stage

gh repo create PPCCo/flux-klein-4b-mirror --public --confirm

echo "# flux-klein-4b-mirror" > README.md
git init
git add README.md
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/PPCCo/flux-klein-4b-mirror.git
git push -u origin main
```

## 2. Download the 4B files, checksum, split

```
cd ~/flux-klein-stage
pip install -U huggingface_hub

hf auth login

caffeinate -i hf download Comfy-Org/flux2-klein-4B split_files/text_encoders/qwen_3_4b.safetensors --local-dir .
caffeinate -i hf download black-forest-labs/FLUX.2-klein-base-4b-fp8 flux-2-klein-base-4b-fp8.safetensors --local-dir .
caffeinate -i hf download black-forest-labs/FLUX.2-klein-4b-fp8 flux-2-klein-4b-fp8.safetensors --local-dir .
caffeinate -i hf download Comfy-Org/flux2-dev split_files/vae/flux2-vae.safetensors --local-dir .

mv split_files/text_encoders/qwen_3_4b.safetensors .
mv split_files/vae/flux2-vae.safetensors .
rm -rf split_files

shasum -a 256 qwen_3_4b.safetensors flux-2-klein-base-4b-fp8.safetensors flux-2-klein-4b-fp8.safetensors flux2-vae.safetensors > SHA256SUMS.txt

split -b 1900M -d qwen_3_4b.safetensors qwen_3_4b.safetensors.part
split -b 1900M -d flux-2-klein-base-4b-fp8.safetensors flux-2-klein-base-4b-fp8.safetensors.part
split -b 1900M -d flux-2-klein-4b-fp8.safetensors flux-2-klein-4b-fp8.safetensors.part
split -b 1900M -d flux2-vae.safetensors flux2-vae.safetensors.part

ls -la *.part* SHA256SUMS.txt
```

## 3. Create the release, upload in two batches

```
cd ~/flux-klein-stage

# batch 1 — creates the release (text encoder + vae + checksums, both small)
caffeinate -i gh release create v1 \
  qwen_3_4b.safetensors.part* flux2-vae.safetensors.part* SHA256SUMS.txt \
  --repo PPCCo/flux-klein-4b-mirror \
  --title "flux-klein-4b v1" \
  --notes "FLUX.2 Klein 4B ComfyUI weights, split into 1900M parts. cat the parts back together, verify with SHA256SUMS.txt."

# batch 2 — the two big diffusion checkpoints
caffeinate -i gh release upload v1 \
  flux-2-klein-base-4b-fp8.safetensors.part* flux-2-klein-4b-fp8.safetensors.part* \
  --repo PPCCo/flux-klein-4b-mirror --clobber
```

If a batch fails mid-upload, re-run that same line — `--clobber` makes it safe to repeat.

---

## Then, on the local machine — download + install into ComfyUI

```
mkdir -p ~/flux-klein-download && cd ~/flux-klein-download
caffeinate -i gh release download v1 --repo PPCCo/flux-klein-4b-mirror --pattern '*'

cat qwen_3_4b.safetensors.part* > qwen_3_4b.safetensors
cat flux-2-klein-base-4b-fp8.safetensors.part* > flux-2-klein-base-4b-fp8.safetensors
cat flux-2-klein-4b-fp8.safetensors.part* > flux-2-klein-4b-fp8.safetensors
cat flux2-vae.safetensors.part* > flux2-vae.safetensors

shasum -a 256 -c SHA256SUMS.txt

mkdir -p ~/ComfyUI/models/text_encoders ~/ComfyUI/models/diffusion_models ~/ComfyUI/models/vae
mv qwen_3_4b.safetensors ~/ComfyUI/models/text_encoders/
mv flux-2-klein-base-4b-fp8.safetensors ~/ComfyUI/models/diffusion_models/
mv flux-2-klein-4b-fp8.safetensors ~/ComfyUI/models/diffusion_models/
mv flux2-vae.safetensors ~/ComfyUI/models/vae/

rm qwen_3_4b.safetensors.part* flux-2-klein-base-4b-fp8.safetensors.part* flux-2-klein-4b-fp8.safetensors.part* flux2-vae.safetensors.part*
```

Once the checksums pass, restart ComfyUI, load the "Flux.2 Klein 4B" template (Browse Templates
→ Images), and the three Loader nodes should resolve the files automatically.

**Note:** `~/ComfyUI` above assumes that's your install path — adjust if yours lives elsewhere.
