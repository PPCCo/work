# Evaluation: can the `publish-puzzle` `.claude/` framework build your Etsy digital and printable products?

**Date:** 2026-10-22 · **Repo commit read:** `a02167610b4ae2756cc313f524a91c459d50f330` · **Scope:** `.claude/` only (as instructed)

## 1. Verdict

**Enhance it. The framework is not sufficient as-is, but it is a strong base.**

- **Reusable as-is (the hard-to-build part):** the 26-state lifecycle with six gates, hash-bound approvals, rights ledger with font and image-provider clearance, artifact provenance, "generate by code, verify by code" pattern, discovery agents, commercial writer, pricing strategist, child-safety review, accessibility gate, offline Etsy package stub, and fan-out workflows.
- **Not sufficient (the product-specific part):** the framework is built around *one project = one book interior*. Your Etsy products are *multi-component kits* sold in *variants* (Letter/A4, colour/ink-friendly, age tiers, pet types) and *offers* (Basic/Expanded). The page renderer, the content types, the Etsy package, the listing imagery, and the quality/claims checks do not cover that.
- **Do not change:** the gates, the "no autonomous publishing" rule, or the exact-hash approvals. Everything proposed here keeps them intact.

## 2. What I found (evidence)

All paths are under `.claude/`. Severity: **Blocker** = a product in your examples cannot be built without it; **Major** = built but unsafe or misleading to ship; **Minor** = friction.

