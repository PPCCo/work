---
name: kit-seasonal-plan
description: >-
  Compute season slack for a kit from explicit dates, gather dated evidence for seasonal demand and competition, and recommend a fast path (ship Standard first, reduce versions) when time is short — never skipping compliance, release, rights, or safety checks.
argument-hint: "<project-id> --today YYYY-MM-DD"
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

# /kit-seasonal-plan

## Goal

Make the timeline explicit and honest: how many days remain, how many the work needs, and what to cut if the two do not meet.

## Arguments

`$ARGUMENTS` must include `--today` (the current date, supplied by the caller or taken from the session's date source and echoed back). The core scripts never read the clock.

## Entry criteria

- `kit.yaml` has `season.target_date` and `season.latest_list_date` (human-set or cited).

## Specialist delegation

- `market-analyst` for dated demand/competition evidence (rule 24 forbids undated "peak" claims).

## Procedure

1. Run `ph_cli.py kit seasonal $ARGUMENTS`. It reports `days_to_latest_list`, remaining-effort estimate by state, human-gate allowances, upload allowance, and `slack_days`.
2. Delegate to `market-analyst` for evidence: Etsy competitor counts/pricing for the occasion, any dated indicator of when buyers search and buy, and what late-season entrants look like. Record each source with retrieval date; mark gaps as unknown.
3. If `slack_days ≥ 0`: write the plan (milestones by date) and stop.
4. If `slack_days < 0`: compute the fast path. Candidate cuts, in order: defer the Expanded SKU; reduce age versions or themes to those with verified content; drop optional components; run variant builds in parallel. Show the recomputed slack for each option.
5. Present the options to the human (`AskUserQuestion` when interactive; otherwise record the recommended option and stop at the decision). Never remove compliance, release, rights, safety, or Etsy preflight steps to recover time.
6. Write `kit/seasonal-plan.md` and `kit/seasonal-plan.json`; register artifacts.

## Required outputs

- Slack report (inputs and arithmetic shown), milestone dates, evidence log with retrieval dates, decision options.

## Stop conditions

- Missing or inconsistent dates; unreachable evidence sources for a claim the plan depends on (record as unknown); slack still negative after the fast path.

## Completion report

State the project, `--today` used, slack, chosen or recommended path, evidence confidence, and the next valid action.
