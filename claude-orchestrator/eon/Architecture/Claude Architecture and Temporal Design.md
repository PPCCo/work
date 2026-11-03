# Entity Onboarding Platform: Architecture and Temporal Design

Nov 4, 2026 · @Abbas

## Executive summary

**Use one long-running Temporal workflow per onboarding request, with child workflows for enrichment and screening. Keep working data in an app-owned Draft Store, not in Temporal history. Treat Servicing Order (SO) as the system of record for committed data and status, and write to it only through one Temporal-driven path behind our own Onboarding API.**

In short: Temporal holds process state, the Draft Store holds work in progress with provenance, and SO holds the committed record. Your instinct to delay posting to SO until the RM is ready is right. The container is the issue: Temporal is the wrong place to hold the data itself.

| Your question | Recommendation | Why |
| --- | --- | --- |
| One workflow per request, or different ones? | One parent workflow per request for the whole lifecycle, plus child workflows for enrichment, screening and re-enrichment. Not one workflow per phase. | The phases share state, timers and cancellation. Children keep the parent history small and isolate failures. |
| Hold enrichment data in Temporal until the RM submits, or write straight to SO? | Neither. Hold it in a Draft Store that the workflow references by ID, and write to SO at explicit commit points. | Workflow history has size limits, cannot be queried and is a poor home for PII. SO validates against final schemas and emits a Kafka event on every write, so drafts there cause failed validations and event noise. |
| Should the co-pilot post to SO directly, or go through our API? | Through our Onboarding API. Only Temporal activities write to SO. | One writer gives idempotency, authorisation, schema validation and an anti-corruption layer. The LLM agent should never hold SO credentials, and submit must be a deliberate human action. |
| Where does the entity's in-progress form data live? | In the Draft Store only. The workflow receives milestone signals (opened, submitted), and SO receives validated data on submit. | Autosave volume would bloat workflow history and flood the SO Kafka topic with events that trigger notifications. |

**Gaps to close before build** (full list in the gap analysis section):

- When does the SO request come into existence: at the first RM message, or at RM commit?
- What SO can actually do: draft status, partial updates, idempotency keys, optimistic locking, rate limits and event schema.
- Kafka events can be duplicated, reordered, or echoed back from our own SO writes.
- AI-enriched data needs provenance, human confirmation and defences against prompt injection from scraped websites.
- How an entity user is authenticated, and who owns each field once the entity and RM can both edit.
- Schema versioning for requests that stay in flight for weeks, with one validator behaviour across frontend, backend and SO.
- Retention, privacy and AML/CTF obligations for data collected from public sources.

## Context and assumptions

The design treats SO as a closed case-management system that we can only reach through its REST API, schema registry and Kafka topic, and treats everything else as ours to shape.

**Fixed constraints taken from your brief**

- SO is third-party. Only its REST API is exposed, so we have no database access and no hooks.
- SO emits a Kafka event on every record create or update, and validates submitted data against orgType JSON Schemas in its schema registry.
- Temporal is the orchestrator. A Kafka consumer is needed to bridge SO events into it, because Temporal workers poll Temporal task queues, not Kafka.
- The same orgType JSON Schemas validate data in the NextJS frontend and in our backend.
- The AI co-pilot may only collect data from whitelisted public sources.

**Assumptions I made.** Each one changes the design if it is wrong, so please confirm or correct them.

| # | Assumption | If wrong |
| --- | --- | --- |
| A1 | "IPO API" means a public registry such as ABN Lookup, ASIC or ACNC, not IP Australia. | The source adapters and the data we can prepopulate change. |
| A2 | SO gives us a stable request ID, a configurable status model, and either partial updates or versioned full updates. | The write pattern in Decision 1 needs a different shape (see open questions). |
| A3 | SO accepts a client-supplied external reference, so we can store our own request ID on the SO record. | We need a mapping table and lookups to join SO events back to workflows. |
| A4 | Entity users sign in with a bank-issued invitation plus a one-time code, not a full customer login. | The entity authentication design needs rework. |
| A5 | A request stays open for days to weeks while the entity gathers information. | If it is hours, the history and versioning concerns shrink. |
| A6 | Volume is modest (not millions of requests). | Worker sizing changes, though the topology does not. SO rate limits matter regardless. |
| A7 | Australian obligations apply: the Privacy Act and AML/CTF customer identification and beneficial ownership rules. | Retention, consent and data-sourcing rules change. |

