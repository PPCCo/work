---
name: book-cover-review
description: Review and preflight a finished cover before it is proofed or packaged - thumbnail legibility, channel specs, claims against the actual interior, series consistency, rights and disclosure. Use before FINAL_PROOF, before /book-package for any channel, and any time someone asks whether a cover is good enough or ready to upload.
---

# /book-cover-review

The gate between a cover that exists and a cover that ships. Assume it is flawed.

## Steps

**1. Machine gates.**

```bash
python .claude/scripts/cover/thumbnail_test.py \
  --front projects/<id>/visuals/cover/front_only.png \
  --out-dir projects/<id>/visuals/cover/thumbs

python .claude/scripts/cover/cover_preflight.py \
  --spec projects/<id>/visuals/cover/spec.json \
  --wrap projects/<id>/visuals/cover/wrap.pdf \
  --ebook projects/<id>/visuals/cover/ebook.jpg \
  --channel kdp-ebook --json
```

**2. Look at the 80 px thumbnail yourself.** Open `thumbs/thumb_80.png`. Read the
title aloud. Name the subject. Over a second on either and the cover fails, no
matter what the metrics said. Then check the greyscale and squint renders.

**3. The lineup test.** Put it mentally among nine competitors in the same
category and age band. Does it vanish? Look cheaper? Look aimed at a different
age? Name which competitor you would click instead, and why.

**4. Claims against the interior.** Every count, age range, difficulty, page size
and paper claim on the cover, verified against the built manuscript. A mismatch
is a blocker. So is an illustration style on the cover that does not appear
inside.

**5. Series consistency.** Pack, palette, type zone, title position, author
position, spine treatment against the siblings.

**6. Rights and disclosure.** Font licences recorded. No real likenesses, no
franchises, no living artist named as a style. AI disclosure prepared with model,
version and which assets were generated. For children's titles, nothing
frightening, sexualised, or showing a child in unresolved danger.

**7. Write `visuals/cover/cover-review.md`** with scores out of 5 for thumbnail
legibility, category fit, hierarchy, craft, series consistency and age fit; every
finding with a severity and a specific fix naming the owning step. Recommend
ship, revise or re-art.

## Rules

- Zero blockers before the cover can move on.
- Before a final print export, confirm the wrap width against the channel's own
  generated template for this trim, page count and paper.
- Recommend the transition; a human approves the artefact hash.
