---
name: implement-api
description: Implement or change NestJS REST API functionality in the nestjs-api repo - endpoints, modules, services, repositories, guards, validation, error handling, and Kafka producers or workflow starts from the API. Use whenever a task adds or modifies an API route, backend business logic, or API-side persistence, even if the user only says "add an endpoint", "expose this over REST", or "the backend needs to...".
---

# Implement API

Work in the `nestjs-api` repo at the path given in `workspace.yaml` (use the real sibling path for searching; symlinks may not be traversed by search tools). Delegate to the `api-engineer` agent when orchestrating.

## Inputs
An approved plan from `plan-feature` that states: endpoints, schemas involved, DB impact, events emitted, workflow started, auth requirements. If any of those is missing, stop and ask `architect` rather than guessing.

## Procedure
1. **Preflight**: run `.claude/scripts/workspace-status.sh`; confirm a clean tree and the task branch exists (`rules/git.md`). Read `rules/nestjs.md`, `rules/typescript.md`, `rules/security.md`, `rules/postgres.md`.
2. **Contracts first**: confirm request/response schemas exist and generated types are current. If not, run `modify-json-schema` then `generate-contracts`. Never write DTOs by hand that duplicate a schema.
3. **Persistence**: if tables or columns change, use `db-migration` first; the API must run against both old and new schema during rollout.
4. **Tests first (red)**: write failing tests for the happy path, each validation failure, authorisation failure, conflict/idempotency, and the not-found case.
5. **Implement** in layers: repository, service, controller, module wiring. Keep controllers thin. Add the guard and ownership check before writing business logic.
6. **Events and workflows**: if the API emits an event, use the outbox pattern and the envelope from `rules/kafka.md` (see `kafka-event`). If it starts a workflow, use a deterministic workflow ID and treat "already started" as success.
7. **Observability**: correlation ID flows in and out; structured logs without PII; health/readiness updated if a new dependency was added (`rules/observability.md`).
8. **Verify**: `.claude/scripts/verify.sh nestjs-api` (lint, typecheck, unit, integration, contract tests, build). Fix failures at the cause.
9. **Self-review** the diff against `standards/definition-of-done.md`, then emit the handoff block.

## Output
Handoff block listing: endpoints added/changed, schemas used, migrations, events, workflow starts, required deploy order, and the verify output summary.

## Do not
Hand-edit generated contract files, call the database from controllers, add an endpoint without auth, or return raw internal errors.
