---
paths:
  - "projects/**/outputs/packages/etsy/**"
  - "projects/**/marketing/**"
  - "projects/**/kit/listing/**"
---

# Etsy listing integrity

Extends rule 16. Etsy limits are time-sensitive: record them in `config/platforms/etsy.json` under `limits` with `verified_on` and `source_url`, and recheck before the `listing` gate. The values below are the working defaults; **`verify_before_release` stays true**.

## Hard limits (validated by `etsy_validate`)

- Title SHALL be ≤ 140 characters. Titles read naturally: no keyword chains, no repeated phrases, no all-caps stuffing.
- Tags SHALL number ≤ 13. **Each tag SHALL be ≤ 20 characters** (count characters, not words). No duplicates (case-insensitive). No trademarked terms, competitor names, or licensed characters.
- Images SHALL number ≤ 10. Image 1 is the thumbnail and SHALL be legible at small size.
- A digital listing's downloadable files SHALL be ≤ 5 files, each ≤ 20 MB (see STD-KIT-CONTRACT delivery strategies). Hosting-by-link strategies need current Etsy policy evidence and a human decision.
- Validation FAILS the SKU on any violation. Never truncate silently; rewrite the offending field and re-validate.

## Listing accuracy

- Every item shown in a listing image or named in the description SHALL be in the download. An item shown but not delivered is a blocker.
- Every number in title, copy, bullets, and images (page counts, card counts, games, versions) SHALL equal the verified count (rule 23). Variant counts ("Letter + A4") SHALL match built files.
- Listing images SHALL be built from **real rendered pages** (rasterised from the built PDFs and placed by the compositor) with text set in cleared fonts. Do not use generated pictures of pages or of products that do not exist.
- Images of "finished crafts" SHALL come from physically made items or be clearly styled as illustrations. If the craft was not make-tested, SHALL NOT present it as a photo of a result.
- Disclose AI-assisted imagery and content in the listing wherever current Etsy creativity standards require it; recheck the standard at each listing gate (rule 12, rule 13). AI disclosure text SHALL be consistent across metadata, description, and image notes.
- SHALL state in the description: digital file, no physical item shipped, page sizes, file types, what is included per SKU, printing guidance, and licence summary.
- Category paths SHALL be recorded as `{path, verified_on}`. An unverified category is a WARNING that blocks the listing gate until a human confirms.

## Offers and pricing

- One listing per SKU by default. Use variations only if current Etsy behaviour lets each variation deliver different files; otherwise Standard and Expanded files would leak into each other.
- Price is a recommendation (`pricing-strategist`); the human sets it at upload. Bundle discounts SHALL be arithmetically true relative to the Standard SKU.

## Conduct

- No review manipulation, fake scarcity, fabricated "bestseller" or "tested by families" claims (rules 14, 21).
- No external write: the framework prepares the package; a human uploads and records platform evidence (rule 16).
