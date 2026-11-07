# EON Entity Onboarding: Architecture Review & Requirements Specification

Nov 7, 2026 · @Q

## Executive summary

The overall shape is right (SO as system of record, Temporal as orchestrator, one schema driving form and API), but five contradictions must be resolved before build: where drafts live, what the statuses mean, who may approve, how SO events become workflow signals, and how the POBO authenticates.

**Top ten findings**

1. **Drafts vs SO validation.** SO validates every write against orgType schemas, yet drafts must accept partial or malformed data. Both cannot be true. Recommendation: EON owns a draft store; SO receives only stage-valid data.
2. **Status model is overloaded.** It mixes lifecycle (RM\_APPROVED), enrichment provenance (IPO\_ENRICHED) and waiting states. POBO\_NOTIFIED means both "first notified" and "more information requested". Recommendation: an explicit state machine with a new INFO\_REQUESTED state; enrichment tracked as events, not states.
3. **Status in PATCH is a privilege-escalation path.** Any PATCH caller, including the AI co-pilot, could set RM\_APPROVED or POBO\_SUBMITTED. Recommendation: separate command endpoints; approval only with an RM's delegated token and a hash of the approved data.
4. **"Login credentials in email" is not bank-grade.** Recommendation: single-use expiring link, MFA, and verification that the POBO is authorised to act for the entity.
5. **The Kafka-to-Temporal bridge is under-specified.** Duplicates, ordering, and echoes of EON's own SO writes will cause double notifications. Recommendation: inbox deduplication, version-monotonic checks, `signalWithStart`, and a reconciliation sweeper.
6. **"Atomic promotion" is not atomic.** EON validation, SO write and Temporal signal are three systems. Recommendation: one SO call carrying data and status, with an expected-version precondition and an idempotency key.
7. **Schema governance is missing.** Browser, EON and SO are three validators with no version pinning, no UI layout metadata, and no home for cross-field business rules.
8. **Document tracking in Temporal state will not scale.** Workflow history is not a query store. Recommendation: a document register in the EON database, malware scanning, authorised download, and data-dependent document requirements.
9. **Compliance is silent.** No audit trail, retention, POBO declaration, privacy notice for public-source collection, or human verification of AI-enriched data.
10. **The API surface is too thin.** About 40 endpoints are needed (search, dry-run validation, enrichments, documents, case-handler commands, admin); section 8 lists them.

Two text problems also need fixing: the requirement ending "Also note that when" is truncated, and "IPO API" is never defined (ABR, ASIC, or an internal service?).

**Recommended solution in one paragraph.** A Next.js wizard and a stateless EON API sit in front of an anti-corruption layer for SO. EON keeps drafts, a document register, audit and notification config in PostgreSQL, and caches only immutable or event-invalidated data in Redis. A single event bridge turns SO Kafka events into idempotent Temporal signals, with one long-running workflow per ServiceOrderId. Schemas are two-tier (structure plus completeness), versioned and pinned per case, and fronted by a UI layout descriptor and a shared rules library.

## Critical review: ambiguities and contradictions

Twenty-two statements are ambiguous or contradict each other; A1 to A10 block the build and need an owner and a decision first.

| ID | Requirement as written | Issue | Proposed resolution |
| --- | --- | --- | --- |
| A1 | SO validates every write against orgType schemas; the server must accept partial, malformed or missing draft data | Both cannot hold. SO would reject draft saves unless it runs a relaxed schema nobody has defined. | EON owns the draft store. SO receives data only at stages where its schema applies. Ask the SO squad whether a draft-tolerant schema variant exists. |
| A2 | "Each request type has a different schema" versus "orgType JSON Schemas" | Unclear whether SO has one request type with many orgType schemas, or one request type per orgType. This drives registry keys and versioning. | One request type (ENTITY\_ONBOARDING); schema ID = orgType + version. Confirm with SO. |
| A3 | Statuses IPO\_ENRICHED, COPILOT\_ENRICHED, "etc." | Enrichments are neither ordered nor exclusive, and the list is open-ended. Legal transitions are undefined. | Publish a closed status list and transition table; track enrichment as events with provenance. |
| A4 | POBO\_NOTIFIED is reused when more information is requested | One status, two meanings. The workflow cannot tell a first notice from a re-request, and timers and UI differ. | Add INFO\_REQUESTED and UNDER\_REVIEW. POBO\_NOTIFIED means first notice only. |
| A5 | Every PATCH updates SO; RM approves by sending status RM\_APPROVED | Approval and submission, both privileged acts, travel on a generic data PATCH. The co-pilot's token could set them. | Command endpoints for approve and finalize. PATCH can never change lifecycle status. |
| A6 | "Atomic Promotion" to POBO\_SUBMITTED | EON validation, the SO write and the Temporal signal are three systems; true atomicity is impossible. | Define it as one SO write carrying data and status, with an expected-version precondition and an idempotency key. Temporal reacts to the resulting event. |
| A7 | Temporal listens for REJECTED and COMPLETE | Nobody is said to set them. The case handler appears once. EON may receive transitions it did not make. | Treat SO as source of truth and accept transitions from any channel via events. Add case-handler commands only if EON hosts the console. |
| A8 | Workflow starts when the request is created as DRAFT | Unclear whether the EON API or the Kafka consumer starts it. Two paths race and duplicate. | One path: the consumer calls `signalWithStart` with workflowId = ServiceOrderId. A sweeper catches misses. |
| A9 | A Kafka consumer bridges SO events into Temporal | Delivery is at-least-once. Ordering, and echoes of EON's own SO writes, are unspecified. | Partition key = ServiceOrderId; inbox table keyed by eventId; drop events whose record version is not newer than the last processed. |
| A10 | Login credentials are emailed to RM and POBO | Credentials in email are phishable and replayable. The POBO's authority to act is never verified. RMs already have SSO. | Single-use link plus MFA through a customer identity service. No secrets in email. Explicit authority check. RMs get a deep link only. |
| A11 | Co-pilot fetches IPO and web data; Temporal also has "data enrichment" child workflows | Enrichment has two owners, with duplicate calls and conflicting writes. | Co-pilot enriches before approval through the API. Temporal enrichment, if kept, only refreshes stale data after approval. |
| A12 | "IPO API" | Undefined. Source, licence, rate limits and failure behaviour are unknown. | Name the source and record its SLA, terms and fallback. |
| A13 | A source field is kept for each field | No shape, location or precedence rule. Inline fields would fail schemas that forbid extra properties. | Sidecar provenance map keyed by JSON Pointer, plus precedence rules (see the form design section). |
| A14 | Redis "for latency reduction and performance" | What is cached, for how long, how it is invalidated and how PII is protected are all unstated. | Cache schemas (immutable per version), SO reads (event-invalidated) and idempotency keys. Never cache the draft of record. Encrypt PII. |
| A15 | The orgType schema specifies required documents | JSON Schema cannot say "document X is required if field Y is Z" without a custom vocabulary. | A document-requirements manifest per orgType version, evaluated against the data by a resolver. |
| A16 | Temporal tracks document status and Documentum links | Workflow history has size limits and is not a query store. The form cannot read it at scale. | A document register table in the EON database. The workflow holds IDs and orchestrates. |
| A17 | Accept "partial, malformed, or missing" data | "Malformed" invites injection, oversized payloads and corrupted stored JSON. | Accept wrong-typed values, but enforce envelope limits: size, depth, known paths, length caps, output encoding. |
| A18 | "PATCH" semantics unspecified | Merge patch, JSON Patch and full replace differ on arrays and null. Autosave requests can race. | JSON Merge Patch (RFC 7396) on objects, arrays replaced whole, with ETag and `If-Match`. |
| A19 | Notification-to-timer mapping is "configurable" | Storage, editors, effect on in-flight cases and business-hours handling are unspecified. | Versioned config table. Workflow snapshots config when the event fires. Business-calendar timers with a reminder cap and escalation. |
| A20 | Text defects | "Also note that when" is cut off, and the SO Kafka and validation sentence appears twice. | Product owner to supply the missing text and confirm the duplicate adds nothing. |
| A21 | A single POBO | Entities may need several signatories, delegates, a replacement POBO, or one POBO acting for several entities. | Define cardinality now. Support POBO replacement in phase 1 and extra collaborators in phase 2. |
| A22 | Notify "the RM, POBO and any other relevant parties" | Recipients and channels are undefined. | A notification matrix per event: recipient group, channel, template, timer. |

