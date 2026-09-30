# Agent operating protocol

How autonomous agents work in this workspace. Goal: maximum autonomy where mistakes are cheap, hard stops where they are not.

## Risk tiers
| Tier | Examples | Autonomy |
|---|---|---|
| 0 | Docs, comments, tests only, formatting | Full auto |
| 1 | Internal logic, UI, compatible schema change, non-breaking endpoint | Auto after a plan; human reviews PR |
| 2 | Breaking schema, DB migration, new/changed topic, workflow versioning, auth, personal data | **Plan approval before code**, reviewer and security-reviewer required |
| 3 | Production infra, credentials, data deletion, disabling controls | **Human only.** Agents prepare a proposal, never execute |

Classify at planning time; if unsure, go one tier up. Reclassify if the work turns out riskier.

## Standard loop
1. `workspace-sync` (clean tree, branch, baseline) -> 2. `understand-feature` -> 3. `plan-feature` (states tier, repos, order, contracts, DB, events, workflow versioning, test plan) -> 4. [Tier 2: wait for human approval] -> 5. implement in dependency order: contracts, data, worker, API, frontend -> 6. `run-tests` / `verify.sh` -> 7. `review-changes` (`reviewer`, plus `security-reviewer`) -> 8. `create-commits` -> 9. `prepare-pr` (evidence block).

## Stop and ask when
- The tree is dirty with work you did not make, or a baseline gate was already failing.
- A requirement is ambiguous in a way that changes contracts, data or deploy order.
- The change needs a breaking schema, destructive DB step, or anything Tier 3.
- The same failure survives three fixes (write a diagnosis note; use `diagnose-failure`).
- A gate can only pass by weakening a test, type, lint rule or security control.

## Hard prohibitions
Force-push, push to protected branches, `--no-verify`, editing generated files or lockfiles by hand, editing applied migrations, running anything against shared or production systems, reading or printing `.env` or credentials, installing dependencies without stating why, and editing outside the repos declared in `workspace.yaml`.

## Handoff block (between agents and into the PR)
```
TASK: <id>            FROM: <agent>  TO: <agent>
REPOS TOUCHED: ...    BRANCH: ...
CONTRACTS: schemas changed, compat class, regenerated Y/N
DATA: migrations, stage, deploy order
EVENTS/WORKFLOWS: topics, workflow types, versioning approach
DONE: what is implemented and verified (with gate output)
OPEN: what is left, risks, assumptions made
NEXT: exact next step for the receiving agent
```

## Working agreements
- Delegate by ownership (contracts to `contract-engineer`, schema to `data-engineer`, and so on); do not edit another agent's area.
- Prefer the smallest change that meets the requirement; no drive-by refactors in a feature PR.
- Record assumptions explicitly in the plan or handoff. Do not silently guess.
- Keep task notes (spec, plan, handoffs, verification log) in the task folder used by `plan-feature`.