| ID | Gap | Evidence | Severity |
|---|---|---|---|
| G1 | **No real renderer for kit content.** Only sudoku grids and coloring images are drawn; every other content type becomes a placeholder page reading "Type #n / Difficulty". The `printable` generator emits page geometry plus a random quote. | `scripts/publishing_house/layout.py` (`build_interior`: sudoku branch, coloring branch, else `_draw_placeholder_page`); `generators/printable.py` | **Blocker** |
| G2 | **No kit/variant/offer model.** One project builds one `interior.pdf`; `link_digital_bundle` copies it to `printable.pdf`; the Etsy package ships that single file. Nothing models 12 cards + 6 projects + tags, size variants, colour variants, age tiers, or Basic vs Expanded offers. | `layout.py` (`link_digital_bundle`), `packages.py` (`_digital_files`, `package_etsy`), `templates/printable-spec.json` (single `page_size`, flat `file_list`) | **Blocker** |
| G3 | **No listing-image stage, and the cover stage cannot be passed by a digital kit.** `workflow_states.json` marks `VISUAL_DEVELOPMENT` as conditional for paperback/hardcover/coloring-book, but no code reads `conditional_stages`; the only forward edges are `INTERIOR_APPROVAL → VISUAL_DEVELOPMENT → COVER_APPROVAL`, and the cover edge needs a PASS `cover-proof-report.json`, which `build_proof` only awards when a print cover spec with a spine width exists. A digital kit therefore either stalls or gets a meaningless print wrap. Rule 16 also requires up to 10 mockup images; nothing produces them. | `config/workflow_states.json` (`conditional_stages`, `gate_reports`), `config/state_playbook.json`, `scripts/publishing_house/planner.py`, `layout.py` (`build_proof`), `rules/16-platform-etsy-gumroad.md` | **Blocker** |
| G4 | **Etsy package is a stub.** Tags are `keywords[:13]` with no per-tag length check; no title-length check; no category, attributes, file list, image list, licence or how-to-print. `marketing listing` derives at most 7 keywords from topic/family/audience. `platforms/etsy.json` only requires one PDF. | `packages.py` (`package_etsy`), `marketing.py` (`build_listing_kit`), `config/platforms/etsy.json` | **Major** (see §3: your Product 03 has a 21-character tag that this code would pass) |
| G5 | **Missing content types.** Only puzzles, activities, journal/tracker/calendar, coloring and one generic printable exist. No craft cards, certificates, keepsake pages, invitations, forms, sign-up sheets, bingo, trivia, charades, gift-tag/cut sheets, ornament templates, prop signs. Generated batches are read from four hard-coded folders. | `generators/*.py`, `generate.py` (`_FAMILY_DIR`), `verify.py` (`_CONTENT_DIRS`), `layout.py` (`_load_batches`) | **Blocker** |
| G6 | **Audience model cannot express "ages 4–7, 8–12, teens, mixed-age families" or "workplace".** Six fixed bands; no 4–7; no mixed-age; no per-variant audience. Craft difficulty differences across ages are not modelled or checked. | `config/age_bands.json`, `schemas/project.schema.json` (`audience` enum) | **Major** |
| G7 | **No editable or personalised output.** No fillable (AcroForm) PDFs, no personalisation-field spec. Canva delivery (needed by Product 02/03) is human-only and has licensing limits (see §6). | no match in `.claude/` for AcroForm; `Canva` appears only as passing mentions | **Major** |
| G8 | **Quality gate and claims audit are puzzle-centric.** At final states the quality gate requires scores for `solvability` and `solution_correctness`; a kit with no solutions will sit at `INCOMPLETE` unless reviewers invent scores. The claims audit matches `"\d+ puzzles"` and the cover builder hard-codes puzzle labels, so "12 Crafts" or "8 Games" claims are never reconciled with verified counts. | `config/quality_gates.json`, `scripts/publishing_house/quality.py`, `claims.py` (`_COUNT_RE`, `_cover_claim_strings`) | **Major** |
| G9 | **Craft, party and pet safety is not standardised.** Rule 06 covers scissors/heat for child bands only. Nothing covers adhesives, small parts, allergens in craft materials, pet-unsafe items, alcohol or adult themes in party games, or workplace-appropriateness. | `rules/06-child-content.md`, `agents/quality/child-safety-reviewer.md` | **Major** |
| G10 | **No buyer licence tiers or delivery pack.** Etsy package hard-codes `personal-use-unless-otherwise-stated`. Your "family-and-classroom bundle" needs a classroom licence; Etsy buyers also expect a how-to-print page and (for templates) a template-link PDF. | `packages.py` (`package_etsy`), `config/platforms/etsy.json` | **Major** |
| G11 | **No seasonal planning.** `niche.py` uses static saturation priors; there is no seasonal calendar, launch deadline, or lead-time check. Today is 22 Oct 2026, so a Christmas line needs a dated build-and-list schedule. The repo's own connectivity notes say Etsy blocks plain HTTP fetches, so Etsy research is browser-assisted or manual. | `scripts/publishing_house/niche.py`, `config/research-sources.json`, `agent-memory/publisher-in-chief/project_web_search_unavailable.md` | **Major** |
| G12 | **Visual toolkit is book-oriented.** The cleared-font list is literacy and book faces (Andika, Atkinson, Charis, Gentium, Literata, Lexend, Archivo, Baloo 2): good body type, thin on festive display and script faces. No theme/style-token system, no borders/frames, no character-consistency method for illustrated pet or craft art. | `config/dependencies.default.json`, `config/tools.default.json`, `scripts/publishing_house/compositor.py` | **Minor** |
| G13 | **Print-at-home QA is shallow.** DPI, margin and font-embedding rules exist; nothing checks ink use, cut-line clarity, text overflow in cards, Letter vs A4 fit, or that "ink-friendly" really reduces fill. | `rules/10-digital-printables.md`, `skills/product-build-digital/SKILL.md` | **Minor** |
| G15 | **Interior proof is book-specific.** `build_proof` fails the interior when there is no `page-map.json`, when the page count is odd ("KDP requires an even page count"), or when solutions are not "back-only". A kit has no solutions and no even-page rule, so `LAYOUT_AND_FORMAT_BUILD → ACCESSIBILITY_VALIDATION` and `FINAL_PROOF → PLATFORM_PACKAGING` (both gated on these reports) cannot pass as designed. The accessibility audit also reads `min_type_pt` and alt-text facts from the same proof. | `layout.py` (`build_proof`, `build_interior`), `config/workflow_states.json` (`gate_reports`), `accessibility.py` | **Blocker** |
| G14 | **Orchestration does not know kit stages.** The state playbook, `recommended_agents` and workflows reference puzzle/book agents; there are no kit fan-out workflows. `agents/README.md` says 31 agents, but 28 definitions exist (doc drift). | `config/state_playbook.json`, `workflows/`, `agents/README.md`, `agents/CATALOG.md` | **Minor** |

## 3. Concrete proof the Etsy package needs hardening