## Gap analysis

Forty-one gaps: 24 must be settled before build (P0), 15 before go-live (P1), and 2 can wait (P2). Items marked "confirm" depend on Compliance or another squad.

| ID | Area | Gap | Recommendation | Pri |
| --- | --- | --- | --- | --- |
| G1 | Identity | POBO authentication and authority are unverified | Single-use link, MFA, session bound to one case; check the POBO against registry officeholders or require signed authority evidence | P0 |
| G2 | Identity | Co-pilot acts with its own identity | OAuth2 token exchange (RFC 8693) so every call carries the RM as subject and the agent as actor; agent scopes exclude approve | P0 |
| G3 | Authorisation | No role, ownership or field-level rules | RBAC plus ownership (RM sees own book); a field-edit matrix by role and status; data locked after POBO\_SUBMITTED | P0 |
| G4 | Security | AI-enriched web data is untrusted input | Treat enrichments as suggestions with confidence and source URL; sanitise; require RM and POBO confirmation | P1 |
| G5 | Security | Session and abuse controls | Idle timeout with save-before-expiry, CSRF protection, rate limits and lockout on POBO endpoints | P1 |
| G6 | Data protection | PII handling unspecified | Encryption at rest, field-level encryption for sensitive identifiers, masked logs, encrypted Redis with short TTLs, AU data residency (confirm) | P0 |
| G7 | Audit | No audit trail | Append-only, field-level: actor, source, time, before and after, correlation ID; log reads of sensitive data | P0 |
| G8 | Compliance | No declaration or consent capture | POBO attestation of accuracy and authority, privacy collection notice, versioned text, timestamp and IP | P0 |
| G9 | Compliance | No retention or deletion rules | Purge abandoned drafts after a set period; retain submitted cases per policy; support access and correction requests (confirm) | P1 |
| G10 | Compliance | Regulatory checks not mapped | Map beneficial-owner and trustee data, sanctions and PEP screening triggers, and operational-risk obligations to requirements (confirm with Compliance) | P0 |
| G11 | Compliance | Public-source collection rules | Governance for the whitelist, site terms of use, and privacy notice for personal data of directors | P1 |
| G12 | Schema | No versioning or case pinning | Semantic versions; pin the schema version on the case at creation; define migration for in-flight cases | P0 |
| G13 | Schema | No form layout metadata | A UI layout descriptor per orgType: steps, order, labels, help text, conditional visibility | P0 |
| G14 | Schema | Cross-field rules cannot live in JSON Schema | Shared rules package (ABN and ACN checksums, ownership totals) used by browser and server | P0 |
| G15 | Schema | Raw JSON Schema errors are cryptic | Error-message catalogue keyed by keyword and path, in plain language | P1 |
| G16 | Schema | Three validators can disagree | One JSON Schema draft, identical custom formats, a shared conformance test suite run against browser, EON and SO | P0 |
| G17 | Data | No duplicate or existing-customer check | Reject a second active case for the same ABN or ACN with 409 and a link; check existing customers (confirm scope) | P1 |
| G18 | Data | Provenance has no precedence rules | Source ranking, locked RM-verified fields, POBO confirmation of prefilled values, history of overwritten values | P0 |
| G19 | Documents | Upload path and safety undefined | Streamed upload through EON, size and type limits, content sniffing, malware scan, handling of password-protected files | P0 |
| G20 | Documents | Lifecycle too coarse | Add REQUESTED, SUPERSEDED, EXPIRED and withdrawn; validity windows if policy requires | P1 |
| G21 | Documents | Ad-hoc requests by the case handler | A document request with reason, due date, notification and its own timer | P1 |
| G22 | Documents | Documentum links exposed | EON serves downloads after an authorisation check; never hand out repository URLs | P1 |
| G23 | Workflow | No cancel, hold or expiry | Withdraw, hold, abandon-after-N-days and reopen, each with a defined status and audit entry | P0 |
| G24 | Workflow | POBO access lifecycle | Resend, re-issue, revoke, replace POBO; handle bounced emails and wrong recipients | P0 |
| G25 | Workflow | Temporal operating model | Workflow ID = ServiceOrderId, continue-as-new, workflow code versioning, search attributes, retry and timeout policy per activity | P0 |
| G26 | Workflow | Failure paths undefined | Behaviour when SO, Documentum or email is down; dead-letter queue; operator tools to retry, replay and terminate | P0 |
| G27 | Workflow | No reconciliation | Scheduled sweeper comparing active SO cases with running workflows and the last processed event | P1 |
| G28 | Operations | Observability | Correlation ID from co-pilot to Temporal, traces, SLOs, alerts on stuck cases and consumer lag | P1 |
| G29 | Operations | No reporting | SLA ageing, funnel and drop-off views for RMs and operations | P2 |
| G30 | Form | Concurrent edits | ETag with `If-Match`, 409 handling, per-field merge hints, multi-tab detection | P0 |
| G31 | Form | Network failure UX | Save-status indicator, retry with backoff, local backup of unsaved changes with PII safeguards | P1 |
| G32 | Form | Accessibility | WCAG 2.2 AA: warnings not conveyed by colour alone, focus moves to the first error, announcements for screen readers | P0 |
| G33 | Form | No review step or receipt | Read-only review page before submit; a PDF copy for the POBO | P1 |
| G34 | Form | Dynamic structure | Repeating groups (directors, owners) and conditional steps driven by the layout descriptor | P0 |
| G35 | Form | Prefill UX | Source badges, confirm or edit controls, revert to the sourced value | P1 |
| G36 | API | No published contract | OpenAPI 3.1, `/v1` versioning, contract tests with co-pilot and SO, a sandbox | P0 |
| G37 | API | Write safety | `Idempotency-Key` on POST and commands, RFC 9457 problem responses, per-client rate limits | P0 |
| G38 | API | SO client resilience | Timeouts, jittered retries, circuit breaker, bulkhead, 429 back-off | P0 |
| G39 | API | No outbound notifications for consumers | Webhooks or server-sent events for status and validation changes | P2 |
| G40 | API | No search or list | Filter by status, orgType, RM, date; cursor pagination | P1 |
| G41 | NFR | No volumes, SLAs, RPO or RTO | Obtain peak cases per day, concurrent POBOs, payload size, availability and recovery targets | P0 |

