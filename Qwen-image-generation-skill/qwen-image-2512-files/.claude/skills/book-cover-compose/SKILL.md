---
name: book-cover-compose
description: Set all cover type and assemble the deliverables - full print wrap with spine and barcode zone, the separately composed ebook cover, the front-only file for mockups, and an editable SVG master. Use after /book-cover-art, during LAYOUT_AND_FORMAT_BUILD, whenever a title, subtitle, author line or back-cover layout changes, and whenever the page count changes, since the spine and the whole wrap change with it.
---

# /book-cover-compose

Turns approved artwork plus approved copy into the files a channel accepts.

## Steps

**1. Recompute the spec** if the page count, trim, paper or binding has moved at
all. Never carry a spine width over from an earlier build.

**2. Write `visuals/cover/copy.json`** from the copywriter's output. Title and
subtitle must match the metadata record character for character.

**3. Pick the fonts** from the table in
`.claude/standards/cover-typography-standard.md`. Confirm each licence covers
commercial use and embedding, and record it for the rights register.

**4. Compose.**

```bash
python .claude/scripts/cover/cover_compose.py \
  --spec projects/<id>/visuals/cover/spec.json \
  --copy projects/<id>/visuals/cover/copy.json \
  --front-art projects/<id>/visuals/cover/art/front.png \
  --back-art  projects/<id>/visuals/cover/art/back.png \
  --title-font Baloo2-ExtraBold --body-font Poppins-Regular \
  --type-zone top-third --align center --author-bottom \
  --out-dir projects/<id>/visuals/cover
```

A non-zero exit means text left the safe area or the back copy reached the
barcode zone. Both are build failures, not notes.

**5. Read `layout-report.json` before looking at the picture.** Title size, title
as a share of cover height (10% floor; 12-18% for children's and activity),
measured contrast, and whether a scrim was applied automatically. An automatic
scrim means the artwork's type zone was not calm enough - going back to
/book-cover-art is usually better than keeping the patch.

**6. If the title will not fit legibly**, shorten the title or demote the
subtitle. Never solve it with smaller type.

**7. Register** `wrap.pdf`, `wrap.png`, `ebook.jpg`, `front_only.png`,
`wrap.svg`, `layout-report.json` as artefacts and hand to /book-cover-review.

## Rules

- The ebook cover is composed in its own layout, not cropped from the print
  front; the aspect ratios differ.
- The barcode zone stays a solid light fill with nothing in it.
- Spine text only above the channel's page minimum, reading top to bottom.
- Two font families maximum.
