# Klein prompt standards

Everything here is specific to FLUX.2 [klein] 4B (Black Forest Labs, Apache 2.0,
distilled from the FLUX.2 base model). Habits carried over from SD 1.5 / SDXL are
the single biggest cause of inconsistent output on this model, so the first half
of this file is about what to stop doing.

Contents:
1. What Klein actually is, and why it changes prompting
2. The prompt contract (slot order)
3. Rules that are non-negotiable
4. Rules of thumb that are worth breaking sometimes
5. Colour, text and counting
6. Failure → fix table
7. Worked examples

---

## 1. What Klein actually is

- A 4B rectified-flow transformer, unifying text-to-image and image editing in one
  model. In ComfyUI it is paired with a **Qwen3 4B text encoder**, not CLIP.
- It ships in two flavours: **base** (undistilled, slower, more faithful, fine-tunable)
  and **distilled** (roughly 4 steps, sub-second, speed first).
- Being distilled from a much larger teacher is why it punches above 4B on lighting,
  materials and composition — and why it collapses when you feed it CLIP-era tag soup.

Three consequences that matter more than anything else:

**There is no 77-token limit and no tag vocabulary.** The encoder is a language
model. It reads sentences. `1girl, masterpiece, best quality, 8k, intricate` is not
a prompt to it, it is a shopping list with no grammar, and the output quality will
swing wildly run to run because there is nothing holding the interpretation still.

**Negative prompts do not work the way you are used to.** Black Forest Labs states
plainly that FLUX.2 does not support negative prompts. On the distilled variant the
guidance pathway is folded into the model, so there is no unconditional branch for a
negative embedding to attach to; a negative box in the workflow may exist and do
nothing. On the base variant with real CFG above 1.0 a negative prompt can have some
effect, but it is weak and unreliable. Either way: **write what you want, never what
you don't.** Saying "no scary faces" puts "scary face" in front of a language model
and frequently produces exactly that.

**Word order is a weighting mechanism.** Klein attends most strongly to the opening
of the prompt. That replaces `(word:1.4)` syntax entirely. If something matters,
move it left.

---

## 2. The prompt contract

Every generation prompt uses these slots, in this order. `build_prompt.py` assembles
them for you; write them in this order by hand too.

```
1  SUBJECT            what it is, in plain words, with the count
2  ACTION             one verb, one thing happening
3  EXPRESSION         the emotional read - kids' art lives or dies here
4  IDENTITY           the character sheet, verbatim, if this is part of a set
5  STYLE SIGNATURE    the style-pack block, verbatim, never reworded
6  DETAIL LEVEL       the age-band phrase
7  SCENE              setting plus at most a few named props
8  LIGHT              one clause
9  COLOUR             palette or hex codes attached to named objects
10 COMPOSITION        framing, what must be inside the frame
11 TEXT               at most one short quoted string, optional
```

Why this order and not another: slots 1–4 decide whether the image is *the right
image*, and they need the model's strongest attention. Slots 5–6 decide whether it
matches the rest of the set. Slots 7–11 are refinement, and it is fine if the model
half-ignores the tail — that is the cheapest thing to lose.

**Length**: 45–90 words for illustration packs, 40–85 for line art. Under 30 words
and the model fills the gaps differently on every seed, which is what "sometimes
good, sometimes bad" usually is. Past about 110 words the tail stops landing and you
have added variance for nothing.

---

## 3. Non-negotiable

- **No negations anywhere.** Not "no", "without", "avoid", "not", "free of". Convert
  each one into its positive form. This is mechanical and the audit script blocks on it.
- **No SD syntax.** No `(word:1.2)`, no `[a|b]`, no `BREAK`, no `<lora:...>` inside
  prompt text, no `--no` flags. Klein reads them as literal characters.
- **No quality tags.** `masterpiece`, `best quality`, `8k`, `ultra detailed`,
  `trending on artstation` do nothing here except crowd out real description.
- **Style signature pasted verbatim.** One character of drift per image and a
  twelve-page set stops looking like one book. If you want to change the look,
  change it in `assets/style_packs.json` and rebuild the whole set.
- **No named commercial characters or franchises.** Describe the qualities instead.
- **No photoreal children, and never a likeness of a real child.** These are
  illustrations. If someone sends a photo of their kid and asks for a cartoon of
  them, don't do it — offer to build an invented character from described traits
  (hair colour, favourite jumper, missing front tooth) instead.

## 4. Worth knowing, occasionally worth breaking

- **Camera and lens language is for photorealism.** "shot on Hasselblad, 85mm,
  f/2.8" genuinely works on FLUX.2 — and it will drag a children's illustration
  toward a photo. Keep it out of illustration packs.
