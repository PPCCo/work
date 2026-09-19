---
name: klein-kids-art
description: Write, audit and run prompts for children's illustrations and printable coloring pages on a local FLUX.2 [klein] 4B ("Klein-4B") install, usually through a ComfyUI MCP server. Use this skill whenever the user mentions Klein, FLUX.2 klein, ComfyUI, a local image model, coloring pages, kids' illustrations, storybook or nursery art, character sets for children, or complains that their image generations are inconsistent, hit-and-miss, or good-sometimes-bad — even if they don't name the model or ask for a "prompt". Also use it when generating any image intended for a child to look at or colour in.
---

# Klein kids' art

A prompt system for FLUX.2 [klein] 4B aimed at one specific failure: output that is
good one run and bad the next. That variance is almost never randomness. It is
usually an under-specified prompt, SD-era habits the Qwen3 encoder can't use, a
negation the model cannot honour, a style description that got reworded between
images, or the 4-step distilled model being asked to do work that needs the base
model.

## The loop

**1. Establish the set, not the image.** Before writing any prompt, settle four
things and keep them fixed: style pack, age band, character sheet (if a character
recurs), palette. One question is usually enough — "who is this for, and is it a
colouring sheet or a coloured illustration?" Then commit. Changing these mid-set is
what makes a set look like three different books.

**2. Build the prompt to the contract.** Eleven slots, fixed order, style signature
pasted verbatim. Read `references/klein-prompt-standards.md` before writing the first
prompt of a session — it is the substance of this skill, not background reading.

```bash
python scripts/build_prompt.py --pack chunky_vector --age 5-7 \
  --subject "a round orange cat" --action "balancing on a beach ball" \
  --setting "a sunny back garden" --props "daisies,a red bucket" --print
```

For anything with more than one image, write a brief instead and build the whole set
at once, so the shared parts genuinely are shared:

```bash
python scripts/build_prompt.py --brief my-brief.json --out plan.json --print
```

`assets/brief.example.json` is the template. The builder emits prompt, runtime
params, a deterministic seed plan and an audit result per image.

**3. Audit before queueing.** The builder runs this automatically; run it directly
when a prompt was written by hand or edited afterwards.

```bash
python scripts/audit_prompt.py --pack coloring_page --age 5-7 --prompt "..."
```

Blockers mean do not queue. Then apply the judgement the script can't —
`references/prompt-audit-agent.md`, Gate 1. State fixes in one line rather than
narrating the audit.

**4. Generate four candidates, not one.** Draft on the distilled variant, pick a
composition, re-render the winner on base at higher steps with the same seed. This
draft-then-finish split is in `references/comfyui-runtime.md` and it is the single
biggest time saver. Via MCP, check what the server's generate tool actually accepts
before the first call — these servers differ. For batches, or when you want a record
of what produced what:

```bash
python scripts/batch_generate.py --plan plan.json --workflow klein_t2i_api.json --out ./run-01
```

**5. QC the images before showing them.** Gate 2 in
`references/prompt-audit-agent.md`. Cropped limbs, fused characters, broken line art,
malformed text, a face that reads as distressed. If all four candidates fail the same
way, the prompt is wrong — look up the symptom in the failure → fix table and change
something. Rerolling an unchanged prompt is how afternoons vanish.

**6. Record what worked.** Prompt, seed, variant, steps, resolution. Consistency is
accumulated, not discovered.

## Quick reference

Full detail is in the reference files; this is what to hold in mind while working.

- Klein reads sentences through a Qwen3 4B text encoder, not CLIP tags. No
  `masterpiece, best quality, 8k`. No `(word:1.3)`. No `BREAK`.
- **No negations.** FLUX.2 has no negative prompt pathway worth relying on, and
  "no scary faces" tends to produce a scary face. Always state the positive form.
- Word order is the weighting mechanism — most important thing first.
- 45–90 words for illustration, 40–85 for line art. Under 30 words is the main cause
  of seed-to-seed swing.
- Hex codes work well but must attach to a named object: `the scarf is color #5B8E7D`.
- One quoted text string, three words maximum.
- Subject counts: one for ages 2–4, two for 5–7, three for 8–10. Above that a 4B model
  fuses characters.
- Dimensions in multiples of 16, at or under ~2MP.
- Distilled ≈ 4 steps, CFG 1.0. Base ≈ 24 steps, CFG ~4. Line art and painted textures
  need base.

## Files

| File | Read when |
|---|---|
| `references/klein-prompt-standards.md` | Before the first prompt of a session. Contract, rules, failure → fix table, worked before/after examples |
| `references/prompt-audit-agent.md` | Before queueing (Gate 1) and before showing images (Gate 2) |
| `references/comfyui-runtime.md` | Variant choice, params, resolutions, seed protocol, MCP behaviour, character consistency via reference images |
| `references/style-packs.md` | Choosing or adding a style pack, age-band guidance |
| `references/runtime.local.md` | Fill in as you go — measured settings and known-good seeds for this install. Check it before trusting any default in this skill |
| `assets/style_packs.json` | The pack data both scripts read. Edit here to change a look |
| `scripts/build_prompt.py` | Building single prompts or whole sets |
| `scripts/audit_prompt.py` | Linting any prompt, by hand or in a pipeline |
| `scripts/batch_generate.py` | Running a plan against ComfyUI over HTTP with a manifest |

## Working with the person

Show the prompt. They are the art director and they can only correct what they can
see. When something is rejected, say what changed and why in one line ("moved the
expression earlier and cut the third duckling — 4B fuses repeated characters").

Push back on requests the model will miss: paragraphs of text in the image, five
named characters interacting, a specific real place, articulated hands. Offer the
version that works instead.

## Non-negotiables for children's images

These hold regardless of how a request is framed.

- Never generate a likeness of a real child, and never work from a photo of one. If
  someone wants "my daughter as a cartoon", build an invented character from described
  traits instead — hair colour, favourite jumper, missing front tooth.
- Nothing frightening, sexualised, or showing a child in danger or distress that the
  image doesn't resolve. Not in any style pack, not as a "spooky Halloween" exception
  beyond friendly pumpkins and smiling ghosts.
- No named commercial characters or franchises. Describe the qualities instead — it
  keeps the work usable and it usually produces something better anyway.
- No photoreal children. These are illustrations.

The audit script blocks on all of these, but the script is a backstop, not the
decision.
