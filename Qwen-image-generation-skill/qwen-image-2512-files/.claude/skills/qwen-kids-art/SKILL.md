---
name: qwen-kids-art
description: Write, audit and run prompts for children's illustrations and printable coloring pages on a local Qwen-Image-2512 (Q8_0) install, usually through a ComfyUI MCP server. Use this skill whenever the user mentions Qwen-Image, Qwen 2512, ComfyUI, a local image model, coloring pages, kids' illustrations, storybook or nursery art, character sets for children, or complains that their image generations are inconsistent, hit-and-miss, or good-sometimes-bad — even if they don't name the model or ask for a "prompt". Also use it when generating any image intended for a child to look at or colour in.
---

# Qwen-Image kids' art

A prompt system for Qwen-Image-2512 (run as a Q8_0 GGUF) aimed at one specific
failure: output that is good one run and bad the next. That variance is almost
never randomness. It is usually an under-specified prompt, SD-era habits the
Qwen2.5-VL encoder can't use, an excluded thing that was described in the
positive prompt instead of the negative field, a style description that got
reworded between images, or the fast Lightning tier being asked to do work
that needs the full model's real CFG.

This skill previously targeted FLUX.2 [klein] 4B. The two models are prompted
the same way in most respects — plain sentences, not tag lists, a fixed
eleven-slot contract, a verbatim style signature per set — but differ in one
big way: **Qwen-Image has a real negative prompt.** Klein didn't. If anything
below contradicts a Klein-era habit, this skill is right and the habit is out
of date.

## The loop

**1. Establish the set, not the image.** Before writing any prompt, settle
four things and keep them fixed: style pack, age band, character sheet (if a
character recurs), palette. One question is usually enough — "who is this
for, and is it a colouring sheet or a coloured illustration?" Then commit.
Changing these mid-set is what makes a set look like three different books.

**2. Pick a runtime tier.** `full` (50 steps, real CFG, negative prompt
works) or `lightning` (4–8 steps, CFG 1.0, negative prompt is inert). Draft
on lightning, finish keepers on full — see `references/comfyui-runtime.md`.

**3. Build the prompt to the contract.** Eleven slots, fixed order, style
signature pasted verbatim, plus a negative prompt if the tier is `full`. Read
`references/qwen-prompt-standards.md` before writing the first prompt of a
session — it is the substance of this skill, not background reading.

```bash
python scripts/build_prompt.py --pack chunky_vector --age 5-7 --variant lightning \
  --subject "a round orange cat" --action "balancing on a beach ball" \
  --setting "a sunny back garden" --props "daisies,a red bucket" --print
```

For anything with more than one image, write a brief instead and build the
whole set at once, so the shared parts genuinely are shared:

```bash
python scripts/build_prompt.py --brief my-brief.json --out plan.json --print
```

`assets/brief.example.json` is the template. The builder emits prompt,
negative prompt, runtime params, a deterministic seed plan and an audit
result per image.

**4. Audit before queueing.** The builder runs this automatically; run it
directly when a prompt was written or edited by hand.

```bash
python scripts/audit_prompt.py --pack coloring_page --age 5-7 --variant full \
  --prompt "..." --negative "shading, grey, watermark, extra limbs"
```

Blockers mean do not queue. Then apply the judgement the script can't —
`references/prompt-audit-agent.md`, Gate 1. State fixes in one line rather
than narrating the audit.

**5. Generate four candidates, not one.** Draft on `lightning`, pick a
composition, re-render the winner on `full` at the same seed with the
negative prompt doing real work against whatever keeps going wrong. This
draft-then-finish split is in `references/comfyui-runtime.md` and is the
single biggest time saver — it was true for Klein too, only the step/CFG
numbers changed. Via MCP, check what the server's generate tool actually
accepts before the first call, including whether it exposes a negative-prompt
field — these servers differ. For batches, or a record of what produced what:

```bash
python scripts/batch_generate.py --plan plan.json --workflow qwen_image_2512_t2i_api.json --out ./run-01
```

**6. QC the images before showing them.** Gate 2 in
`references/prompt-audit-agent.md`. Cropped limbs, fused characters, broken
line art, malformed text, a face that reads as distressed. If all four
candidates fail the same way, the prompt is wrong — and now there's a second
lever before rewriting it: has the defect actually been put in the negative
prompt yet? Look up the symptom in the failure → fix table.

**7. Record what worked.** Prompt, negative prompt, seed, variant, steps.
Consistency is accumulated, not discovered.

## Quick reference

Full detail is in the reference files; this is what to hold in mind while
working.

- Qwen-Image-2512 reads sentences through a Qwen2.5-VL text encoder, not CLIP
  tags. No `masterpiece, best quality, 8k`. No `(word:1.3)`.
