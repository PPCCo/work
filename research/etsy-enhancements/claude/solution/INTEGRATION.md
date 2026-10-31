# Integration guide

How to drop this pack into `publish-puzzle/.claude/` and wire it in. Everything is additive; the patch list at the end is the only edit to existing files.

## 1. Pack layout (mirrors your `.claude/`)

```
.claude/
  rules/        23-kit-products … 29-licensing-and-terms          (7 files)
  standards/    kit-contract, variant-matrix-contract, listing-image-contract
  agents/       8 new agents, placed in the existing department folders
                (content/, production/, visual/, quality/)
  skills/       11 kit-* skills (one folder each, SKILL.md)
  workflows/    4 workflow specs
  scripts-spec/ Python module specs (implement under scripts/publishing_house/)
  config-additions/  JSON/schema additions as markdown (copy into config/ and schemas/)
  templates/    kit.yaml, listing-image-plan, terms-of-use, host-guide, etc.
```

Specs in `scripts-spec/`, `workflows/` and `config-additions/` are markdown by request; each contains the exact code/JSON skeleton to paste into the real `.py`, `.js` or `.json` file.

## 2. Design decisions

1. **New family `digital-kit`**, not a stretched `digital-printable`. A kit is many components × many variants; a printable is one file. `digital-printable` stays for single sheets.
2. **No new lifecycle states.** Kits reuse the existing 26 states and six gates:

   | Existing state | Kit meaning |
   |---|---|
   | `CONTENT_GENERATION` / `CONTENT_VERIFICATION` | components generated; craft desk-check, fact-check, deterministic verifiers |
   | `INTERIOR_APPROVAL` | content gate for the whole kit (author-once content, all age versions) |
   | `VISUAL_DEVELOPMENT` / `COVER_APPROVAL` | **hero + gallery listing images** (the "cover" of an Etsy listing) |
   | `LAYOUT_AND_FORMAT_BUILD` | variant matrix render (Letter/A4 × colour/ink × age × theme) |
   | `ACCESSIBILITY_VALIDATION`, `RIGHTS_CLEARANCE`, `COMPLIANCE_APPROVAL` | unchanged, plus safety + IP evidence |
   | `METADATA_AND_COMMERCIAL_PACKAGE` / `LISTING_APPROVAL` | per-SKU Etsy listing packages and Etsy preflight |
   | `PLATFORM_PACKAGING` | delivery packaging (ZIPs, start-here guide) |
3. **Author once, render many.** Content varies by *age version* and *theme* (authored/generated); page size and ink mode are render-time transforms. Never author A4 separately.
4. **One project = one kit = N SKUs.** The Standard and Expanded offers are SKUs inside one project, not separate projects, so content is shared and hashed once.
5. **Seasonality is data.** `kit.yaml` carries `season.target_date` and `season.latest_list_date`; `kit seasonal` computes slack from an *explicit* `--today` argument (core modules stay clock-free).

## 3. Implementation order

| Priority | Deliver | Why first |
|---|---|---|
| P0 | `kit_render` (spec → PDF with embedded fonts, Letter/A4, ink-friendly) and `etsy_validate` | Nothing ships without them; Etsy validator is small and catches the 21-char tag today |
| P1 | `kit` manifest + `variants` expansion + `delivery` | Defines the data model everything else reads |
| P1 | Generators: `bingo`, `schedule`, `shopping_list`, `gift_exchange` + verifiers | Deterministic, fits rule 04 |
| P2 | Agents + skills + rules | Pure markdown; can start immediately and refine against real runs |
| P2 | `listing_images` via existing compositor | Needs P0 renderer to produce page rasters |
| P3 | Fillable-field support (AcroForm) | Needed for P2 and P3 products; Canva stays a manual human step |

**Suggested pilot:** Product 01 first. It exercises every new capability (content, variants, age versions, safety, 2 SKUs). Do the Etsy validator and rules in the first hour; they are independent of rendering.

## 4. New CLI surface (`ph_cli.py kit …`)

