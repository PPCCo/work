Our Bank is building an entity onboarding application, where entities are different types of entity/organization (Company, Trust, Government Org, etc) who submit onboarding requests. Each organization type has slightly different data requirements so we use JSON Schema validation for each orgType, which will be used by both the frontend and the backend to validate the data submitted by the entity.

We are using a ServicingOrder (SO) System (with an API and database), owned and maintained by another squad, that maintains all the requests and the status changes. Only the Rest API is exposed to us. We will need to call the API to change the request status, and to add more request specific data as it gets enriched by different sources or the RM or the customer. SO also stores JSON Schemas in its schema registry, each request type will have a different schema that SO will will validated the submitted request data against. SO emits a Kafka event on every record create or update, and validates submitted data against orgType JSON Schemas in its schema registry.

Redis cache will be used to latency reduction and performance.

Documents submitted as part of the onboarding request will be stored in Documentum. The OrgType specific JSON Schema will specify which documents are required. The Temporal workflow will maintain which documents have been submitted, along with their status (eg submitted, in-review, approved, rejected, etc) and the link to specific documentum location where they are stored. The case handler can request additional documents for a specific case, which will be tracked in the same manner by the workflow.

The journey starts when Bank's Relationship Manager (RM) submits a Servicing Order Request through a AI-driven (co-pilot) chat-like interface, where RM provides initial data for the org that needs to be onboarded, like the Org Name, Org Type, ABN/ACN number. RM will also provide name and email of an entity representative (POBO, short for Person-on-behalf-of). The AI Agent will fetch additional data from different sources, like fetch the data from IPO API, organization website, and other public whitelisted sources. The more data we collect from publicly available sources the better, as it provides convenience to the organizations by prepopulation a lot of data when they are asked to fill in and submit the form.

SO will emit a Kafka event on every record create or update, and validates submitted data against orgType JSON Schemas in its schema registry. Temporal will be used as the orchestrator. There will be one long-running Temporal workflow per onboarding case, with activities and child workflows for specific work such as data enrichment, document collection, validation and notifications. A Kafka consumer will bridge SO events into Temporal, since Temporal workers poll Temporal task queues, not Kafka. The same orgType JSON Schemas validate data in the NextJS frontend and in our backend.

The co-pilot will not directly interact with SO. It will only interact with EON API to create (POST) and update (PATCH) an onboarding request. Since co-pilot work is being done by another team, we don't need to worry about that part, we only need to expose the necessary API endpoints that will allow co-pilot, or any consumer app, to do CRUD operations (with proper authorizations) in different ways.

EON API will expose a POST endpoint for creating a new onboarding request, and it will authenticate and validate the request before submitting a SO-Create request to SO API. A PATCH request will also be exposed and every PATCH request will update the data in SO. The RM and the co-pilot agent will be able to call the PATCH endpoint multiple times, every time the request data and status needs to be updated. There would by multiple statuses. When the initial SO request is created for the first time for a specific entity, the status will be set to 'DRAFT'. Then there can be multiple statuses, for example IPO_ENRICHED, COPILOT_ENRICHED, etc. A source field will also be maintained for each field to keep a track of where the data came from. Once the data has been enriched from different sources, and RM is satisfied with the enriched data, he will approve the request submission by submitting the request with status of RM_APPROVED.
There will be separate command endpoints; approval only with an RM's delegated token and a hash of the approved data.

When the request is initially created with DRAFT status Temporal workflow will start for that specific case (ServiceOrderId). It will Wait for RM approval (status: RM_APPROVED), and on the RM_APPROVED signal, Temporal workflow will trigger different activities, like sending notification to RM and the POBO along with context and login credentials. On successfully sending the notification, the status will change to POBO_NOTIFIED, and Temporal workflow will start waiting for status POBO_SUBMITTED (entity submission).

The status changing to POBO_NOTIFIED and the POBO receiving an email is the first time the EON UI Forms will come into play. The POBO, after logging in with the credentials received in the email, will be presented with the onboarding form. The form presented to POBO will be a form wizard, a stepped, multi-page form, and many of the form fields will be pre-populated with the data enriched by different sources and stored in SO database. 

Each time a notification is sent to the RM or POBO, the workflow may or may not start a timer with predefined duration specific to the event, and if the status is not changed by the timer expiry, another notification will be sent to the relevant party. This notification to timer mapping should be configurable, since each notification may have different timer duration, notification group, email text/template, etc.

Note that the temporal piece is still under development, so in the initial implementation, only form functionality, including the auto-populating data from existing SO record (fetch via EON API for the current onboarding request ID). Also note that when 

## Form

The form submission workflow will follow the "Draft-Saving Progressive Wizard" pattern. It separates the user's temporary progress from the final completion, balancing a forgiving user experience (UX) with strict data integrity.

Here is the engineering and UX strategy broken down by stage.

### 1. Step-Level Soft Validation & Error UI

The goal here is to guide the user without trapping them. "Soft validation" means checking the data but never blocking the user from clicking "Next" or "Back."

