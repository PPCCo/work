---
paths:
  - "projects/**/outputs/kit/**"
  - "projects/**/outputs/packages/**"
  - "projects/**/kit/**"
---

# Licensing and terms of use

Kits are licensed to buyers, not sold as ownership. Licence text is a product feature and a compliance artifact.

- Each SKU SHALL declare one `licence_tier` in `kit.yaml`:
  - `personal`: printing and use by the buyer's household; no resale, redistribution, or sharing of files.
  - `classroom`: personal plus use with one teacher's own students in a single classroom or small group; no sharing across a school or district; no resale.
  - `commercial`: **not offered by default.** Requires a human decision, an extended-use rights review (all assets and fonts cleared for it), and a separate SKU.
- The "family-and-classroom bundle" pattern SHALL be `classroom` tier and SHALL state the permitted group scope plainly.
- A `Terms-of-Use` PDF SHALL be generated from `templates/terms-of-use.md` and included in every SKU. It restates the tier, prohibited uses (resale, redistribution, claiming as own, uploading to file-sharing sites, AI-training use), editable-file rules (rule 27), and refund/support contact placeholders to be filled by the human.
- The framework drafts terms but is **not counsel and does not accept legal terms** (rule 11, rule 12). A human approves the text at the `compliance` gate.
- Etsy's current digital-goods policies, and buyer-facing refund practice, are time-sensitive; the human confirms them at the listing gate (rule 26).
- Licences for embedded assets SHALL be compatible with the chosen tier. A single personal-use-only asset forces the SKU to `personal` or blocks release (rule 12). OFL fonts in the repo may be embedded in PDFs; record attribution as the OFL requires.
- The licence tier SHALL appear identically in `etsy-listing-<sku>.json`, the description, and the `Terms-of-Use` PDF. A mismatch is a blocker.
- `package_etsy` SHALL read the tier from `kit.yaml` instead of using a hard-coded licence string.
