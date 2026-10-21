---
paths:
  - "projects/**/content/etsy/**"
  - "projects/**/metadata/**"
  - "projects/**/marketing/**"
  - "projects/**/outputs/**"
---
# Rule — Etsy Digital Products

When working on an Etsy-targeted digital product, apply the active versions of:

- `.claude/standards/etsy-digital-product-standard.md`
- `.claude/standards/etsy-listing-standard.md`
- `.claude/standards/etsy-release-gate-standard.md`

Treat the project component matrix and delivery manifest as the source of truth for all public claims. Never advertise a count, variant, editable feature, access method, or format unless the exact deliverable is present and checked. Distinguish instant-download from made-to-order fulfillment. Refresh Etsy requirements from current official sources before release and record the review date. Use existing specialist agents and lifecycle gates; never self-approve, freeze, release-authorize, publish, or upload to Etsy. If the deterministic Etsy validator is not implemented or does not pass, report that explicitly—do not infer a pass from manual inspection.
