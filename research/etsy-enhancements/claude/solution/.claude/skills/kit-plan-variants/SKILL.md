---
name: kit-plan-variants
description: >-
  Expand the kit's variant matrix (age version × theme × page size × ink mode), check the per-SKU cap, estimate download size against Etsy file limits, and select or recommend a delivery strategy.
argument-hint: "<project-id> [--sku <sku-id>]"
user-invocable: true
effort: high
model: '@bedrock-eus1/us.anthropic.claude-sonnet-5'
allowed-tools:
  - Read
  - Write
  - Bash
  - Skill
  - "Bash(${CLAUDE_PROJECT_DIR}/.venv/bin/python3 .claude/scripts/ph_cli.py *)"
---

# /kit-plan-variants

## Goal

Know exactly which files will exist, how many, roughly how big, and how they will reach the buyer — before content is generated.

## Arguments

Use `$ARGUMENTS` exactly. Never change `kit.yaml` here; propose edits as findings for `kit-architect`.

## Entry criteria

- `kit.yaml` validates; SKUs and axes are declared.

## Procedure

1. Run `ph_cli.py kit variants $ARGUMENTS`. Read: variant keys in deterministic order, count per SKU, cap status, file-name list.
2. Check STD-VARIANT-MATRIX rules: Letter/A4 and ink-friendly are render transforms only; mixed-age bands resolve by most-restrictive-wins; item counts are invariant across sizes.
3. Run `ph_cli.py kit deliver-estimate $ARGUMENTS` to estimate page counts and sizes from component types (before rendering). Compare with 5 files × 20 MB (config limits, `verify_before_release`).
4. Choose the delivery strategy: `zip-by-axis` with the axis that yields ≤ 4 ZIPs plus `Start-Here`; else `single-zip`; else flag `hosted-links` as needing a human decision and Etsy policy evidence.
5. If the cap is exceeded or the estimate cannot fit, list the smallest scope reductions that fix it.
6. Write `kit/variant-plan.md` (table of variants, sizes, strategy, risks) and register it.

## Required outputs

- Variant table, cap check, size estimate, delivery recommendation, reduction options.

## Stop conditions

- Stop if the manifest is invalid or axes conflict with the `digital-kit` design policy.

## Completion report

State the project, matrix size per SKU, delivery strategy and fit, risks, and next valid action.