## Recommended architecture and key decisions

Twelve decisions define the solution; D1 and D2 are the foundation and need SO squad agreement before anything else is built.

| # | Decision | Recommendation | Why, and what was rejected |
| --- | --- | --- | --- |
| D1 | Where working data lives | EON keeps the working copy (RM, co-pilot and POBO edits) in PostgreSQL JSONB. SO is updated at milestones: creation, enrichment checkpoints, every lifecycle transition, and finalize. | Every SO write emits a Kafka event, so a 2-second autosave would flood the bridge and SO history. Autosave also survives an SO outage. Rejected: writing every keystroke pause to SO. |
| D2 | Status-gated validation profiles | Three profiles per orgType version: DRAFT (types and formats only), RM (minimum to approve), FINAL (complete, including documents). SO and EON pick the profile from the target status. | Resolves the draft-versus-validation conflict (A1) with one schema source. Needs SO to accept a profile or schema ID per write. Rejected: a separate relaxed schema maintained by hand. |
| D3 | Lifecycle control | A closed status list and transition table enforced in EON. Approve, finalize, withdraw and case-handler actions are commands; PATCH changes data only. | Closes the escalation path in A5 and makes each privileged act auditable. Rejected: status as a PATCH field. |
| D4 | SO integration | An anti-corruption layer inside the EON API: typed SO client, mapping, retries with jitter, circuit breaker, and an outbox table for checkpoint syncs. | Isolates SO's model and availability from the rest of EON. Rejected: calling SO directly from controllers or workers. |
| D5 | Event bridge | A separate small service. Consumes the SO topic, filters by request type, deduplicates in an inbox table by eventId, ignores stale record versions, then calls `signalWithStart` on workflow ID = ServiceOrderId. Failures go to a dead-letter topic. | Kafka is at-least-once and Temporal workers do not read Kafka. A single start path prevents races (A8). Rejected: EON API also starting workflows. |
| D6 | Temporal model | One long-running workflow per case; child workflows for enrichment refresh, document collection and notifications; continue-as-new on a size or age threshold; search attributes for case ID, status, orgType, RM; worker versioning for deploys. | Cases can last weeks, so history size and code changes are real risks. Workflow state holds IDs and timers, not documents or PII. |
| D7 | Schemas | Schemas, layout descriptors, document manifests and rules are versioned together as one release. The version is pinned on the case. Validation uses Ajv with one JSON Schema draft and identical custom formats in browser and server. | Prevents drift between SO, EON and the browser. Rejected: fetching "latest" schema on each request. |
| D8 | Provenance | A sidecar map keyed by JSON Pointer: source, retrieved-at, confidence, verified-by, previous value. Source precedence: RM-verified over POBO-confirmed over registry data over web data over co-pilot inference. | Keeps data schemas clean and makes overwrite rules testable (A13). |
| D9 | Documents | A document register in EON's database. Uploads stream through EON to Documentum after scanning. Downloads are proxied after an authorisation check. Temporal activities update the register. | Gives the form a fast, queryable list and keeps Documentum internal (A16). |
| D10 | Identity and access | Workforce SSO for RMs and case handlers. Token exchange so the co-pilot acts on behalf of an RM. POBO signs in via single-use link and MFA through a customer identity service. Row-level ownership and a field-edit matrix. | Removes emailed credentials (A10) and stops an agent approving its own work. |
| D11 | Concurrency and PATCH | JSON Merge Patch on objects, arrays replaced whole, ETag with `If-Match`, 412 on stale writes. Autosave carries a client revision so late requests are discarded. | Autosave races are certain with debounced saves and multiple tabs (A18). |
| D12 | Redis | Cache-aside for schema bundles (immutable by version, long TTL), SO record reads (invalidated by the event bridge), idempotency keys and rate-limit counters. PII entries are encrypted with short TTLs. | Caching what cannot go stale is safe; caching mutable drafts is not (A14). |

**Resulting data ownership.**

| Data | System of record | Copies |
| --- | --- | --- |
| Request status and validated request data | SO | EON read cache in Redis |
| Working draft, provenance, validation reports | EON PostgreSQL | None |
| Document files | Documentum | Register rows in EON PostgreSQL |
| Workflow timers and orchestration state | Temporal | Status mirrored from SO events |
| Notification rules and templates | EON PostgreSQL | Cached in workers |
| Audit trail | EON PostgreSQL (append-only) | Forwarded to the bank's log platform |

## System design and architecture

EON owns the working data and the event bridge; SO stays the system of record, and Temporal reacts only to SO events.

&#91;embedded content: architecture · request plane and event plane\]

The request plane (top) carries every caller through the EON API, which writes to SO only at milestones. The event plane (bottom) turns each SO event into a Temporal signal. Workers also read and write PostgreSQL, which is not drawn.

**Component responsibilities**

| Component | Responsibility |
| --- | --- |
| EON API | Authenticates and authorises callers, enforces the transition table, runs the envelope check and the validation profiles, serves forms and documents, and talks to SO through the anti-corruption layer |
| PostgreSQL | Working drafts, provenance, snapshots, document register, notification rules and logs, inbox, outbox, audit |
| Redis | Immutable schema bundles, event-invalidated SO reads, idempotency keys, rate-limit counters |
| Event bridge | Consumes the SO topic, deduplicates, checks record versions, starts or signals the case workflow, dead-letters poison messages |
| Temporal and workers | One workflow per case; activities for notifications, SO status writes, document tracking and enrichment refresh; timers from notification rules |
| SO | Request records, status, schema registry; emits an event on every create or update |
| Documentum | Document files; reached only through the EON API |
| Identity | Workforce SSO and token exchange for RMs and agents; link and MFA sign-in for POBOs |
| Notification service | Sends email and SMS from templates chosen by the workflow |

## Status model and workflows

A closed set of ten statuses, moved only by named commands, replaces the open-ended list; enrichment becomes provenance data instead of status.

&#91;embedded content: status model · 10 statuses, 3 editable\]

Data can be edited in three statuses only: DRAFT (RM and agent), POBO\_NOTIFIED (POBO) and INFO\_REQUESTED (POBO, limited to the sections the handler reopened). The dashed zone groups every open status; any of them can end in WITHDRAWN or EXPIRED.

**Transition table**

| From | To | Command | Actor | Guard |
| --- | --- | --- | --- | --- |
| (none) | DRAFT | create | RM, agent | Creation profile valid; no active duplicate |
| DRAFT | RM\_APPROVED | approve | RM only, no agent actor | RM profile valid; ETag matches what the RM reviewed |
| RM\_APPROVED | POBO\_NOTIFIED | notify | Workflow | Notification sent and POBO access provisioned |
| POBO\_NOTIFIED | POBO\_SUBMITTED | finalize | POBO | FINAL profile, rules, documents and declaration pass |
| POBO\_SUBMITTED | UNDER\_REVIEW | pick up | Case handler | Handler authorised for the case |
| POBO\_SUBMITTED or UNDER\_REVIEW | INFO\_REQUESTED | request-info | Case handler | Sections and documents to reopen are named |
| INFO\_REQUESTED | POBO\_SUBMITTED | finalize | POBO | Requested scope passes and the FINAL profile still holds |
| UNDER\_REVIEW | COMPLETE | complete | Case handler | All required documents approved |
| POBO\_SUBMITTED or UNDER\_REVIEW | REJECTED | reject | Case handler | Reason required |
| Any open status | WITHDRAWN | withdraw | RM | Reason required; POBO access revoked |
| Any open status | EXPIRED | timer | Workflow | Per-status expiry from configuration |
| Any open status | ON\_HOLD, and back | hold, resume | RM, handler | Phase 2; resumes to the prior status |

