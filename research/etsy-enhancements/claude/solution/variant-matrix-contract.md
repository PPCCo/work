# STD-VARIANT-MATRIX: variant axes, keys, transforms, checks

Applies to `kit variants`, `kit render`, `kit verify`, and `kit deliver`.

## 1. Axes

| Axis | Values (defaults) | Nature |
|---|---|---|
| `age_version` | from `kit.yaml` `audience_versions[].id` | content (authored/generated) |
| `theme` | from `themes[].id` | content or style tokens |
| `page_size` | `us-letter`, `a4` | render transform |
| `ink_mode` | `full-colour`, `ink-friendly` | render transform |

Axis value order is the order declared in `kit.yaml`; expansion is the cartesian product in that order (age_version → theme → page_size → ink_mode). Output order is deterministic and identical across runs.

## 2. Keys and filenames

- Variant key: `<sku>.<age_version>.<theme>.<page_size>.<ink_mode>`, lowercase, e.g. `std.ages-4-7.neutral.us-letter.ink-friendly`.
- File name: `<kit-slug>_<age_version>_<theme>_<page_size>_<ink_mode>.pdf`. Use `default` for a single theme. No spaces, no uppercase, ≤ 80 characters.
- Each variant has a registered artifact id, SHA-256, page count, and a row in `bundle_index.json`.

## 3. Mixed-age rule

A "mixed-age" version SHALL be built by **most-restrictive-wins** across its included bands: largest body type size, highest-contrast requirement, strictest safety tagging (no task disallowed for the youngest band unless assigned to an adult explicitly), and shortest instruction length. The rule is deterministic and recorded in the verification report. It is not a new band.

## 4. Render transforms

**Page size.** Render from layout specs with page-size-aware geometry; never scale-to-fit a Letter page into A4 or the reverse.

- Letter: 8.5 × 11 in (215.9 × 279.4 mm). A4: 210 × 297 mm (8.27 × 11.69 in).
- Safe margin ≥ 0.25 in (6 mm) on every side (rule 10).
- Grid-based components (gift tags, cut-out cards) are re-laid per size; the **item count is invariant** and page count may differ. Listing copy states item counts, not page counts, unless it states both sizes.
- Text SHALL reflow, not shrink, below the audience minimum type size (`accessibility.py` minimums).

**Ink mode.**

- `full-colour`: the design as approved.
- `ink-friendly`: same layout and text; remove full-bleed or large background fills; replace filled shapes with outlines or ≤ 10% tints; render body text in black or near-black; convert photographic or painted art to line art or a light tint; keep contrast ≥ 4.5:1 for body text (7:1 for `kids-4-8` and large-print bands).
- Ink-friendly SHALL pass `ink_coverage_pct ≤ 15` per page (rasterise at 100 DPI; coverage = fraction of non-white pixels). Configurable in `design_policy.json`; a page over budget fails the variant.

## 5. Checks per variant (all by code)

1. Page size matches the declared axis value for every page.
2. Margins and cut-guides within the safe area.
3. Fonts embedded; fonts cleared in the rights ledger.
4. Raster assets ≥ 300 DPI at final size.
5. Fillable fields fit the stress list (rule 27).
6. Ink-friendly coverage within budget.
7. Item counts equal the verified counts for the SKU.
8. Answer keys sit in a back-only section or separate file (rule 04/05); never adjacent to the item.
9. Accessibility: alt text or decorative designation for every image; contrast measured.

A variant failure names the variant key, page, and check, so a repair targets only that variant.

## 6. Scale controls

- Cap of 24 PDFs per SKU by default (rule 23).
- Build variants in parallel (workflow `kit-variant-build-batch`); a verification pass reads every variant independently.
- Build is idempotent: an unchanged `(source hashes, variant key, renderer version)` skips and reuses the prior artifact.
