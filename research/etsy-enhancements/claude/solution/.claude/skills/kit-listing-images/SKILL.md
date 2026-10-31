---
name: kit-listing-images
description: >-
  Plan and compose the Etsy listing gallery for each SKU from real rendered pages with verified counts, thumbnail-legible headlines, alt text, and truthful content, then write the proof report that stands in for the cover gate.
argument-hint: "<project-id> --sku <sku-id>"
user-invocable: true
effort: high
model: '@bedrock-eus1/us.anthropic.claude-sonnet-5'
allowed-tools:
  - Read
  - Write
  - Bash
  - Agent
  - Skill
  - "Bash(${CLAUDE_PROJECT_DIR}/.venv/bin/python3 .claude/scripts/ph_cli.py *)"
---

# /kit-listing-images

## Goal

Build a gallery that sells honestly: only what is delivered, with numbers that match the verification report.

## Arguments

Use `$ARGUMENTS` exactly.

## Entry criteria

- Variant PDFs exist for the SKU (page rasters can be taken from them) and verified counts are available.
- Style tokens approved by `art-director`.

## Specialist delegation

`listing-image-director`; `art-director` (style tokens, scene providers).

## Procedure

1. Run `ph_cli.py kit images $ARGUMENTS --plan-only` to scaffold `kit/listing/image-plan-<sku>.yaml` from SKU contents and verified counts.
2. Delegate refinement to `listing-image-director` against STD-LISTING-IMAGES (roles, truth rules, thumbnail test).
3. Run `ph_cli.py kit images $ARGUMENTS` to rasterise pages, compose images with the compositor, run thumbnail/contrast/element-in-SKU/count checks, and write `outputs/proof/cover-proof-report.json` (`kind: listing-images`).
4. If a hero needs a physical craft photo, request it from the human or switch to a labelled illustration (rule 26). Do not generate fake photos.
5. Produce the contact sheet and alt-text list; register artifacts; assemble the cover gate packet with `product-gate-packet --gate cover`.

## Required outputs

- Image plan, composites per SKU, contact sheet, alt-text list, proof report (PASS/FAIL).

## Stop conditions

- Stop on a depicted item not in the SKU, a count mismatch, unresolved scene-asset rights, or a failed thumbnail test that cannot be repaired.

## Completion report

State the project, SKU, images built (≤ 10), proof decision, disclosures needed, and the next valid action (cover gate or auto-approval by policy).
