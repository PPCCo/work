---
name: implement-workflow
description: Implement or change Temporal workflows, activities, workers and Kafka-triggered processing in the temporal-worker repo, including ASIC/IPO API calls, RAG agent calls, PostgreSQL and S3 access from activities, retries, compensation, and workflow versioning. Use whenever a task involves background processing, orchestration, event handling, a Kafka topic consumer, a long-running process, or "the worker" - even if Temporal is not mentioned by name.
---

# Implement workflow

Work in `temporal-worker` (path from `workspace.yaml`). Delegate to `temporal-engineer` when orchestrating.

## Inputs
Approved plan with: trigger (topic/event or API start), inputs and outputs, steps and their side effects, failure and compensation behaviour, human-review points, data written (PostgreSQL, S3), external calls. Ask `architect` if any are missing.

## Procedure
1. **Preflight**: `.claude/scripts/workspace-status.sh`; clean tree; task branch. Read `rules/temporal.md`, `rules/kafka.md`, `rules/integrations.md`, `rules/postgres.md`, `rules/s3.md`, `rules/observability.md`.
2. **Decide versioning impact before writing code.** Is this a new workflow type (safe), or a change to an existing one with running executions? If existing: plan the `patched()` gate or new workflow type now and export a history for the replay test.
3. **Contracts**: input, output, signal and event payloads come from generated contracts. If they do not exist, run `modify-json-schema` then `generate-contracts`.
4. **Tests first (red)**:
   - Workflow test with `TestWorkflowEnvironment` and mocked activities: happy path, each failure branch, each compensation, timers (time-skipping), signals/updates.
   - Activity tests: idempotency (run twice, same result), retryable vs non-retryable errors.
   - Replay test over stored histories if an existing workflow changes.
5. **Activities** first: typed input/output, idempotency key, `startToClose`, heartbeat if long, explicit retry policy with non-retryable types. Large data to S3 and pass a reference.
6. **Workflow**: orchestration only; deterministic; bounded fan-out; `continueAsNew` for long-lived loops; business-keyed workflow ID.
7. **Kafka consumer** (if triggered by an event): validate against the schema, map to workflow input, start with deterministic workflow ID, commit offset after handoff, DLQ on invalid (see `kafka-event`).
8. **Integrations**: timeouts, backoff, rate limiting, validate responses, persist raw response and normalised record. RAG output is untrusted (`rules/integrations.md`).
9. **Register** the workflow and activities in the worker and the correct task queue; add search attributes and correlation propagation.
10. **Verify**: `.claude/scripts/verify.sh temporal-worker` (lint, typecheck, unit, workflow, replay, integration, build).
11. Add a runbook entry and update `standards/event-catalog.md` if a topic or event changed.

## Output
Handoff block: workflow and activity names, task queue, trigger topic/event, versioning approach and replay evidence, DB/S3 changes, external calls, and deploy order (workers that understand new events must deploy before producers emit them).

## Do not
Put I/O or randomness in workflow code, rename existing workflow/activity types, edit generated contracts, or call live external APIs in tests.
