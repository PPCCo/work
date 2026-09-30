# Workflow: release and rollout order

Applies when changes span more than one repo. Agents prepare and describe the rollout; humans merge and deploy.

## Default deploy order (dependencies flow downstream)
1. **Contracts published** (immutable schema version to S3 by CI) and **DB migration (expand)**
2. **temporal-worker** (new consumers and workflow code, versioned, replay-tested)
3. **nestjs-api** (new endpoints and producers)
4. **nextjs-frontend** (uses the new API/contract)

Rule of thumb: whatever *reads* a new shape deploys before whatever *writes* it. Reverse the order for contract/cleanup stages.

## Pre-merge checklist (per PR set)
- All PRs linked, each states its position in the order and what it depends on.
- Gates green in every repo; `contracts:check` green; replay tests green for any changed workflow.
- Feature flag or safe-by-default behaviour for anything that can be deployed ahead of its counterpart.
- Migration is expand-only unless a human approved a destructive step.
- Runbook and event catalog updated; alerts exist for new failure modes.

## Rollback
- Application: redeploy the previous version; every change must tolerate this (that is why expand/contract exists).
- Workflow code: rollback is safe only if the previous worker build can replay histories created by the new one; verify with replay tests in the rollback direction when a patch was introduced.
- Data: forward-fix with a new migration; never edit applied migrations.
- Events: stop the producer first, leave consumers running to drain, then decide on DLQ reprocessing.

## Post-deploy
Watch the agreed signals (error rate, DLQ depth, consumer lag, workflow failures) for a defined period; record the result in the PR or ticket.
