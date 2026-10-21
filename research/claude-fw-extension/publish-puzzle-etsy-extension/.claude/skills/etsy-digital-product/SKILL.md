---
name: etsy-digital-product
description: >-
  Plan, produce, and preflight Etsy-targeted digital products that contain multiple printable, editable, or downloadable components. Use for craft kits, keepsakes, party games, planners, templates, and other bundled digital offers; preserves the existing human gates and offline-only Etsy packaging.
argument-hint: "<project-id> [--stage plan|audit|package]"
user-invocable: true
effort: high
model: '@bedrock-eus1/us.anthropic.claude-sonnet-5'
allowed-tools:
  - Read
  - Write
  - Skill
  - Bash
  - "Bash(python3 ${CLAUDE_PROJECT_DIR}/.claude/scripts/ph_cli.py *)"
---
# /etsy-digital-product

## Goal

Extend the existing `digital-printable` lifecycle for Etsy bundle products. Use the repository as the source of truth and do not create content outside the active project. This skill describes a process; it does not itself implement new `ph_cli.py` verbs or make the packager support formats it currently does not support.

## Entry criteria

- The human has created the project and approved the scope for planning, or has named a project ID for an audit/package stage.
- Read `project.yaml`, `state.json`, current lifecycle/gate evidence, `.claude/config/platforms/etsy.json`, and all relevant registered artifacts.
- Read `.claude/standards/etsy-digital-product-standard.md`, `.claude/standards/etsy-listing-standard.md`, and `.claude/standards/etsy-release-gate-standard.md`.
- Confirm whether the project is `instant-download` or `made-to-order-digital`; do not guess.

## Routing

- Discovery/evidence and competition: reuse `market-analyst` and the existing `/research` pipeline.
- Brief and component matrix: invoke `etsy-product-architect`.
- Content: route to the existing domain/content agents. Reuse `printable-designer`, `journal-prompt-writer`, `content-architect`, `content-verifier`, and code-backed puzzle/game verification where applicable.
- Safety: invoke `child-safety-reviewer` for child-facing crafts or any product risk requiring its remit.
- Visuals/layout: reuse `art-director`, `cover-designer`, `layout-engineer`, `prepress-specialist`, and `accessibility-auditor` as applicable.
- Rights/compliance: reuse `rights-manager`, `originality-auditor`, and `compliance-officer`.
- Listing and pricing: reuse `commercial-writer` and `pricing-strategist`; do not duplicate their work with a new standalone SEO agent.
- Independent bundle audit: invoke `etsy-bundle-auditor`.
- Packaging/release: reuse `packaging-engineer` and `release-coordinator`; require the existing human gates.

## Procedure

1. **Inspect state.** Confirm a valid project, approved brief, and next permissible lifecycle action. Never bypass state transitions or human-only skills.
2. **Establish product archetype and fulfillment.** Record an `etsy_archetype` and explicit fulfillment mode in the project brief. If the project schema has not yet been extended, record these as project-local intake metadata rather than inventing unsupported CLI arguments.
3. **Design the product system.** Create component matrix, variant matrix, acceptance tests, exact buyer instructions, and a claims-to-component map. Count every deliverable.
4. **Build and verify content.** Content authors produce artifacts; separate validators verify objective facts/answers, completeness, counts, and difficulty/age claims. Use code checks where possible and independent expert reviews where deterministic checks are insufficient.
5. **Build every promised edition.** Render separate US Letter and A4 layouts when both are sold. Build and compare color and ink-friendly versions when promised. Test editable/template access paths and access instructions.
6. **Run risk reviews.** Complete age/safety review, rights ledger, originality, accessibility, disclosure, and print-preflight checks relevant to the product.
7. **Create listing draft.** Use the existing commercial writer with the Etsy listing standard. Treat title/tags/categories/prices as draft metadata; verify current rules and evidence. Every public claim must map to a real file/component.
8. **Package and preflight.** Generate the delivery manifest, `START-HERE` guide where needed, upload-ready files, checksums, and listing/galleries. Run the Etsy validator when implemented; if it is absent, report `NOT IMPLEMENTED` and do not claim script validation passed.
9. **Independent audit.** The bundle auditor compares files and metadata against the approved component manifest and flags all inconsistencies. Producer fixes are rechecked independently.
10. **Prepare gate packet.** Provide evidence and unresolved decisions for the existing listing/compliance/release gates. Stop at the next human gate. Do not publish or upload to Etsy.

## Completion report

Return project ID, current state, input/output paths and hashes, tests and exit codes, findings by severity, platform-rule snapshot date, unresolved assumptions, human decisions required, and next valid action. Use PASS / CONDITIONAL_PASS / FAIL / ESCALATE.
