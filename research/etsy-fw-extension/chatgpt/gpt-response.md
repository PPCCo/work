# Evaluation: `publish-puzzle` for Etsy digital products

Recommendation: enhance the existing framework rather than build a separate Etsy framework.

Your repository already has much of the architecture needed for an autonomous digital-product publishing operation. The most important gaps are in the Etsy-specific product model, multi-file delivery, editable-template fulfillment, and end-to-end product validation.

I inspected the public repository README, extension guide, agent catalogue, workflow conventions, and Etsy channel configuration. The repository already supports digital printables, market research, specialist agents, independent verification, accessibility and rights reviews, metadata generation, artifact tracking, and controlled release.&#x20;

However, its current Etsy configuration is narrower than the products you have in mind: it specifies `digital-pdf`, an instant-download mode, and a required `printable.pdf` output.&#x20;

That is a reasonable starting point for a simple printable, but not a complete delivery model for a multi-component craft kit, editable keepsake collection, or party-game bundle.

I have prepared a 14-file Markdown extension pack with proposed agents, skills, standards, rules, templates, a workflow runbook, and a deterministic-validator implementation specification. I have not created any of the example products themselves.

Complete Etsy extension pack

ZIP archive · 14 Markdown files · proposed repository paths preserved

- `./README-ETSY-EXTENSION.md` Explains where each file belongs and which existing components must be extended.

## 1. What is already sufficient, and what needs improvement?

| Capability                                 | Assessment                      | Recommended action                                                                                       |
| ------------------------------------------ | ------------------------------- | -------------------------------------------------------------------------------------------------------- |
| Product discovery and competition research | Existing foundation is suitable | Reuse existing research pipeline; strengthen Etsy-specific evidence and seasonal timing.                 |
| Product planning and content generation    | Good foundation                 | Add component inventories, variants, buyer instructions, and explicit acceptance criteria.               |
| Specialist agents and independent review   | Good foundation                 | Add an Etsy product architect and independent bundle auditor.                                            |
| Child safety and originality               | Existing controls are useful    | Require explicit craft hazards, age-specific supervision, material checks, and independent review.       |
| Printable production                       | Good foundation for PDFs        | Validate every promised size, color mode, and audience edition independently.                            |
| Multi-file bundles and editable templates  | Needs enhancement               | Add component manifests, ZIP packaging, editable-template access checks, and fulfillment modes.          |
| Etsy metadata and listing creation assets  | Partial                         | Strengthen current-policy validation, listing-gallery consistency, tag-length checks, and AI disclosure. |
| Quality control and release                | Strong existing foundation      | Extend deterministic preflight and preserve the existing human approval gates.                           |
| Post-release improvement                   | Existing foundation is suitable | Reuse performance and review analysis once genuine shop data becomes available.                          |

The key architectural principle is to extend your existing `digital-printable` product family with an Etsy-specific bundle model, instead of creating an entirely separate product lifecycle or a different agent for every type of printable.

## 2. The most important Etsy-specific gaps

### A. Support bundles, not just individual PDFs

The current adapter expects a relatively simple printable deliverable. Your examples require the framework to assemble and validate sets of related assets.

For a Christmas craft kit, that could mean instruction cards, separate gift-tag designs, a host guide, age-specific variants, US Letter and A4 files, and full-colour and ink-friendly editions. For a party kit, it could mean invitations, scorecards, answer keys, and several game formats.

The extension therefore introduces a component inventory and delivery-manifest model. Each component has an ID, expected count, source artifact, output formats, variants, acceptance tests, and a required verifier.

This lets the framework check whether the actual package matches the contents advertised in the listing.

### B. Distinguish instant-download products from personalized products

This is an important gap for the pet-keepsake concept.

There are two different fulfillment models:

- Instant download: the buyer receives ready-made files or an editable template and personalizes it themselves.
- Made-to-order digital: the buyer supplies information, such as a pet's name or photograph, and the seller prepares the customized files after purchase.

Etsy supports both types of digital listings, but the workflow and buyer expectations differ. Etsy's current help documentation also states that digital listings cannot use listing variations.&#x20;

The extension makes fulfillment mode explicit and flags different-price bundles for separate listing plans. It also requires access testing and clear instructions for editable templates.

### C. Validate Etsy requirements instead of relying on remembered rules

The listing workflow needs deterministic checks for current platform constraints, including:

| Requirement             | Current documented constraint                                                              |
| ----------------------- | ------------------------------------------------------------------------------------------ |
| Listing title           | Maximum 140 characters; Etsy's 2026 guidance favors clear, concise, buyer-friendly titles. |
| Tags                    | Up to 13 tags, each no more than 20 characters.                                            |
| Download files          | Up to 5 uploaded files, maximum 20 MB per file for instant downloads.                      |
| AI-created items        | Disclose AI use in the listing description when required by Etsy's policy.                 |
| Digital listing content | The digital item must be made and/or designed by the seller.                               |

Sources:

