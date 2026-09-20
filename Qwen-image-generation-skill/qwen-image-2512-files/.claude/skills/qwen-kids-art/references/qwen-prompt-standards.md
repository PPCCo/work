# Qwen-Image-2512 prompt standards

Everything here is specific to Qwen-Image-2512 (Alibaba/Tongyi Lab, Apache 2.0),
run here as a Q8_0 GGUF. It replaced FLUX.2 [klein] 4B in this skill. The two
models are prompted differently in one important way — Qwen-Image has a real
negative-prompt channel — and similarly in most others. Read this even if you
used the old Klein version of this skill; do not carry Klein habits over
unchecked.

Contents:
1. What Qwen-Image-2512 actually is, and why it changes prompting
2. The prompt contract (slot order)
3. The negative prompt — the biggest behavioural difference from Klein
4. Rules that are non-negotiable
5. Rules of thumb that are worth breaking sometimes
6. Colour, text and counting
7. Failure → fix table
8. Worked examples

---

## 1. What Qwen-Image-2512 actually is

- A 20B-parameter Multimodal Diffusion Transformer (MMDiT). This is a much
  larger model than Klein's 4B — expect meaningfully better coherence, and
  meaningfully slower and heavier generation. Plan hardware and time budgets
  accordingly; see `references/comfyui-runtime.md`.
- Text conditioning comes from **Qwen2.5-VL**, a real frozen vision-language
  model, not a lightweight text encoder. It reads full sentences with strong
  comprehension of spatial relationships, counts and compound instructions —
  and, notably, is bilingual, with particular strength in Chinese text.
- The VAE is a 16-channel design adapted from Wan2.1-VAE. Doesn't affect
  prompting, but explains why ComfyUI wires a specific `qwen_image_vae.safetensors`
  rather than a generic SD VAE.
- 2512 is the December-2025 update to the original August-2025 Qwen-Image
  release. It specifically improved human realism (less "AI-plastic" skin,
  individually rendered hair, natural ageing), natural texture (fur, foliage,
  landscapes), and text rendering. None of the interior-illustration or
  cover-art use cases in this skill lean on photoreal humans, but the general
  coherence lift benefits every pack.
- Ships in two effective speed tiers: the **full** model (50 steps, real
  classifier-free guidance) and a **Lightning** LoRA overlay (4-step or
  8-step distilled, CFG forced to 1.0). This mirrors Klein's base/distilled
  split conceptually, but it's the same checkpoint with a LoRA added, not two
  separately released models.

Two consequences that matter more than anything else:

**Qwen2.5-VL is a full language model, so prompts are still sentences, not
tag lists.** `1girl, masterpiece, best quality, 8k, intricate` is exactly as
wrong here as it was for Klein — a real language encoder gets a grammar-free
shopping list instead of a description, and the ambiguity shows up as
run-to-run variance. This part of the Klein-era discipline carries over
unchanged.

**Qwen-Image genuinely supports negative prompts.** This is the one place
Klein's rules do not transfer. See section 3 — it is worth its own heading
because getting this backwards (writing negation into the positive prompt,
the old Klein-safe habit) throws away real, working guidance.

---

## 2. The prompt contract

Same eleven-slot shape as before, because the underlying reason — a language
model reads left to right and gives real prose more grip than a keyword list —
still holds:

```
1  SUBJECT            what it is, in plain words, with the count
2  ACTION             one verb, one thing happening
3  EXPRESSION         the emotional read
4  IDENTITY           the character sheet, verbatim, if this is part of a set
5  STYLE SIGNATURE    the style-pack block, verbatim, never reworded
6  DETAIL LEVEL       the age-band phrase
7  SCENE              setting plus at most a few named props
8  LIGHT              one clause
9  COLOUR             palette or hex codes attached to named objects
10 COMPOSITION        framing, what must be inside the frame
11 TEXT               at most one short quoted string, optional (see §6)
```

**Length**: 45–90 words for illustration packs, 40–85 for line art — same
targets as before. Qwen2.5-VL's comprehension is strong enough to hold more,
but padding a prompt past what the image actually needs still adds noise, not
control.

**Word order**: front-loading the important content is still a reasonable
habit with any transformer-based encoder, though it is a heuristic here, not
a documented hard rule the way it was asserted for Klein's smaller encoder.
Lead with subject and action regardless — it reads better to a human editing
the prompt too.

---

## 3. The negative prompt