- **Negation still doesn't belong in the positive prompt** — it's still read
  by a language model and still tends to surface what it's told to avoid.
  The difference from Klein: there is now somewhere real to put it. Use
  `--negative`, not "no X" in the description.
- **The negative prompt only works on `full` (CFG > 1).** On `lightning` it's
  inert — leave it blank rather than writing one that's silently ignored.
- 45–90 words for illustration, 40–85 for line art. Under 30 words is still
  the main cause of seed-to-seed swing in the positive prompt.
- Hex codes work well but must attach to a named object: `the scarf is color #5B8E7D`.
- One quoted text string, three words maximum, for anything that must be
  exactly right. Qwen-Image renders in-scene text well (including bilingual),
  which makes short incidental text usable in interiors — see
  `references/qwen-prompt-standards.md` #5 — but exact wording still belongs
  in real type, not a diffusion prompt.
- Subject counts: one for ages 2–4, two for 5–7, three for 8–10. A bigger
  model tolerates more than Klein did, but characters still fuse past a
  handful.
- `--age` also accepts the publish-book framework's audience values
  (`early-reader-6-8`, `middle-grade-9-12`, `teen-13-17`, `adult-general`), so
  a project's `audience` field can be passed straight through.
- Native aspect ratios: 1328×1328 (1:1), 1472×1104 / 1104×1472 (4:3 / 3:4),
  1584×1056 / 1056×1584 (3:2 / 2:3), 1664×928 / 928×1664 (16:9 / 9:16).
- `lightning` ≈ 4–8 steps, CFG 1.0. `full` ≈ 50 steps, CFG ~4.0. Line art and
  painted textures need `full`.
- This is a 20B model, not 4B. Expect it to be slower and heavier than the
  old Klein setup — see `references/comfyui-runtime.md` #1 before assuming
  your hardware is already sized for it.

## Files

| File | Read when |
|---|---|
| `references/qwen-prompt-standards.md` | Before the first prompt of a session. Contract, the negative-prompt channel, rules, failure → fix table, worked before/after examples |
| `references/prompt-audit-agent.md` | Before queueing (Gate 1) and before showing images (Gate 2) |
| `references/comfyui-runtime.md` | Hardware reset, model files, GGUF loaders, variant choice, resolutions, seed protocol, MCP behaviour |
| `references/style-packs.md` | Choosing or adding a style pack, age-band guidance, the per-pack negative list |
| `references/runtime.local.md` | Fill in as you go — measured settings and known-good seeds for this install. Check it before trusting any default in this skill |
| `assets/style_packs.json` | The pack data both scripts read, including each pack's starter negative prompt. Edit here to change a look |
| `scripts/build_prompt.py` | Building single prompts or whole sets, positive and negative |
| `scripts/audit_prompt.py` | Linting any prompt, by hand or in a pipeline, including negative-prompt sanity checks |
| `scripts/batch_generate.py` | Running a plan against ComfyUI over HTTP with a manifest, now actually wiring the negative node |

## Book covers

Covers are a different job and live in a separate pack (`publish-book-cover-pack`,
dropped into a publish-book repo as `.claude/`). It reuses this skill's prompt
contract and auditor, adds cover-specific style packs keyed to the four
audience bands, and enforces the rule that matters most: **the image model
renders the artwork, never the title.** Cover type is set from real font
files at 300 DPI so it is exact, editable and inside the safe area — this
holds regardless of how good the art model has gotten at in-image text,
because the reasons are about exact wording, editability and font licensing,
not rendering quality. If a cover request arrives here, point at
`.claude/skills/book-cover-brief` and set `QWEN_SKILL_PATH` to this skill so
the cover prompts are audited with the same rules.

## Working with the person

Show the prompt (and the negative prompt, on `full`). They are the art
director and they can only correct what they can see. When something is
rejected, say what changed and why in one line ("moved the expression earlier
and added 'fused characters' to the negative prompt — it kept happening on
this seed range").

Push back on requests the model will still miss: precise long text, more than
a handful of named characters interacting, exact finger counts, a specific
real place. Offer the version that works instead.

## Non-negotiables for children's images

These hold regardless of how a request is framed.

- Never generate a likeness of a real child, and never work from a photo of
  one. If someone wants "my daughter as a cartoon", build an invented
  character from described traits instead — hair colour, favourite jumper,
  missing front tooth. Qwen-Image-2512's improved human realism makes this
  worth holding to more carefully, not less.
- Nothing frightening, sexualised, or showing a child in danger or distress
  that the image doesn't resolve. Not in any style pack, not as a "spooky
  Halloween" exception beyond friendly pumpkins and smiling ghosts.
- No named commercial characters or franchises. Describe the qualities
  instead — it keeps the work usable and it usually produces something
  better anyway.
- No photoreal children. These are illustrations.

The audit script blocks on all of these, but the script is a backstop, not
the decision.
