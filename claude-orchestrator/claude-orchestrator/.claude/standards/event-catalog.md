# Event catalog

Single register of Kafka topics and events. Update in the same PR as any topic or event change (`workflows/kafka-event-change.md`). Schemas are in `contracts.schema_dir`; this file links to them and never copies them.

| Topic | Event type | Schema (`$id` / version) | Key | Producer | Consumer(s) and group | Starts workflow | DLQ | Retention | Owner |
|---|---|---|---|---|---|---|---|---|---|
| `<domain>.<entity>.<event>.v1` | `<entity>.<event>` | `<id> 1.0.0` | `<entityId>` | `nestjs-api` | `temporal-worker` (`worker.onboarding`) | `<WorkflowType>` | `<topic>.dlq` | 7d | `<team>` |

## Workflows
| Workflow type | Task queue | Trigger | ID pattern | Versioning notes | Runbook |
|---|---|---|---|---|---|
| `<WorkflowType>` | `<queue>` | `<topic or API>` | `<prefix>:<businessKey>` | `<patches in flight>` | `<link>` |

## Conventions
Topic naming, envelope and compatibility rules are in `rules/kafka.md`. Do not list payload fields here.
