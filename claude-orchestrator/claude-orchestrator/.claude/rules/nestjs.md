# NestJS API rules (`nestjs-api`)

Applies to all work in the `nestjs-api` repo. Shared TypeScript rules are in `typescript.md`.

## Structure
- One feature module per bounded context: `*.module.ts`, `*.controller.ts`, `*.service.ts`, `*.repository.ts`, `dto/` (only for non-schema shapes), `*.spec.ts`.
- Controllers are thin: parse, authorise, call a service, map the result. No business logic, no SQL.
- Services hold business logic and depend on repository interfaces. Repositories are the only layer that talks to PostgreSQL.
- Cross-module access goes through the exported service, never another module's repository.

## Contracts and validation
- Request and response validation comes from the generated JSON Schema contracts, enforced by a shared validation pipe (Ajv). Do not hand-write a class-validator DTO that duplicates a schema.
- Validate at the boundary, then trust typed values inside. Responses are validated in tests, and optionally in non-production environments.
- Generated contract files are read-only. Request changes via `contract-engineer`.

## API design
- Versioned routes (`/v1/...`). Plural nouns, HTTP verbs used correctly, correct status codes (201 on create, 204 on empty, 409 on conflict, 422 on semantic validation failure).
- Errors are `application/problem+json` (RFC 9457) via one global exception filter. No stack traces or internal IDs in client responses.
- Cursor pagination for lists. Deterministic ordering with a unique tiebreaker.
- Non-idempotent `POST`s that trigger workflows or events accept an `Idempotency-Key` header and dedupe on it.
- Starting a Temporal workflow from the API: use a deterministic business-keyed workflow ID, handle "already started" as success, return 202 with a status resource.

## Config, lifecycle, ops
- Config loaded and validated once at boot (fail fast); no `process.env` reads outside the config module.
- Enable shutdown hooks; drain HTTP, Kafka producer, DB pool in order.
- Health endpoints: liveness (process) and readiness (DB, Kafka, Temporal reachable).
- Structured logging with correlation ID from `rules/observability.md`.
- If the API writes to PostgreSQL and publishes an event in one operation, use the transactional outbox pattern (see `rules/kafka.md`). Never write then publish and hope.

## Security
Every route has an explicit guard. Authorisation checks resource ownership or tenancy, not only identity. See `security.md`.

## Testing
- Unit: services with mocked repositories.
- Integration: controllers plus real PostgreSQL (container) through the Nest testing module and supertest.
- Contract: every endpoint's happy path and one failure path validated against its schema.
- Kafka producers: test the envelope and headers, not the client library.