This is the load-bearing difference from the Klein version of this skill.

**Klein had no working negative pathway.** FLUX.2 [klein] doesn't support
negative prompts in any reliable way, so the old rule was absolute: never
write "no X" anywhere, always restate as the positive fact.

**Qwen-Image has a real one**, driven by actual classifier-free guidance
(`true_cfg_scale` in the reference pipeline; on the sampler side in ComfyUI
this is just the ordinary `cfg` value on the KSampler, with a negative
conditioning branch wired in). When CFG is above 1.0 — i.e. on the **full**
50-step model — content named in the negative prompt is genuinely pushed away
from the output. This is the single biggest lever available for fixing a
model that is "sometimes good, sometimes bad": put the recurring failure mode
in the negative prompt instead of hoping the positive prompt avoids it by
omission.

Two rules follow, and they are easy to get backwards:

- **Put excluded content in the dedicated negative-prompt field. Never write
  it as a negation inside the positive prompt.** "a cat, not scary" is still
  wrong — the positive prompt is still read by a real language model and
  still tends to surface what it's told to avoid. The negative field is a
  separate, purpose-built channel; use it instead of fighting the positive
  prompt into an unnatural shape.
- **On Lightning (fast/4-step/8-step) generation, the negative prompt does
  nothing**, because CFG is forced to 1.0 for speed and the negative branch
  isn't computed. Pass an empty or single-space negative prompt there rather
  than writing one that will be silently ignored — a filled-in negative field
  on a fast draft creates false confidence that something is being excluded.
  This is the same "distilled models can't take a negative" situation Klein
  was in, just now true only for the fast tier instead of always.

**What goes in the negative prompt.** It doesn't need to be a sentence — this
is the one field where short comma-separated fragments are the normal,
working convention (the opposite of the positive-prompt rule), because it
isn't being parsed for meaning the same way; it's steering the CFG difference.
Typical contents: rendering-quality complaints (`blurry, low quality, jpeg
artifacts`), unwanted medium drift (`photorealistic, photo` on an illustration
pack), and specific recurring defects you've actually seen (`extra fingers,
fused characters, watermark, signature, text`). Each style pack in
`assets/style_packs.json` now carries a starter `negative` string; extend it
per-project rather than replacing it, and keep a running note of what you add
after a bad batch — the negative prompt is where the "record what worked"
habit pays off fastest.

**Full vs Lightning at a glance:**

| | Full | Lightning |
|---|---|---|
| Steps | 50 | 4 or 8 |
| CFG (`true_cfg_scale`) | ~4.0 | 1.0 |
| Negative prompt | works | inert — leave blank |
| Use for | keepers, anything the negative prompt needs to fix | drafts, composition search |

---

## 4. Non-negotiable

- **No negation in the positive prompt.** Excluded content goes in the
  negative field (§3), not as "no X" or "without X" in the description.
- **No SD-era weighting or control syntax.** No `(word:1.2)`, no `[a|b]`, no
  `BREAK`, no `<lora:...>` inside prompt text. Qwen2.5-VL reads these as
  literal characters, same as Klein did.
- **No dead quality-tag stacking** (`masterpiece, best quality, 8k, ultra
  detailed, trending on artstation`). See §5 for the one documented exception.
- **Style signature pasted verbatim.** Still the main defence against a set
  drifting across images — nothing about the model change affects this.
- **No named commercial characters or franchises.**
- **No photoreal children, and never a likeness of a real child.** Qwen-Image-
  2512's improved human realism makes this more important to hold the line
  on, not less — a stronger model produces a more convincing likeness from
  the same careless prompt.

## 5. Worth knowing, occasionally worth breaking

- **The "positive magic" suffix is a real, documented Qwen-Image convention**
  — the reference pipeline appends a fixed phrase to every prompt: `, Ultra
  HD, 4K, cinematic composition.` (or the Chinese equivalent `，超清，4K，电影级构图`
  for Chinese-language prompts). Unlike Klein's dead quality tags, this one
  measurably helps in Qwen's own benchmarks — but only for photographic and
  cinematic output. For the flat, vector, gouache and line-art packs this
  skill actually uses, the suffix pulls the image toward photographic
  rendering values and fights the illustration style. Leave it off for every
  pack in `assets/style_packs.json` as shipped. `build_prompt.py --magic-
  suffix` is there if you ever add a photorealistic pack and want it.
- **Bilingual strength is real.** Prompting in the language of the cultural
  setting (particularly Chinese) gives more authentic results than an
  English description of a Chinese scene. Not typically relevant to this
  skill's audiences, but worth knowing if a project needs it.
- **In-scene text is a genuine capability now, not just a risk to manage.**
  Qwen-Image-2512 renders short in-image text well, including bilingual
  signage. For interior illustrations — a labelled diagram, a sign in a
  picture-book scene — a short quoted string is workable where it would have
  been a coin-flip on Klein. The length and count limits in §6 still apply.
  Cover titles are a separate matter — see the cover pack's standards, which
  set cover type from real fonts regardless of the art model's text ability,
  for reasons of exact wording, editability and licensing that have nothing
  to do with rendering quality.
- **One action, one spatial relation** is still the safer default at anything
  past a single clause, though the larger model tolerates a bit more
  compound instruction than Klein did before it starts blending.

## 6. Colour, text and counting

**Hex codes** work the same way as before: attach each to a named object
(`the scarf is color #5B8E7D`), four or five per image as a practical ceiling.

