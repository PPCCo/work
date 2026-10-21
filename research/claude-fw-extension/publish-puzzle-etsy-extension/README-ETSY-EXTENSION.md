# Etsy Digital Product Extension for `publish-puzzle`

**Purpose:** extend the existing publishing-house framework to produce and quality-check richer Etsy digital products without replacing its current lifecycle or creating the products listed in the user's examples.

**Assessment date:** 2026-10-21. Etsy rules change; all external limits and policies must be refreshed immediately before release.

## Recommendation

Reuse the existing discovery, product state, rights, accessibility, commercial-writing, pricing, packaging, and release-gate infrastructure. Add an Etsy bundle layer: a product-component manifest, mixed-file delivery rules, editable/made-to-order fulfillment support, instructions/safety/game-content audits, listing-gallery planning, and deterministic package validation.

The current public framework already documents `digital-printable`, Etsy packaging, US Letter/A4, rights/accessibility/compliance checks, metadata/channel audits, artifact hashes, and manual-upload packages. The present Etsy adapter is intentionally narrow: it declares only `digital-pdf`, instant downloads, and a `printable.pdf` required output. It therefore needs enhancement for product bundles with multiple components, editable templates, template-link delivery, ZIPs, multiple versions, and made-to-order digital fulfillment.

## Files in this extension

| File | Purpose |
|---|---|
| `.claude/standards/etsy-digital-product-standard.md` | Product-family, audience, claims, safety, rights, and fulfillment rules. |
| `.claude/standards/etsy-listing-standard.md` | Etsy-specific metadata, SEO, tags, gallery, and disclosure rules. |
| `.claude/standards/etsy-release-gate-standard.md` | Release blockers, deterministic checks, and human approval expectations. |
| `.claude/rules/etsy-digital-products.md` | Scoped rule reminding agents to apply the Etsy standards to project artifacts. |
| `.claude/agents/content/etsy-product-architect.md` | Agent to convert a validated commercial concept into a complete bundle specification. |
| `.claude/agents/quality/etsy-bundle-auditor.md` | Independent reviewer for completeness, usability, file delivery, claims, and risk. |
| `.claude/skills/etsy-digital-product/SKILL.md` | Entry skill and routing instructions. |
| `.claude/skills/etsy-digital-product/workflows/etsy-launch-workflow.md` | End-to-end Markdown workflow/runbook. |
| `.claude/templates/etsy-product-brief.md` | Reusable, filled-in-by-agents project brief template. |
| `.claude/templates/etsy-delivery-manifest.md` | Reusable delivery manifest template. |
| `.claude/scripts/etsy-package-validator-spec.md` | Requirements for the deterministic validator that should be implemented in Python and wired to `ph_cli.py`. |
| `.claude/agents/CATALOG-additions.md` | Catalogue row additions; merge rows into the existing catalogue after confirming IDs. |
| `.claude/workflows/README-additions.md` | Workflow catalogue / implementation note. |

## Add to the existing repository

1. Copy the `.claude/` subdirectories into the same locations in `publish-puzzle`; resolve conflicts manually rather than overwriting existing project policies.
2. Read `.claude/standards/agent-contract.md` and `EXTENSION_GUIDE.md` in the target repository. These files were followed as far as the publicly inspectable conventions permitted.
3. Merge the two proposed agent rows into `.claude/agents/CATALOG.md`. The current visible catalogue ends at `AGT-034`; if your checked-out version has newer IDs, allocate the next unused IDs and update each new agent header and catalogue row together.
4. Merge the workflow note into `.claude/workflows/README.md` only if you also implement a dynamic workflow. The included `.md` is a native prose runbook, not an executable `.js` workflow.
5. Update `.claude/config/platforms/etsy.json` and the publishing-house package builder to accept multiple registered deliverables and ZIP bundles. Do not just change documentation and assume the packager can handle files it was not coded to handle.
6. Add the new deterministic validator specified in `.claude/scripts/etsy-package-validator-spec.md`; integrate it as a `ph_cli.py` verb, tests, and release-gate evidence. The extension does **not** pretend that this implementation already exists.
7. Update the canonical project schema/intake to support an `etsy_archetype`, `fulfillment_mode`, component inventory, variant matrix, listing-gallery plan, and delivery manifest. Keep `product-type: digital-printable` as the base product type until the engine schema is deliberately extended.
8. Run the repository's required checks: `python3 .claude/scripts/ph_cli.py framework validate` and `python -m unittest discover -s tests -v`, plus the new Etsy package fixtures.

## Important integration decisions

- Keep the existing human approval, artifact hash, rights clearance, and release authorization controls. No new workflow can bypass them.
- Reuse `market-analyst`, `content-architect`, `printable-designer`, `child-safety-reviewer`, `content-verifier`, `originality-auditor`, `accessibility-auditor`, `rights-manager`, `compliance-officer`, `commercial-writer`, `pricing-strategist`, `packaging-engineer`, and `release-coordinator` where their current remit applies.
- The new architect specifies the product system; it does not replace the commercial writer or the independent quality agents.
- The new bundle auditor never verifies its own generated work. It reports evidence and blockers; it cannot approve or release.
- Keep live Etsy publishing and credentialed writes disabled. Produce a human-reviewable upload package only.
- For multiple Etsy price tiers (for example, basic and expanded), model them as separate listings unless a currently supported Etsy mechanism explicitly allows the intended choice. Etsy's current help says variations are unavailable for digital listings.
- An instantly downloadable editable template is not the same as a seller-personalized order. Force the project to state which fulfillment path it uses.

## Current external references used for this draft

- Etsy listing fields, digital file upload, tags, and variation rules: <https://help.etsy.com/hc/en-us/articles/115015628707-How-to-Create-a-Listing>
- Etsy digital listing file count / size / supported formats / instant vs made-to-order: <https://help.etsy.com/hc/en-us/articles/115015628347-How-to-Manage-Your-Digital-Listings>
- Etsy title guidance, published 2026-04-27: <https://www.etsy.com/au/seller-handbook/article/1399426136697>
- Etsy tag guidance (13 tags; up to 20 characters per tag): <https://www.etsy.com/au/seller-handbook/article/382774281517>
- Etsy Creativity Standards and seller-prompted AI disclosure: <https://www.etsy.com/au/legal/creativity>
- Etsy personalized listing workflow: <https://help.etsy.com/hc/en-us/articles/360000344528-How-to-Offer-Personalized-Listings>

These links are sources to refresh, not a substitute for release-time checking. Record the review date and any changed constraints in project evidence.
