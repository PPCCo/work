# Installing the Etsy digital-products extension

This package has two kinds of files. Keep them straight and the install is simple.

| Kind | Where | How to use |
|---|---|---|
| **Drop-in** | `.claude/rules/`, `.claude/standards/`, `.claude/agents/`, `.claude/skills/` | Copy into the repo's `.claude/` folder. They are ordinary framework files in the framework's own format. |
| **Specs** | `specs/` | **Not drop-in.** Workflow code, Python module specs, schema/config changes and templates. Each section starts with `Target path:`. Implement or paste them with Claude Code (prompts below). |

Gap IDs (`G1`–`G15`) refer to `EVALUATION.md`.

## 1. File map

### Drop-in

| File (under `.claude/`) | What it does | Closes |
|---|---|---|
| `rules/23-etsy-digital-products.md` | Etsy listing law: title/tag limits, AI disclosure, designed-by-seller, manual upload only | G4 |
| `rules/24-kit-and-bundle-products.md` | Kit structure, components, variants, offers, count integrity | G2 |
| `rules/25-craft-party-pet-safety.md` | Craft, party, pet and workplace safety | G9 |
| `rules/26-personalization-and-editable.md` | Personalisation fields, fillable PDFs, Canva template-link path | G7 |
| `rules/27-seasonal-launch.md` | Seasonal calendar, list-by dates, freshness | G11 |
| `rules/28-buyer-license-and-delivery.md` | Licence tiers, delivery pack, how-to-print | G10 |
| `rules/29-listing-imagery.md` | Listing image set, mockups, honest representation | G3 |
| `rules/30-print-at-home-qa.md` | Ink, cut lines, fit, overflow, Letter/A4 checks | G13 |
| `standards/kit-product-contract.md` | `STD-KIT`: kit spec, variant matrix, file naming | G2 |
| `standards/etsy-listing-contract.md` | `STD-ETSY`: listing package, SEO title, tags, images | G4 |
| `standards/buyer-license-contract.md` | `STD-LICENSE`: licence tiers and wording rules | G10 |
| `agents/content/kit-architect.md` | AGT-035: brief → kit spec | G2 |
| `agents/content/craft-instruction-writer.md` | AGT-036: step cards, materials, age adaptation | G5, G6 |
| `agents/content/game-designer.md` | AGT-037: party games, bingo, trivia, answer keys | G5 |
| `agents/content/personalization-designer.md` | AGT-038: keepsakes, fields, editable variants | G5, G7 |
| `agents/visual/listing-imagery-designer.md` | AGT-039: cover, listing image set, mockup composites | G3 |
| `agents/commercial/etsy-listing-strategist.md` | AGT-040: SEO title, tags, category, validation plan | G4 |
| `agents/quality/print-readiness-tester.md` | AGT-041: print test, ink, overflow, fit | G13 |
| `agents/quality/craft-safety-reviewer.md` | AGT-042: craft/party/pet safety | G9 |
| `agents/discovery/seasonal-launch-planner.md` | AGT-043: seasonal window and list-by dates | G11 |
| `skills/product-kit-spec/SKILL.md` … 13 skills | One skill per new step (see `EVALUATION.md` §5) | G1–G15 |

### Specs (implement)

| File | Contents | Closes |
|---|---|---|
| `specs/scripts-01-renderer-and-content-types.md` | Component renderer library, theme tokens, new content types and independent validators | G1, G5, G12 |
| `specs/scripts-02-kit-variants-delivery-proof.md` | Kit spec loader, variant matrix, builder, delivery pack, kit proof | G2, G10, G15 |
| `specs/scripts-03-etsy-validation-and-audits.md` | Etsy package v2, `etsy validate`, count audit, print test, listing images | G3, G4, G8, G13 |
| `specs/config-schemas-and-deltas.md` | New schemas, `etsy.json` v2, age bands, quality-gate profile, fonts, one-line code edits | G6, G8, G12 |
| `specs/config-state-machine-and-playbook.md` | Gate-report and playbook changes so a kit can move through the lifecycle | G3, G14, G15 |
| `specs/workflows.md` | Four workflow files (code) | G14 |
| `specs/templates.md` | Kit spec, variant matrix, Etsy listing, licence text, how-to-print, listing-image brief, seasonal plan, offer ladder | all |

## 2. Install order

1. **Copy the drop-in folders** into the repo's `.claude/`.
2. **Edit the existing files** listed in §3 (small, mechanical).
3. **Implement the three script specs** with Claude Code (prompt in §5). Do them in order: 01, then 02, then 03.
4. **Apply the config and state-machine specs** (`specs/config-*.md`).
5. **Create the four workflow files** from `specs/workflows.md`.
6. **Validate:** `.venv/bin/python3 .claude/scripts/ph_cli.py framework validate`, then the unit tests, then the smoke test in §6.

