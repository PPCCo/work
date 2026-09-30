# Workflow: database migration

Use for any PostgreSQL schema or data change. Skill: `db-migration`. Owner: `data-engineer`.

1. **Plan** (architect + data-engineer): which tables, who reads/writes (API, worker, both), expand/migrate/contract stage, data volume, lock risk. Destructive or large: Tier 2, written rollback, human approval.
2. **Migration PR (expand)**: additive and backward compatible only. Must pass with the **currently deployed** app versions.
3. **Application PR(s)**: API and worker updated to use the new structure (dual-write or read-new-fallback-old if migrating). Merge only after the migration has been deployed.
4. **Backfill** (if needed): batched, resumable, idempotent, throttled, run as a Temporal workflow or a scripted job; never one giant transaction.
5. **Enforce**: add `NOT NULL`/constraints after backfill using `NOT VALID` then `VALIDATE CONSTRAINT`.
6. **Contract PR (later release)**: drop old columns/tables only after no deployed version references them and a human confirms.

## Checks
- Applied from empty and on top of a populated snapshot of the previous schema.
- Integration tests of both services pass on the new schema, and previous app version passes too.
- No long locks: `lock_timeout`, concurrent index builds, `SET LOCAL statement_timeout`.
- Deploy order recorded: migration -> worker -> API -> frontend.
