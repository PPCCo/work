# Workflow: schema change

Use when a JSON Schema changes (API shape, event payload, workflow input/output). Because API, worker and frontend deploy independently, a schema change is a **rollout plan**, not just an edit.

## Roles
`architect` (plan) -> `contract-engineer` (schema, generation) -> `data-engineer` (if persisted) -> `api-engineer` / `temporal-engineer` / `frontend-engineer` (consumers and producers) -> `test-engineer` -> `reviewer` (+ `security-reviewer` if personal data) -> human.

## 1. Classify (skill: `modify-json-schema`)
Compatible, compatible-for-producers-only (enum add), or breaking. Risk tier: compatible = Tier 1, breaking = Tier 2 (plan approval required, `standards/agent-operating-protocol.md`).

## 2a. Compatible change (single release)
1. Schema + fixtures -> regenerate -> validate in all repos.
2. Implement the **consumers first** (accept the new optional field / enum value), then producers.
3. Deploy order: consumers, then producers, then frontend.

## 2b. Breaking change (expand / migrate / contract across releases)
| Release | Schema | Consumers | Producers |
|---|---|---|---|
| **Expand** | Add new field/shape/version alongside the old (new optional field, or a new `v2` schema / topic) | Accept old **and** new | Keep emitting old; optionally dual-write |
| **Migrate** | Both valid | Prefer new | Emit new (or both); backfill persisted data |
| **Contract** | Remove old, bump major | New only | New only |

Each stage is its own PR set with its own gates. Never contract until every deployed consumer and in-flight Temporal execution has stopped depending on the old shape.

## 3. Persisted and in-flight data
- PostgreSQL columns derived from the schema follow `workflows/db-migration.md`.
- Temporal: in-flight executions carry old-shape inputs in history. Handle both shapes in activities, or version the workflow (`rules/temporal.md`). Replay tests are required.
- S3: published schema versions are immutable; publish the new version from CI (`rules/s3.md`).

## 4. Verify
- `validate-contracts` green in all three repos; `contracts:check` passes in CI.
- Old valid fixtures still validate under the compatible path; new fixtures validate under the new shape.
- Consumer tests cover both shapes during the expand and migrate stages.

## 5. Deliver
PR per repo with merge order stated (`workflows/release.md`), compatibility class, stage, consumers affected, rollback note. Update `standards/event-catalog.md` for event changes.
