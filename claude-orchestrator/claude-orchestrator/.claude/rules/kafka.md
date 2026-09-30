# Kafka rules

The client library is whatever the repo already uses. These rules are library-agnostic.

## Topics and events
- Topic name: `<domain>.<entity>.<event>.v<major>`, lowercase, dot-separated (for example `onboarding.organisation.submitted.v1`). Dead-letter: `<topic>.dlq`.
- Never rename a topic or change partition semantics in place. A breaking change is a new `vN` topic, dual-published during migration.
- Message **key** is the business entity ID so one entity's events stay ordered. Never use PII as a key.
- Every message uses the standard envelope:

```json
{
  "eventId": "uuid-v7",
  "eventType": "organisation.submitted",
  "schemaVersion": "1.2.0",
  "occurredAt": "RFC3339 UTC",
  "correlationId": "uuid",
  "causationId": "uuid",
  "producer": "nestjs-api",
  "payload": { }
}
```
- `payload` is validated against the JSON Schema for `eventType` + `schemaVersion`. The envelope itself is also a schema. Both live in the contracts source of truth, never inline.
- Every topic is registered in `standards/event-catalog.md` (producer, consumers, key, schema, retention, DLQ).

## Producers
- `acks=all`, idempotent producer enabled, bounded retries with backoff.
- DB change plus event must be atomic: write the event to an `outbox` table in the same transaction, and a relay publishes it. Consumers must still be idempotent (delivery is at-least-once).
- Set headers: `correlation-id`, `event-type`, `schema-version`.

## Consumers
- **At-least-once, so idempotent.** Dedupe on `eventId` (or start the workflow with a deterministic workflow ID derived from it and treat "already started" as success).
- Commit offsets only after the work is durably handed off (workflow started, row written).
- Validate before acting. Invalid messages are never retried forever: send to the DLQ with the original bytes, error, topic, partition, offset and attempt count as headers. Alert on DLQ depth.
- Poison-message safe: one bad message must not block a partition. Transient failures use bounded retry with backoff; Temporal handles business retries after handoff.
- Consumer groups named `<service>.<purpose>`. Rebalances must not cause duplicate side effects (see idempotency).
- Consumers contain no business logic. They validate, map event to workflow input, start the workflow, commit.

## Evolution
Additive, optional fields only within a major version. New required field, removed field, type change, enum removal or semantic change means a new major. See `json-schema.md` and `workflows/kafka-event-change.md`. Deploy consumers that accept the new shape **before** producers emit it.

## Testing
- Schema fixtures (valid/invalid) per event type.
- Consumer tests: duplicate delivery, out-of-order delivery, malformed payload to DLQ, and crash between handoff and commit.
- Integration with a Kafka-compatible container (Redpanda or Kafka) where the repo already provides one.