## Temporal design

Use one parent workflow per onboarding request as the lifecycle spine, and spawn child workflows for bounded, retryable pieces of work. The parent starts at the RM's first action, before any SO request exists, so drafting, commit, entity completion and review are one execution with one set of timers and one cancellation scope.

### Workflow topology

| Workflow | Instances | Typical life | Responsibility | Why it is separate |
| --- | --- | --- | --- | --- |
| OnboardingRequestWorkflow (parent) | One per request | Days to weeks | Lifecycle state machine, timers, SO writes at commit points, handling of RM and entity actions | The single owner of request state and cancellation |
| EnrichmentWorkflow (child) | One per enrichment run | Minutes | Fan out to whitelisted sources, normalise results, write them to the Draft Store with provenance, return a summary | Isolates retries and rate limits, keeps parent history small, can be re-run on demand |
| ScreeningWorkflow (child), if in scope | One per submission | Minutes to days | Sanctions, PEP and KYC provider calls, possibly waiting on manual review | A long wait with different retry rules |
| NotificationWorkflow (short) | One per notification | Seconds to minutes | Send, retry and record a notification to the RM or entity | Workflow ID equals the event ID, so duplicate Kafka events cannot send twice |

Do not make one workflow per phase (an RM workflow, then an entity workflow). The phases share state and timers, and a hand-off between workflows adds a failure window. Do not put everything inline in the parent either: history growth, versioning pain and failure blast radius all get worse.

### Identity and start semantics

- **Workflow ID** is `onb-{requestId}`. The requestId is a UUID minted by our Onboarding API, not the SO ID, because the SO request may not exist yet.
- **Idempotent start**: use a conflict policy that returns the existing execution when the same ID is started twice, so a double-click or retry never creates two requests.
- **Search attributes**: requestId, soRequestId (once known), orgType, schemaVersion, phase and rmId. Keep names and personal data out of search attributes and IDs.
- **Correlation**: write our requestId to the SO record's external reference field, so SO Kafka events can be routed back to the right workflow without a lookup table.

### How the outside world talks to the workflow

| Event | Mechanism | Reason |
| --- | --- | --- |
| RM clicks Submit on the review screen | Update `commitByRM` | An Update validates before it enters history and returns the SO request ID to the caller. |
| Entity submits the form | Update `submitByEntity` | Same: a synchronous accept or reject with validation errors the UI can show. |
| RM asks to re-run enrichment | Update `requestEnrichment` | Starts a child workflow and returns its ID. |
| Entity opens or saves the form | At most one `entityActive` signal per session | Resets the reminder timer without writing an event per autosave. |
| Someone else changes the SO status | Signal `soStatusChanged` from the Kafka consumer | SO is not the only actor. See the Kafka handling section. |
| Cancel or withdraw | Signal or Update `cancel` | Triggers compensation. |
| UI needs current status | Read model (Draft Store plus SO GET), not a Query | Queries fail when no worker is running and add worker load. Keep them for diagnostics. |

### Rules for activities

Every side effect is an activity: SO calls, public-source calls, LLM calls, notifications and Draft Store writes.

- **Idempotent**: derive an idempotency key from requestId, step and data version.
- **Explicit timeouts and retries**: treat 4xx validation errors as non-retryable, and 429 and 5xx as retryable with backoff.
- **Separate task queues** for orchestration, SO integration, enrichment and notifications. Set a per-queue rate limit on the SO queue so an enrichment burst cannot exhaust SO's API quota.
- **Heartbeats** on long scraping or LLM extraction activities, so a stuck worker is detected quickly.
- **LLM calls are activities**, never workflow code, because they are non-deterministic.