Any other transition returns 409 `invalid_transition`. A transition made through another SO channel is accepted via the event, checked against this table, and raises an alert if illegal.

### Case workflow (phase 2)

One long-running workflow per case sleeps at three waits and does work only when an SO event or a timer wakes it.

&#91;embedded content: case workflow · 3 waits, 2 loops\]

The reminder loop and the INFO\_REQUESTED loop repeat until the case moves on or the reminder cap is reached.

- **Identity:** workflow ID = ServiceOrderId, started only by `signalWithStart` from the event bridge.
- **Signals:** each carries the SO event ID and record version; the workflow ignores any at or below the last version it handled.
- **Notification rules:** read through an activity when an event fires and snapshotted into workflow state, so later configuration changes do not alter timers already running (to confirm with the business).
- **Timers:** business-calendar aware (AEST or AEDT, public holidays), computed in an activity because workflow code must be deterministic.
- **Side effects:** every email and SO write carries a key built from workflow ID, event ID and step, so a retry never repeats it.
- **Retries:** SO and Documentum calls retry with exponential back-off; after the email retry limit the workflow flags the case and alerts the RM instead of failing.
- **Size and deploys:** continue-as-new at each status change, carrying case ID, last version and timer state; worker versioning for code changes; search attributes for case ID, status, orgType, RM and next timer due.

## Form, draft and validation design

The Draft-Saving Progressive Wizard pattern stays, with five changes: validation profiles, a layout descriptor, a draft envelope check on the server, field provenance, and optimistic concurrency.

### Validation layers

| Layer | Where | What runs | When | Blocks the user? |
| --- | --- | --- | --- | --- |
| 1. Field check | Browser | DRAFT profile fragment for the field, plus shared rules | On blur | No; amber warning |
| 2. Step check | Browser | FINAL profile subset for the step | On Next, Back, step change | No; amber warning and step icon |
| 3. Envelope check | EON API | Body size, depth, known paths, length caps | Every draft save | Only a malformed envelope (400 or 413) |
| 4. Draft report | EON API | FINAL profile evaluated against the saved draft | Every draft save | No; returned with the save response |
| 5. Pre-flight | Browser | Full FINAL profile, rules, required-document check | On Submit | Yes; warnings turn red and focus jumps to the first error |
| 6. Finalize gate | EON API | FINAL profile, rules, document resolver, from the stored draft | `POST .../finalize` | Yes; 422 |
| 7. SO validation | SO | FINAL profile | On the SO write | Yes; should never fire if validators agree, so it raises an alert |

Layer 4 matters because step indicators then look the same on every device and after a reload. Severity has three levels: info, warning (incomplete or badly formatted in draft) and error (blocking, only at submit).

### Draft saves

- **Triggers:** Next, Back, 2 seconds after the last keystroke, and page hide (using `fetch` with `keepalive`). Send only changed fields, not the whole payload.
- **Envelope limits** (values to confirm): body at most 256 KB, nesting depth at most 10, strings capped per field, unknown paths rejected. Values are stored as entered and always output-encoded when rendered or emailed.
- **Ordering:** each save carries a `clientRevision`; the server discards a save older than the stored revision for the same fields.
- **Conflicts:** `If-Match` with the draft ETag; a stale write gets 412 and the current representation so the client can merge.

### Provenance and prefill

The wizard loads one merged view: each field's value plus its provenance (source, retrieved-at, confidence, verified-by). Prefilled fields show a "Prefilled from \<source>" badge. If the POBO edits one, provenance becomes POBO and the previous value is kept.

Fields marked `requiresConfirmation` in the layout descriptor count as complete only after the POBO confirms them. Lower-ranked automated sources never overwrite higher-ranked values. Any POBO change to a field the RM approved is flagged to the case handler as a diff.

### Schema release bundle

One immutable bundle per orgType version holds the three schema profiles, the layout descriptor, the document manifest, the rules version and the message catalogue. The case pins the bundle version at creation. Moving an in-flight case to a newer bundle is an explicit, audited command with a diff, never automatic.

### Finalize algorithm

1. Authenticate the POBO and check the case is POBO\_NOTIFIED or INFO\_REQUESTED and owned by them.
2. Require `If-Match` equal to the current draft ETag, so what the client validated is what is submitted.
3. Validate the FINAL profile, rules, and the document resolver (every required document present, scanned clean, not rejected).
4. Require the declaration payload (text version, accepted, timestamp, IP).
5. Make one SO write carrying the data and status POBO\_SUBMITTED, with the expected SO record version and an idempotency key derived from the draft ETag.
6. On success, lock the draft, store an immutable submission snapshot with its hash, write the audit entry and return a receipt.
7. On failure, keep the draft editable: 422 with JSON Pointer errors, 409 if SO's version moved, 503 if SO is unavailable. Retrying is always safe.

### Accessibility and session behaviour

Warnings use an icon and text as well as amber. Moving focus to the first error is announced to screen readers. A visible save status reads "Saving", "Saved at 10:42" or "Could not save, retrying". The session warns two minutes before idle timeout, and unsaved changes are flushed before sign-out.

## High-level scenarios

One happy path and 34 edge scenarios cover creation, enrichment, notification, the form, post-submission review and platform failures.

**S1. Happy path**

1. The RM gives the co-pilot the entity name, orgType, ABN or ACN, and the POBO's name and email. The co-pilot calls `POST /v1/onboarding-requests`. EON authenticates, validates the creation profile, creates the SO request as DRAFT and a working-copy row.
2. SO emits a create event. The event bridge starts the case workflow.
3. The co-pilot enriches data and sends PATCHes with provenance. The RM reviews and corrects.
4. The RM approves through `POST .../approve`. EON checks the RM profile and writes RM\_APPROVED to SO with a hash of the approved data.
5. The workflow wakes on the event, provisions POBO access, sends the notification and starts the configured timer.
6. The workflow writes POBO\_NOTIFIED to SO.
7. The POBO opens the link, passes MFA and sees the prefilled wizard.
8. The POBO completes steps with soft validation, autosave and document uploads.
9. The POBO submits. EON runs the finalize gate and writes POBO\_SUBMITTED to SO.
10. The workflow notifies the RM, POBO and case handler, and stops the POBO timers.
11. The case handler reviews data and documents and sets COMPLETE.
12. The workflow sends final notifications, closes, and the retention clock starts.

**Edge scenarios**

