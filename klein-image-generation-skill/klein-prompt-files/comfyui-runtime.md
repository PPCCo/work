# ComfyUI runtime for Klein 4B

Prompt shape fixes most of the inconsistency. The rest of it lives here: running the
wrong variant for the job, and treating seeds as luck instead of as a process.

---

## 1. Two models, two jobs

| | base (undistilled) | distilled |
|---|---|---|
| File | `flux-2-klein-base-4b-fp8.safetensors` | `flux-2-klein-4b-fp8.safetensors` |
| Steps | ~20–28 | ~4 |
| Speed | roughly 15–20s on a 5090-class card | ~1s |
| CFG | real CFG, typically ~3–5 | 1.0 — leave it alone |
| Negative prompt | weakly effective above CFG 1.0 | inert |
| Use for | keepers, line art, painted styles, anything with texture | drafts, composition search, flat styles |

Both need `qwen_3_4b.safetensors` (text encoder) and `flux2-vae.safetensors`, in
`ComfyUI/models/text_encoders/` and `ComfyUI/models/vae/`.

**The numbers in this file and in `build_prompt.py` are starting points.** The
defaults shipped in ComfyUI's own Flux.2 Klein templates (Workflow → Browse
Templates → `image_flux2_klein_text_to_image`) win over anything written here. Once
you have measured what your install likes, write it down in `runtime.local.md` next
to this file and use those numbers instead.

## 2. The draft-then-finish pipeline

This is the core workflow and it is what most directly fixes "sometimes good,
sometimes bad":

1. **Draft on distilled.** Four seeds, 4 steps, a second each. You are choosing a
   composition and a pose, not judging quality. Distilled output looks soft and
   slightly plastic; ignore that.
2. **Pick one seed.** Judge silhouette, framing, expression, and whether the idea
   reads at a glance.
3. **Finish on base.** Same prompt, same seed, base model, ~24 steps. The composition
   stays recognisably the same and the render quality arrives.
4. **Lock the seed** for the rest of the set if you are making a series.

Rendering everything on base from the start costs twenty times more time per idea and
is why an afternoon disappears into eight images.

## 3. Resolution

Dimensions must be **multiples of 16**. Stay at or under about 2 megapixels; a 4B
model starts duplicating subjects when pushed much past its training resolution.

| Use | Size |
|---|---|
| Square (cards, app art) | 1024 × 1024 |
| Portrait | 1024 × 1360 |
| Landscape | 1360 × 1024 |
| Storybook spread | 1440 × 816 |
| Printable coloring page (A4-ish) | 1216 × 1600 |

For print, generate at these sizes and upscale afterwards rather than asking the model
for 3000px directly.

## 4. Seeds

Seeds are not quality. A seed is a composition lottery ticket, and the ticket is only
meaningful for one exact prompt — change a word and the same seed gives a different
picture. So:

- Generate 4 candidates per idea, always. One candidate is not a sample.
- `build_prompt.py` derives seeds deterministically from the prompt text, so the same
  brief regenerates the same candidates tomorrow.
- Write the winning seed into your notes with the exact prompt. A seed without its
  prompt is worthless.
- If all four candidates fail the same way, fix the prompt. Rerolling a broken prompt
  is the most common way to waste an hour.

## 5. Consistency across a set

Three mechanisms, strongest last:

1. **Character sheet.** A 20–30 word description of the character, pasted verbatim
   into every prompt: species, body shape, face colouring, eyes, one signature item
   of clothing. Keep it in the brief so it cannot drift.
2. **Locked palette.** Hex codes attached to named objects, identical across the set.
3. **Reference editing.** Klein unifies generation and editing, with single- and
   multi-reference input. Once you have one approved image, feed it back as a
   reference and ask for the next pose. This holds a character far tighter than text
   alone. Keep the edit instruction short — the reference carries the appearance, the
   prompt only carries the change ("the same hedgehog, now holding a lantern, three
   quarter view"). Long descriptions fight the reference.

## 6. Talking to ComfyUI

**Via MCP (default for conversational work).** ComfyUI MCP servers differ a lot from
each other — some take a whole API-format workflow, some take a prompt plus a few
parameters, some inject LoRA nodes. Before the first generation of a session, list the
available tools and check what the generate tool actually accepts, rather than assuming.
The usual shape is: queue → get a `prompt_id` back → poll for completion → retrieve
image URLs. Many return immediately and expect polling, so don't treat the first
response as a finished image.

Parameters worth setting explicitly every time, because server defaults are rarely
right for this model: model file (base vs distilled), steps, CFG, width, height, seed.
If the tool exposes a negative prompt field, leave it empty rather than filling it with
habit-tokens; on the distilled model it does nothing, and on base it is a weak lever
best left at rest.

**Via HTTP (batches).** `scripts/batch_generate.py` posts an API-format workflow to
`/prompt`, polls `/history/{prompt_id}`, pulls the files from `/view`, and writes a
`manifest.jsonl` recording prompt, seed and params per file. Export the workflow with
**Workflow → Export (API)** — a normal export will not queue.

## 7. When the model is not the problem

- **Missing nodes on template load** usually means ComfyUI needs updating; the Flux.2
  Klein nodes are recent.
- **Instant failures** are almost always a filename mismatch in the loader nodes.
- **Out of memory**: the 4B fp8 build fits in roughly 8–13GB. Drop resolution before
  dropping steps; steps are where the quality is.
- **Everything suddenly looks different** — check whether a LoRA is still loaded from a
  previous workflow, and whether you are on the variant you think you are on.