### Long-running concerns

- **History limits**: roughly 51,200 events or 50 MB per execution, with warnings from about 10,000 events, and about 2 MB per payload. Check the exact limits for your Temporal version. Pass references to Draft Store records rather than the data, and use Continue-As-New at phase boundaries.
- **Versioning**: requests live for weeks, so a deploy will land mid-flight. Adopt Worker Versioning or the patching API from day one, and replay captured histories in CI.
- **Payload encryption**: use a custom Data Converter with a codec server so workflow inputs, results and signals are encrypted at rest in the Temporal history.
- **Timers**: durable timers in the parent for entity reminders, entity expiry and RM draft idle timeout.
- **Compensation**: if a request is cancelled or expires after the SO record exists, run an explicit saga step that moves SO to a cancelled status and notifies the parties.

## Decision 1: where working data lives

**Keep enrichment and draft data in a Draft Store that we own, reference it from the workflow by ID, and write to SO only at explicit commit points.** This keeps your idea of not posting to SO until the RM is ready, without turning Temporal history into a database.

| Criterion | A. Data held in Temporal | B. Data written straight to SO | C. Draft Store, commit to SO (recommended) |
| --- | --- | --- | --- |
| Fit for document-sized, evolving data | Poor: payloads are about 2 MB and history is append-only and capped | Good, if SO accepts partial data | Good: versioned JSON |
| Query, audit and reporting | Poor: history is not a queryable store, and Queries need a running worker | Good: SO is the record | Good: SQL over drafts, evidence kept alongside |
| PII control, retention, deletion | Hard: data sits in immutable history until retention expires | Governed by SO | Ours to govern: redact, retain and delete by policy |
| Validation | Whatever we code | SO validates the final schema, so partial data is rejected or needs relaxed schemas | We validate in draft mode, SO validates at commit |
| Kafka noise | None | An event per write, so enrichment bursts reach notification logic | Events only at commit points |
| Recovery | A reset or terminated workflow can lose or replay data | SO is durable | Draft survives a workflow reset, and the workflow can be rebuilt from it |
| Extra components | None | None | One service and one database |

Option C costs one extra service, but it is the only option that is acceptable on every row. Option A fails on size, queryability and PII. Option B fails on validation and event noise, and it also makes SO responsible for data nobody has confirmed yet.

**What the Draft Store holds**

- One working JSON document per request, with a version for optimistic concurrency, plus the pinned orgType and schemaVersion.
- Field-level provenance: source, retrieval time, confidence, a pointer to the evidence, and a status (suggested, confirmed by RM, attested by entity, overridden).
- Raw evidence such as API responses and website snapshots in object storage, with a retention period. The document stores only references.
- An audit trail of who or what changed each field and when.

**What Temporal keeps**: phase, IDs, data version numbers, timer state and pending-action flags. Nothing larger than a reference. The RM's chat transcript stays in the co-pilot's session store, not in the workflow.

**Commit points**

| When | Written to SO | Validated against | Status change |
| --- | --- | --- | --- |
| RM commits | Create the SO request with identity data and the prepopulated fields the RM confirmed | The intake-stage schema (see the schema section) | Request created and submitted to the entity |
| Entity submits | Complete entity data | The full orgType schema | Moves to review |
| After submission | Screening results, RM and ops notes, extra documents | Per-attachment rules | Per the SO status model |
| Cancel or expiry | Reason code | None | Cancelled or expired |

**When to create the SO request earlier.** Your brief reads as if the RM creates the SO request on the first message. If ops or compliance need to see in-flight drafts, or if SO must issue the ID up front, create it at the first RM message in a draft status with identity data only, and still keep everything else in the Draft Store. The cost is that abandoned drafts pollute SO and emit events, so a cleanup path is required. Prefer commit-time creation unless a requirement forces the earlier one. Either way, run a duplicate check on ABN or ACN before creating a request.