| ID | Scenario | Expected behaviour |
| --- | --- | --- |
| S2 | Duplicate create for an ABN with an active case | 409 with the existing case ID. A retry with the same `Idempotency-Key` returns the original response. |
| S3 | ABN or ACN fails checksum, or orgType unsupported | 422 with JSON Pointer errors; nothing created in SO. |
| S4 | Registry API times out during enrichment | Case stays DRAFT; the enrichment is marked failed with a retry option; the RM is told in the response. |
| S5 | Registry and web data disagree | Both kept as candidates; the higher-ranked source is shown; the conflict is flagged to the RM. |
| S6 | An agent PATCH targets an RM-verified field | Rejected with 409 `field_locked`. |
| S7 | The co-pilot calls approve | 403; approve needs an RM subject token with no agent actor. |
| S8 | RM approves with RM-profile data incomplete | 422 listing the missing fields; status unchanged. |
| S9 | RM and agent edit at the same time | The second write gets 412; the agent re-reads and merges. |
| S10 | Email sending fails | Activity retries with back-off. After the limit the case stays RM\_APPROVED, is flagged, and the RM is alerted. |
| S11 | Email sent, then the POBO\_NOTIFIED write fails | Activity retries only the SO write; the email idempotency key prevents a second email. |
| S12 | POBO email bounces | RM alerted; the RM corrects the email through the change-POBO command; old link revoked; new link sent. |
| S13 | POBO link expired or already used | The POBO can request a fresh link to the same address, rate-limited; no case data is shown. |
| S14 | RM replaces the POBO mid-way | Old sessions revoked, draft kept, new POBO notified, audit entry written. |
| S15 | POBO is inactive | Reminder 1, reminder 2, escalation to the RM, then expiry, all from configuration. Any status change cancels pending timers. |
| S16 | POBO has the form open in two tabs | The stale tab's save gets 412 and offers reload or merge. |
| S17 | Network drops while typing | Unsaved changes are backed up locally; the banner shows retrying; the flush on reconnect carries the revision. |
| S18 | Session times out | Warning first, save flushed, re-authenticate, return to the same step. |
| S19 | A new schema bundle is released during a case | The case keeps its pinned version. Migration only by an explicit audited command. |
| S20 | Submit with a required document missing | Pre-flight blocks and jumps to the documents step. If bypassed, the server returns 422 `missing_document`. |
| S21 | Draft changed after the client pre-flight | `If-Match` fails with 412; the client reloads and re-validates. |
| S22 | SO unavailable at finalize | 503 with `Retry-After`; draft intact; retry is safe. |
| S23 | SO rejects data that EON accepted | 502, an alert, the case stays POBO\_NOTIFIED, and the validator-parity suite gets a new test case. |
| S24 | POBO double-clicks Submit | The second call returns the same receipt through the idempotency key. |
| S25 | Case handler requests more information or a document | INFO\_REQUESTED; the POBO is notified; only the requested sections open for edit; a timer starts. |
| S26 | POBO resubmits | Finalize runs on the requested scope; a diff against the previous snapshot goes to the handler. |
| S27 | Case handler rejects | REJECTED; RM and POBO notified; terminal. A new case may copy data forward. |
| S28 | Case completes | COMPLETE; notifications sent; workflow closes; retention starts. |
| S29 | RM withdraws | WITHDRAWN; timers cancelled; POBO access revoked; documents kept per policy. |
| S30 | Case abandoned | EXPIRED after the configured period; the draft purge is scheduled. |
| S31 | Kafka delivers an event twice | The inbox table drops the duplicate. |
| S32 | Events arrive out of order | Events with a record version at or below the last processed are ignored. |
| S33 | Event bridge is down for hours | The backlog is consumed on recovery; the sweeper reconciles any gap. |
| S34 | A worker deployment happens mid-case | Worker versioning keeps in-flight workflows on compatible code. |
| S35 | Another channel changes the SO status | The bridge signals the workflow, EON invalidates its cache, and the UI reflects the change on next load. |

## Use cases

Twenty-two use cases cover eight actors; the five most critical are detailed after the catalogue. Phase 1 is the form-only first release, phase 2 adds orchestration, phase 3 adds review and operations.

**Actors.** RM (Relationship Manager); Co-pilot agent (acts on behalf of an RM); POBO (person on behalf of the entity); Case handler; Operations admin; Support engineer; Auditor; Consumer app (any other API client).

| ID | Use case | Primary actor | Phase |
| --- | --- | --- | --- |
| UC-01 | Create onboarding request | RM through co-pilot | 1 |
| UC-02 | Enrich and edit draft data | Co-pilot, RM | 1 |
| UC-03 | View request, provenance and validation report | RM, POBO | 1 |
| UC-04 | Approve request for POBO | RM | 1 (command), 2 (workflow reaction) |
| UC-05 | Notify POBO and provision access | Workflow | 2 |
| UC-06 | Sign in as POBO | POBO | 1 |
| UC-07 | Complete the wizard with autosave | POBO | 1 |
| UC-08 | Upload and manage documents | POBO | 1 |
| UC-09 | Review and submit | POBO | 1 |
| UC-10 | Receive reminders and escalations | RM, POBO | 2 |
| UC-11 | Review a submission | Case handler | 3 |
| UC-12 | Request additional information or documents | Case handler | 3 |
| UC-13 | Provide the requested information | POBO | 3 |
| UC-14 | Reject or complete a case | Case handler | 3 |
| UC-15 | Withdraw, hold or reopen a case | RM | 2 |
| UC-16 | Replace POBO or resend access | RM | 2 |
| UC-17 | Search and monitor my cases | RM | 2 |
| UC-18 | Configure notification rules and timers | Operations admin | 2 |
| UC-19 | Publish and pin schema bundles | Schema owner | 1 |
| UC-20 | Investigate and repair a stuck case | Support engineer | 2 |
| UC-21 | Audit a case | Auditor | 2 |
| UC-22 | Subscribe to case events | Consumer app | 3 |

### UC-01 Create onboarding request

**Actor:** RM through the co-pilot. **Precondition:** the caller holds a valid RM-subject token with the create scope. **Postcondition:** an SO request exists in DRAFT, EON holds a working copy, and the case workflow is started by the event bridge.

1. The client sends `POST /v1/onboarding-requests` with `Idempotency-Key`, orgType, entity name, ABN or ACN, and POBO name and email.
2. EON authenticates, authorises, and validates the creation profile and ABN or ACN checksum.
3. EON checks for an active case with the same identifier.
4. EON creates the SO request and the working-copy row in one idempotent operation, pinning the schema bundle version.
5. EON returns 201 with the case ID, ETag, status DRAFT and the validation report.

*Alternates:* duplicate case returns 409 with a link; invalid input returns 422; SO unavailable returns 503 and nothing is created.

### UC-04 Approve request for POBO

**Actor:** RM. **Precondition:** status DRAFT, RM profile satisfied, and the token carries an RM subject with no agent actor. **Postcondition:** status RM\_APPROVED with an approval record.

1. The RM reviews the data, provenance badges and any enrichment conflicts.
2. The RM calls `POST .../approve` with the draft ETag they reviewed.
3. EON checks the ETag still matches, validates the RM profile, and records the approval with a hash of the data.
4. EON writes RM\_APPROVED to SO with the expected record version.
5. The event reaches the bridge and wakes the workflow.

*Alternates:* stale ETag returns 412 and the RM re-reviews; incomplete data returns 422 with the missing fields; agent-only token returns 403.

### UC-07 Complete the wizard with autosave

