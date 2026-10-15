## 3. LoRAs

### 3.1 Install workflow (HF `.safetensors` → Draw Things)
**Option A (preferred, auto-detects the model version):** Draw Things app → Settings → LoRA → Manage → Import → *Select from Files* (installing from a downloaded file is more reliable than from a URL; choose "LoRA", not "Model"; if asked for the base, pick FLUX.2 4B) [V — DT wiki]. HF model pages also expose a "Draw Things" local-app deep link: `https://drawthings.ai/import/diffusers/pipeline.load_lora_weights?repo_id=<owner>/<repo>` [V].
**Option B (CLI-only, community tool):** `vcspr/drawthings-lora-convert` builds Draw Things' own `LoRAConverter` (≈25 min first build, Swift toolchain, default tag `v26.0910.1`) [V].
```bash
git clone https://github.com/vcspr/drawthings-lora-convert && cd drawthings-lora-convert
./build.sh
python3 dtlora.py convert ~/Dev/t2/loras/numzoo/numzoo_klein.safetensors \
  --models-dir ~/Library/Containers/com.liuliu.draw-things/Data/Documents/Models
# Its filename-based version guess maps "flux" -> FLUX.1; for Klein, if auto-detect fails pass --version
# explicitly (exact Klein-4B string unverified: copy it from the custom_lora.json entry of a LoRA the app imported).
```
Output name rule [V]: lowercase; every char except letters/digits/`.` becomes `_`; suffix `_lora_f16.ckpt` (e.g. `numzoo_klein.safetensors` → `numzoo_klein_lora_f16.ckpt`). **The app may name imports differently — after importing, run `ls "<models dir>" | grep _lora_f16` and use the exact filename in `--config-json`.** Example commands below use the predicted names [I].


### 3.2 Download + convert
Needs `hf` CLI (`pip install -U "huggingface_hub[cli]"`). Not runnable from the research sandbox (HF blocked) → commands are **[U] until run on the Mac**.
```bash
mkdir -p ~/Dev/loras_src ~/Dev/t2
hf download giannisan/light-fantasy-flux2-klein-base-lora --include "*.safetensors" --local-dir ~/Dev/loras_src/light_fantasy
hf download Norod78/flux2-klein-4b-base-lora-vintage-book-cover --include "*.safetensors" --local-dir ~/Dev/loras_src/vintage_book_cover
hf download fal/flux-2-klein-4b-spritesheet-lora flux-spritesheet-lora.safetensors --local-dir ~/Dev/loras_src/spritesheet
hf download adirik/pixel-art-lora-flux.2-klein-4B klein_pixelart_lora_f16.ckpt --local-dir ~/Dev/loras_src/pixelart
```
If a repo holds several `.safetensors` (checkpoints), keep the final/largest-step one.

Convert (pick one):
- **A. Draw Things app (no build):** Manage LoRAs → Import → pick file → set base to FLUX.2 [klein] 4B → name it exactly as in the table below. The app writes `<name>_lora_f16.ckpt` into the Models folder and registers it.
- **B. Script:** `vcspr/drawthings-lora-convert` (third-party, GPL-3.0). Build once (`./build.sh <tag matching your CLI>`, ~25 min), then:
  ```bash
  MODELS="$HOME/Library/Containers/com.liuliu.draw-things/Data/Documents/Models"
  python3 dtlora.py convert ~/Dev/loras_src/light_fantasy/FILE.safetensors --models-dir "$MODELS" --version flux2_4b
  ```
  Upstream `LoRAImporter` has `flux2_4b` code paths [V]; the wrapper's README lists other families → Klein through it is [U]. Verify with its `verify` subcommand.
Output name = lowercase, every non-alnum/non-`.` → `_`, + `_lora_f16.ckpt` [V]. Names assumed by examples below:

| Source | Expected converted file |
|---|---|
| light_fantasy | `light_fantasy_lora_f16.ckpt` |
| vintage_book_cover | `vintage_book_cover_lora_f16.ckpt` |
| spritesheet | `klein4b_spritesheet_lora_f16.ckpt` |
| pixelart | `klein4b_pixelart_lora_f16.ckpt` |

Check: `ls "$MODELS" | grep -i lora`. If an example's LoRA file is missing, **drop the `loras` array** (prompt-only fallback still works).