## Decision 2: how the co-pilot submits

**The co-pilot calls our Onboarding API, which sends an Update to the workflow. The workflow's activities are the only code that writes to SO.** The co-pilot never posts to SO directly.

- **Single writer**: only the SO-integration activities hold SO credentials, so retries, idempotency and rate limiting live in one place.
- **Server-side validation** against the orgType schema plus business rules JSON Schema cannot express, such as ABN and ACN checksums.
- **Authorisation and audit**: an RM can only act on entities in their own portfolio, and every commit is logged against a named person.
- **Anti-corruption layer**: SO's data model and API quirks stay inside one adapter, so a vendor change does not ripple into the UI or the agent's tools.
- **Agent safety**: the LLM agent gets narrow tools such as `get_draft`, `propose_fields` and `request_enrichment`. It does not get `submit`. Commit is a button on a review screen showing each field with its source and confidence, executed with the RM's own token. The agent can prepare, but a human commits.
- **Idempotency**: the API requires a client idempotency key, so a double-click or a retried request cannot create two SO records.

The cost is one more hop, and Temporal's availability becomes part of the commit path. If SO is down at commit time, the activity retries with backoff while the RM sees a "submitting" state. Nothing is lost because the data is already in the Draft Store. If Temporal itself is unavailable, the API returns an error and the RM retries, which is the same behaviour you would have with SO down.

## Decision 3: entity form data

**Store in-progress entity data in the Draft Store only. The workflow hears about milestones, not keystrokes, and SO receives validated data on submit.**

- **Not in the workflow**: every autosave would add history events and a workflow task. Across many entities that bloats history, adds latency and raises cost, and file attachments would hit payload limits.
- **Not in SO**: every write would emit a Kafka event that can trigger notifications, partial data would fail schema validation, and SO's API quota would be spent on transient state.
- **Not both**: two copies of unfinished data will diverge, and you would then have to decide which one wins.

**How it works**

1. The entity opens the invitation link and authenticates (invite token plus one-time code). The API loads the Draft Store document, which already carries the prepopulated, RM-confirmed data.
2. Autosave sends a debounced JSON Merge Patch with the document version. The API validates in draft mode, writes to the Draft Store, and returns 409 on a version conflict so the UI can merge.
3. Section validation runs against the full schema for that section, with no workflow involvement.
4. The first open in each session sends one `entityActive` signal, which resets the reminder timer.
5. Submit calls the Update `submitByEntity` with the draft version. The workflow runs full-schema validation, freezes that version, writes to SO, moves the status, and returns accept or reject with field errors.
6. Attachments go to object storage with a malware scan, and the draft stores references. How they reach SO depends on whether SO has an attachment API.

**Draft mode versus final mode.** Derive a draft schema mechanically from each orgType schema by dropping `required` and minimum-count constraints, and keep type and format checks. Validate drafts against it and submissions against the full schema. This avoids maintaining two schemas by hand.

**Field ownership.** When the RM and entity can both edit, agree precedence per field. A sensible default is entity-attested over RM-entered over public-source. While the entity form is open, co-pilot changes arrive as suggestions rather than overwrites.

## Decision 4: Kafka event handling

**Run a dedicated bridge service that consumes SO events and turns them into Temporal signals or short workflows. Make it idempotent, and decide per event type what it may trigger.** A Temporal worker polls Temporal task queues, not Kafka, so a separate consumer is required.

| Concern | Approach |
| --- | --- |
| Ordering | Partition by SO record ID so one request's events stay in order. |
| Delivery | At-least-once: commit the Kafka offset only after Temporal accepts the signal or start. |
| Duplicates | The workflow keeps the last processed record version and ignores older or repeated events. NotificationWorkflow IDs are derived from the SO event ID, so a replay cannot send twice. |
| Echo of our own writes | Every status change we make comes back as an event. The workflow ignores a `soStatusChanged` signal whose status it already holds, so echoes are harmless. |
| Update noise | Notifications fire on status transitions, never on record updates. Data-only updates are ignored or refresh the read model. |
| Unknown records | Events with no external reference to one of our requests are dropped and counted. |
| Poison events | Malformed events go to a dead-letter topic with an alert. |
| Missed events | A scheduled reconciliation compares SO status with workflow phase for open requests and repairs drift. Kafka retention is finite and consumers fall behind. |

