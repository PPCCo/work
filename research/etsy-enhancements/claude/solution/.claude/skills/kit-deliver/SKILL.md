---
name: kit-deliver
description: >-
  Build the per-SKU download package — Start-Here guide, Terms-of-Use, ZIPs by axis, bundle index with hashes — within Etsy file-count and size limits without downsampling print art, or recommend a human-approved alternative strategy.
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

# /kit-deliver

## Goal

Turn rendered variants into the exact files a buyer downloads.

## Arguments

Use `$ARGUMENTS` exactly. No upload, hosting, or link creation is performed by the framework.

## Entry criteria

- Variants rendered and proofed; licence tier set; Terms-of-Use drafted and approved at the compliance gate; state `PLATFORM_PACKAGING`.

## Specialist delegation

`template-engineer` (Start-Here and Terms-of-Use PDFs), `packaging-engineer` (manifest, checksums).

## Procedure

1. Run `ph_cli.py kit deliver $ARGUMENTS --budget-only` to compute size by strategy.
2. If `zip-by-axis` fits (files ≤ 5, each ≤ 20 MB), run `kit deliver $ARGUMENTS` to build `Start-Here.pdf`, `Terms-of-Use.pdf`, the ZIPs, `bundle_index.json` (variant keys, page ranges, SHA-256), and `checksums.sha256`.
3. If it does not fit, do not downsample below 300 DPI. Report options: reduce variants per ZIP by axis choice; ink-friendly/greyscale line-art optimisation that preserves 300 DPI; or `hosted-links`, which needs a human decision and current Etsy policy evidence.
4. Verify checksums after build; confirm every file in each ZIP is listed in the index and every listed file exists.
5. Register the package artifact; write `package-manifest.json` with `external_write_performed: false`.

## Required outputs

- Per-SKU files under `outputs/packages/etsy/<sku>/files/`, `bundle_index.json`, `package-manifest.json`, `checksums.sha256`, size-budget report.

## Stop conditions

- Stop on a failed checksum, a file over the limit with no approved strategy, or a missing licence/terms file.

## Completion report

State the project, SKU, strategy, file count and sizes, checksums, and the next valid action (`/kit-etsy-preflight`).
