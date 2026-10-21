# Etsy Digital Product Launch Workflow (Prose Runbook)

This is an agent-facing prose workflow. It is not a dynamic Claude Code `.js` workflow. If the repository needs one-click orchestration, implement and test a separate `.claude/workflows/etsy-digital-product-launch.js` using the existing workflow API, and keep all human approval actions outside the script.

## Phase 0 — Project and evidence intake

- Confirm the project was created through existing project initialization.
- Establish the audience, market hypothesis, buyer outcome, product archetype, delivery mode, tier structure, target currency, and planned channel.
- Refresh current Etsy constraints from official pages and record the observed values and timestamp.
- Record source links, evidence quality, geography/time window where available, and open research questions.
- Stop if the concept depends on unverified intellectual property, unclear permissions, prohibited resale content, or a fulfillment design the channel cannot support.

## Phase 1 — Scope and product contract

- Invoke `etsy-product-architect`.
- Build the component inventory, count matrix, format/size matrix, variant matrix, acceptance tests, and claim map.
- Define what the buyer receives, what they need, what is excluded, how they access it, and what happens if a template link fails.
- Treat each price/contents tier as its own product scope; check current Etsy digital variation policy.
- Present the brief through the existing niche/planning gate. No bulk generation before scope approval.

## Phase 2 — Content production

- Delegate each component to its most appropriate existing content agent.
- Produce stable source content/data first; render variants from the canonical source where appropriate.
- Record every file's source component ID and artifact hash.
- For games/quiz/education materials, independently verify rules and answer keys.
- For craft activities, reconcile instruction steps with materials, tools, timing, difficulty, and safety notes.
- For editable templates, test the exact template access settings and user steps; don't expose edit access to the seller's master file.

## Phase 3 — Build and visual QA

- Produce US Letter and A4 independently when promised.
- Produce separate color and ink-friendly variants when promised.
- Confirm text legibility at realistic print size, safe margins, orientation, page order, and no clipped content.
- Verify page/component counts against the inventory.
- Check previews are faithful to the final files and not a different tier.

## Phase 4 — Specialist controls

- Safety: child safety review for child-use/craft products; record age-specific limitations and adult-only steps.
- Rights: verify fonts, images, patterns, icons, template-library assets, and AI disclosure obligations.
- Accessibility: verify contrast, type size, information hierarchy, and understandable instructions for the actual audience.
- Print/file integrity: use deterministic PDF/image/ZIP preflight where possible.
- Escalate blockers; do not replace formal rights or safety clearance with model confidence.

## Phase 5 — Listing draft and buyer communication

- Use the existing `commercial-writer`; use `.claude/standards/etsy-listing-standard.md` as the channel brief.
- Validate current title and tag hard limits. Generate no more than 13 tags and ensure every tag is at most 20 characters under the currently documented Etsy rule.
- Use live category/attributes guidance instead of hardcoded category paths.
- Use buyer-friendly title wording; current 2026 Etsy guidance favors clarity and generally fewer than 15 words over keyword stuffing.
- Write the exact included files/counts, instructions, prerequisites, no-physical-item reminder, usage terms, and AI disclosure where required.
- Draft a listing-gallery sequence. Every feature shown must be included in the chosen tier.

## Phase 6 — Package validation

- Produce the delivery manifest.
- Verify every manifest entry exists and hashes/sizes match.
- Count the top-level files intended for Etsy upload and check per-file size and supported format against the latest policy snapshot.
- If using ZIPs, test archive integrity, file names, nested structure, and buyer-facing file extraction instructions.
- Check editable-template URLs/access instructions without using live seller credentials.
- Run the deterministic Etsy package validator when implemented. Record version, exit code, and report hash.

## Phase 7 — Independent review and gate packet

- Invoke `etsy-bundle-auditor` after the producer is finished.
- Correct findings and request independent re-audit of changed artifacts.
- Attach listing claim map, safety/rights/accessibility/print reports, policy snapshot, delivery manifest, checksum report, and unresolved findings.
- Stop at the existing human gate. The workflow may recommend readiness but may not approve, freeze, release-authorize, or submit.

## Phase 8 — Post-release learning

- Once real listing/performance data is supplied, reuse `performance-analyst` to assess it honestly.
- Track impressions/visits/conversion/refunds/questions only where real data exists. Do not fabricate metrics or attribute performance to a title/tag edit without a defensible comparison.
- Record buyer confusion, repeated support issues, broken template access, printing issues, and requested variants as evidence for edition maintenance.