**Single path for status notifications.** Send status-change notifications from the Kafka bridge only, not also from the workflow after its own SO write. SO is the record for status, and ops or other systems may change it too, so one path keeps behaviour consistent. The cost is a little extra latency. The workflow still sends the notifications SO never announces: reminders, expiry warnings and enrichment-complete messages.

## JSON Schema strategy

**Keep every orgType schema in one versioned repository, publish it as a package that the frontend and backend both consume, and register the same bytes in SO's registry from CI.** Three validators will judge the same data (browser, backend, SO), so the main risk is drift between them.

- **Layout**: `schemas/<orgType>/<semver>/` holds an intake schema and a full schema. UI hints live in a separate uischema file, so SO never sees them.
- **Self-contained schemas**: bundle `$ref` and `$defs` at build time, so each registered schema resolves without cross-file references. Registries often cannot follow them.
- **One schema per orgType**, selected by the orgType field. Avoid one large schema with `oneOf` branches, which gives poor error messages.
- **CI pipeline**: lint, run shared valid and invalid fixtures per orgType, build the frontend and backend packages, register the version in SO, and record the content hash. A contract test compares the hash registered in SO with the one the app uses, and the deploy fails on mismatch.
- **Validator parity**: confirm which JSON Schema dialect SO supports and use that one. Avoid custom keywords. Document the keyword subset in use. Run the same fixtures through all three validators, because format assertions, `$ref` resolution and `unevaluatedProperties` are where they differ.
- **Stages**: the intake schema is a subset of the full schema, used at RM commit. The draft schema is derived mechanically from the full schema (Decision 3). SO must be able to accept the intake stage, or the RM commit cannot validate there. This is an open question.
- **Rules JSON Schema cannot express**: ABN and ACN checksums, cross-field rules and registry cross-checks go in a shared validation library with the same unit tests in frontend and backend, run after schema validation. SO will not know these rules, so the backend must enforce them.
- **Field metadata in a sidecar file**, not in the registered schema: which public sources may prefill a field, and its PII classification. The enrichment mapping and log masking use it, and the SO registry stays clean.
- **Version pinning**: a request records orgType and schemaVersion at creation, in the workflow input, the Draft Store and the SO record. In-flight requests finish on their pinned version. Changes within a major version are additive only. A breaking change is a new major version, with a migration activity for open drafts if the business needs it.

## Ambiguity and gap analysis

**Twenty-two gaps stand out; eleven are high priority and should be settled before build.** They fall into five groups. The unknowns about what SO can do (G7 to G10) are the most urgent, because several design choices above depend on them.

### Process and scope

| # | Gap or ambiguity | Recommendation | Priority |
| --- | --- | --- | --- |
| G1 | When the SO request is created is unclear. The brief has the RM submitting a request first, and also proposes holding data until the RM is ready. | Create it at RM commit. Use an early draft status with identity data only if ops need visibility. | High |
| G2 | No SO status model is given: which statuses exist, who may trigger each transition, and how they map to workflow phases. | Draw one status model. Map each SO status to a workflow phase and name the owner of each transition. | High |
| G3 | KYC and AML screening, document verification, and an approval or four-eyes review step are not mentioned. They are core to bank onboarding. | Confirm scope, then add them as explicit phases, with screening as a child workflow. | High |
| G4 | Related parties are missing: directors, trustees, beneficial owners and signatories each need their own identity checks, and possibly their own invitation. | Model them as sub-entities with their own tasks. Consider one child workflow per party. | High |
| G5 | Exit paths are undefined: reject, withdraw, expiry, reopen, and amendment after submission. | Define each path. Add expiry timers and compensation steps. Treat a reopen as a new request linked to the old one. | Medium |
| G6 | Duplicate and existing-customer detection is absent. | Check ABN or ACN against open requests and existing customers before creating the SO request. | Medium |

