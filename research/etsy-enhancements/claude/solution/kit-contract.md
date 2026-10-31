# STD-KIT-CONTRACT: digital-kit manifest, components, SKUs, delivery

Applies to every `digital-kit` project. Schema: `kit.schema.json` (see `config-additions/SCHEMAS.md`). Template: `templates/kit.yaml`.

## 1. Manifest (`projects/<id>/kit/kit.yaml`)

The manifest is canonical for kit structure the way `project.yaml` is canonical for the product. It is registered as an artifact; approvals bind to its hash. Required top-level keys:

| Key | Content |
|---|---|
| `schema_version`, `kit_id`, `project_id` | identifiers (`kit_id` = project id) |
| `positioning` | `promise` (one sentence), `buyer`, `occasion`, `differentiators[]` (each tied to evidence), `competitor_gap` |
| `season` | `occasion`, `target_date`, `latest_list_date`, `evidence_refs[]` (rule 24) |
| `audience_versions[]` | `{id, band[], min_age, max_age, label}`; every entry in `band` SHALL exist in `age_bands.json`; more than one band means mixed-age (most-restrictive-wins) |
| `themes[]` | `{id, label}` (e.g. dog, cat, neutral, minimalist); may be a single `default` |
| `components[]` | see §2 |
| `skus[]` | see §3 |
| `variant_axes` | `page_size`, `ink_mode`, `age_version`, `theme` value lists in render order (STD-VARIANT-MATRIX) |
| `delivery` | see §4 |
| `listing` | `title_candidates[]`, `tag_candidates[]`, `category_candidate {path, verified_on}`, `image_plan_ref` |
| `validation` | `angle`, `hypothesis`, `test_plan_ref` (human-run experiment; framework does not run ads) |

## 2. Components

Each component entry: `{id, type, count, per_age_version, per_theme, authored_by, verifier, editable, hazards[], notes}`.

- `type` SHALL exist in `config/kit_components.json`.
- `authored_by`: a generator key (`bingo`, `schedule`, …) or an agent id (`craft-designer`, `party-game-designer`, `keepsake-designer`).
- `verifier`: `code` (deterministic verifier), `desk-check` (craft/safety), or `fact-check` (trivia). Exactly one primary route; more may be added.
- `count` is the number of **items** (cards, tags, games), not pages. Page counts vary by page size and are recorded per variant.
- `per_age_version: true` means the component is authored once per age version. Otherwise it is shared.
- `editable: true` requires a field spec (rule 27).

## 3. SKUs (offer ladder)

`{sku_id, name, includes[], licence_tier, price_recommendation {amount, currency, basis}, listing_overrides}`.

- `includes` lists component ids; `"*"` means all. An Expanded SKU SHALL include every Standard component id (superset rule).
- `licence_tier` ∈ `personal | classroom | commercial` (rule 29).
- `price_recommendation.basis` cites the evidence or comparison used; absent evidence the field says `human-to-set`.

## 4. Delivery strategies

Etsy digital-listing limits (default 5 files, 20 MB each; verify) force an explicit strategy. Every SKU SHALL declare one.

| Strategy | When | Output |
|---|---|---|
| `zip-by-axis` (default) | variants exceed what one ZIP can hold | `Start-Here.pdf` + one ZIP per value of `split_axis` (default `age_version`); total files ≤ 5, each ≤ 20 MB |
| `single-zip` | few variants, small size | `Start-Here.pdf` + one ZIP |
| `hosted-links` | ZIPs cannot fit the size cap at ≥ 300 DPI | `Start-Here.pdf` carrying human-hosted download links; requires current Etsy policy evidence and an explicit human decision; the framework never uploads or hosts |

- `kit deliver` computes a size budget before building ZIPs and reports which strategy fits. It SHALL NOT downsample print art below 300 DPI to fit (rule 10); the fallback is a different strategy.
- Every download includes `Terms-of-Use.pdf` and `bundle_index.json` (rule 10 plus `variant_key`).

## 5. Verification report (kit)

`verification/content-verification-latest.json` for a kit SHALL additionally contain, per component: `verified_count`, `verification_route`, `status`, and evidence ids; per age version: a differentiation record (what differs: difficulty, reading level, materials, safety). The interior gate reads this report; listing copy and images read the counts from it.

## 6. Provenance

All kit artifacts record: component id, age version, theme, generator/agent, seed (if any), source artifact hashes, and rights status (rule 03). Rendered variants are downstream build outputs (rule 03): re-rendering from unchanged approved source does not invalidate approvals.
