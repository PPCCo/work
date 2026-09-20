# Style packs

A style pack is a fixed block of words describing a medium, plus a palette, a light
clause, a default composition, a starter negative prompt, and a runtime
recommendation. The block is pasted
verbatim into every prompt in a set. That is the whole trick: the model isn't being
asked to reinvent the look each time, so it stops.

Data lives in `assets/style_packs.json`. Edit that file, not individual prompts.

Each pack's `negative` field is new since the move to Qwen-Image-2512 - Klein
had no working negative-prompt channel, so the old version of this file had
nowhere to put one. It only does anything on the **full** (50-step) runtime
tier; on Lightning it's correctly left unused. See
`references/qwen-prompt-standards.md` #3.

## Choosing

| Pack | Looks like | Best for | Cost |
|---|---|---|---|
| `coloring_page` | black line art on white | printable colouring sheets, activity books | high (base + 28 steps) |
| `chunky_vector` | bold flat shapes, thick outlines | toddlers, app art, flashcards, quick sets | low (distilled) |
| `storybook_gouache` | soft painted picture book | narrative spreads, gifts, keepsakes | high (base) |
| `soft_watercolor` | pale washes on paper | bedtime, nature, nursery prints | high (base) |
| `cut_paper_collage` | layered torn paper | craft themes, anything with tricky anatomy | low (distilled) |
| `friendly_3d` | rounded toy render | characters, covers, single hero images | high (base) |

Two practical notes. `cut_paper_collage` is the most forgiving pack there is — paper
shapes have no anatomy to get wrong, so the failure rate is far lower than the others,
which makes it a good rescue when a character keeps coming out mangled. `friendly_3d`
is the least forgiving; it needs the base model and still produces the most rejects,
so reach for it only when you specifically want that look.

## Age bands

The band sets three things: how many subjects are allowed, how many props, and the
detail phrase and line weight that go into the prompt.

- **2–4** — one subject, two props, very simple shapes, huge friendly features, lots
  of empty space. Very thick outlines. Small children read shape and face before
  anything else, and detail actively hurts.
- **5–7** — up to two subjects, three props, simple shapes with a few playful details.
  Thick outlines. Colouring within the lines is still developing, so keep line-art
  areas large.
- **8–10** — up to three subjects, five props, richer decorative detail, medium-weight
  lines. Small areas and patterns become a feature rather than a frustration.

## Adding a pack

Copy an existing entry in `assets/style_packs.json` and fill in:

- `signature` — 15–25 words naming the **medium and its physical qualities**. Name the
  material (gouache, cut paper, vector), not an artist and not a studio. If you can't
  describe it without naming a company, it isn't a style, it's someone's IP.
- `palette` — four or five hex codes. These get attached to objects in the prompt.
- `light`, `composition`, `background` — one clause each, phrased positively.
- `require_tokens` — the words the audit will insist are present. This is what makes
  the pack enforceable.
- `forbid_tokens` — words from other packs that would muddy this one.
- `negative` — a short, comma-fragment starting list of what tends to go wrong
  in this medium (e.g. for a painted pack: `muddy colours, flat lighting,
  photorealistic, blurry`). Extend it per project after a bad batch rather than
  replacing it wholesale.
- `word_budget` and `runtime` — see `references/comfyui-runtime.md`. `runtime.variant`
  is `"full"` or `"lightning"`, not the old `"base"`/`"distilled"`.

Then generate the same three test subjects (a character, a character plus prop, a
character in a scene) through the new pack and look at them side by side before
committing a whole set to it.
