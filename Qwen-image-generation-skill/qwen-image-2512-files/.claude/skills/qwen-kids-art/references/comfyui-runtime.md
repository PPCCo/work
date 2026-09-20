# ComfyUI runtime for Qwen-Image-2512 (Q8_0)

Prompt shape and the negative prompt fix most of the inconsistency (see
`qwen-prompt-standards.md`). The rest of it lives here: this is a much bigger
model than Klein was, the loader stack is different, and the numbers below
are what change if you switch quantisation or speed tier.

---

## 1. Read this before anything else: it's a 20B model, not a 4B one

Everything about hardware and timing in the old Klein version of this skill
is wrong for Qwen-Image-2512. Reset expectations:

| | Klein 4B (previous) | Qwen-Image-2512 Q8_0 (current) |
|---|---|---|
| Parameters | 4B | 20B |
| Diffusion weights on disk (Q8_0) | ~4–5 GB | **~20 GB** |
| Text encoder | Qwen3 4B | Qwen2.5-VL 7B |
| Full generation | 24 steps, ~15–20s | 50 steps, expect well over a minute on a single consumer GPU |
| Fast generation | 4 steps, ~1s | 4–8 step Lightning, a few seconds |

If your ComfyUI box was sized for Klein, check it can actually hold this
model before building a pipeline around it — see §3.

## 2. Model files

| Component | File (Q8_0 as specified) | Folder |
|---|---|---|
| Diffusion model | `Qwen-Image-2512-Q8_0.gguf` (~20 GB) | `ComfyUI/models/unet/` (or `diffusion_models/`, depending on your ComfyUI-GGUF version) |
| Text encoder | `Qwen2.5-VL-7B-Instruct-Q8_0.gguf` (~7.5 GB), **or** `qwen_2.5_vl_7b_fp8_scaled.safetensors` (~8 GB, not a GGUF, the more common companion) | `ComfyUI/models/text_encoders/` |
| VAE | `qwen_image_vae.safetensors` (~242 MB) — always safetensors, never GGUF | `ComfyUI/models/vae/` |
| Fast tier (optional) | `Qwen-Image-Lightning-4steps-V1.0.safetensors` or the 8-step variant | `ComfyUI/models/loras/` |

GGUF for the diffusion model requires the **ComfyUI-GGUF** custom node
extension (`city96/ComfyUI-GGUF`) — install it before the loader nodes below
will appear. The VAE never needs it; the text encoder only needs it if you
chose the GGUF text encoder over the fp8 safetensors one.

**On mixing quantisations**: the user's spec here is Q8_0 for the diffusion
model. The text encoder does not have to match — fp8_scaled is the lighter,
more common pairing and the quality cost versus a Q8_0 text encoder is
small. Use the fp8_scaled text encoder unless VRAM is genuinely not the
constraint; it saves real memory for very little loss.

## 3. VRAM and disk

Rough numbers, GGUF quantisation:

- Q8_0 diffusion model: ~20 GB disk. Close to lossless relative to the
  original bf16 weights — this is why it was chosen over a smaller quant —
  but it is the heaviest GGUF tier short of full precision.
- fp8_scaled text encoder: ~8 GB disk.
- VAE: ~0.25 GB disk.
- **Total disk**: roughly 28–29 GB for the model set.
- **VRAM**: ComfyUI-GGUF streams and dequantises on the fly, so it does not
  strictly require the full 20 GB resident at once, but for reasonable speed
  a card with **24 GB VRAM or more** is the comfortable target. Below that,
  expect either CPU offload (slow) or the need to drop to a smaller GGUF
  quant (Q4_K_M or similar) for the diffusion model specifically. CPU-only
  operation is possible — RAM plus VRAM combined should exceed the model
  size — but is slow enough that it's a fallback, not a workflow.
- If VRAM is tight: keep the diffusion model at Q8_0 (that was the explicit
  choice here) and drop the text encoder to a smaller quant or fp8 first;
  the text encoder is the cheaper place to save memory without touching the
  quantisation the setup was built around.

