# Prompt audit agent

Two gates. The first runs before anything is queued and is mostly mechanical. The
second runs on the returned images and is where taste lives. Skipping the second one
is why bad batches get shipped.

---

## Gate 1 — prompt audit (before queueing)

Run the script first; it catches the mechanical failures deterministically:

```bash
python scripts/audit_prompt.py --pack storybook_gouache --age 5-7 --prompt "<the prompt>"
```

It returns a score out of 100 with blockers, warnings and notes. Blockers mean do not
queue. Then add the judgement the script cannot make:

**A. Is the subject unambiguous?**
Read only the first ten words. Could they describe two different pictures? "A bear
playing" — indoors or out, toy or animal, what kind of play? Ambiguity in the head of
the prompt is the main source of seed-to-seed swing.

**B. Is there exactly one thing happening?**
Count the verbs describing the subject. More than one and the model will blend them.

**C. Does the emotional read match the age?**
A children's image works when the feeling is legible in one glance from two metres
away. "Standing in a field" has no feeling. "Grinning with both arms thrown up" does.

**D. Is the style signature byte-identical to the pack?**
Diff it against `assets/style_packs.json`. Reworded signatures are the usual reason a
set drifts, and the drift is subtle enough that people blame the model.

**E. Is anything in the prompt beyond a 4B model's reach?**
Legible long text, more than three characters, articulated fingers, complex reflections,
precise spatial arrangements of many objects, a specific real location. Each of these
is a coin flip. Either remove it or accept that you will be culling more candidates.

**F. Is it right for the child who will see it?**
Would a cautious parent be happy with this image? Anything frightening, sad in a way a
small child can't resolve, or physically unsafe to copy (a toddler on a ladder, a child
alone near deep water) gets rewritten. No real children's likenesses, ever — invented
characters only.

**Verdict format**, kept short:

```
AUDIT: PASS (score 94)
Fixed before queueing: removed "no shading" -> "flat even lighting";
cut the count from five ducklings to two.
Accepted risk: quoted text "PLAY" may need a reroll.
```

---

## Gate 2 — image QC (after generation, before showing the user)

Look at every returned image against this list. It takes seconds and it is the
difference between a reliable pipeline and a lottery.

**Reject outright:**
- Anything cut off at the frame edge that shouldn't be (head, feet, ears, tail)
- Fused or duplicated characters, extra or missing limbs, a second head
- Melted hands or paws that the style doesn't excuse
- Malformed lettering
- Eyes looking in two directions, or an expression that reads as distressed when it
  should read as happy
- Anything uncanny about a child figure — proportions drifting adult, or drifting photoreal

**Line art only:**
- Broken outlines, or gaps where a shape should close (bucket-fill test: would paint
  leak out?)
- Grey pixels, hatching or gradient shading where there should be flat white
- Lines too fine for the age band to colour inside

**Consistency across a set:**
- Same character, same colours, same proportions, same outline weight page to page
- Same background treatment and same amount of white space
- Same apparent "camera height" — one page from above and the next from below reads
  as a mistake even to a four-year-old

**Then diagnose, don't reroll.** A reroll with an unchanged prompt is how people burn
an afternoon. Look up the symptom in the failure → fix table in
`references/klein-prompt-standards.md`, change the prompt or the runtime, and note
what you changed. If four candidates all fail the same way, the prompt is wrong, not
the seed.

**Keep a record.** For each kept image, note prompt, seed, variant, steps, CFG. That
record is the asset — after a couple of sessions it tells you exactly which settings
your install likes, and the inconsistency problem mostly disappears.
