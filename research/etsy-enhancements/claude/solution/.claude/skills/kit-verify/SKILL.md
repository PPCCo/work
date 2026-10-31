---
name: kit-verify
description: >-
  Independently verify kit content by route — code verifiers (bingo, schedules, lists, exchanges, cut grids, keys), craft and safety desk-checks with make-test status, and trivia fact-checks — and write the kit content-verification report with verified counts and age-version differentiation evidence.
argument-hint: "<project-id> [--route code|desk-check|fact-check]"
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

# /kit-verify

## Goal

Produce the evidence the interior gate and the listing copy depend on: what exists, how many, and whether it is correct.

## Arguments

Use `$ARGUMENTS` exactly. A generator or author never signs off its own verification.

## Entry criteria

- State `CONTENT_VERIFICATION`; generated content registered; seeds recorded.

## Specialist delegation

- `content-verifier` (code route, via CLI), `craft-safety-reviewer` (desk-check route), `fact-checker` (fact-check route), `originality-auditor` and `child-safety-reviewer` (existing, for crafts and kids' content).

## Procedure

1. Run `ph_cli.py kit verify $ARGUMENTS`. It re-derives and checks every code-verifiable component: bingo boards distinct and fair; schedule fits its time window; shopping list equals the aggregate of card materials; gift exchange has no self-assignment or excluded pair and is solvable for the declared groups; cut grids hold the declared item counts at both page sizes; answer keys equal stored answers.
2. Delegate desk-checks to `craft-safety-reviewer` and fact-checks to `fact-checker`, each with exact artifact hashes and `finding.schema.json` output. Run them in parallel via `kit-verification-batch` when the plan is large.
3. Run `originality-auditor` on crafts and games, and `child-safety-reviewer` on kids' versions.
4. Aggregate to `verification/content-verification-latest.json`: per component `{verified_count, route, status, evidence_ids}`; per age version `{differences: [...]}`; make-test coverage (`n tested / n cards`); fact-check status counts.
5. Compare verified counts to `kit.yaml`. A shortfall is a **blocker** for the promise: either repair content or send a change request to `kit-architect`.
6. Run `ph_cli.py quality evaluate $ARGUMENTS`; ensure critical dimensions meet thresholds (originality, rights, accessibility, audience fit; plus safety and solution correctness where relevant).
7. Never set a status the underlying script or evidence did not produce.

## Required outputs

- `verification/content-verification-latest.json` (kit-extended), `verification/craft-safety-review.json`, `verification/fact-check-report.json`, findings list, make-test summary.

## Stop conditions

- Stop on blockers, a failing code verifier, hash mismatch, or when only the author could verify an item.

## Completion report

State the project, stage, agents used, verified counts per component and SKU, open findings by severity, untested crafts, and the next valid action (gate packet for the interior gate).
