# STD-LISTING-IMAGES: Etsy listing image plan and proof

For Etsy kits the "cover" is the gallery. This standard defines the image plan, truth rules, and proof that stand in for the cover gate (see `INTEGRATION.md`: `kit images` writes `outputs/proof/cover-proof-report.json` so existing gate config applies unchanged).

## 1. Image plan (`kit/listing/image-plan-<sku>.yaml`)

Max 10 images per listing (rule 26); recommended 7–10. Default role order:

| # | Role | Content |
|---|---|---|
| 1 | `hero` | Headline with exact verified counts, 2–4 real rendered pages arranged, one clear promise. Must read at thumbnail size |
| 2 | `whats-included` | Grid or list of components with counts |
| 3–5 | `sample-pages` | Close-ups of real pages (e.g. a craft card, gift tags, host checklist) |
| 6 | `versions-and-sizes` | Age versions, Letter + A4, full-colour + ink-friendly |
| 7 | `how-it-works` | Buy → download → print → use (instant download; no physical item) |
| 8 | `personalise` | Only if editable/fillable: show a filled sample with a fictional name |
| 9 | `licence-and-support` | Plain licence summary (personal/classroom) |
| 10 | `faq-printing` | Printing tips, paper suggestions, scale reminder |

Standard and Expanded SKUs get separate plans; the Expanded plan SHALL show only items its SKU includes.

## 2. Spec per image

`{image_id, role, size_px, background, elements[], alt_text, headline_text}`; each element is `{kind: page-raster | text | shape | icon | scene, source_artifact_id, page, box, transform}`. Compose with `compositor.compose` (deterministic; absolute integer geometry; cleared fonts).

Defaults (verify against current Etsy guidance, record `verified_on`): 4:3 landscape, 3000 × 2400 px, sRGB, JPEG or PNG.

## 3. Truth rules

1. Every `page-raster` element references a built variant page by artifact id and page; rasterise at ≥ 150 DPI before placement.
2. No element depicts a deliverable that is not in the SKU. Decorative `scene` elements (table, props) SHALL NOT show extra printables, extra crafts, or extra pages.
3. Counts in `headline_text` and text elements come from the verification report, not from the plan.
4. "Finished craft" visuals follow rule 26: physical photo, or labelled illustration; never a pretend photo of an untested craft.
5. Scene or illustration elements produced by an image-generation provider SHALL use a provider with `commercial_rights_verified: true` in `tools.default.json`, carry a rights record, and appear in the AI-disclosure.
6. Fictional names in samples (pet name, host name) SHALL be invented, not real people or pets.
7. No logos or marks of Etsy, Canva, or other platforms implying endorsement.

## 4. Legibility and accessibility

- **Thumbnail test:** downscale each image to 340 × 272 px; the hero headline SHALL remain ≥ 14 px tall (cap height) and pass contrast ≥ 4.5:1 (use the compositor's `_contrast_ratio`).
- Safe zone: no essential text within 4% of any edge (marketplace crops differ).
- `alt_text` recorded for every image; describes content, not keywords.

## 5. Proof report

`kit images` writes `outputs/proof/cover-proof-report.json` with `{kind: "listing-images", sku, decision: PASS|FAIL, checks: {thumbnail_legibility, counts_match, elements_in_sku, alt_text_present, rights_cleared, size_ok}, issues[]}`. The `cover` gate packet presents this report and the contact sheet of all images. Craft/quality gates may auto-approve under policy only when `decision = PASS` and no open blocker/major finding exists (rule 02).