### Servicing Order integration

| # | Gap or ambiguity | Recommendation | Priority |
| --- | --- | --- | --- |
| G7 | SO capabilities are unknown: partial updates, optimistic locking, idempotency keys, rate limits, an attachment API, lookup by external reference, and uptime. | Run a one-week SO capability spike. Record the answers as a written SO contract and build contract tests against its sandbox. | High |
| G8 | Schema registry semantics are unknown: JSON Schema dialect, whether a request can pin a version, and whether an intake-stage subset is accepted. | Ask the vendor now. Fallback: one full schema plus an SO draft status. | High |
| G9 | The Kafka event contract is unknown: payload content, event ID, record version, actor, ordering guarantee and retention. | Get the written contract. Build the reconciliation job regardless. | High |
| G10 | SO outage behaviour is undefined at commit and submit time. | Retry with backoff, show a "submitting" state, keep data in the Draft Store, and alert on backlog. | Medium |

### AI enrichment

| # | Gap or ambiguity | Recommendation | Priority |
| --- | --- | --- | --- |
| G11 | Scraped and LLM-extracted data could be treated as fact in a regulated record. | Store it as a suggestion with an evidence link and confidence. Require RM confirmation and entity attestation before it counts. | High |
| G12 | Prompt injection: a scraped website can carry instructions aimed at the agent. | Treat fetched content strictly as data. Give the extraction step no tools. Constrain outputs to the schema. Restrict network egress to allowlisted hosts. Give the agent no submit tool. | High |
| G13 | "Whitelisted public sources" is not defined, including terms of use, fees, rate limits and permitted data. | Keep a source registry: owner, terms, cost, rate limit, permitted fields and applicable orgTypes. Approve each source before use. | Medium |
| G14 | Coverage differs by orgType. Trusts and government bodies publish little, so prepopulation benefits vary. | Write an enrichment plan per orgType. Measure the prefill rate so the benefit claim can be checked. | Medium |
| G15 | Rules for conflicting or stale data are undefined. | Set precedence by source and recency. Re-fetch before submit if data is older than an agreed age. | Medium |
| G16 | No quality measure or change control for the agent. Model updates can change behaviour. | Keep a golden evaluation set, pin model versions, log prompts and outputs for audit, and define a fallback when the LLM is down. | Medium |
| G17 | The term "IPO API" is ambiguous. | Confirm which registry is meant (see assumption A1). | Medium |

### Security, privacy and compliance

| # | Gap or ambiguity | Recommendation | Priority |
| --- | --- | --- | --- |
| G18 | How an entity user proves identity and authority to act for the entity is unspecified. This is a fraud vector. | Invite through an RM-verified contact, with a one-time code or MFA, short-lived single-purpose tokens, rate limiting and session binding. Verify authority during KYC. | High |
| G19 | Personal information about directors and officeholders collected from public sources raises privacy obligations. | Run a privacy impact assessment. Collect the minimum, give notice to the entity, and set retention by data class. | High |
| G20 | PII can leak into Temporal history, logs, LLM prompts and Kafka. | Encrypt Temporal payloads, mask logs, review LLM provider terms and region, and keep PII out of search attributes. | High |

### Operations

| # | Gap or ambiguity | Recommendation | Priority |
| --- | --- | --- | --- |
| G21 | Audit and record keeping: who or what set each field, when, and from which source, kept for the regulatory period. | Keep an append-only audit trail in the Draft Store and export the final provenance at commit. Confirm retention periods with compliance. | High |
| G22 | Volumes, availability targets, disaster recovery and support tooling are not stated. | Gather targets and set RPO and RTO. Provide a per-request timeline, stuck-request alerts and a runbook for reset and terminate. | Medium |
