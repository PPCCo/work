# Observability rules

Goal: given one customer complaint, find the HTTP request, the Kafka message, the workflow execution and the DB rows in under five minutes.

## Correlation
One `correlationId` (UUID) created at the edge and carried everywhere:
- HTTP: `x-correlation-id` header in and out; generate if absent.
- Kafka: envelope `correlationId` and message header `correlation-id`; `causationId` is the `eventId` that triggered this one.
- Temporal: propagated with a header interceptor; also set as a search attribute together with the business key (for example `OrganisationId`).
- Logs: every line includes `correlationId`, `service`, and where relevant `workflowId`, `runId`, `eventId`.
- DB and S3: store `correlation_id` on rows or object metadata written by a workflow.

## Logging
Structured JSON only (pino or the repo's logger). Levels: `error` needs a human, `warn` is recoverable and unexpected, `info` is a business milestone, `debug` is off in production. No PII and no payload dumps (see `security.md`). Never log and rethrow the same error at every layer; log once where it is handled.

## Metrics and tracing
- OpenTelemetry for traces where the repo already has it; propagate W3C `traceparent` over HTTP and Kafka headers.
- Minimum metrics: request rate/latency/errors per route, Kafka consumer lag and DLQ depth, workflow start/success/failure counts and latency per type, activity retry counts, external API latency and error rate, DB pool saturation.
- Alerts are on symptoms (failed workflows, DLQ growth, lag) and link to a runbook.

## Runbooks
Each new workflow, topic or integration adds a short runbook entry: what it does, how to see it failing, how to retry or replay safely, who owns it.
