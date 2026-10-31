---
name: kit-listing
description: >-
  Draft the per-SKU Etsy listing package — title within 140 characters, up to 13 tags of at most 20 characters, description, category candidate with verification date, price recommendation, licence tier, files, images, and AI disclosure — validated against Etsy limits and the verified counts, with no external write.
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

# /kit-listing

## Goal

Produce a listing the human can paste and upload with confidence: every claim true, every limit met.

## Arguments

Use `$ARGUMENTS` exactly. Titles, tags, and descriptions are DRAFTS for human review. Prices are recommendations.

## Entry criteria

- Compliance approved; metadata stage reached; verified counts and rendered variants exist; images built or in progress.

## Specialist delegation

`commercial-writer` (title, tags, description, bullets), `pricing-strategist` (ladder with basis), `rights-manager` (trademark/association screen of coined terms and tags).

## Procedure

1. Run `ph_cli.py project status $ARGUMENTS`; read `kit.yaml`, the verification report, and `etsy.json` limits.
2. Delegate to `commercial-writer`: title ≤ 140 characters, natural phrasing; up to 13 tags, **each ≤ 20 characters**, unique, descriptive, no trademarks; description stating digital file, no physical item, sizes, file types, per-SKU contents, printing guidance, licence summary, and AI disclosure; counts copied from the verification report.
3. Delegate the trademark/association screen to `rights-manager` for coined or seasonal terms (e.g. party names) in titles, tags, and images; fallback wording if unresolved.
4. Delegate the price recommendation (basis stated); never set as final.
5. Run `ph_cli.py kit listing $ARGUMENTS` to assemble `etsy-listing-<sku>.json` (schema `etsy-listing-sku.schema.json`) and `listing-checklist-<sku>.md`. Fix, do not truncate, any field the validator rejects.
6. Record `category.path` with `verified_on` (null if unverified: a WARNING that blocks the listing gate until a human confirms).
7. Run `ph_cli.py kit preflight $ARGUMENTS --channel etsy`; FAIL blocks the listing gate.

## Required outputs

- Per-SKU listing JSON, checklist, tag/limit validation report, trademark screen record, price recommendation with basis.

## Stop conditions

- Stop on any limit violation, count mismatch, unresolved trademark screen, missing AI disclosure, or licence mismatch.

## Completion report

State the project, SKU, validation results (title length, tag count and max length), warnings, and the next valid action (listing gate).
