---
name: kit-generate
description: >-
  Generate all kit components — deterministic generators for bingo, schedules, shopping lists, gift exchanges, checklists, tags, and answer keys, and specialist agents for crafts, games, keepsakes, and guides — in batches by component and age version, registering every output as an artifact.
argument-hint: "<project-id> [--component <id>] [--age-version <id>]"
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

# /kit-generate

## Goal

Produce every component's content once per required age version and theme, in controlled batches, ready for verification.

## Arguments

Use `$ARGUMENTS` exactly. A component filter runs a single batch; no filter runs the full plan via the workflow `kit-content-fanout`.

## Entry criteria

- Niche approved; `kit.yaml` registered; briefs exist; state `CONTENT_GENERATION`.
- Rights status of fonts and assets in briefs is cleared or pending-with-plan (not unknown).

## Specialist delegation

`craft-designer`, `party-game-designer`, `keepsake-designer`, `kit-architect` (host guide, Start-Here, Terms-of-Use drafts). Deterministic generators run through the CLI.

## Procedure

1. Run `ph_cli.py project status $ARGUMENTS`; confirm hashes and state.
2. Group components into batches: (A) deterministic — bingo, schedule, shopping_list (after craft cards exist), gift_exchange, checklist, cutgrid, answer_key; (B) crafts and gift projects per age version; (C) games and trivia; (D) keepsakes and templates; (E) guides and terms. Order: B before A's shopping list; C before A's answer keys.
3. For each deterministic component run `ph_cli.py kit generate <id> --component <cid> [--seed <n>]` (project-derived seeds; record them). Never hand-write pairings, boards, or key tables.
4. For authored components, delegate in parallel per age version with exact briefs, schemas, and acceptance tests. Use the workflow `kit-content-fanout` for the full plan.
5. Register every artifact with provenance (agent, seed, source hashes, rights status).
6. Do not verify here. Hand off to `/kit-verify`.

## Required outputs

- Generated batches under `content/kit/**` per component and age version, with a manifest listing artifact ids and hashes.

## Stop conditions

- Stop on stale hashes, schema failure, rights-unknown assets, or an agent returning ESCALATE; report recovery actions.

## Completion report

State the project, stage, agents used, components completed vs remaining, seeds used, artifacts with hashes, and next valid action (`/kit-verify`).
