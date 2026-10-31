---
paths:
  - "projects/**/kit/**"
  - "projects/**/content/kit/**"
  - "projects/**/outputs/kit/**"
---

# Digital-kit products

A **kit** is a multi-component, multi-variant digital download sold as one or more SKUs. Product family key: `digital-kit`. Canonical plan: `projects/<id>/kit/kit.yaml` (standard: STD-KIT-CONTRACT).

## Structure

- Every kit SHALL declare, in `kit.yaml`: positioning (promise, buyer, occasion), season window, components (type, count, generator or author agent, verifier), variant axes, SKUs (offer ladder), delivery strategy, licence tier, and the listing image plan.
- Every component SHALL have a registered type from the component catalogue (`config/kit_components.json`) and a verification route: code verifier, desk-check evidence, or fact-check evidence. A component with no verification route SHALL NOT enter the interior gate.
- Counts in positioning, listing copy, and images ("12 craft cards") SHALL equal the verified counts in the content-verification report. A mismatch is a blocker.

## Variants

- **Author once, render many.** Content differs by `age_version` and `theme` (authored or generated). `page_size` (US Letter, A4) and `ink_mode` (full-colour, ink-friendly) are render-time transforms of the same content and SHALL NOT be authored separately.
- The variant matrix SHALL be expanded by code (`kit variants`) in deterministic key order. Every variant is built, hashed, and verified; a failing variant fails its SKU.
- A single PDF SHALL use one page size. A download MAY contain per-size PDFs (this amends rule 10's bundle wording).
- Default cap: 24 PDFs per SKU. Exceeding it requires a recorded reason in `kit.yaml`.
- Age versions SHALL differ in substance (task difficulty, reading level, safety-controlled materials, instruction length), not only in labels. "Genuine age differentiation" is a stated differentiator and SHALL be evidenced in the verification report.

## SKUs and offers

- Each SKU has its own `includes` list, price recommendation, and listing package. Prices are RECOMMENDATIONS until a human sets them at upload.
- The Expanded SKU SHALL be a strict superset of Standard (same component ids plus extras), so shared content is generated and hashed once.
- Default is one Etsy listing per SKU. A variation-based listing requires current Etsy evidence that variations can carry distinct files (see rule 26).

## Delivery

- Each SKU SHALL include `Start-Here` (usage, printing tips, what's included) and `Terms-of-Use` PDFs.
- Every download SHALL ship a `bundle_index.json` per rule 10, extended with variant keys.

## Boundaries

- Kits follow rules 00–22. Where this rule is stricter it wins for `digital-kit`; it never relaxes a human gate.