These limits are documented in the extension, but the framework should refresh them from official sources before release rather than assume they will remain unchanged.

I also checked the tags in your supplied examples: `printable party games` is 21 characters, which exceeds Etsy's current 20-character tag limit. The other tags shown in your three examples meet that limit.

### D. Validate product usability, not just file existence

Your examples contain content where incomplete instructions can undermine the product even if the PDFs render correctly.

The framework should independently review:

- Craft instructions, materials, tools, activity duration, age suitability, and adult-supervision notes.
- Game rules, setup, scoring, tie handling, and answer-key correctness.
- Pet-keepsake personalization instructions and editable-template access.
- Counts and variants across product files, listing descriptions, cover images, and gallery previews.
- Print size, legibility, margins, ZIP integrity, file checksums, and ink-friendly versions.

Your existing safety, accessibility, rights, and content-verification agents should remain responsible for their specialist areas. The new Etsy agents coordinate the product specification and check the finished bundle without replacing those existing controls.

## 3. What's inside the extension pack?

The archive contains these proposed additions.

- Etsy product architect `.claude/agents/content/etsy-product-architect.md` - Converts the approved product idea into components, variants, fulfillment instructions, and acceptance tests.
- Etsy bundle auditor `.claude/agents/quality/etsy-bundle-auditor.md` - Independently compares the actual files, listing claims, access instructions, and delivery manifest.
- Etsy digital-product skill `.claude/skills/etsy-digital-product/SKILL.md` - Routes work through your existing agents and lifecycle without bypassing human gates.
- Etsy launch workflow `.claude/skills/etsy-digital-product/workflows/etsy-launch-workflow\.md` - Provides the step-by-step production, validation, packaging, and release runbook.
- Digital-product standard `.claude/standards/etsy-digital-product-standard.md` - Defines bundle structure, customer experience, craft safety, originality, and delivery requirements.
- Listing standard `.claude/standards/etsy-listing-standard.md` - Covers title and tag limits, listing descriptions, galleries, claims, and disclosure.
- Release-gate standard `.claude/standards/etsy-release-gate-standard.md` - Defines blockers, required evidence, independent review, and human approval.
- Scoped Etsy rules `.claude/rules/etsy-digital-products.md` - Reminds agents to apply the Etsy standards to relevant project artifacts.
- Product brief template `.claude/templates/etsy-product-brief.md` - Records audience, market evidence, product scope, requirements, and unresolved decisions.
- Delivery manifest template `.claude/templates/etsy-delivery-manifest.md` - Specifies the files, components, variants, hashes, and technical checks required for a listing.
- Validator implementation specification `.claude/scripts/etsy-package-validator-spec.md` - Defines the deterministic checks and tests needed for an Etsy package validator.
- Agent catalogue additions `.claude/agents/CATALOG-additions.md` - Provides proposed catalogue entries for the new agents.
- Workflow catalogue additions `.claude/workflows/README-additions.md` - Documents the distinction between the Markdown runbook and an executable workflow.
- Extension README `README-ETSY-EXTENSION.md` - Installation order, integration notes, and the architectural decisions needed to incorporate the extension.

Open README

## 4. How I recommend integrating it

Do not replace or rewrite your existing lifecycle. Instead, make the following changes in order.

1. Add the Markdown definitions. Merge the new agents, standards, skill, scoped rule, and templates into the repository at their specified paths.
2. Extend the project and delivery schemas. Add the Etsy archetype, fulfillment mode, component matrix, variant matrix, gallery plan, and machine-readable delivery manifest. Keep the existing `digital-printable` type unless a broader schema change is justified.
3. Extend the Etsy adapter and package builder. Support multiple deliverables, ZIP bundles, documented template links, separate product tiers, and the relevant fulfillment modes. Continue producing upload-ready packages without performing live Etsy writes.
4. Implement and test the validator. The included validator file is an implementation specification, not executable Python. Integrate the eventual script into `ph_cli.py`, provide test fixtures, and add its evidence to the release gate.
5. Validate the integration. Follow your existing `EXTENSION_GUIDE.md`, run `framework validate` and the unit-test suite, then test at least one representative bundle with multiple files and variants.

One important implementation detail: the supplied launch workflow is a Markdown runbook, not an executable Claude Code dynamic workflow. Your repository expects dynamic workflows to be implemented as `.js` files. If you want one-command orchestration later, implement that separately using the repository's workflow API and keep human approvals outside the workflow.&#x20;

I could inspect the public source files, but I couldn't clone the repository in this session or execute integration tests against your local checkout. Therefore, this is a proposed extension pack ready for integration and review, not a tested commit to your repository. Check the proposed agent IDs against your current checkout before merging.

Final verdict: Your framework is a strong foundation for the proposed Etsy business. The missing piece is not another large collection of general-purpose agents. It is a rigorously validated, Etsy-specific bundle and fulfillment layer that connects product planning, content quality, listing claims, and actual downloadable files. The supplied pack is designed around that narrower enhancement.