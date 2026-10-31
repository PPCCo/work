---
name: kit-etsy-preflight
description: >-
  Run an independent pre-upload audit of a SKU's Etsy package — limits, counts versus verification, images versus contents, licence consistency, disclosure, category verification date, files and checksums — and produce a pass, warning, or fail report plus a human upload checklist.
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

# /kit-etsy-preflight

## Goal

Catch every mismatch between what the listing says, what the images show, and what the download contains — before a human uploads anything.

## Arguments

Use `$ARGUMENTS` exactly. This skill is independent of the writers: it does not edit listing text or images; it reports.

## Entry criteria

- Package built (`/kit-deliver`), listing drafted (`/kit-listing`), images proofed (`/kit-listing-images`).

## Specialist delegation

`compliance-officer` (disclosure, policy), `rights-manager` (screens), and the workflow `kit-etsy-preflight-audit` for independent parallel checks.

## Procedure

1. Run `ph_cli.py kit preflight $ARGUMENTS --channel etsy` for the deterministic checks:
   - title ≤ 140; tags ≤ 13, each ≤ 20 characters, unique; images ≤ 10; files ≤ 5, each ≤ 20 MB;
   - every number in title/description/images equals the verified count;
   - every item shown in images or listed in the description exists in the package;
   - licence tier identical across listing JSON, description, Terms-of-Use;
   - AI-disclosure text present and consistent;
   - category has `verified_on`; limits have `verified_on` (else WARNING);
   - checksums match; `external_write_performed` is false.
2. Run `kit-etsy-preflight-audit` for independent reads (images vs listing; description vs package; policy snapshot freshness).
3. Collect findings in `finding.schema.json` format. FAIL on any blocker; WARNING when only unverified-date items remain.
4. Generate the human upload checklist: create listing, upload files and images in order, paste fields, set price, set digital delivery, confirm category, confirm AI disclosure and policy snapshot date, **then** record platform evidence with `submission record` after the human publishes.
5. Write `outputs/packages/etsy/<sku>/preflight-report.json` and register it.

## Required outputs

- Preflight report (PASS/WARNING/FAIL), findings, upload checklist.

## Stop conditions

- Stop on FAIL. Do not mark the package ready for the listing gate until blockers are repaired and the preflight re-run.

## Completion report

State the project, SKU, decision, findings by severity, items needing human verification (limits, category, policy dates), and the next valid action.