**Actor:** POBO. **Precondition:** status POBO\_NOTIFIED or INFO\_REQUESTED and a valid session. **Postcondition:** the draft holds the latest data; step indicators reflect the draft report.

1. The wizard loads the merged view, layout descriptor and draft report.
2. The POBO edits fields; blur triggers field warnings.
3. Next, Back, a 2-second pause, or page hide triggers a save of changed fields.
4. The server applies the merge patch, updates provenance, recomputes the draft report and returns the new ETag.
5. The step tab shows complete, in progress, or warning.

*Alternates:* 412 prompts reload or merge; envelope violation shows a system error without losing local input; offline shows the retry banner.

### UC-09 Review and submit

**Actor:** POBO. **Precondition:** the wizard has reached the review step. **Postcondition:** status POBO\_SUBMITTED, draft locked, receipt issued.

1. The POBO opens the read-only review step and ticks the declaration.
2. The browser runs the pre-flight; on errors it jumps to the first broken step and turns warnings red.
3. The browser calls `POST .../finalize` with the draft ETag and declaration.
4. EON runs the finalize algorithm and writes POBO\_SUBMITTED to SO.
5. EON returns a receipt; the POBO can download a PDF copy.

*Alternates:* 422 with errors by pointer; 412 reload; 503 retry later; double submission returns the same receipt.

### UC-12 Request additional information or documents

**Actor:** Case handler. **Precondition:** status POBO\_SUBMITTED or UNDER\_REVIEW. **Postcondition:** status INFO\_REQUESTED with a tracked request.

1. The handler selects fields or sections and optionally adds document requests with reason and due date.
2. EON records the request, opens only those sections for editing, and writes INFO\_REQUESTED to SO.
3. The workflow notifies the POBO and starts the timer configured for this event.
4. The document register adds each requested document as REQUESTED.

*Alternates:* a handler action while the POBO is mid-edit is not possible because the draft is locked in submitted states; the timer expiry sends reminders and then escalates to the RM.

## User stories

Thirty-four stories in eight epics; 19 are phase 1, the form-only release. Acceptance criteria are the minimum testable conditions.

### Epic 1: Request creation and enrichment

| ID | Story | Acceptance criteria | Ph |
| --- | --- | --- | --- |
| US-01 | As an RM, I want to create an onboarding request so enrichment can start. | Valid orgType, ABN or ACN and POBO email return a case ID and status DRAFT; an active duplicate returns 409 with a link; the same idempotency key returns the same result. | 1 |
| US-02 | As the co-pilot, I want to PATCH enriched values with a source label so provenance is kept. | Each patched field carries source and confidence; the response returns updated provenance; a lower-ranked source cannot overwrite a higher-ranked value (409). | 1 |
| US-03 | As an RM, I want to see where each value came from and where sources conflict. | GET returns provenance per field and candidate values; I can choose a value and mark it verified. | 1 |
| US-04 | As a consumer-app developer, I want an OpenAPI spec and a validate-only call. | Dry run returns the same report as a save with no state change; schemas are fetchable by orgType and version. | 1 |

### Epic 2: Approval and lifecycle

| ID | Story | Acceptance criteria | Ph |
| --- | --- | --- | --- |
| US-05 | As an RM, I want to approve only when the data meets the RM profile. | Approve returns 422 with missing fields if incomplete; success stores an approval hash; a token with an agent actor gets 403. | 1 |
| US-06 | As an RM, I want to withdraw or hold a case. | Allowed only from permitted states; withdraw revokes POBO access and cancels timers; audit entry written. | 2 |
| US-07 | As an RM, I want to replace the POBO or resend access. | Old link revoked; draft kept; new notification sent; audit entry written. | 2 |
| US-08 | As an RM, I want to search my cases by status, orgType and age. | Cursor pagination; results limited by role and ownership; default sort is most recently updated. | 2 |

### Epic 3: POBO access and identity

| ID | Story | Acceptance criteria | Ph |
| --- | --- | --- | --- |
| US-09 | As a POBO, I want to sign in with an emailed link and a second factor. | Link is single-use and expires; MFA required; session bound to one case; lockout after repeated failures; no password in the email. | 1 |
| US-10 | As a POBO, I want to declare I am authorised to act for the entity. | Declaration stored with text version, time and IP; authority evidence rules apply per orgType. | 1 |

### Epic 4: Wizard and validation

| ID | Story | Acceptance criteria | Ph |
| --- | --- | --- | --- |
| US-11 | As a POBO, I want known data prefilled so I type less. | Prefilled fields show a source badge; edits are recorded as POBO; fields needing confirmation require an explicit tick. | 1 |
| US-12 | As a POBO, I want warnings rather than blocks while filling the form. | Amber icon-and-text warnings on blur and Next; Next and Back never blocked; step tabs show status. | 1 |
| US-13 | As a POBO, I want progress saved automatically. | Saves on Next, Back, 2-second pause and page hide; visible save status; nothing lost on refresh or on another device. | 1 |
| US-14 | As a POBO, I want to know if the form changed elsewhere. | A stale save returns 412; the UI offers reload or merge; no silent overwrite. | 1 |
| US-15 | As a POBO, I want to add repeating items and see only relevant steps. | Directors and owners can be added and removed; steps appear by orgType and answers; indicators ignore hidden steps. | 1 |
| US-16 | As a POBO, I want to review everything and submit once. | Read-only review; pre-flight jumps to the first error and turns warnings red; receipt and PDF copy on success; double click is safe. | 1 |
| US-17 | As a POBO using assistive technology, I want a fully usable form. | WCAG 2.2 AA; keyboard operable; focus moves to the first error and is announced; no colour-only signals. | 1 |
| US-18 | As a compliance officer, I want the server to reject invalid submissions. | Finalize re-validates from the stored draft including documents; 422 with JSON Pointer errors; an SO rejection leaves no partial state. | 1 |

### Epic 5: Documents

| ID | Story | Acceptance criteria | Ph |
| --- | --- | --- | --- |
| US-19 | As a POBO, I want to upload each required document and see its status. | The list comes from the manifest and my data; type and size limits; scan result shown; status visible. | 1 |
| US-20 | As a case handler, I want to request an extra document with a reason and due date. | Appears as REQUESTED for the POBO; POBO notified; timer starts. | 3 |
| US-21 | As a case handler, I want to approve or reject a document with a reason. | Status change recorded with reason; rejection notifies the POBO; history kept. | 3 |
| US-22 | As a security officer, I want document downloads authorised and logged. | No repository URLs exposed; every download checked and logged. | 1 |

### Epic 6: Orchestration and notifications

| ID | Story | Acceptance criteria | Ph |
| --- | --- | --- | --- |
| US-23 | As an RM, I want to be told when the POBO is notified, submits or stalls. | Notification matrix is configurable; messages carry a deep link and context. | 2 |
| US-24 | As an operations admin, I want to configure text, recipients and timers per event. | Versioned configuration with change audit; applies to new events; preview available. | 2 |
| US-25 | As an RM, I want reminders sent and then escalated automatically. | Timers cancel on any status change; business-calendar aware; reminder cap; defined escalation target. | 2 |
| US-26 | As a platform owner, I want each SO event to take effect exactly once. | Duplicates and stale events ignored; poison messages go to a dead-letter topic with an alert; the sweeper reconciles gaps. | 2 |

