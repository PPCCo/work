---
name: book-cover-brief
description: Produce the cover brief and the exact cover geometry for a book project - trim, spine, bleed, safe areas, barcode zone, channel targets, audience art direction and back-cover copy. Use this at the start of any cover work, whenever a book reaches VISUAL_DEVELOPMENT, whenever someone asks for a cover, a front cover, a back cover or a spine, and whenever page count, trim size or paper type changes, because all three change the wrap.
---

# /book-cover-brief

First step of cover production. Produces a brief that the art, typography and
review steps all read, so the geometry is calculated exactly once.

## Inputs

From `project.yaml`: `audience`, `book_type`, `formats`, working title, series
membership. From the built or planned interior: **final page count**, trim size,
paper type, binding. From the series record, if any: the locked look.

If the page count is not final, say so and mark the spec provisional. A cover
built on a provisional page count will be rebuilt.

## Steps

**1. Geometry.**

```bash
python .claude/scripts/cover/cover_spec.py \
  --trim 8.5x11 --pages 108 --paper white \
  --binding paperback --audience early-reader-6-8 --book-type coloring-book \
  --title "<working title>" \
  --out projects/<id>/visuals/cover/spec.json \
  --guides projects/<id>/visuals/cover/guides.svg
```

Repeat the warnings in your summary. The spine-text warning in particular is a
design decision, not noise.

**2. Art direction.** Delegate to `cover-art-director`, or follow
`.claude/standards/cover-audience-standard.md` directly: pick the style pack,
palette, type zone and hero idea, and produce three distinct concepts with the
risk of each named.

**3. Copy.** Delegate to `cover-copywriter` for the back-cover headline, blurb,
bullets and the listing fields. Every number comes from the interior.

**4. Channel list.** From `formats` and the sales channels, list the deliverables
needed - print wrap, ebook cover, Etsy or eBay listing images, audiobook square.
See `.claude/standards/cover-channel-specs.md`.

**5. Write the brief** to `visuals/cover/cover-brief.md` from
`.claude/templates/cover-brief.template.yaml`, register it as an artefact, and
recommend the next transition. Do not approve a gate.

## Rules

- The cover brief is the only place cover geometry is calculated. Nothing
  downstream retypes a spine width.
- Before a final print export, generate the channel's own template for this
  trim, page count and paper and confirm the wrap width matches.
- Audience comes from `project.yaml`, never from the topic.
