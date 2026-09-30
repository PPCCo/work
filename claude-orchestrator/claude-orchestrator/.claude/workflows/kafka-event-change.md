# Workflow: new or changed Kafka event / topic

Use when adding a topic, changing an event payload, or changing who consumes what. Skill: `kafka-event`.

1. **Spec** (architect): trigger, producer, consumers, key, ordering, volume, retention, DLQ, failure handling. Risk tier 2 if a topic is new or breaking.
2. **Contract** (contract-engineer): schema and fixtures via `modify-json-schema`; envelope fields per `rules/kafka.md`. Update `standards/event-catalog.md`.
3. **Consumer first** (temporal-engineer): validate, dedupe via deterministic workflow ID, start workflow, commit after handoff, DLQ path, tests for duplicate / out-of-order / malformed / crash-before-commit.
4. **Producer** (api-engineer or temporal-engineer): envelope, outbox if tied to a DB write, idempotent producer, headers, test the emitted message against the schema.
5. **Provisioning** (devops-engineer): topic and DLQ config, ACLs, retention, compose/dev config. Flag anything a human must create.
6. **Verify** in every repo touched; integration test producer to consumer against a local broker container if available.
7. **Review**: `reviewer` (messaging checklist). Add `security-reviewer` if the payload contains personal data.
8. **Rollout**: consumer deploys before producer. Breaking change means a new `vN` topic with dual publish, then retire the old topic only after lag is zero and consumers are gone.
