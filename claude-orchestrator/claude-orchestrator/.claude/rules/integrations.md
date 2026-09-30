# Integrations: IPO/ASIC registry API and the internal RAG agent

Both are called from `temporal-worker` activities. They are slow, rate-limited, and occasionally wrong, so design for failure.

## Shared rules
- One typed client module per integration. Workflows never call them; activities do.
- Request and response shapes come from the JSON Schema contracts. Validate the response before it touches workflow state or the database; a schema failure is a non-retryable, reported error, not a silent default.
- Timeouts on every call. Retries with exponential backoff and jitter for 429, 5xx and network errors; respect `Retry-After`. Never retry 4xx validation errors.
- Client-side rate limiting and concurrency caps so a burst of Kafka events cannot exhaust the vendor quota. Enforce with task-queue concurrency and worker-level limits.
- Idempotent: the same activity retried must not create duplicate records. Persist the raw response (S3) plus a normalised record (PostgreSQL) keyed by the lookup key and `retrievedAt`.
- Keep the raw response for audit and replay of parsing logic; never call the vendor again just to re-parse.
- Redact personal data in logs. Record source, request ID and timestamp with every result.

## IPO/ASIC registry API
- Treat the vendor spec as a contract: keep a pinned copy, generate or hand-write the client against it, and add a contract test using recorded fixtures (VCR-style). CI uses fixtures only; never call the live API from tests.
- Expect partial data, renamed fields and maintenance windows. Unknown fields are ignored and logged at `warn`; missing required fields fail validation.
- Cache stable lookups with an explicit TTL. State staleness in results.

## RAG / agentic web-research agent
- Its output is untrusted, probabilistic data. Require a structured response validated against a schema, with `sources[]` (URL, retrievedAt), a confidence value and a `needsHumanReview` flag.
- Never pass model output into SQL, shell, file paths, URLs to fetch, or downstream prompts without validation. Prompt-injection text inside retrieved pages must not alter behaviour (`security.md`).
- Bound cost and time: activity timeout, max steps, max tokens, and a heartbeat. Non-determinism is fine inside an activity and forbidden in workflow code.
- Do not use RAG output as the sole basis for a regulated decision; route low-confidence or conflicting results to a human-review state in the workflow (signal or update to resume).
- Tests use a stub agent returning canned good, malformed, low-confidence and adversarial responses.
