---
name: modify-json-schema
description: Create or change a JSON Schema, the single source of truth for API validation, zod schemas, TypeScript types and Kafka/event payloads. Use whenever a field, payload, request, response, event or enum is added, removed, renamed or retyped, or when someone asks about schema compatibility - even if they phrase it as "add a field", "change the payload" or "update the model". Always run before touching generated zod or TypeScript types.
---

# Modify JSON Schema

Schemas live in `contracts.schema_dir` (see `workspace.yaml`). The `contract-engineer` agent owns this skill. Read `rules/json-schema.md` and `rules/kafka.md` first.

## Procedure
1. **Locate** the schema and every consumer: search all three repos (real paths) for the `$id`, the type name, and the field being changed. List consumers before editing.
2. **Classify the change** using this matrix (direction matters because producers and consumers deploy independently):

| Change | Class |
|---|---|
| Add optional property | Compatible |
| Add new schema or new event type | Compatible |
| Add enum value | Compatible for producers, **breaking for strict consumers**: deploy consumers first |
| Add required property, remove property, rename, change type, narrow constraints (min/max/pattern/enum removal), change `additionalProperties` to false | **Breaking** |
| Loosen constraints | Compatible for consumers, check producers and DB columns |
| Change meaning without changing shape | **Breaking** (treat as new version) |

3. **If breaking**: stop. Do not edit in place. Hand off to `architect` with the consumer list and follow `workflows/schema-change.md` (expand/contract or new major version). Continue only with an approved plan.
4. **Edit the schema**: keep `$id` stable within a major; bump the version field per the repo convention; reuse `$defs`; write `description` on every property; set `additionalProperties` deliberately; use `format` only if the validator enables it.
5. **Fixtures**: add a valid example for the new shape and an invalid example for each new constraint. Keep old valid examples; they prove backward compatibility.
6. **Regenerate** with `generate-contracts`, then **validate** with `validate-contracts` in all three repos. Fix consumers for real, never by widening types.
7. **Publish note**: if runtime consumers read the schema from S3, record that CI must publish the new immutable version (`rules/s3.md`). Do not publish manually.
8. If an event schema changed, update `standards/event-catalog.md`.

## Output
Handoff block: schema files changed, compatibility class, consumers affected per repo, required deploy order, fixtures added, S3 publish needed (yes/no).
