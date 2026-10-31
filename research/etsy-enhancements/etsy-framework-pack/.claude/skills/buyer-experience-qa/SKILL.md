---
name: buyer-experience-qa
description: >-
  Independently simulate the buyer's journey on the final download package (unzip, open every file, print-scale check, editable-link open-test record, START-HERE accuracy, licence file, hash match) and emit structured findings; used before the listing and final-proof gates for digital products; changes nothing.
argument-hint: "<project-id> [--channel <etsy|gumroad|generic>]"
user-invocable: true
effort: high
allowed-tools:
  - Read
  - Write
  - Bash
  - Agent
  - "Bash(${CLAUDE_PROJECT_DIR}/.venv/bin/python3 .claude/scripts/ph_cli.py *)"
---

# /buyer-experience-qa

## Goal

Catch the failures that generate refunds and bad reviews for digital products: files that will
not open, pages that print clipped or at the wrong scale, broken or wrong-permission template
links, instructions that do not match the files, and counts that differ from the listing.

This is an **independent** review. The agent that built or packaged the files SHALL NOT run it.

## Arguments

Use `$ARGUMENTS` exactly. Resolve a project ID first. This skill never modifies product
files, state, or approvals; it writes findings only.

## Entry criteria

- A built package exists under `projects/<id>/outputs/packages/<channel>/` with a registered manifest.
- `bundle_index.json` exists; `START-HERE.pdf` and `LICENSE-AND-TERMS.pdf` are present (`offer-architecture-contract.md`).

## Delegation

- `quality-lead` runs the checks and writes findings.
- `accessibility-auditor` supplies contrast/legibility/alt-text results for printables where required.
- No builder agent participates.

## Checks

1. **Package integrity:** unzip into a clean directory; every file in `bundle_index.json` exists, SHA-256 matches, no extra or missing files, no hidden/system files, ASCII file names.
2. **Open test:** each file opens in at least two common viewers (or the closest available equivalents); fonts embedded; no missing-glyph boxes; fillable fields work if present.
3. **Print test:** pages match the declared size (US Letter/A4), safe margins ≥ 0.25 in, nothing clipped at "actual size / 100%", legible in black-and-white where the product claims it, acceptable ink coverage for a home printer.
4. **START-HERE accuracy:** every instruction matches the files; steps for printing/opening editable links are correct; supply lists consistent with the content.
5. **Editable delivery:** a recorded **human** open-test exists for each template link (copy flow, not edit-original) and licensing status is `clear` per `digital-licensing-contract.md`. If no human test is recorded, the finding is `blocker`.
6. **Licence text:** present, plain-language, and consistent with upstream licences.
7. **Counts and claims:** every count/claim in the listing kit and image briefs equals the verified numbers in `bundle_index.json`.
8. **Audience fit:** instructions at the audience reading level; supervision wording where crafts involve scissors, heat, or small parts (rule 06).
9. **Failure modes:** what happens if the buyer prints only one page, uses A4 instead of Letter, or opens on a phone? Record the outcome and any needed mitigation text.

## Output

Structured findings per `.claude/schemas/finding.schema.json` (severity, location, evidence,
recommendation, acceptance test, status), written to the project's reviews folder and
registered. Summarise as PASS / WARNING / FAIL. Never report `not-run` as pass.

## Stop conditions

Stop and report on missing package/manifest, hash mismatch against the registered manifest,
or tools unavailable for a required check (state which check could not run).

## Completion report

State project, channel, checks run and not run, findings by severity, gate-relevant result, and
the next valid action (typically `/product-revise` for open majors, otherwise continue to the
`listing`/`final-proof` stage).
