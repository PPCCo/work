---
name: db-migration
description: Create and verify PostgreSQL schema migrations safely, using expand/contract so nestjs-api and temporal-worker can deploy independently. Use whenever a task adds, alters, renames or drops tables, columns, indexes or constraints, backfills data, or changes how the database is accessed - even if the request only says "store this new field" or "we need a table for...".
---

# DB migration

The `data-engineer` agent owns this. Read `rules/postgres.md` and `workflows/db-migration.md`. Migration tool and location come from `workspace.yaml` (`database.migration_tool`, `database.migrations_dir`).

## Procedure
1. **Map usage**: search both repos (real paths) for the tables and columns involved; list all readers and writers.
2. **Choose the stage** for this release:
   - *Expand*: add nullable columns/new tables/indexes; old code keeps working.
   - *Migrate*: backfill in batches, dual-write if needed.
   - *Contract*: drop old columns only after every deployed version stopped using them (a later release).
3. **Write the migration** (forward-only): `timestamptz`, UUID keys, `NOT NULL` and constraints added safely (add nullable, backfill, then enforce with `NOT VALID` + `VALIDATE`), `CREATE INDEX CONCURRENTLY` on existing tables, explicit `lock_timeout`/`statement_timeout`.
4. **Verify against a real PostgreSQL container**: apply from empty, apply over the previous release's schema with sample data, and run both services' integration tests against the new schema. Check that the previous application version still passes against it.
5. **Destructive or large changes** (drop, type change, big backfill): stop and get human approval with a written rollback and estimated lock/duration.
6. Update repository code and types, run `verify.sh` for each repo touched.

## Output
Handoff block: migration files, stage (expand/migrate/contract), readers/writers affected, deploy order (migration first), rollback story, test evidence.

## Do not
Run migrations on shared or production databases, edit an already-applied migration, combine a drop with the code that stops using it, or add a blocking index on a large table.