**Text rendering** is stronger than Klein's across the board, and reliably
bilingual. The same discipline still applies: one quoted string, three words
maximum for anything that has to be legible and correct, with a stated
position and style. For anything the customer will actually read at speed —
a title, a price, a specific claim — generate the art with blank space and
set the type afterwards, the same rule as before; a diffusion model, however
good, still can't promise the exact string a metadata record requires.

**Counting** is meaningfully better than a 4B model but still a soft limit,
not a solved problem. The age-band caps in `assets/style_packs.json` are kept
as-is (one subject for 2–4, two for 5–7, three for 8–10, and so on for the
publish-book audience bands) — treat them as a starting point to loosen
cautiously per project rather than a number to discard because the new model
is bigger.

## 7. Failure → fix

| What you see | Actual cause | Fix |
|---|---|---|
| Same prompt, wildly different quality per seed | Prompt underspecified | Fill all 11 slots; get to 45+ words |
| A specific defect keeps recurring across a set | It was never told to avoid it | Add the defect to the negative prompt on the **full** model — this is now a real lever |
| Fix seemed to do nothing | Generating on Lightning/4-step/8-step | Negative prompt is inert below CFG ~2. Switch to full for anything the negative has to fix |
| Set looks like different artists | Style signature reworded per image | Paste signature verbatim from the pack |
| Asked for "no X" in the positive prompt, got X anyway | Negation fed to the positive language channel | Move it to the negative-prompt field |
| Image looks like a photo when you wanted flat illustration | The positive-magic suffix, or photographic language, leaked into an illustration pack | Drop the suffix; check for camera/lens/photoreal words |
| Broken or doubled outlines in line art | Too few steps for high-frequency edges | Full model, more steps, plus "every shape fully closed" in the prompt |
| Characters fused or extra limbs | Too many subjects for the scene, or a known defect not yet in the negative prompt | Cut the count to the age-band limit; add "fused characters, extra limbs" to negative |
| Cropped head, cut-off feet | No framing slot | "full body, centred, generous space around it" |
| Colours drift across a set | Palette described in words instead of hex | Hex codes attached to named objects |
| Text is gibberish | String too long, or more than one string | One string, ≤3 words, or set type afterwards |

## 8. Worked examples

**Before** (Klein-era habits, now doubly wrong — negation in the positive
prompt AND an unused negative field):

```
positive: cute cat, coloring page for kids, no shading, not scary, masterpiece,
          best quality, 8k, white background
negative: (empty)
```

**After**:

```
positive: A round fluffy cat sitting upright with its tail curled around its
          paws, with a warm friendly expression, clean black-and-white
          coloring book line art, thick uniform black outlines, every shape
          fully closed, flat pure white background, large open areas left
          blank ready for colouring, printable children's coloring page,
          simple clear shapes with a few playful details, a plain white
          background with a simple rug shape beneath it, even flat lighting,
          single centred subject, whole subject inside the frame, wide white
          margin around the edges.
negative: shading, grey, gradient, texture, photorealistic, watermark,
          signature, extra limbs, blurry
variant:  full (50 steps, cfg 4.0) — line art needs the negative prompt doing
          real work against grey creeping into "flat" areas
```

Note what moved: the two things the old prompt tried to prevent by asking
nicely ("no shading", "not scary") now live in the negative field, where they
actually do something, and the positive prompt is a clean, entirely positive
description exactly as before.