### Epic 7: Case handling

| ID | Story | Acceptance criteria | Ph |
| --- | --- | --- | --- |
| US-27 | As a case handler, I want submitted data, provenance and changes since approval. | Read-only snapshot with hash; POBO changes to approved fields highlighted. | 3 |
| US-28 | As a case handler, I want to request information and receive a resubmission. | Only requested sections editable; diff against the previous snapshot. | 3 |
| US-29 | As a case handler, I want to reject or complete a case with a reason. | Terminal status; notifications sent; audit entry written. | 3 |

### Epic 8: Platform, security and operations

| ID | Story | Acceptance criteria | Ph |
| --- | --- | --- | --- |
| US-30 | As an auditor, I want a tamper-evident history of every case. | Append-only, field-level with actor, source and time; access to sensitive data logged; exportable. | 1 |
| US-31 | As a support engineer, I want to find and repair stuck cases. | Search by case ID; view workflow state; retry, reset or terminate with audit. | 2 |
| US-32 | As a platform owner, I want schema releases versioned and pinned. | Bundles are immutable; the case pins its version; migration is an explicit command. | 1 |
| US-33 | As an SRE, I want traces and alerts across the whole path. | One correlation ID end to end; dashboards; alerts on consumer lag and stuck cases. | 2 |
| US-34 | As a privacy officer, I want abandoned drafts purged. | Configurable period; purge audited; retention exceptions honoured. | 3 |

## API specification

The EON API needs 52 routes in eight groups; 24 are phase 1. Conventions come first, then the catalogue.

### Conventions

- **Versioning and format:** all routes under `/v1`, JSON bodies, opaque UUID identifiers, no PII in URLs or query strings.
- **Authentication:** OAuth 2.0 / OIDC bearer tokens for RMs, agents, handlers and admins, with token exchange so an agent call carries the RM as subject. POBOs use a session cookie (HttpOnly, SameSite) issued after link and MFA.
- **Headers:** `Idempotency-Key` on every POST and command; `ETag` and `If-Match` on every case representation and write; `X-Correlation-Id` echoed back; `Retry-After` on 429 and 503.
- **Status codes:** 400 envelope violation, 401, 403, 404 (also used when the caller may not know the case exists), 409 (duplicate, `field_locked`, `invalid_transition`), 412 stale write, 413 too large, 422 validation failure, 428 missing `If-Match`, 429, 502 and 503 for SO problems.
- **Errors:** RFC 9457 `application/problem+json` with a `code`, `correlationId` and an `errors` array of JSON Pointers.
- **Lists:** cursor pagination, `limit` up to 100, stable sort.

```json
{
  "type": "https://eon.example/problems/validation-failed",
  "title": "Submission failed validation",
  "status": 422,
  "code": "validation_failed",
  "correlationId": "c3f2a9e1",
  "errors": [
    { "pointer": "/directors/0/dateOfBirth", "code": "format", "severity": "error", "message": "Enter a valid date of birth" },
    { "pointer": "/documents/trustDeed", "code": "missing_document", "severity": "error", "message": "Upload the trust deed" }
  ]
}
```

A data PATCH carries values and, optionally, provenance keyed by JSON Pointer:

```json
{
  "data": { "organisation": { "legalName": "Example Pty Ltd" } },
  "provenance": {
    "/organisation/legalName": { "source": "REGISTRY", "confidence": 0.99, "retrievedAt": "2026-11-07T10:15:00Z" }
  }
}
```

### Requests and data

| Route | Purpose | Caller | Ph |
| --- | --- | --- | --- |
| `POST /onboarding-requests` | Create a request (status DRAFT) | RM, agent, consumer app | 1 |
| `GET /onboarding-requests` | Search and list by status, orgType, RM, date | RM, handler | 2 |
| `GET /onboarding-requests/{id}` | Full view: status, allowed actions, merged data, provenance, report, document summary, ETag | RM, handler, agent | 1 |
| `PATCH /onboarding-requests/{id}/data` | Merge patch of data with optional provenance | RM, agent | 1 |
| `POST /onboarding-requests/{id}/validate` | Dry-run validation against a chosen profile; no state change | Any caller with read access | 1 |
| `GET /onboarding-requests/{id}/validation-report` | Latest report by step and pointer | RM, POBO, handler | 1 |
| `GET /onboarding-requests/{id}/provenance` | Provenance and candidate values per field | RM, handler | 1 |
| `POST /onboarding-requests/{id}/enrichments` | Append enrichment candidates with source and confidence; merged by precedence | Agent | 1 |
| `GET /onboarding-requests/{id}/history` | Status and audit timeline | RM, handler, auditor | 1 |
| `GET /onboarding-requests/{id}/status` | Lightweight status and allowed actions (cacheable) | Any case participant | 1 |

### Lifecycle commands

| Route | Purpose | Caller | Ph |
| --- | --- | --- | --- |
| `POST /onboarding-requests/{id}/approve` | DRAFT to RM\_APPROVED; needs `If-Match` and an RM subject | RM only | 1 |
| `POST /onboarding-requests/{id}/withdraw` | Withdraw with reason; revokes POBO access | RM | 2 |
| `POST /onboarding-requests/{id}/hold` | Put on hold with reason | RM, handler | 2 |
| `POST /onboarding-requests/{id}/resume` | Resume from hold | RM, handler | 2 |
| `POST /onboarding-requests/{id}/reopen` | Reopen a withdrawn or expired case | RM | 2 |
| `PUT /onboarding-requests/{id}/pobo` | Replace the POBO or correct the email | RM | 2 |
| `POST /onboarding-requests/{id}/pobo/access-links` | Issue or resend an access link | RM | 2 |
| `DELETE /onboarding-requests/{id}/pobo/access-links/{linkId}` | Revoke a link | RM, admin | 2 |
| `POST /onboarding-requests/{id}/migrate-schema` | Move a case to a newer schema bundle, with diff | Admin | 3 |

### POBO form

| Route | Purpose | Caller | Ph |
| --- | --- | --- | --- |
| `GET /onboarding-requests/{id}/form` | Layout descriptor, merged data, provenance, report, editable scope, ETag | POBO | 1 |
| `PATCH /onboarding-requests/{id}/draft` | Save changed fields for a step, with `clientRevision` | POBO | 1 |
| `POST /onboarding-requests/{id}/finalize` | Run the finalize gate and submit; needs `If-Match` and declaration | POBO | 1 |
| `GET /onboarding-requests/{id}/submission` | Immutable submission snapshot and receipt | POBO, RM, handler | 1 |
| `GET /onboarding-requests/{id}/submission/receipt.pdf` | PDF copy for the POBO | POBO | 1 |

### POBO access

| Route | Purpose | Caller | Ph |
| --- | --- | --- | --- |
| `POST /access/exchange` | Exchange the emailed single-use token for a pending session | POBO | 1 |
| `POST /access/mfa/challenge` | Start the second factor | POBO | 1 |
| `POST /access/mfa/verify` | Complete MFA and activate the session | POBO | 1 |
| `DELETE /access/session` | Sign out | POBO | 1 |

### Documents