- Trigger on Blur and "Next": Run validation rules locally (client-side) when a user moves away from an input fields (blur) or clicks the "Next" button.
- Inline Warnings, Not Errors: Use a distinct visual style for step-level failures. Instead of aggressive red "Error" banners, use amber/yellow warning text or subtle helper messages (e.g., "This looks incomplete, but you can finish it later").
- Persistent Step Indicators: Show a "Warning" or "Incomplete" icon (like an exclamation mark) on the step navigation tabs at the top or side of the form. This allows users to visually track which steps still need attention before final submission.

### 2. Auto-Saving Progress (Server-Side)

To save data regardless of validation state, the server must treat step-level submissions as a "Draft" state.

- Debounced or "Next" Anchored Saves: Send a payload to the server every time a user clicks "Next", "Back", or after a 2-second typing pause (debounce).
- Bypass Server-Side Validation Constraints: The server endpoint for step-saving must accept partial, malformed, or missing data.
- JSON Schema Validation: The OrgType specific JSON Schema wil drive both the frontend and backend validation.

### 3. Hard Validation on Complete Submission

The final "Submit" action requires a completely different architectural treatment.

- Client-Side "Pre-Flight" Check: When the user clicks the final "Submit" button, a global client-side validation script will run to validate the full JSON payload (across all steps combined). If errors are found, prevent the network request, jump the user's viewport directly to the first broken step, and flip the amber warnings to red hard errors.
- Server-Side Hard Validation (The Gatekeeper): Once the client-side check passes, send a POST /submissions/finalize request. The server must re-validate everything from scratch. It should pull the compiled draft data, run strict validation business rules, and reject the request with a 422 Unprocessable Entity status code if anything is wrong. The validation will also include validation of all the required documents being submitted.
- Atomic Promotion: Only if the server-side hard validation passes should the ServicingOrder request status will change from POBO_NOTIFIED to POBO_SUBMITTED. The temporal worker, that is listening for this POBO_SUBMITTED status, will notify the RM and POBO and any other relevant parties about it. Temporal will then listen for different status changes, for example, INFO_REQUESTED (in case POBO is asked to provide additional information), REJECTED (in case the request is rejected), or COMPLETE (if the request is successfully completed).

### Summary of the Workflow Architecture

| Action | Client-Side Behaviour | Server-Side Behaviour | Data Integrity |
| --- | --- | --- | --- |
| User types & clicks "Next" | Evaluates fields; shows amber warnings if invalid. Does not block navigation. | Accepts payload as-is. Stores in a nullable/JSON draft state. | Flexible (Garbage in, draft saved). |
| User clicks final "Submit" | Aggregates all steps. Blocks submission if invalid; points user to errors. | Runs strict, non-nullable validation logic against the entire dataset. | Strict (Only perfect data is finalized). |

## TASK

Act as a Expert System Architect and conduct a critical/ambiguity review and gap analysis of the above requirements and architecture, and suggest any gaps or improvements and potentially, the best/optimal solution to implement this. Also create a requirements specifications (including high level system design, workflow diagrams and architecture diagrams, high level scenarios, use cases, and user stories). Think hard of any other scenarios and API features/requirements/endpoints that I may have missed or would be beneficial.

---
---
---
---

# Claude Response

## Completed: EON architecture review and requirements specification

Download the EON Architecture Review and Requirements Specification (Word)

The document is 31 pages and is based on your supplied requirements. It includes:

- Critical ambiguity and gap analysis, with 20 identified findings and recommended resolutions.
- Recommended target architecture, component responsibilities and system-of-record boundaries.
- Case lifecycle and status-transition model, with workflow and architecture diagrams.
- JSON Schema versioning, draft validation, autosave and final-submission strategy.
- Proposed EON REST API catalogue, endpoint purposes, contract rules and example payloads.
- Documentum upload, scanning, review, replacement and additional-document workflows.
- Kafka event contract, Temporal workflow model, retries, idempotency and recovery.
- Security, authorisation, provenance, notifications, audit and non-functional requirements.
- High-level use cases, 24 edge-case scenarios, user stories and acceptance criteria.
- Delivery phases, implementation decisions requiring agreement, test strategy and open questions.

### The most important architectural finding

Your requirements contain a conflict between strict SO schema validation on every update and saving incomplete wizard drafts. A schema that requires mandatory fields will reject a partial draft. The specification therefore recommends separate draft-persistence and finalisation behaviours: draft saves accept valid partial JSON and return diagnostics, while finalisation strictly validates the authoritative data and documents before SO conditionally changes the status.

The other major recommendation is to keep SO authoritative for case data and lifecycle status, use Kafka as an at-least-once event transport with idempotent consumers, and use Temporal for durable orchestration—not as a second case database. Temporal's messaging and workflow execution models support this separation.

The report also flags several decisions that must be confirmed with the SO, product, security and operations teams before implementation. In particular, whether SO can support permissive draft updates and an atomic, revision-conditional finalisation command is a key delivery dependency.