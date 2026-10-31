---
name: kit-render
description: >-
  Render every kit variant — US Letter and A4, full-colour and ink-friendly, per age version and theme — from the frozen approved source with embedded cleared fonts, cut grids, fillable fields, and the nine per-variant checks, producing a render report and an aggregate interior proof.
argument-hint: "<project-id> [--variant <key>|--all]"
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

# /kit-render

## Goal

Build every variant deterministically and prove each one is print-ready.

## Arguments

Use `$ARGUMENTS` exactly. `--all` renders the matrix in batches; `--variant` repairs one failing variant.

## Entry criteria

- Interior gate approved and source frozen; state `LAYOUT_AND_FORMAT_BUILD`.
- Layout specs exist or are written by `template-engineer` in this run.
- Fonts cleared (`dependency select` evidence); assets in the rights ledger.

## Specialist delegation

`template-engineer` (layout specs, repairs), `prepress-specialist` (DPI, margin spot-checks), `accessibility-auditor` (after render).

## Procedure

1. Confirm source hashes match the frozen approved artifacts (`project status`).
2. Delegate layout-spec authoring to `template-engineer`; run `ph_cli.py kit render $ARGUMENTS` (idempotent; unchanged inputs skip).
3. Read `outputs/kit/render-report.json`. For each failing `(variant, page, check)` repair the layout spec, not content, and re-run only that variant. Max five targeted repairs per artifact; then escalate.
4. Confirm the nine STD-VARIANT-MATRIX checks pass for **every** variant; ink-friendly coverage within budget; field-fit on the stress list; fonts embedded; margins ≥ 0.25 in; counts equal verified counts.
5. Write the aggregate `outputs/proof/interior-proof-report.json` (PASS only if all variants pass).
6. Register all PDFs as downstream build artifacts (not bound by upstream approvals, rule 03).

## Required outputs

- `outputs/kit/<variant-key>.pdf` per variant, `render-report.json`, aggregate proof, repair log.

## Stop conditions

- Stop on hash mismatch with approved source, a variant failing after five repairs, or an uncleared font/asset.

## Completion report

State the project, stage, variants built vs planned, failing variants and repairs, proof decision, artifact hashes, and next valid action (accessibility validation).