Checking the tags and titles you supplied against the limits I could verify (title ≤ 140 characters; 13 tags, each ≤ 20 characters; see §6 for sources):

| Product | Title length | Tag count | Tags over 20 characters |
|---|---|---|---|
| 01 Christmas Craft Night | 64 | 13 | none |
| 02 Pet's First Christmas | 62 | 13 | none |
| 03 Friendsmas Bundle | 63 | 13 | **`printable party games` = 21 characters** |

`package_etsy` would accept that tag unchanged (`keywords[:13]`). Your own note ("check each final tag against the current character limit") is exactly the check the framework lacks. Fix: `etsy validate` (spec in `scripts/03-etsy-validation-audits.md`).

## 4. Product-by-product readiness (the three products you supplied)

Legend: **Ready** = existing framework covers it · **Partial** = exists but needs the listed gap fixed · **Missing** = not present.

| Capability needed | P01 Craft Night | P02 Pet Keepsake | P03 Friendsmas | Gaps |
|---|---|---|---|---|
| Niche evidence, competition, positioning | Partial | Partial | Partial | G11 |
| Multi-component kit spec (counts, parts) | Missing | Missing | Missing | G2 |
| Illustrated step-by-step cards with difficulty/time/materials | Missing | n/a | n/a | G1, G5 |
| Age-tier versions (4–7, 8–12, teen, mixed) | Missing | n/a | n/a | G6 |
| Cut sheets: gift tags, keepsake cards, ornament templates | Missing | Missing (pet tags) | Missing (labels) | G1, G5 |
| Certificates, passport, profile, photo-frame pages | n/a | Missing | n/a | G5 |
| Personalisation fields / editable files | n/a | Missing | Missing | G7 |
| Games with answer keys (bingo, trivia, charades) | n/a | n/a | Partial (verify pattern exists, no generators) | G5 |
| Variants: Letter/A4, colour/ink-friendly; dog/cat/neutral/minimal; small/large group, workplace | Missing | Missing | Missing | G2 |
| Offers and price tiers | Partial | Partial | Partial | G2, G10 |
| Cover and 5–10 listing images | Missing | Missing | Missing | G3 |
| Pass the interior/cover proof gates (no solutions, no even-page rule, no spine) | Missing | Missing | Missing | G3, G15 |
| SEO title, 13 tags, category | Partial | Partial | Partial (21-char tag) | G4 |
| Craft/pet/party safety | Partial | Partial | Partial | G9 |
| Licence tiers and delivery pack | Partial | Partial | Partial | G10 |
| Fonts/art rights | Ready (ledger) / Partial (fonts) | same | same | G12 |
| Quality gate and count claims ("12 Crafts", "8 Games") | Partial | Partial | Partial | G8 |

You mentioned **10** products but supplied **3**. I generalised from these three plus common Etsy printable patterns; the extension is built around reusable *component kinds*, so the other seven should mostly fit. If any of them need something unusual (for example, audio, video, or physical shipping), tell me and I will check.

## 5. What I recommend you add (all delivered as markdown in this package)

| Area | New files | Closes |
|---|---|---|
| Rules (8) | `23`–`30` in `.claude/rules/` | G4, G6, G7, G9, G10, G11, G13 |
| Standards (3) | kit contract, Etsy listing contract, buyer-licence contract | G2, G4, G10 |
| Agents (9) | `AGT-035`–`AGT-043` | G2, G3, G5, G6, G9, G11, G13 |
| Skills (13) | `product-kit-spec`, `product-build-components`, `product-build-variants`, `product-personalization`, `product-listing-images`, `product-etsy-package`, `product-etsy-validate`, `product-count-audit`, `product-print-test`, `product-craft-safety-review`, `product-delivery-pack`, `product-seasonal-plan`, `product-offer-ladder` | G1–G13, G15 |
| Workflows (4) | kit component fan-out, variant-matrix build, listing-image fan-out, launch-readiness audit | G14 |
| Script specs (3 docs) | renderer library and new content types; kit/variant/delivery/proof builders; Etsy validation and audits | G1, G2, G4, G5, G8, G13, G15 |
| Config and schema deltas | schemas, `etsy.json` v2, age bands, quality-gate profile, proof and cover-gate changes | G3, G6, G8, G15 |
| Template pack | kit spec, variant matrix, Etsy listing, licence text, how-to-print, listing-image brief, seasonal plan | all |