| Route | Purpose | Caller | Ph |
| --- | --- | --- | --- |
| `GET /onboarding-requests/{id}/documents` | Required documents resolved from the manifest and data, with register status | POBO, RM, handler | 1 |
| `POST /onboarding-requests/{id}/documents` | Upload (multipart, or resumable for large files) against a requirement | POBO | 1 |
| `GET /onboarding-requests/{id}/documents/{docId}` | Metadata, scan result, status history | POBO, RM, handler | 1 |
| `GET /onboarding-requests/{id}/documents/{docId}/content` | Authorised download | POBO, RM, handler | 1 |
| `DELETE /onboarding-requests/{id}/documents/{docId}` | Withdraw before submission (marks SUPERSEDED) | POBO | 1 |
| `POST /onboarding-requests/{id}/documents/{docId}/review` | Approve or reject with reason | Handler | 3 |
| `POST /onboarding-requests/{id}/document-requests` | Request an additional document with reason and due date | Handler | 3 |
| `GET /onboarding-requests/{id}/document-requests` | List requests and their status | POBO, RM, handler | 3 |

### Case handling

| Route | Purpose | Caller | Ph |
| --- | --- | --- | --- |
| `POST /onboarding-requests/{id}/request-info` | INFO\_REQUESTED with the sections to reopen | Handler | 3 |
| `POST /onboarding-requests/{id}/complete` | COMPLETE | Handler | 3 |
| `POST /onboarding-requests/{id}/reject` | REJECTED with reason | Handler | 3 |
| `GET /onboarding-requests/{id}/diff` | Diff between two snapshots or approval and submission | Handler | 3 |

### Reference data

| Route | Purpose | Caller | Ph |
| --- | --- | --- | --- |
| `GET /org-types` | Supported orgTypes and active bundle versions | Any client | 1 |
| `GET /schemas/{orgType}/versions` | Released bundle versions | Any client | 1 |
| `GET /schemas/{orgType}/versions/{version}` | Immutable bundle: profiles, layout, manifest, rules version, messages | Any client | 1 |
| `GET /lookups/abn/{abn}` | Registry lookup for wizard and RM, cached | RM, POBO | 2 |

### Administration and operations

| Route | Purpose | Caller | Ph |
| --- | --- | --- | --- |
| `GET` and `PUT /admin/notification-rules/{ruleId}` | Versioned notification, template and timer rules | Admin | 2 |
| `POST /onboarding-requests/{id}/notifications` | Resend a notification | RM, admin | 2 |
| `GET /admin/cases/{id}/workflow` | Workflow state, pending timers, last events | Support engineer | 2 |
| `POST /admin/cases/{id}/workflow/{action}` | Retry, reset or terminate, with reason and audit | Support engineer | 2 |
| `POST /admin/reconcile` | Trigger the SO-to-Temporal sweeper | Support engineer | 2 |
| `GET /audit/cases/{id}` | Audit export | Auditor | 2 |
| `POST`, `GET`, `DELETE /webhooks/subscriptions` | Event subscriptions for consumer apps | Consumer app | 3 |
| `GET /health/live` and `/health/ready` | Probes | Platform | 1 |

## Data model, non-functional requirements and security

EON needs thirteen tables, targets that are proposals until the business supplies volumes, and a control set mapped to bank obligations that Compliance must confirm.

### Data model (EON PostgreSQL)

| Table | Key fields | Notes |
| --- | --- | --- |
| `onboarding_case` | case ID (= ServiceOrderId), orgType, schema bundle version, mirrored status, last SO record version, RM ID, current POBO ID | One row per case; the status is a mirror, SO is the source |
| `case_draft` | case ID, data (JSONB), ETag, client revision, updated by, updated at | Working copy; locked after submission |
| `field_provenance` | case ID, JSON Pointer, source, confidence, retrieved at, verified by, previous value reference | Sidecar to the draft |
| `enrichment_candidate` | case ID, pointer, value, source, confidence, status | Candidates not yet merged |
| `case_snapshot` | ID, case ID, kind (approval or submission), data, SHA-256 hash, actor, time | Immutable |
| `document_register` | ID, case ID, requirement key, status, repository ID, scan result, reason, due date, version | Documentum holds the file |
| `pobo_party` | ID, case ID, name, email, status | History kept when the POBO is replaced |
| `access_link` | ID, party ID, token hash, expires at, used at, revoked at | Hash only; never the token |
| `declaration` | case ID, party ID, text version, accepted at, IP, user agent | Evidence of attestation |
| `notification_rule`, `notification_log` | Versioned rule (event, recipients, channel, template, timer); one log row per send with idempotency key | Rules edited by admins |
| `event_inbox` | event ID (unique), case ID, SO record version, processed at | Deduplication and ordering |
| `sync_outbox` | case ID, payload, attempts, next attempt | Checkpoint syncs to SO |
| `audit_event` | case ID, actor, on-behalf-of, action, pointer, before, after, correlation ID, previous hash | Append-only with hash chain |

Idempotency keys live in Redis with a 24-hour TTL and are mirrored to PostgreSQL for finalize and approve, which must survive a cache flush.

### Non-functional requirements

All targets are proposals pending volumes and criticality ratings from the business (gap G41).

| Quality | Proposed target |
| --- | --- |
| Availability | 99.9% for the POBO form and API; the form stays usable for saves when SO is down |
| Latency (server side, p95) | Draft save under 300 ms; form load under 500 ms; finalize under 3 s excluding Documentum |
| Event lag | SO event to workflow signal under 5 s at p95 |
| Durability | Zero loss of acknowledged draft saves; zero loss of acknowledged finalize |
| Recovery | RPO 5 minutes, RTO 1 hour for EON data; Temporal and Kafka per platform standards |
| Scalability | Stateless API and workers scale horizontally; sizing from peak cases per day and concurrent POBOs |
| Accessibility | WCAG 2.2 AA, tested with automated checks and manual screen-reader passes |
| Browsers and devices | Current and previous major versions of Chrome, Edge, Safari and Firefox; responsive down to phone width |
| Observability | One correlation ID from co-pilot to Temporal; structured logs without PII; alerts on lag, dead letters, and cases stuck beyond a threshold |
| Testability | Contract tests with SO and co-pilot; validator-parity suite; Temporal replay tests on every workflow change |

### Security and compliance controls

| Area | Requirement |
| --- | --- |
| Transport and storage | TLS 1.2 or higher everywhere; encryption at rest; managed keys with rotation; field-level encryption for sensitive identifiers |
| Data classification | Classify every schema field (public, internal, personal, sensitive); drive masking, logging and retention from the classification |
| Application security | Verify against OWASP ASVS level 2; output encoding for all stored values; CSP and CSRF protection; no secrets or PII in URLs or logs |
| Files | Streaming upload, content sniffing, malware scan before storage, size and type allow-list |
| Agent boundary | All co-pilot output is untrusted input: validated, sanitised, attributed, never allowed to approve |
| Audit | Append-only audit of data changes, approvals, access to sensitive data and administrative actions |
| Privacy | Collection notice at the POBO's first sign-in; support access and correction requests; collect only what the schema needs |
| Retention | Retention and purge periods set by policy, with legal-hold override |
| Regulatory mapping | Map requirements to AML/CTF customer due diligence, the Privacy Act's Australian Privacy Principles, and APRA CPS 234 and CPS 230; Compliance to confirm scope |
