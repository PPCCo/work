---
name: kit-new
description: >-
  Create a new digital-kit project (Etsy printable kit family) with engine-derived design policy, a seeded kit manifest skeleton, and a season window — without performing any external action.
argument-hint: "--topic <t> --occasion <o> --audience <band> [--season-target YYYY-MM-DD] [--latest-list-date YYYY-MM-DD] [--project-id <id>]"
user-invocable: true
effort: high
model: '@bedrock-eus1/us.anthropic.claude-sonnet-5'
allowed-tools:
  - Read
  - Write
  - Bash
  - "Bash(${CLAUDE_PROJECT_DIR}/.venv/bin/python3 .claude/scripts/ph_cli.py *)"
---

# /kit-new

## Goal

Create a `digital-kit` project that is ready for `/kit-seasonal-plan` and `/kit-brief`.

## Arguments

Use the invocation arguments exactly as `$ARGUMENTS`. Do not invent dates, approvals, prices, or evidence. Ask (or, if unattended, state the assumption) when `--season-target` is missing for a seasonal product.

## Entry criteria

- Topic, occasion, and primary audience band are supplied by the human.
- The framework has the `digital-kit` family installed (`framework validate` passes).

## Procedure

1. Run `${CLAUDE_PROJECT_DIR}/.venv/bin/python3 .claude/scripts/ph_cli.py project init --topic "<topic>" --audience <band> --product-type digital-kit --formats digital-pdf` (add `--project-id` and `--working-title` if supplied). Channels default to `etsy` (edit `sales_channels` to `["etsy"]` if the template added `kdp`).
2. Run `ph_cli.py kit init <project-id> --occasion "<occasion>" --season-target <date> --latest-list-date <date>` to seed `kit/kit.yaml` from `templates/kit.yaml` with placeholders only.
3. Confirm `production.design` was derived (rule 20) and `colour_interior` is true (rule 22 digital editions).
4. Run `ph_cli.py project status <project-id>` and `project plan <project-id>`; record the first valid action.
5. Do not generate content, listings, or images in this skill.

## Required outputs

- New `projects/<id>/` with `project.yaml`, `state.json`, `events.ndjson`.
- `kit/kit.yaml` skeleton (status `draft`) registered as an artifact.
- A one-paragraph summary: project id, band, season window, next action (`/kit-seasonal-plan`).

## Stop conditions

- Stop on an invalid audience band, a duplicate project id, or a missing season date for a seasonal occasion that the human cannot supply; report the exact recovery action.

## Completion report

State the project, current stage, files created with hashes, validation results, open questions, and the next valid action.
