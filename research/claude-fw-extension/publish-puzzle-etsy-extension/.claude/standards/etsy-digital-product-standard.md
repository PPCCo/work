# STD-ETSY-001 — Etsy Digital Product Standard

**Status:** proposed extension standard. **Owner:** Publisher-in-Chief / Product Quality. **Applies to:** Etsy-targeted digital downloads and made-to-order digital products.

## 1. Product model

Treat an Etsy item as a buyer outcome plus a versioned set of deliverables, not as a single PDF by default. The canonical project may continue to use `product-type: digital-printable`, with a more precise `etsy_archetype` in the brief.

Supported archetypes should be data-driven and extensible, for example:

- `craft-kit` — craft cards, project instructions, templates, schedules, supply lists, host notes.
- `keepsake-kit` — certificates, memory pages, photo frames, trackers, personalized/editable fields.
- `party-game-kit` — invitations, RSVP and planning sheets, game cards, boards, answer keys, host rules.
- `planner-bundle` — planning pages, trackers, checklists, calendars, and usage instructions.
- `editable-template` — Canva or other editable-template access instructions, licensed assets, and export guidance.
- `printable-art-or-template-set` — page-based printables, SVG/PNG assets, cut files, or other defined formats.
- `education-or-activity-bundle` — worksheets, prompts, activity sheets, solutions where applicable, and teacher/parent guidance.

Do not add every archetype to the product-type enum unless the code genuinely requires it. Prefer a validated archetype field and component inventory over a brittle one-product-type-per-niche design.

## 2. Canonical brief and component inventory

Before content generation, the approved brief must specify:

1. Target buyer, end user, age/audience band, context of use, problem being solved, promise, differentiation, and explicit exclusions.
2. Product archetype and fulfillment mode: `instant-download` or `made-to-order-digital`.
3. Tier/edition plan (for example, basic vs expanded), price hypothesis and currency, and whether each tier is a separate Etsy listing.
4. Component-level inventory: stable component ID, name, count, format, page/asset size, page size variants, color mode, intended use, source artifact, rights status, and acceptance criteria.
5. Required variations: audience bands, dog/cat/neutral designs, small/large group versions, color/ink-friendly versions, US Letter/A4, and editable/non-editable output as applicable.
6. What a buyer receives, what the buyer must supply, what is not included, software/printer requirements, and instructions to access/use the files.
7. Required QA mode per component (code, content expert, safety expert, visual reviewer, human review) and release blockers.

Every promise in title, listing description, gallery image, and product cover must map to a deliverable in the component inventory. No ghost features.

## 3. Content and instruction quality

- All instructions must be complete enough for the named audience and intended use without requiring the buyer to reconstruct missing steps.
- Use concrete materials, tools, quantities, estimated time, difficulty/skill level, and outcome descriptions where relevant.
- Time, difficulty, age suitability, counts, and claims must be estimates grounded in documented assumptions or review evidence; do not present untested estimates as measured facts.
- For games and educational content, rules must define setup, player count, turn flow, scoring/winning, tie handling when relevant, and required materials. Every answer key must be independently verified where an objective answer exists.
- For editable templates, include exact access steps, duplicate/use instructions, software/account prerequisites, editable fields, export steps, and an access-failure fallback. Never imply that the buyer receives a fully personalized file if the purchase only provides a template.
- For multi-age bundles, define age-specific adaptations rather than simply relabeling the same page. Confirm reading level, motor skills, supervision, complexity, and group-size fit.
- Where content is meant to be printed, specify page size and orientation per file. A4 and US Letter are distinct variants; do not merely stretch one layout if it harms margins or usability.

## 4. Child safety and practical feasibility

For craft kits or products used by children:

- Identify hazards by activity and age band: sharp tools, hot glue/heat, small parts/choking, allergens, food contact, cords/strangulation, fumes, adhesives, and supervision requirements.
- State safer substitutions and adult-only steps. Do not portray an activity as safe for a broad age band when critical parts require adult handling.
- Do not provide false guarantees such as “completely safe” or “non-toxic” without reliable product-specific evidence. Tell the host to follow the labels and directions for the actual materials used.
- Require an independent child-safety review for any kid-facing kit; a checklist written by the content author is not an independent clearance.
- Check that shopping lists, craft instructions, card counts, and project variants agree. Every listed material must be used or explicitly labeled optional.

## 5. Rights and originality

- Every included illustration, font, icon, pattern, photograph, game text, template element, and external resource must have provenance and rights status in the rights ledger.
- Etsy digital items must be made and/or designed by the seller; do not package third-party work as if it were original seller work.
- AI-generated elements require the listing disclosure required by Etsy's current policy. AI use does not clear copyright, trademark, personality, privacy, or third-party asset rights.
- Do not use trademarks, character names, brand terms, lyrics, or competitor listings as a shortcut for demand. Escalate plausible IP concerns rather than trying to “SEO around” them.
- For Canva or other editable-template assets, verify the current platform license for every included asset and the intended template-sharing method. Do not distribute a third-party asset outside the permissions granted by its licence.
- Unknown or undocumented rights are blockers, not assumed permission.

## 6. Bundle integrity and customer experience

- Generate a single source of truth for all item counts, page counts, size variants, and included file names.
- Cross-check component inventory against generated files, gallery preview, listing metadata, pricing tier, and buyer instructions.
- Provide a short `START-HERE` or equivalent guide for any bundle with multiple files, software steps, or multiple size/color variants.
- Provide a print guide for PDF products: page size, actual-size/100% printing recommendation where applicable, scaling cautions, color/ink note, and paper suggestions without guaranteeing identical printer results.
- Clearly mark `DIGITAL DOWNLOAD — NO PHYSICAL ITEM SHIPPED` in listing copy and/or supporting preview materials where needed to prevent buyer confusion.
- Separate color and ink-friendly versions when promised. The ink-friendly version must have a materially lower ink burden and remain legible; do not just rename the color PDF.
- Names and paths must be stable, readable, platform-compatible, and mapped in the delivery manifest.

## 7. Evidence and uncertainty

- Separate sourced facts, observed competitor evidence, assumptions, and recommendations.
- Market validation cannot guarantee demand, sales, ranking, or profit. Record date, query/search scope, geography if known, evidence URLs, observable listing information, and limitations.
- Price is a hypothesis. Document comparable offers, bundle scope, seller effort, fees/cost assumptions when known, and the planned validation signal.
- Research seasonal demand early enough to leave room for production, proofing, and listing review.

## 8. Mandatory statuses

Each component must end with `PASS`, `CONDITIONAL_PASS`, `FAIL`, or `ESCALATE`; every FAIL/ESCALATE must contain evidence and an owner. A release bundle cannot pass while a blocker remains open.