```
kit init        --topic --occasion --season-target YYYY-MM-DD --skus-json
kit seasonal    <id> --today YYYY-MM-DD          # slack, fast-path advice
kit variants    <id>                              # expand and print the matrix
kit generate    <id> --component <id> [--seed]
kit verify      <id>                              # code verifiers + desk-check evidence present
kit render      <id> [--variant <key>|--all]
kit images      <id>                              # listing image plan → composites
kit listing     <id> --sku <sku>                  # etsy-listing-<sku>.json
kit deliver     <id> --sku <sku>                  # zips + start-here guide + size budget
kit preflight   <id> --channel etsy               # limits, claims-vs-counts, licence, images
```

All verbs are offline, write under `projects/<id>/`, and set `external_write_performed: false`.

## 5. Minimal patches to existing files

| File | Change |
|---|---|
| `schemas/project.schema.json` | add `digital-kit` to `book_type` and `product_type` enums; add optional `kit`, `season` objects; add `family-mixed`, `workplace-adult` to `audience` enum (or keep enum and carry `audience_versions` in `kit`) |
| `schemas/pipeline.schema.json`, `schemas/series.schema.json` | add `digital-kit` to the family enums |
| `scripts/publishing_house/cli.py` | add `digital-kit` to `PRODUCT_TYPES`; register the `kit` subparser |
| `scripts/publishing_house/research.py` (`_PRODUCT_TYPES`), `series.py` (family tuple) | add `digital-kit` |
| `scripts/publishing_house/niche.py` | add `digital-kit` to `_FAMILY_SATURATION` (suggest 0.80 for generic Christmas, scored per-niche by the new seasonal skill) and `_FAMILY_DIFFERENTIATORS` |
| `config/design_policy.json` | add `book_type_overrides["digital-kit"]` (see config-additions) |
| `config/platforms/etsy.json` | add the `limits` block and `required_outputs` per SKU (see config-additions) |
| `config/workflow_states.json` + `state_playbook.json` | make `VISUAL_DEVELOPMENT` apply to `digital-kit` (listing images); resolve G13 first by dry-run |
| `rules/10-digital-printables.md` | amend: "do not mix page sizes in a bundle" → "…in one PDF; a download may contain per-size PDFs" |
| `rules/16-platform-etsy-gumroad.md` | add: tag ≤ 20 chars, title ≤ 140, per-SKU listings (or point to rule 26) |
| `scripts/publishing_house/packages.py::package_etsy` | call `etsy_validate`; stop slicing tags silently; emit one listing per SKU; read licence tier |
| `scripts/publishing_house/metadata_audit.py` | title ≤ 140 for Etsy; tag char limit |
| `agents/CATALOG.md`, `agents/README.md` | append AGT-035…042 (rows in `config-additions/CATALOG-additions.md`); update the "31 agents" count to 39. Keep the additions file **outside** `agents/`: `validation.py` treats every other `.md` under `agents/` as an agent and requires frontmatter |
| `scripts/publishing_house/validation.py` | no change: the new agents/skills follow the existing frontmatter contract |

## 6. Tests to add (rule 18)

- `test_etsy_validate.py`: 21-char tag fails; 13 tags pass; duplicate tags fail; title 141 chars fails; image count 11 fails.
- `test_variants.py`: matrix size, deterministic key ordering, per-variant file naming.
- `test_bingo.py`, `test_gift_exchange.py`: same seed → identical output; bingo cards pairwise-distinct; no self-assignment or couple-exclusion violations; every assignment solvable.
- `test_render_fit.py`: fillable field fits the longest sample name at declared font size; Letter/A4 safe margins ≥ 0.25 in; fonts embedded; ink-friendly has no full-bleed fills.
- `test_delivery.py`: ≤ 5 files per SKU; each ≤ 20 MB; checksums match `bundle_index.json`.
- `test_seasonal.py`: slack math with explicit dates; negative slack escalates.

## 7. First dry-run checklist (do this before trusting the pack)

1. `ph_cli.py framework validate` after copying the pack (checks frontmatter of new agents/skills).
2. Create a `digital-kit` project and walk `project plan` through every state with a stub PDF; confirm the `VISUAL_DEVELOPMENT`/cover-proof behaviour (gap G13).
3. Confirm whether `layout.py` embeds fonts (gap G14) before relying on rule 10.
4. Verify Etsy limits and category taxonomy against current Etsy documentation with a recorded date, then update `etsy.json`.
