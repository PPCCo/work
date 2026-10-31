# Evaluation: can `publish-puzzle/.claude` build the Etsy kit products?

Scope: only the `.claude/` folder of `PPCCo/publish-puzzle` (commit `a021676`), read on 2026-10-29. I read config, rules, standards, agents, skills and the core modules that matter for digital printables (`layout.py`, `generators/printable.py`, `packages.py`, `niche.py`, `marketing.py`, `metadata_audit.py`, `compositor.py`, hooks). I did **not** run the framework or its tests, so "verify by dry-run" items below are genuine open checks, not hedging.

The task text says 10 products, but the file contained 3 (Christmas Craft Night, Pet's First Christmas, Friendsmas). I evaluated those three and generalised to likely patterns in the other seven (planners, checklists, games, keepsakes, templates).

## Verdict

**Enhance it. Do not rebuild it, and do not use it as-is.**

The governance spine is strong and reusable. The production spine (content types, rendering, variants, Etsy listing) is built for puzzle/coloring *books* and cannot produce these kits. Everything needed can be added additively, with about ten small patches to existing files and no change to the six human gates.

## What you can reuse unchanged

| Capability | Where | Why it helps kits |
|---|---|---|
| State machine, six gates, auto-approve policy, exact-hash approvals | `workflow_states.json`, rules 00–03 | Compliance/release stay human; craft gates can auto-pass |
| Artifact registry, provenance, immutable revisions | rule 03, `artifacts.py` | Every card, variant and image is hash-tracked |
| Rights ledger, font clearance, image-provider commercial-rights flags | rule 12, `dependencies.default.json`, `tools.default.json` | OFL fonts bundled; unverified providers block the rights gate |
| Accessibility gate | `accessibility.py`, rule 11 | Contrast, type size, alt text |
| Compositor (cleared fonts + real text over images, deterministic) | `compositor.py`, `composite-spec.schema.json` | Reuse for listing/gallery images |
| Research fetch ladder, niche assessment, series layer | `net/fetch.py`, `niche.py`, `series.py` | Discovery and tiered offers |
| Offline Etsy package skeleton | `packages.py::package_etsy`, rule 16 | Extend, do not replace |
| Commercial-writer, pricing-strategist, child-safety-reviewer | `agents/` | Extend with kit-specific skills and rules |

## Gaps found (with evidence)

| # | Gap | Evidence | Severity |
|---|---|---|---|
| G1 | **No renderer for kit components.** `build_interior` draws sudoku grids and image pages; every other content type becomes a placeholder page titled "`<Type> #n`" plus a difficulty line. Craft cards, certificates, gift tags, invitations, checklists, bingo, passports have no drawing path. | `layout.py::build_interior`, `_draw_placeholder_page` | **Blocker** |
| G2 | **`printable` generator is wall-art only** (quote + page geometry). No generators for bingo, schedules, shopping lists, sign-ups, forms. | `generators/printable.py` | Blocker |
| G3 | **No variant matrix.** A project has one trim and one colour policy. The products need US Letter + A4, full-colour + ink-friendly, 3–4 age versions, dog/cat/neutral/minimalist themes: up to 16–24 PDFs per SKU. Rule 10 also forbids mixing page sizes in a bundle. | rule 10, `project.yaml` template, `printable-spec.json` | Blocker |
| G4 | **No multi-SKU offer ladder.** Products are sold as Standard ($5.99–8.99) and Expanded ($9.99–12.99). Framework has one `digital_price` and one listing. | `project.yaml`, `package_etsy` | Major |
| G5 | **Audience model is age-band only.** No "mixed-age family", "workplace", or "all-ages". Age-differentiated *versions* of one kit are not modelled. | `age_bands.json`, `project.schema.json` | Major |
| G6 | **No personalisation / editable-file path.** Fillable PDFs and Canva templates are required by P2 and P3. Nothing builds or validates form fields, text fit, or Canva dependency evidence. | no AcroForm code; `Canva` is only mentioned in passing | Major |
| G7 | **Etsy listing checks are thin.** `package_etsy` slices tags to 13 but never checks the 20-character tag limit; `metadata_audit` only warns on titles over 200 chars (Etsy's limit is 140). No category taxonomy, image plan, file-count/size packaging, or per-SKU licence text (licence is hard-coded `personal-use-unless-otherwise-stated`). | `packages.py`, `metadata_audit.py` | Major |
| G8 | **Listing images are required but nothing builds them.** Rule 16 says "up to 10 mockups"; no agent, skill or script produces them. The P1 cover concept ("finished crafts alongside instruction cards") is a misrepresentation risk if the crafts were never made. | rule 16, absent tooling | Major |
| G9 | **Seasonality is invisible.** `niche.py` uses one flat saturation prior per family. No calendar, no lead-time/slack check. All three examples are Christmas products and today is 29 Oct 2026, about 8 weeks from 25 Dec. | `niche.py` | Major (time-critical) |
| G10 | **Craft instructions are unverifiable by code.** Puzzles can be proven solvable; a craft card cannot. Nothing checks materials-vs-steps consistency, quantities, time estimates, or records physical make-testing. | `content-verifier` scope | Major |
| G11 | **Trivia/fact content has no source discipline.** `claims.py` audits listing claims, not question banks. Christmas content also carries lyric/character IP risk (Grinch, Elf on the Shelf, Rudolph, carol lyrics). | `claims.py`, rule 07 | Major |
| G12 | **Safety rule covers age bands only.** No craft hazard tagging (scissors, hot glue, heat, small parts), no supervision flags, no pet-handling guidance. | rule 06 | Major |
| G13 | **Possible gate mismatch for digital-only kits.** `VISUAL_DEVELOPMENT` is conditional on `paperback/hardcover/coloring-book`, so a `digital-pdf`-only project skips the cover stage, yet `FINAL_PROOF -> PLATFORM_PACKAGING` requires `cover-proof-report.json = PASS`. I could not see how `state.py` reconciles this. | `workflow_states.json`, `state_playbook.json` | Verify by dry-run |
| G14 | Interior draw helpers call built-in Helvetica. Rule 10 requires embedded fonts. `_register_embed_fonts` exists but I did not trace whether it remaps these calls. | `layout.py` lines 70–133 | Verify |

## Fit per example product

| Product | Works today | Needs added |
|---|---|---|
| **01 Christmas Craft Night** | Brief, niche gate, rights, packaging skeleton | Craft-card content + desk-check verifier, step diagrams, 4 age versions, hazard tagging, host/shopping/schedule generators, Letter/A4 × colour/ink matrix, 2-SKU ladder, classroom licence text |
| **02 Pet's First Christmas** | Brief, niche gate, fonts | Certificate/passport/frame renderer, **fillable fields + name-fit validation**, optional Canva dependency record, species/theme variants, pet-safety rule, "last-minute" timing |
| **03 Friendsmas** | Brief, niche gate | Editable invitation/RSVP/sign-up, **bingo + game generators with verification**, trivia fact-check, group-size scaling, workplace variant, **trademark screen on "Friendsmas"**, answer keys |

## Things I found in your three examples

- **Product 03 tag `printable party games` is 21 characters.** Etsy tags are capped at 20; the other 38 tags and all three titles (62–64 chars vs a 140 limit) pass. Your own note ("check each tag against the current limit") anticipated this; the framework currently has no check that would catch it.
- Category paths in the examples are labelled "or closest available". They must be recorded with a verification date, never assumed.
- "Editable Canva template where licensing permits" requires a human with a Canva account. The framework cannot create accounts or touch Canva; the extension records the dependency and evidence instead.

## Limits I could not verify from here

Etsy's current limits (title 140, 13 tags × 20 chars, 10 images, **5 files × 20 MB per digital listing**, variation/file behaviour, AI-disclosure and creativity standards) are recalled, not checked live, and Etsy itself is bot-blocked from this environment. The extension stores them in config with `verify_before_release: true`, matching the framework's own rule 16 ("recheck before the listing gate").

## Timing note (today is 2026-10-29)

Christmas products have a hard window. The six-gate flow plus a human upload means the schedule, not the content, is the constraint. The extension adds a slack calculator and a **fast path** (ship Standard SKU first, Expanded as a later update) that compresses effort but never skips the compliance or release gates.