**Design choice that keeps the change small:** keep `digital-printable` as the product family and put kit data under the existing free-form `production.kit` and `commercial.offers` keys in `project.yaml` (their schema allows extra properties). That avoids changing the `book_type` enum in five places. If you later want a first-class `printable-kit` family, `config/schemas-and-config-deltas.md` lists the exact edits.

### Suggested build order (fastest route to a shippable first product)

1. **Renderer core + three component kinds** (instruction card, cut-sheet, form page) and the kit spec (G1, G2, G5). Without this, nothing renders.
2. **Kit-aware proof reports** (`kit proof`, G15) so a built kit can pass `LAYOUT_AND_FORMAT_BUILD` and `FINAL_PROOF`. Without this, the lifecycle stalls even if rendering works.
3. **Etsy package v2 + `etsy validate`** (G4). Small, high value, protects every listing.
4. **Variants (size and colour) + delivery pack** (G2, G10).
5. **Listing images** and the cover-gate change so a digital kit's "cover" is its hero image plus listing set (G3).
6. **Quality-gate profile and count audit** (G8) so the final gate can pass.
7. **Personalisation/fillable, print test, safety review, seasonal plan** (G7, G13, G9, G11).

Because your examples are Christmas products and today is 22 October, run `product-seasonal-plan` first for each product to fix a realistic list-by date, then work backwards.

## 6. Verified platform facts (and what I could not verify)

Checked on 2026-10-22; the framework's own rule (`refresh_before_release`) still requires a dated recheck at the listing gate.

- **Title:** at most 140 characters. **Tags:** 13 per listing, at most 20 characters each. **Description:** roughly 10,000 characters; only the first ~160 characters reliably show in search previews. Source is a third-party guide updated July 2026 ([Outfy](https://www.outfy.com/blog/etsy-character-limit/)), so treat as "recheck against Etsy's help centre".
- **AI disclosure:** Etsy's Creativity Standards allow AI-assisted items under "designed by a seller" when based on the seller's own original prompts or inputs, and require AI use to be disclosed in the listing description ([Etsy](https://etsy.com/legal/creativity)). The existing `commercial-writer` already adds an AI-disclosure sentence; the new standard makes it a hard check.
- **Digital downloads:** original designs the seller created can be sold; PDFs of other people's work cannot (same Etsy page). The page does not mention templates or printables explicitly.
- **Canva:** Etsy does not accept direct Canva links; sellers deliver an instant-download PDF containing a Canva "Template link" (never a View/Edit link), and Canva's content licence does not allow reselling its elements on their own, so the product must be your own composition ([Gelato guide](https://www.gelato.com/blog/how-to-sell-canva-templates-on-etsy), third-party summary). The framework cannot create Canva accounts or designs, so the Canva path is a **human-assisted step**; the framework-native editable path is a fillable PDF.
- **Not verified:** maximum number of listing images, digital file count and size limits, category names, required attributes. The new `etsy.json` v2 stores these as `unverified` values with a mandatory dated check.
- Nothing here is legal advice; licence text templates are drafting aids for your own review.

## 7. How I reviewed it, and the limits of that review

- I cloned the repo and read only `.claude/`. I listed the top-level folder names of the repo once to orient myself but opened nothing outside `.claude/`.
- I read about 50 of the 276 non-font files: the constitution, state machine and playbook, rules 00–04, 06–10, 12–14, 16–18, 20–22, schemas for project/composite, config (age bands, design policy, quality gates, tools, dependencies, research sources, Etsy platform), the layout/packages/marketing/niche/quality/claims/generate/verify/accessibility/state/planner modules, the printable/journal generators, the hook policy, the printable-designer, commercial-writer and market-analyst agents, and the digital-build and listing-kit skills.
- I did not run the framework or its tests, and I did not read the remaining agents, skills, commands, patterns, plans, maintenance code or the repo's existing `projects/`. If one of those already covers a gap above, the matching new file is redundant; run `ph_cli.py framework validate` after installing to catch duplicates.
- The quality-gate finding (G8) comes from reading `quality.py`; I have not confirmed it by running a kit through the gate.