## 4. Two speed tiers

| | Full | Lightning |
|---|---|---|
| Steps | 50 | 4 or 8 |
| CFG | ~4.0 | 1.0 |
| Sampler / scheduler | euler or your ComfyUI default flow-match sampler | same |
| Negative prompt | works | inert — see `qwen-prompt-standards.md` §3 |
| Extra file | none | Lightning LoRA loaded on top |
| Use for | keepers, anything the negative prompt needs to fix, final renders | drafts, composition search, quick iteration |

**Draft-then-finish still applies**, same as it did with Klein: explore
composition on Lightning, pick a seed, re-render that exact prompt and seed
on full once the negative prompt is doing real work. The mechanics are
identical to the old Klein workflow; only the step/CFG numbers changed.

## 5. Resolution

Qwen-Image-2512's trained aspect ratios, at native resolution (this table is
the one to design generation sizes around, not an arbitrary multiple-of-16
choice):

| Ratio | Size (px) |
|---|---|
| 1:1 | 1328 × 1328 |
| 4:3 | 1472 × 1104 |
| 3:4 | 1104 × 1472 |
| 3:2 | 1584 × 1056 |
| 2:3 | 1056 × 1584 |
| 16:9 | 1664 × 928 |
| 9:16 | 928 × 1664 |

Native resolution is noticeably slower than a smaller canvas (roughly +50%
runtime at 1328 vs 1024 square). For draft/Lightning work, a smaller square
(1024×1024) is a reasonable practical default; reserve native sizes for full-
model keepers. Unlike Klein, going up to native resolution here is generally
safe rather than something that starts duplicating subjects — this model was
trained at these sizes.

## 6. Talking to ComfyUI

**Loader nodes** (names as of current ComfyUI-GGUF releases; some builds
label these slightly differently — check your node picker):

- `UNETLoaderGGUF` (or `UnetLoaderGGUF`) → the Q8_0 diffusion model file
- `CLIPLoaderGGUF` if the text encoder is also GGUF, or the plain
  `CLIPLoader` node with its type set to the Qwen-Image family if using the
  fp8_scaled safetensors encoder
- `VAELoader` → `qwen_image_vae.safetensors`
- `EmptySD3LatentImage` (reused — Qwen-Image's 16-channel VAE is compatible
  with this node despite the name) for canvas size, or a Qwen-specific empty
  latent node if your ComfyUI version ships one
- A standard `KSampler` — the "true CFG" behaviour is just the ordinary `cfg`
  input with negative conditioning wired in, not a special node

**Via MCP.** As before: check what the server's generate tool actually
accepts before the first call in a session — these servers wrap the
underlying graph differently. Set both a positive and a negative text field
explicitly if the tool exposes one; on Klein that field was pointless, on
Qwen-Image it is real and should carry the pack's negative string (see
`qwen-prompt-standards.md` §3), except on the Lightning/fast tier where it
should be left blank.

**Via HTTP (batches).** `scripts/batch_generate.py` patches both the
positive and negative text-encode nodes it finds in an API-format workflow,
and writes cfg/steps into the sampler node from the plan — the same script as
before, now actually using the negative branch it detects.

## 7. When the model is not the problem

- **Missing nodes on template load**: install `ComfyUI-GGUF` if you haven't;
  the loader nodes above don't exist without it.
- **Out of memory**: see §3. Drop the text encoder quant before dropping the
  diffusion model's Q8_0 — that quant was the explicit choice this setup was
  built around.
- **Much slower than you remember from Klein**: expected. This is a 20B
  model at up to 50 steps versus a 4B model at up to 24. Use Lightning for
  anything exploratory.
- **Everything suddenly looks photographic**: check for the positive-magic
  suffix or camera/lens language leaking into an illustration-pack prompt —
  see `qwen-prompt-standards.md` §5.
