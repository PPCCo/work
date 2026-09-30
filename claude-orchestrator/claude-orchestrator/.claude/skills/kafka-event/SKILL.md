---
name: kafka-event
description: Add or change a Kafka topic, event type, producer or consumer - including event envelope, schema, key, DLQ, idempotency and the mapping from an event to a Temporal workflow start. Use whenever a task mentions a topic, event, message, publish, consume, producer, consumer, DLQ, or "when X happens do Y" in this system.
---

# Kafka event

Follow `rules/kafka.md` and `workflows/kafka-event-change.md`. Coordinate `contract-engineer` (schema), `api-engineer` or `temporal-engineer` (producer/consumer), and `devops-engineer` (topic provisioning).

## Procedure
1. **Define the event** in a short spec: topic name (`<domain>.<entity>.<event>.v<major>`), key, trigger, producer, consumers, expected volume, ordering needs, retention, and failure handling.
2. **Schema**: run `modify-json-schema` for the payload (and envelope if new). Fixtures required.
3. **Catalog**: add or update the row in `standards/event-catalog.md` before code.
4. **Topic provisioning**: add topic config (partitions, retention, DLQ topic) to the repo's infra-as-code or compose file; note it for the human if creation is outside the repo.
5. **Producer** (usually `nestjs-api`): envelope with `eventId`, `correlationId`, `causationId`; outbox if tied to a DB write; idempotent producer; headers set. Test the emitted envelope against the schema.
6. **Consumer** (usually `temporal-worker`): validate, dedupe via deterministic workflow ID, start workflow, commit offset after handoff, DLQ with error headers. Tests: duplicate, out-of-order, malformed, crash-before-commit.
7. **Rollout order**: consumer (accepts new event) deploys before producer (emits it). For a breaking change use a new `vN` topic and dual-publish.
8. `verify.sh` in every repo touched; emit the handoff block including topic, schema version, and deploy order.

## Do not
Reuse a topic for a different meaning, key on PII, put business logic in a consumer, or change a topic's name or partition key in place.