Skills that call new CLI commands (`kit …`, `etsy …`, `listing-images …`) will not work until step 3 is done. The agents, rules and standards work immediately.

## 3. Edits to existing files

| File | Edit |
|---|---|
| `.claude/agents/CATALOG.md` | Add rows `AGT-035` … `AGT-043` (IDs 005, 007, 011, 015, 028, 030 are retired; do not reuse them). |
| `.claude/agents/README.md` | Says "31 agents"; 28 exist today, 37 after install. Add a line for the kit-related roles. |
| `.claude/config/platforms/etsy.json` | Replace with v2 from `specs/config-schemas-and-deltas.md`. |
| `.claude/config/age_bands.json` | Add the bands/variant audiences in `specs/config-schemas-and-deltas.md`. |
| `.claude/config/quality_gates.json` | Add `profiles.kit` (critical dimensions for kits). |
| `.claude/config/workflow_states.json` | Gate-report changes in `specs/config-state-machine-and-playbook.md`. |
| `.claude/config/state_playbook.json` | Add recommended agents/skills for kit stages. |
| `.claude/config/dependencies.default.json` | Add the festive display fonts you choose (clear each under OFL before use). |
| `scripts/publishing_house/generate.py` | Add `"kit": "content/kit"` to `_FAMILY_DIR`. |
| `scripts/publishing_house/verify.py` | Add `"content/kit"` to `_CONTENT_DIRS`. |
| `scripts/publishing_house/layout.py` | Add `"content/kit"` to the folder list in `_load_batches`. |
| `scripts/publishing_house/packages.py` | `package_etsy` delegates to the v2 builder when a kit spec exists; otherwise keeps today's behaviour. |
| `scripts/publishing_house/claims.py`, `quality.py` | Kit-profile handling per `specs/scripts-03-etsy-validation-and-audits.md`. |
| `scripts/publishing_house/cli.py` | Register the new command groups (§4). |

## 4. New commands (defined in the script specs)

| Command | Purpose |
|---|---|
| `kit spec-validate <id>` | Validate `kit/kit-spec.yaml` against its schema and the standards |
| `kit variants <id>` | Expand the variant matrix and offers |
| `kit generate <id> [--component <cid>]` | Deterministically generate component content |
| `kit build <id> [--variant <vid> \| --all]` | Render component PDFs per variant |
| `kit proof <id>` | Write kit-aware `interior-proof-report.json` and `cover-proof-report.json` |
| `kit delivery <id> [--offer <oid>]` | Build the buyer delivery pack |
| `kit audit-counts <id>` | Reconcile claims with verified counts |
| `kit print-test <id>` | Print-at-home checks |
| `etsy package <id>` / `etsy validate <id>` | Etsy package v2 and its validator |
| `listing-images spec <id>` / `listing-images build <id>` | Listing image brief and composites |
| `seasonal plan <id>` / `offers plan <id>` | Dated schedule; offer ladder |

## 5. Prompts to give Claude Code in the repo

**Per script spec (run three times):**

> Read `specs/scripts-0N-….md` and `.claude/rules/18-python.md`. Implement exactly what the spec describes under `.claude/scripts/publishing_house/`, register the CLI commands in `cli.py`, add unittest coverage listed in the spec's "Acceptance tests", and keep every module offline and deterministic. Do not change gate logic, approvals, or state transitions other than what `specs/config-state-machine-and-playbook.md` specifies. Show me the diff summary and test results.

**For the config and state-machine specs:**

> Apply `specs/config-schemas-and-deltas.md` and `specs/config-state-machine-and-playbook.md`. Validate every JSON file against its schema, run `ph_cli.py framework validate`, and tell me about any duplicate agent or skill names.

## 6. Smoke test (before real products)

1. Create a throwaway project: `ph_cli.py project init --topic "smoke test kit" --audience kids-6-10 --product-type digital-printable --formats digital-pdf --project-id kit-smoke-test`.
2. Copy `specs/templates.md` § Kit spec into `projects/kit-smoke-test/kit/kit-spec.yaml` with two components (one instruction card, one cut sheet) and two variants (Letter, A4).
3. Run `kit spec-validate`, `kit variants`, `kit generate`, `kit build --all`, `kit proof`, `kit print-test`, `kit delivery`, `etsy package`, `etsy validate`.
4. Confirm the project can walk the lifecycle to `PLATFORM_PACKAGING` with no placeholder pages in any PDF.

## 7. Things this package deliberately does not do

- It does not create products, listings, Canva designs or accounts, and it never publishes. Etsy upload stays manual after the release gate.
- It does not weaken any gate or approval.
- Platform limits it could not verify (image count, file count/size, category names, required attributes) are stored as `unverified` and must be checked with a dated source before the listing gate.