- **Klein is multilingual.** Prompting in the language of the cultural context gives
  more authentic results. Useful for a book set somewhere specific.
- **One action, one spatial relation.** Three simultaneous clauses ("while", "as",
  "behind", "in front of") is about where a 4B model starts fusing objects.
- **Prompt upsampling / auto-enhance features** add detail you didn't ask for and
  therefore add variance. Leave them off for set work.

## 5. Colour, text and counting

**Hex codes work**, and they are the cleanest way to hold a palette steady across a
set. They must be attached to a named object: `the scarf is color #5B8E7D` lands;
`use #5B8E7D somewhere` does not. Four or five per image is the practical ceiling.
Gradients work by naming both ends: `a sky gradient starting at #1B0A3E and
finishing at #E8728A`.

**Text rendering is a real strength** of FLUX.2 for its size, but it degrades with
length. One quoted string, three words maximum, with a stated position and style:
`the word "HELLO" hand-lettered in chunky rounded letters across the top`. For a
book title or anything that must be perfect, generate the art with blank space and
set the type afterwards — it will be sharper and editable.

**Counting is a weakness.** Ages 2–4: one subject. 5–7: two. 8–10: three. Above
that, a 4B model starts merging characters into each other, and repeated animals
develop extra limbs. "A few ducklings" is safer than "five ducklings" if the exact
number doesn't matter to the story.

**Hands, feet and small props** are still the weak points. Kids' art gets a free
pass here: mittens, paws, holding something large, hands behind the back, or a
chunky style where fingers aren't articulated at all will dodge the problem entirely.

## 6. Failure → fix

| What you see | Actual cause | Fix |
|---|---|---|
| Same prompt, wildly different quality per seed | Prompt underspecified; model free-associating the gaps | Fill all 11 slots; get to 45+ words |
| Set looks like different artists | Style signature reworded per image | Paste signature verbatim from the pack |
| Asked for "no X", got X | Negation fed to a language encoder | Rewrite as the positive fact |
| Muddy, washed-out, plasticky | Distilled variant on a painterly pack | Re-render the keeper on base with ~24 steps |
| Broken or doubled outlines in line art | 4-step sampling on high-frequency edges | Base variant, ~28 steps, and "every shape fully closed" |
| Grey shading in a coloring page | A colour or lighting word survived in the prompt | Strip every colour/shadow/texture word |
| Characters fused or extra limbs | Too many subjects for a 4B model | Cut the count to the age-band limit |
| Cropped head, cut-off feet | No framing slot | "full body, centred, generous space around it" |
| Text is gibberish | String too long, or more than one string | One string, ≤3 words, or set type afterwards |
| Colours drift across the set | Palette described in words | Hex codes attached to named objects |
| Too detailed / busy for a toddler | Age band not applied | Use the 2–4 detail phrase and one subject |
| Faces look uncanny or adult | Style pack pulling photoreal | Check for camera/lens/photoreal words |

## 7. Worked examples

**Before** (a real-shaped bad prompt — tag soup, negation, no framing):

```
cute cat, coloring page for kids, no shading, (thick lines:1.3), masterpiece,
best quality, 8k, white background, no color
```

Two negations, a weight, four dead quality tags, twelve words of actual content.
Every seed will interpret this differently.

**After**:

```
A round fluffy cat sitting upright with its tail curled around its paws, with a
warm friendly expression, clean black-and-white coloring book line art, thick
uniform black outlines, every shape fully closed, flat pure white background,
large open areas left blank ready for colouring, printable children's coloring
page, simple clear shapes with a few playful details, a plain white background
with a simple rug shape beneath it, even flat lighting, single centred subject,
whole subject inside the frame, wide white margin around the edges.
```

**Before** (illustration, style-led and vague):

```
storybook illustration of a hedgehog in a forest, beautiful, highly detailed,
soft lighting, 4k
```

**After**:

```
A small round hedgehog peering up at a tall spotted mushroom, curious with its
eyebrows raised, a hedgehog named Pip with a cream face, rust-brown spines, round
black eyes and a tiny green scarf, soft gouache picture book illustration, visible
brush texture, warm muted palette, rounded friendly character design, classic
children's storybook art, simple clear shapes with a few playful details, a mossy
forest floor with two ferns, warm afternoon light with gentle soft shadows, colour
palette of #E8C07D #9EBC8A #D08C60 #6B705C #FDF6EC, subject in the near foreground
with a soft background.
```

The second one will not be *better* on every seed. It will be *consistent* across
seeds, which is the thing you are actually missing.
