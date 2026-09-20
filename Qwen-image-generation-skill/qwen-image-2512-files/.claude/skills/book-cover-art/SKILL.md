---
name: book-cover-art
description: Generate cover artwork with the local Qwen-Image-2512 (Q8_0) model through ComfyUI - front hero art with a reserved type zone, low-contrast back art, and spine art where the spine is wide enough. Use after /book-cover-brief, whenever cover artwork needs generating or regenerating, and whenever a cover review sends the artwork back. Never asks the model to render the title; type is set later by /book-cover-compose.
---

# /book-cover-art

Generates the artwork only. Every word on the cover comes later, from a font
file. A prompt that asks the model for text is a defect and the builder
blocks it.

## Steps

**1. Build the audited plan.**

```bash
QWEN_SKILL_PATH=<path to qwen-kids-art> \
python .claude/scripts/cover/cover_prompt.py \
  --spec projects/<id>/visuals/cover/spec.json \
  --audience early-reader-6-8 --book-type coloring-book --pack kids_activity_bold \
  --subject "..." --action "..." --setting "..." \
  --type-zone top-third --faces front,back --variant full \
  --out projects/<id>/visuals/cover/art-plan.json --print
```

The plan carries prompts, negative prompts, params, deterministic seeds, the
audit result and the upscale factor needed to reach print resolution. Clear
every blocker before generating anything. Default to `--variant full` — a
cover is almost always a keeper, and the negative prompt only does anything
there (it's a real CFG channel on this model, unlike the old Klein setup,
but it's inert on the fast `lightning` tier — see the qwen-kids-art skill's
`qwen-prompt-standards.md` #3).

**2. Draft, then finish.** If the concept itself is still in question,
generate a quick round on `lightning` to explore composition cheaply; once a
direction is chosen, render the kept candidates on `full` with the plan's
negative prompt actually doing work against whatever keeps going wrong.
Check the MCP's generate tool signature before the first call — these
servers differ, and confirm it exposes a negative-prompt field, not just a
positive one.

**3. Upscale properly.** Qwen-Image-2512's native resolutions top out around
1.3–1.8 MP; a 300 DPI print front needs three to nine. Use a ComfyUI upscale
model (4x-UltraSharp or RealESRGAN x4) and resize down to the plan's
`target_front_px`, or run a second full-model pass at a larger canvas with
the kept image as input at denoise ~0.4–0.5 (hi-res-fix style). Flat vector
and graphic packs survive either approach almost perfectly. Do not let the
composer upscale — it uses plain Lanczos and softens the art.

**4. Judge.** Cropped limbs, fused subjects, uncanny faces, a busy type zone,
a back cover with too much contrast for text to sit on. Then shrink the
front to 80 px and confirm the hero still reads. If all four candidates fail
the same way, check first whether the defect is actually in the negative
prompt yet — that's now a real lever — before rewriting the whole thing; see
the failure-to-fix table in the qwen-kids-art skill.

**5. Save** keepers to `visuals/cover/art/front.png`, `back.png`,
`spine.png`, record prompt, negative prompt, seed, variant and steps for
each, and register the artefacts.

## Rules

- No text, no titles, no lettering in any prompt.
- No negation in the positive prompt — put excluded content in the negative
  prompt instead (only meaningful on `full`; see step 1). Writing "no X" into
  the positive description is a Klein-era habit that no longer applies here
  and still tends to backfire, because the positive prompt is still read by a
  real language model.
- The type zone stays genuinely empty. If it fills with detail, regenerate
  rather than relying on a scrim later.
- No franchises, no real likenesses, no photoreal children, nothing
  frightening on a children's title. Qwen-Image-2512's stronger human realism
  makes the real-likeness rule worth watching more closely, not less.
