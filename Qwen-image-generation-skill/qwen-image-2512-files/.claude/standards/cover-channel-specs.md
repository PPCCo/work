# Standard: cover channel specifications

Numbers live in `.claude/assets/cover_channel_specs.json` so scripts and prose
cannot drift apart. This file explains how to use them and what each channel
expects as a deliverable.

**Verification rule.** Retailer specs change without notice. The JSON records the
month it was last verified against public documentation. Before any release
batch, re-check the numbers against the channel's own documentation, and for any
KDP print cover generate KDP's template for that exact trim, page count and paper
and confirm the full-wrap width matches `cover_spec.py`. The calculation exists
so a cover can be designed before the template is pulled — not so the template
can be skipped.

---

## Print wrap (KDP paperback and hardcover)

One file containing back cover, spine and front cover, left to right, with bleed
on all four outer edges.

- Full wrap width = bleed + trim width + spine + trim width + bleed
- Full wrap height = bleed + trim height + bleed
- Spine width = page count × paper thickness (white 0.002252, cream 0.0025,
  colour 0.002347), plus any binding allowance for the format
- Bleed 0.125 in; safe margin 0.25 in inside trim; 300 DPI minimum
- Hardcover adds 0.625 in wrap on all outer edges and 0.375 in hinge each side of
  the spine, and important elements stay 0.625 in clear of the spine
- Spine text only at 79 pages or more
- Barcode zone 2 × 1.2 in, lower right of the back cover, solid light fill
- PDF preferred; CMYK preferred, RGB accepted; fonts embedded or outlined

Sources disagree on whether the paperback spine includes a ~0.06 in cover-stock
allowance. The default is no allowance. If KDP's template comes out wider, rerun
`cover_spec.py --cover-thickness 0.06` and re-export.

## Ebook covers

| Channel | Size | Format | Notes |
|---|---|---|---|
| Amazon KDP / Kindle | 1600 × 2560 px, 1:1.6 | JPEG or TIFF, sRGB, under 50 MB | at least 1000 px on the long edge; front only |
| Apple Books | at least 1400 px on the short edge; 1600 × 2560 recommended | JPEG or PNG, RGB | never upscale a smaller image to reach the minimum — blurry art is rejected; a separate in-book cover image is also required |

The ebook cover is composed independently rather than cropped from the print
front: the aspect ratios differ, and a scaled print front crops the type badly.
`cover_compose.py` builds it as its own layout.

## Marketplace listing images

| Channel | Primary image | Notes |
|---|---|---|
| eBay | ~1600 × 1600, square | show the physical product; for a digital download show the cover plus an interior preview |
| Etsy | ~2000 × 2000, 1:1 | listing image 1 is the cover; images 2–10 must show interior pages, what is included, and the print size — Etsy buyers are buying a printable, not a book |

For both, produce flat mockups from `front_only.png`. Never present a mockup as
a photograph of a product that does not exist in that form.

## Audiobook

3000 × 3000 px, square, RGB JPEG. Composed from scratch with a square-safe
composition — cropping a portrait cover to square is always visibly wrong.

## Deliverable set per book

Produced into `visuals/cover/` and registered as artefacts:

```
spec.json              geometry, from cover_spec.py
guides.svg             trim/bleed/safe/barcode guides
art-plan.json          prompts, seeds, params, upscale plan
art/front.png          upscaled hero art
art/back.png           upscaled back art
wrap.pdf               print wrap, 300 DPI          -> kdp-print
wrap.png               raster equivalent
ebook.jpg              1600 x 2560                  -> kdp-ebook, apple-books
front_only.png         front face at print res      -> mockups, listings
wrap.svg               editable master
layout-report.json     measured type, contrast, violations
thumbs/                80/120/240 px, greyscale, squint
preflight.json         channel checks
```
