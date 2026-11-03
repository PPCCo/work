# Recommended architecture

My recommendation is to build an Onboarding Orchestration Layer between the RM/Next.js experiences and the third-party Servicing Order (SO) System.

Use one long-running Temporal workflow per onboarding case, with activities and child workflows for specific work such as data enrichment, document collection, validation and notifications. Do not create a separate top-level workflow for every API call or every field update.

The most important design principle is to keep three responsibilities separate:

1. Business data ownership: a database and the SO System hold the actual onboarding data.
2. Process orchestration: Temporal coordinates the lifecycle, waits for people and systems, retries work and records process progress.
3. User interaction and integration: your own APIs handle RM and entity requests, enforce access and validation rules, and integrate with SO and external data sources.

I would not use Temporal workflow state as the primary storage for the application’s form data. Temporal is durable orchestration, not a substitute for an application database. Workflow history is valuable for recovering and understanding a process, but it is not the right place to keep a continually edited, potentially sensitive entity profile.

The recommended ownership model is:

| Information                                                | Recommended owner                                                            |
| ---------------------------------------------------------- | ---------------------------------------------------------------------------- |
| RM's working draft before official SO submission           | Your Onboarding Application database                                         |
| Workflow progress, timers, retries and waiting conditions  | Temporal                                                                     |
| Official SO request and its official status after creation | Servicing Order System                                                       |
| Entity's saved form responses after submission             | SO, with an application-side projection/cache where needed                   |
| External enrichment results and their provenance           | Your application database                                                    |
| Documents                                                  | Approved document-management/object-storage platform; store references in SO |
| Notifications and delivery attempts                        | Notification service, coordinated by Temporal                                |

There is one important qualification: if SO supports a genuine Draft/Incomplete state, I would seriously consider creating the SO record at the beginning of the journey instead. That may let SO remain the canonical owner of the entire request from the outset. I explain the decision criteria below.

## 1. High-level architecture

I would introduce the following components.

| Component               | Responsibility                                                                                             |
| ----------------------- | ---------------------------------------------------------------------------------------------------------- |
| RM Copilot              | Conversational intake, questions, source discovery, enrichment review and RM approval                      |
| Entity Portal (Next.js) | Customer-facing onboarding forms, document uploads, saving and submitting information                      |
| Onboarding API / BFF    | Single trusted API entry point for both experiences; identity, access, validation and request coordination |
| Onboarding Database     | Drafts, working data, revisions, enrichment evidence, integration records and read models                  |
| Temporal                | Long-running request lifecycle and orchestration                                                           |
| Enrichment Service      | Connectors for ABR, ASIC, other approved registers, websites and AI-assisted extraction                    |
| SO Integration Adapter  | Encapsulates all Servicing Order REST API interactions                                                     |
| Schema Service          | Retrieves, caches and distributes versioned organization-specific JSON Schemas                             |
| SO Kafka Consumer       | Consumes SO events, deduplicates them, updates projections and signals workflows                           |
| Notification Service    | Email/SMS/other approved notifications to RMs, customers and internal teams                                |

### Proposed component diagram

\#chatgpt-mermaid-\_r_c7\_{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;fill:rgb(13, 13, 13);}@keyframes edge-animation-frame{from{stroke-dashoffset:0;}}@keyframes dash{to{stroke-dashoffset:0;}}#chatgpt-mermaid-\_r_c7\_ .edge-animation-slow{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 50s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-\_r_c7\_ .edge-animation-fast{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 20s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-\_r_c7\_ .error-icon{fill:rgb(243, 243, 243);}#chatgpt-mermaid-\_r_c7\_ .error-text{fill:rgb(13, 13, 13);stroke:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_c7\_ .edge-thickness-normal{stroke-width:1px;}#chatgpt-mermaid-\_r_c7\_ .edge-thickness-thick{stroke-width:3.5px;}#chatgpt-mermaid-\_r_c7\_ .edge-pattern-solid{stroke-dasharray:0;}#chatgpt-mermaid-\_r_c7\_ .edge-thickness-invisible{stroke-width:0;fill:none;}#chatgpt-mermaid-\_r_c7\_ .edge-pattern-dashed{stroke-dasharray:3;}#chatgpt-mermaid-\_r_c7\_ .edge-pattern-dotted{stroke-dasharray:2;}#chatgpt-mermaid-\_r_c7\_ .marker{fill:rgb(143, 143, 143);stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_c7\_ .marker.cross{stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_c7\_ svg{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;}#chatgpt-mermaid-\_r_c7\_ p{margin:0;}#chatgpt-mermaid-\_r_c7\_ .label{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";color:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_c7\_ .cluster-label text{fill:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_c7\_ .cluster-label span{color:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_c7\_ .cluster-label span p{background-color:transparent;}#chatgpt-mermaid-\_r_c7\_ .label text,#chatgpt-mermaid-\_r_c7\_ span{fill:rgb(13, 13, 13);color:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_c7\_ .node rect,#chatgpt-mermaid-\_r_c7\_ .node circle,#chatgpt-mermaid-\_r_c7\_ .node ellipse,#chatgpt-mermaid-\_r_c7\_ .node polygon,#chatgpt-mermaid-\_r_c7\_ .node path{fill:rgb(222, 234, 251);stroke:rgb(83, 154, 248);stroke-width:1px;}#chatgpt-mermaid-\_r_c7\_ .rough-node .label text,#chatgpt-mermaid-\_r_c7\_ .node .label text,#chatgpt-mermaid-\_r_c7\_ .image-shape .label,#chatgpt-mermaid-\_r_c7\_ .icon-shape .label{text-anchor:middle;}#chatgpt-mermaid-\_r_c7\_ .node .katex path{fill:#000;stroke:#000;stroke-width:1px;}#chatgpt-mermaid-\_r_c7\_ .rough-node .label,#chatgpt-mermaid-\_r_c7\_ .node .label,#chatgpt-mermaid-\_r_c7\_ .image-shape .label,#chatgpt-mermaid-\_r_c7\_ .icon-shape .label{text-align:center;}#chatgpt-mermaid-\_r_c7\_ .node.clickable{cursor:pointer;}#chatgpt-mermaid-\_r_c7\_ .root .anchor path{fill:rgb(143, 143, 143)!important;stroke-width:0;stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_c7\_ .arrowheadPath{fill:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_c7\_ .edgePath .path{stroke:rgb(143, 143, 143);stroke-width:1px;}#chatgpt-mermaid-\_r_c7\_ .flowchart-link{stroke:rgb(143, 143, 143);fill:none;}#chatgpt-mermaid-\_r_c7\_ .edgeLabel{background-color:rgb(252, 252, 252);text-align:center;}#chatgpt-mermaid-\_r_c7\_ .edgeLabel p{background-color:rgb(252, 252, 252);}#chatgpt-mermaid-\_r_c7\_ .edgeLabel rect{opacity:0.5;background-color:rgb(252, 252, 252);fill:rgb(252, 252, 252);}#chatgpt-mermaid-\_r_c7\_ .labelBkg{background-color:rgba(252, 252, 252, 0.5);}#chatgpt-mermaid-\_r_c7\_ .cluster rect{fill:rgb(243, 243, 243);stroke:rgba(0, 0, 0, 0.1);stroke-width:1px;}#chatgpt-mermaid-\_r_c7\_ .cluster text{fill:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_c7\_ .cluster span{color:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_c7\_ div.mermaidTooltip{position:absolute;text-align:center;max-width:200px;padding:2px;font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:12px;background:rgb(243, 243, 243);border:1px solid rgba(0, 0, 0, 0.1);border-radius:2px;pointer-events:none;z-index:100;}#chatgpt-mermaid-\_r_c7\_ .flowchartTitleText{text-anchor:middle;font-size:18px;fill:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_c7\_ rect.text{fill:none;stroke-width:0;}#chatgpt-mermaid-\_r_c7\_ .icon-shape,#chatgpt-mermaid-\_r_c7\_ .image-shape{background-color:rgb(252, 252, 252);text-align:center;}#chatgpt-mermaid-\_r_c7\_ .icon-shape p,#chatgpt-mermaid-\_r_c7\_ .image-shape p{background-color:rgb(252, 252, 252);padding:2px;}#chatgpt-mermaid-\_r_c7\_ .icon-shape .label rect,#chatgpt-mermaid-\_r_c7\_ .image-shape .label rect{opacity:0.5;background-color:rgb(252, 252, 252);fill:rgb(252, 252, 252);}#chatgpt-mermaid-\_r_c7\_ .label-icon{display:inline-block;height:1em;overflow:visible;vertical-align:-0.125em;}#chatgpt-mermaid-\_r_c7\_ .node .label-icon path{fill:currentColor;stroke:revert;stroke-width:revert;}#chatgpt-mermaid-\_r_c7\_ .node .neo-node{stroke:rgb(83, 154, 248);}#chatgpt-mermaid-\_r_c7\_ [data-look="neo"].node rect,#chatgpt-mermaid-\_r_c7\_ [data-look="neo"].cluster rect,#chatgpt-mermaid-\_r_c7\_ [data-look="neo"].node polygon{stroke:url(#chatgpt-mermaid-\_r_c7\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_c7\_ [data-look="neo"].swimlane.cluster rect{filter:none;}#chatgpt-mermaid-\_r_c7\_ [data-look="neo"].node path{stroke:url(#chatgpt-mermaid-\_r_c7\_-gradient);stroke-width:1px;}#chatgpt-mermaid-\_r_c7\_ [data-look="neo"].node .outer-path{filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_c7\_ [data-look="neo"].node .neo-line path{stroke:rgb(83, 154, 248);filter:none;}#chatgpt-mermaid-\_r_c7\_ [data-look="neo"].node circle{stroke:url(#chatgpt-mermaid-\_r_c7\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_c7\_ [data-look="neo"].node circle .state-start{fill:#000000;}#chatgpt-mermaid-\_r_c7\_ [data-look="neo"].icon-shape .icon{fill:url(#chatgpt-mermaid-\_r_c7\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_c7\_ [data-look="neo"].icon-shape .icon-neo path{stroke:url(#chatgpt-mermaid-\_r_c7\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_c7\_ .node text{font-size:14px;font-weight:600;letter-spacing:normal;fill:rgb(0, 79, 153);}#chatgpt-mermaid-\_r_c7\_ .edgeLabels text{font-size:13px;font-weight:600;letter-spacing:-0.08px;fill:rgb(0, 79, 153);}#chatgpt-mermaid-\_r_c7\_ .node tspan[font-weight="normal"],#chatgpt-mermaid-\_r_c7\_ .edgeLabels tspan[font-weight="normal"]{font-weight:600;}#chatgpt-mermaid-\_r_c7\_ .edgeLabel .label rect{opacity:1;rx:13px;ry:13px;fill:rgb(245, 250, 255);stroke:rgb(206, 219, 229);stroke-width:1px;}#chatgpt-mermaid-\_r_c7\_ .node rect,#chatgpt-mermaid-\_r_c7\_ .node circle,#chatgpt-mermaid-\_r_c7\_ .node ellipse,#chatgpt-mermaid-\_r_c7\_ .node polygon,#chatgpt-mermaid-\_r_c7\_ .node path{fill:rgb(229, 243, 255);stroke:rgba(0, 0, 0, 0.1);stroke-width:1px;}#chatgpt-mermaid-\_r_c7\_ .node rect{rx:16px;ry:16px;}#chatgpt-mermaid-\_r_c7\_ .mermaid-decision .label-container{fill:rgb(245, 250, 255);stroke:rgb(206, 219, 229);stroke-dasharray:2,2;}#chatgpt-mermaid-\_r_c7\_ .edgePaths .flowchart-link{stroke:rgb(143, 143, 143);stroke-width:1px;stroke-linecap:round;stroke-linejoin:round;}#chatgpt-mermaid-\_r_c7\_ .marker{fill:rgb(143, 143, 143);stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_c7\_ :root{--mermaid-font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";}External SystemsTemporal PlatformBank Onboarding ApplicationABR / ASIC / ACNCApproved Data SourcesWhitelisted Websitesand Other SourcesServicing Order REST APIServicing Order Kafka TopicSO Schema RegistryTemporal ServiceOnboarding WorkflowWorkersEnrichment ActivitiesSO Integration ActivitiesNotification ActivitiesOnboarding API / BFFIdentity, Authorization andPolicyOnboarding DatabaseDrafts, Revisions, Evidence,Inbox / Outbox, Read ModelsSchema ServiceVersioned Schema CacheAI / Enrichment ServiceRM - Copilot ChatEntity - Next.js PortalEnterprise NotificationServicesSO Kafka ConsumerReads application state

There are a few deliberate architectural decisions here.

First, the frontend never communicates directly with Servicing Order. Both the RM Copilot and Entity Portal communicate through the Onboarding API.

Second, Temporal Workers own process execution, not business-data persistence. Workers use Activities to retrieve and save data through the appropriate application services and external APIs.

Third, the SO Kafka Consumer is a separate integration component. It receives external changes and communicates with Temporal; it does not need to be part of the Temporal Worker itself.

Fourth, the Schema Service separates schema distribution from form presentation. The same versioned schema is used by both the frontend and backend, while the frontend can also use additional UI metadata to decide how to render forms.

## 2. Temporal design: one workflow per onboarding request

This is probably the most important decision in the architecture.

I recommend using the Entity Workflow Pattern, where each onboarding request has one long-lived Temporal Workflow.

For example:

```
Workflow Type: OrganizationOnboardingWorkflow

Workflow ID: onboarding-{onboardingCaseId}
```

Suppose the RM creates the following requests:

```
onboarding-10001  -> Company: ABC Pty Ltd
onboarding-10002  -> Trust: XYZ Family Trust
onboarding-10003  -> Government Org: Department ABC
```

Each request has its own isolated workflow execution.

The Workflow handles the lifecycle of that onboarding request, irrespective of its organization type.

Temporal's Entity Workflow Pattern specifically recommends one Workflow per long-lived business entity, using the entity identifier as the Workflow ID. It also recommends keeping workflow state minimal and using Continue-As-New to control growing histories.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://docs.temporal.io\&sz=32)

Temporal Documentation+1



### Why one workflow per request?

An onboarding request has a lifecycle that can last days, weeks or potentially months.

During that lifecycle, it might:

- Receive initial RM information.
- Run several data-enrichment operations.
- Wait for RM approval.
- Be submitted to Servicing Order.
- Wait for the entity to complete its forms.
- Receive several rounds of additional information.
- Wait for bank verification.
- Move through approval or rejection.
- Send notifications at different stages.
- Handle reminders, escalations and timeouts.

These are all parts of one business process.

Temporal is particularly useful here because the Workflow can wait for an external event or a human action without occupying a continuously running application process.

For example:

```
Start workflow
      |
      v
Enrich organization data
      |
      v
Wait for RM approval
      |
      v
Create Servicing Order
      |
      v
Wait for entity submission
      |
      v
Validate entity submission
      |
      v
Wait for bank review
      |
      v
Approved / Rejected / More Information
```

If the entity takes two weeks to complete a form, the Workflow waits durably. You do not need to keep a Next.js session, API server thread or background process alive for those two weeks.

### Should you create child workflows?

Not for every operation.

I would initially use one parent Workflow and ordinary Activities.

For example:

| Operation                      | Recommended Temporal construct |
| ------------------------------ | ------------------------------ |
| Search ABN                     | Activity                       |
| Fetch ASIC/company information | Activity                       |
| Read organization website      | Activity                       |
| Call LLM for data extraction   | Activity                       |
| Generate enrichment summary    | Activity                       |
| Create SO request              | Activity                       |
| Update SO request              | Activity                       |
| Send email notification        | Activity                       |
| Wait for RM approval           | Signal / Update                |
| Wait for entity submission     | Signal / Update                |
| Wait for SO status event       | Signal                         |
| Wait for a deadline            | Durable Workflow Timer         |

Use Child Workflows when the sub-process genuinely has an independent lifecycle, requires separate scaling or isolation, or is sufficiently complex to justify its own workflow history.

Examples where Child Workflows might eventually make sense:

- A separate beneficial ownership verification process.
- An independently managed document verification process.
- A complex KYC/AML assessment.
- A multi-party approval process involving several independent reviewers.

Do not create a child Workflow simply because you want to organize Activities into separate code files. Temporal's own guidance recommends starting with one Workflow when the problem is bounded and using Activities when in doubt.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://docs.temporal.io\&sz=32)

Temporal Documentation



### Proposed Workflow responsibilities

I would organize the Workflow into the following logical stages:

| Stage             | Responsibilities                                                      |
| ----------------- | --------------------------------------------------------------------- |
| Intake            | Initialize the request, capture RM information and organization type  |
| Enrichment        | Fetch, extract, normalize and store external information              |
| RM Review         | Present suggestions, identify missing information and obtain approval |
| SO Registration   | Create the official SO request and record its identifier              |
| Entity Onboarding | Send invitation and await customer data                               |
| Data Validation   | Validate the organization's data against the pinned schema            |
| Bank Review       | Request additional information and coordinate internal checks         |
| Finalization      | Update SO status and trigger completion notifications                 |

These can all be methods or logical functions inside one Workflow initially.

One further consideration: use Temporal Worker Versioning as the application evolves. Your running workflows may span several application releases, so you must not assume that changing the Workflow implementation is automatically safe for existing executions.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://docs.temporal.io\&sz=32)

Temporal Documentation+1



## 3. The biggest data ownership decision: keep drafts in your database or create SO records immediately?

There are two viable architectures.

### Option A: Maintain a separate draft before creating the SO request

My default recommendation

The flow looks like this:

1. RM starts an onboarding request in Copilot.
2. Onboarding API creates a draft in your database.
3. Temporal starts the request's Workflow.
4. Temporal coordinates the initial enrichment operations.
5. Enriched data is saved in your database.
6. RM reviews and approves the enriched information.
7. When RM submits, Temporal calls the SO REST API to create the official request.
8. SO returns an SO Request ID.
9. Your database associates that ID with the original onboarding case.
10. Entity onboarding continues against the registered request.

Diagram:

Servicing OrderEnrichment ServiceTemporalOnboarding DBOnboarding APICopilotServicing OrderEnrichment ServiceTemporalOnboarding DBOnboarding APICopilot#chatgpt-mermaid-\_r_dl\_{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;fill:rgb(13, 13, 13);}@keyframes edge-animation-frame{from{stroke-dashoffset:0;}}@keyframes dash{to{stroke-dashoffset:0;}}#chatgpt-mermaid-\_r_dl\_ .edge-animation-slow{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 50s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-\_r_dl\_ .edge-animation-fast{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 20s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-\_r_dl\_ .error-icon{fill:rgb(243, 243, 243);}#chatgpt-mermaid-\_r_dl\_ .error-text{fill:rgb(13, 13, 13);stroke:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_dl\_ .edge-thickness-normal{stroke-width:1px;}#chatgpt-mermaid-\_r_dl\_ .edge-thickness-thick{stroke-width:3.5px;}#chatgpt-mermaid-\_r_dl\_ .edge-pattern-solid{stroke-dasharray:0;}#chatgpt-mermaid-\_r_dl\_ .edge-thickness-invisible{stroke-width:0;fill:none;}#chatgpt-mermaid-\_r_dl\_ .edge-pattern-dashed{stroke-dasharray:3;}#chatgpt-mermaid-\_r_dl\_ .edge-pattern-dotted{stroke-dasharray:2;}#chatgpt-mermaid-\_r_dl\_ .marker{fill:rgb(143, 143, 143);stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_dl\_ .marker.cross{stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_dl\_ svg{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;}#chatgpt-mermaid-\_r_dl\_ p{margin:0;}#chatgpt-mermaid-\_r_dl\_ .actor{stroke:rgb(83, 154, 248);fill:rgb(222, 234, 251);stroke-width:1;}#chatgpt-mermaid-\_r_dl\_ rect.actor.outer-path[data-look="neo"]{filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_dl\_ rect.note[data-look="neo"]{stroke:rgb(107, 198, 127);fill:rgb(243, 243, 243);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_dl\_ text.actor>tspan{fill:rgb(13, 13, 13);stroke:none;}#chatgpt-mermaid-\_r_dl\_ .actor-line{stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_dl\_ .innerArc{stroke-width:1.5;stroke-dasharray:none;}#chatgpt-mermaid-\_r_dl\_ .messageLine0{stroke-width:1.5;stroke-dasharray:none;stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_dl\_ .messageLine1{stroke-width:1.5;stroke-dasharray:2,2;stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_dl\_ [id$="-arrowhead"] path{fill:rgb(143, 143, 143);stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_dl\_ .sequenceNumber{fill:#707070;}#chatgpt-mermaid-\_r_dl\_ [id$="-sequencenumber"]{fill:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_dl\_ [id$="-crosshead"] path{fill:rgb(143, 143, 143);stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_dl\_ .messageText{fill:rgb(13, 13, 13);stroke:none;}#chatgpt-mermaid-\_r_dl\_ .labelBox{stroke:rgba(0, 0, 0, 0.1);fill:rgb(252, 252, 252);filter:none;}#chatgpt-mermaid-\_r_dl\_ .labelText,#chatgpt-mermaid-\_r_dl\_ .labelText>tspan{fill:rgb(13, 13, 13);stroke:none;}#chatgpt-mermaid-\_r_dl\_ .loopText,#chatgpt-mermaid-\_r_dl\_ .loopText>tspan{fill:rgb(13, 13, 13);stroke:none;}#chatgpt-mermaid-\_r_dl\_ .sectionTitle,#chatgpt-mermaid-\_r_dl\_ .sectionTitle>tspan{fill:rgb(13, 13, 13);stroke:none;}#chatgpt-mermaid-\_r_dl\_ .loopLine{stroke-width:2px;stroke-dasharray:2,2;stroke:rgba(0, 0, 0, 0.1);fill:rgba(0, 0, 0, 0.1);}#chatgpt-mermaid-\_r_dl\_ .note{stroke:rgb(107, 198, 127);fill:rgb(243, 243, 243);}#chatgpt-mermaid-\_r_dl\_ .noteText,#chatgpt-mermaid-\_r_dl\_ .noteText>tspan{fill:rgb(13, 13, 13);stroke:none;font-weight:normal;}#chatgpt-mermaid-\_r_dl\_ .activation0{fill:rgb(243, 243, 243);stroke:hsl(0, 0%, 85.2941176471%);}#chatgpt-mermaid-\_r_dl\_ .activation1{fill:rgb(243, 243, 243);stroke:hsl(0, 0%, 85.2941176471%);}#chatgpt-mermaid-\_r_dl\_ .activation2{fill:rgb(243, 243, 243);stroke:hsl(0, 0%, 85.2941176471%);}#chatgpt-mermaid-\_r_dl\_ .actorPopupMenu{position:absolute;}#chatgpt-mermaid-\_r_dl\_ .actorPopupMenuPanel{position:absolute;fill:rgb(222, 234, 251);box-shadow:0px 8px 16px 0px rgba(0,0,0,0.2);filter:drop-shadow(3px 5px 2px rgb(0 0 0 / 0.4));}#chatgpt-mermaid-\_r_dl\_ .actor-man circle,#chatgpt-mermaid-\_r_dl\_ line{fill:rgb(222, 234, 251);stroke-width:2px;}#chatgpt-mermaid-\_r_dl\_ g rect.rect{filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));stroke:rgb(83, 154, 248);}#chatgpt-mermaid-\_r_dl\_ .node .neo-node{stroke:rgb(83, 154, 248);}#chatgpt-mermaid-\_r_dl\_ [data-look="neo"].node rect,#chatgpt-mermaid-\_r_dl\_ [data-look="neo"].cluster rect,#chatgpt-mermaid-\_r_dl\_ [data-look="neo"].node polygon{stroke:url(#chatgpt-mermaid-\_r_dl\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_dl\_ [data-look="neo"].swimlane.cluster rect{filter:none;}#chatgpt-mermaid-\_r_dl\_ [data-look="neo"].node path{stroke:url(#chatgpt-mermaid-\_r_dl\_-gradient);stroke-width:1px;}#chatgpt-mermaid-\_r_dl\_ [data-look="neo"].node .outer-path{filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_dl\_ [data-look="neo"].node .neo-line path{stroke:rgb(83, 154, 248);filter:none;}#chatgpt-mermaid-\_r_dl\_ [data-look="neo"].node circle{stroke:url(#chatgpt-mermaid-\_r_dl\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_dl\_ [data-look="neo"].node circle .state-start{fill:#000000;}#chatgpt-mermaid-\_r_dl\_ [data-look="neo"].icon-shape .icon{fill:url(#chatgpt-mermaid-\_r_dl\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_dl\_ [data-look="neo"].icon-shape .icon-neo path{stroke:url(#chatgpt-mermaid-\_r_dl\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_dl\_ :root{--mermaid-font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";}Relationship ManagerEnter organization details1Create onboarding draft2Save draft and outbox event3Start workflow4Enrich organization5Save enriched data and evidence6Enrichment complete / awaiting review7Review and approve8Submit onboarding request9Persist submission command10Signal submission11Load approved request revision12POST create request13SO Request ID14Save SO ID and registration result15Official request created16Relationship Manager

Advantages:

- SO only receives requests that are ready for official registration.
- You can enrich and revise data without generating multiple SO updates.
- You control the RM experience independently of the SO API.
- You can perform validation and completeness checks before registration.
- You avoid coupling every Copilot interaction to SO API availability.
- You can build a proper enrichment and data-provenance model.

Disadvantages:

- You introduce an additional application database.
- There are now two lifecycle phases: draft and officially registered.
- You must reliably transition a draft into an SO request.
- You need reconciliation between your application and SO.

I consider these disadvantages manageable.

### Option B: Create the SO request immediately in Draft status

The alternative is:

1. RM starts an onboarding request.
2. Your API immediately creates a Draft SO record.
3. SO returns an identifier.
4. Temporal starts using the SO identifier.
5. Every subsequent enrichment or customer update is synchronized to SO.
6. SO manages the request throughout the entire lifecycle.

Diagram:

Enrichment ServiceApplication Read ModelTemporalServicing OrderOnboarding APICopilotEnrichment ServiceApplication Read ModelTemporalServicing OrderOnboarding APICopilot#chatgpt-mermaid-\_r_ds\_{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;fill:rgb(13, 13, 13);}@keyframes edge-animation-frame{from{stroke-dashoffset:0;}}@keyframes dash{to{stroke-dashoffset:0;}}#chatgpt-mermaid-\_r_ds\_ .edge-animation-slow{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 50s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-\_r_ds\_ .edge-animation-fast{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 20s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-\_r_ds\_ .error-icon{fill:rgb(243, 243, 243);}#chatgpt-mermaid-\_r_ds\_ .error-text{fill:rgb(13, 13, 13);stroke:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_ds\_ .edge-thickness-normal{stroke-width:1px;}#chatgpt-mermaid-\_r_ds\_ .edge-thickness-thick{stroke-width:3.5px;}#chatgpt-mermaid-\_r_ds\_ .edge-pattern-solid{stroke-dasharray:0;}#chatgpt-mermaid-\_r_ds\_ .edge-thickness-invisible{stroke-width:0;fill:none;}#chatgpt-mermaid-\_r_ds\_ .edge-pattern-dashed{stroke-dasharray:3;}#chatgpt-mermaid-\_r_ds\_ .edge-pattern-dotted{stroke-dasharray:2;}#chatgpt-mermaid-\_r_ds\_ .marker{fill:rgb(143, 143, 143);stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_ds\_ .marker.cross{stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_ds\_ svg{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;}#chatgpt-mermaid-\_r_ds\_ p{margin:0;}#chatgpt-mermaid-\_r_ds\_ .actor{stroke:rgb(83, 154, 248);fill:rgb(222, 234, 251);stroke-width:1;}#chatgpt-mermaid-\_r_ds\_ rect.actor.outer-path[data-look="neo"]{filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_ds\_ rect.note[data-look="neo"]{stroke:rgb(107, 198, 127);fill:rgb(243, 243, 243);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_ds\_ text.actor>tspan{fill:rgb(13, 13, 13);stroke:none;}#chatgpt-mermaid-\_r_ds\_ .actor-line{stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_ds\_ .innerArc{stroke-width:1.5;stroke-dasharray:none;}#chatgpt-mermaid-\_r_ds\_ .messageLine0{stroke-width:1.5;stroke-dasharray:none;stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_ds\_ .messageLine1{stroke-width:1.5;stroke-dasharray:2,2;stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_ds\_ [id$="-arrowhead"] path{fill:rgb(143, 143, 143);stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_ds\_ .sequenceNumber{fill:#707070;}#chatgpt-mermaid-\_r_ds\_ [id$="-sequencenumber"]{fill:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_ds\_ [id$="-crosshead"] path{fill:rgb(143, 143, 143);stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_ds\_ .messageText{fill:rgb(13, 13, 13);stroke:none;}#chatgpt-mermaid-\_r_ds\_ .labelBox{stroke:rgba(0, 0, 0, 0.1);fill:rgb(252, 252, 252);filter:none;}#chatgpt-mermaid-\_r_ds\_ .labelText,#chatgpt-mermaid-\_r_ds\_ .labelText>tspan{fill:rgb(13, 13, 13);stroke:none;}#chatgpt-mermaid-\_r_ds\_ .loopText,#chatgpt-mermaid-\_r_ds\_ .loopText>tspan{fill:rgb(13, 13, 13);stroke:none;}#chatgpt-mermaid-\_r_ds\_ .sectionTitle,#chatgpt-mermaid-\_r_ds\_ .sectionTitle>tspan{fill:rgb(13, 13, 13);stroke:none;}#chatgpt-mermaid-\_r_ds\_ .loopLine{stroke-width:2px;stroke-dasharray:2,2;stroke:rgba(0, 0, 0, 0.1);fill:rgba(0, 0, 0, 0.1);}#chatgpt-mermaid-\_r_ds\_ .note{stroke:rgb(107, 198, 127);fill:rgb(243, 243, 243);}#chatgpt-mermaid-\_r_ds\_ .noteText,#chatgpt-mermaid-\_r_ds\_ .noteText>tspan{fill:rgb(13, 13, 13);stroke:none;font-weight:normal;}#chatgpt-mermaid-\_r_ds\_ .activation0{fill:rgb(243, 243, 243);stroke:hsl(0, 0%, 85.2941176471%);}#chatgpt-mermaid-\_r_ds\_ .activation1{fill:rgb(243, 243, 243);stroke:hsl(0, 0%, 85.2941176471%);}#chatgpt-mermaid-\_r_ds\_ .activation2{fill:rgb(243, 243, 243);stroke:hsl(0, 0%, 85.2941176471%);}#chatgpt-mermaid-\_r_ds\_ .actorPopupMenu{position:absolute;}#chatgpt-mermaid-\_r_ds\_ .actorPopupMenuPanel{position:absolute;fill:rgb(222, 234, 251);box-shadow:0px 8px 16px 0px rgba(0,0,0,0.2);filter:drop-shadow(3px 5px 2px rgb(0 0 0 / 0.4));}#chatgpt-mermaid-\_r_ds\_ .actor-man circle,#chatgpt-mermaid-\_r_ds\_ line{fill:rgb(222, 234, 251);stroke-width:2px;}#chatgpt-mermaid-\_r_ds\_ g rect.rect{filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));stroke:rgb(83, 154, 248);}#chatgpt-mermaid-\_r_ds\_ .node .neo-node{stroke:rgb(83, 154, 248);}#chatgpt-mermaid-\_r_ds\_ [data-look="neo"].node rect,#chatgpt-mermaid-\_r_ds\_ [data-look="neo"].cluster rect,#chatgpt-mermaid-\_r_ds\_ [data-look="neo"].node polygon{stroke:url(#chatgpt-mermaid-\_r_ds\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_ds\_ [data-look="neo"].swimlane.cluster rect{filter:none;}#chatgpt-mermaid-\_r_ds\_ [data-look="neo"].node path{stroke:url(#chatgpt-mermaid-\_r_ds\_-gradient);stroke-width:1px;}#chatgpt-mermaid-\_r_ds\_ [data-look="neo"].node .outer-path{filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_ds\_ [data-look="neo"].node .neo-line path{stroke:rgb(83, 154, 248);filter:none;}#chatgpt-mermaid-\_r_ds\_ [data-look="neo"].node circle{stroke:url(#chatgpt-mermaid-\_r_ds\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_ds\_ [data-look="neo"].node circle .state-start{fill:#000000;}#chatgpt-mermaid-\_r_ds\_ [data-look="neo"].icon-shape .icon{fill:url(#chatgpt-mermaid-\_r_ds\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_ds\_ [data-look="neo"].icon-shape .icon-neo path{stroke:url(#chatgpt-mermaid-\_r_ds\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_ds\_ :root{--mermaid-font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";}Relationship ManagerStart onboarding1Create request2POST Draft SO request3SO Request ID4Store SO ID and projection5Start workflow6Enrich organization7Enriched attributes8PATCH Draft SO request9Updated request10Review and submit11Submit request12Update SO status13Submission accepted14Relationship Manager

Advantages:

- One official request exists from the beginning.
- SO is the authoritative request store throughout the entire journey.
- There is less duplication of request data.
- SO's audit and status history covers the entire lifecycle.
- You avoid a separate pre-registration data lifecycle.

Disadvantages:

- Your SO API must support incomplete or draft requests.
- The SO system will receive frequent modifications.
- You become more dependent on the third-party SO API's availability.
- You need to handle many more integrations and synchronization operations.
- The SO system may not be designed to support conversational, rapidly changing draft information.

### My recommendation

I would use the following decision rule:

| SO capability                                                                      | Recommendation                                                     |
| ---------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| Supports proper Draft/Incomplete status, partial updates and draft access controls | Option B                                                           |
| Only supports official submission/registration                                     | Option A                                                           |
| Draft state exists but customer data cannot be safely updated until submission     | Option A, with an application-side staging area                    |
| SO cannot reliably support high-frequency updates or autosave                      | Option A, or batch synchronization using explicit save checkpoints |

The question to resolve with your SO vendor is:

Can Servicing Order create a Draft request that accepts incomplete organization-specific data, customer updates, enrichment updates and subsequent status transitions without treating every update as a formal submission?

The answer has a significant impact on the architecture.

## 4. Should Copilot call the SO API directly, or should you have your own API?

My recommendation is unambiguous:



Recommended

&#x20;Always go through your own Onboarding API.



Do not allow the Copilot, the LLM, or the Next.js frontend to call the third-party SO API directly.

The interaction should be:

```
RM Copilot
    |
    v
Onboarding API
    |
    +-- Authentication / Authorization
    |
    +-- Business validation
    |
    +-- JSON Schema validation
    |
    +-- Idempotency and duplicate detection
    |
    +-- Audit recording
    |
    v
Temporal
    |
    v
SO Integration Adapter
    |
    v
Servicing Order REST API
```

### Why this is important

1\. Avoid coupling the application to a third-party API.

Your Copilot should understand your business domain, not the implementation details of Servicing Order.

For example, your internal command might be:

```
{
  "command": "SubmitOnboardingRequest",
  "onboardingCaseId": "10001"
}
```

Your SO Adapter translates this into whatever request structure the vendor requires.

If the SO API changes, you only need to change the adapter, not the Copilot and frontend applications.

2\. Centralize authorization.

You must verify that the RM is authorized to:

- Create the onboarding request.
- Modify the organization.
- Submit the request.
- Change its status.
- Access the customer's information.

The LLM should never decide whether an RM has permission to perform a business operation.

3\. Maintain a consistent audit trail.

The Onboarding API can record:

- Who initiated the request.
- Who changed a particular field.
- Whether the change originated from an RM, entity, external source or AI.
- Which data was submitted to SO.
- Which schema version validated the data.
- Whether the operation succeeded or failed.

4\. Implement reliable integrations.

Your API and integration layer can manage timeouts, retries, rate limits, idempotency, circuit breakers, reconciliation and API version changes.

5\. Protect credentials and sensitive information.

Only backend services should have the necessary SO API credentials. The browser and LLM should never receive these credentials.

### A particularly important distinction concerning AI

I would not give the AI Agent unrestricted access to your integration layer.

Instead, expose a controlled set of business tools:

```
searchOrganization()
enrichOrganization()
getEnrichmentResults()
updateDraft()
requestRMApproval()
submitOnboardingRequest()
getOnboardingStatus()
```

Each tool calls a controlled backend API.

The LLM can recommend that a request be submitted, but actual submission must be an explicit, authorized business command.

I would also require RM confirmation before committing AI-generated information that has material consequences for onboarding.

## 5. Should transient entity data be in Temporal, SO or both?

This is another important distinction.

My recommendation:

Store application data in the database. Store process state in Temporal. Store official servicing data and status in SO.

Do not store the full entity form JSON inside the Workflow.

Consider an entity completing a 100-field company onboarding form.

The entity might:

1. Open the form.
2. Enter 20 fields.
3. Save.
4. Return the following day.
5. Complete another 30 fields.
6. Upload several documents.
7. Correct previously entered information.
8. Submit.

These are application data operations, not necessarily workflow transitions.

### Recommended entity submission architecture

Servicing OrderTemporalValidation ServiceOnboarding DBOnboarding APINext.js PortalServicing OrderTemporalValidation ServiceOnboarding DBOnboarding APINext.js Portal#chatgpt-mermaid-\_r_er\_{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;fill:rgb(13, 13, 13);}@keyframes edge-animation-frame{from{stroke-dashoffset:0;}}@keyframes dash{to{stroke-dashoffset:0;}}#chatgpt-mermaid-\_r_er\_ .edge-animation-slow{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 50s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-\_r_er\_ .edge-animation-fast{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 20s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-\_r_er\_ .error-icon{fill:rgb(243, 243, 243);}#chatgpt-mermaid-\_r_er\_ .error-text{fill:rgb(13, 13, 13);stroke:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_er\_ .edge-thickness-normal{stroke-width:1px;}#chatgpt-mermaid-\_r_er\_ .edge-thickness-thick{stroke-width:3.5px;}#chatgpt-mermaid-\_r_er\_ .edge-pattern-solid{stroke-dasharray:0;}#chatgpt-mermaid-\_r_er\_ .edge-thickness-invisible{stroke-width:0;fill:none;}#chatgpt-mermaid-\_r_er\_ .edge-pattern-dashed{stroke-dasharray:3;}#chatgpt-mermaid-\_r_er\_ .edge-pattern-dotted{stroke-dasharray:2;}#chatgpt-mermaid-\_r_er\_ .marker{fill:rgb(143, 143, 143);stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_er\_ .marker.cross{stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_er\_ svg{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;}#chatgpt-mermaid-\_r_er\_ p{margin:0;}#chatgpt-mermaid-\_r_er\_ .actor{stroke:rgb(83, 154, 248);fill:rgb(222, 234, 251);stroke-width:1;}#chatgpt-mermaid-\_r_er\_ rect.actor.outer-path[data-look="neo"]{filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_er\_ rect.note[data-look="neo"]{stroke:rgb(107, 198, 127);fill:rgb(243, 243, 243);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_er\_ text.actor>tspan{fill:rgb(13, 13, 13);stroke:none;}#chatgpt-mermaid-\_r_er\_ .actor-line{stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_er\_ .innerArc{stroke-width:1.5;stroke-dasharray:none;}#chatgpt-mermaid-\_r_er\_ .messageLine0{stroke-width:1.5;stroke-dasharray:none;stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_er\_ .messageLine1{stroke-width:1.5;stroke-dasharray:2,2;stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_er\_ [id$="-arrowhead"] path{fill:rgb(143, 143, 143);stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_er\_ .sequenceNumber{fill:#707070;}#chatgpt-mermaid-\_r_er\_ [id$="-sequencenumber"]{fill:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_er\_ [id$="-crosshead"] path{fill:rgb(143, 143, 143);stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_er\_ .messageText{fill:rgb(13, 13, 13);stroke:none;}#chatgpt-mermaid-\_r_er\_ .labelBox{stroke:rgba(0, 0, 0, 0.1);fill:rgb(252, 252, 252);filter:none;}#chatgpt-mermaid-\_r_er\_ .labelText,#chatgpt-mermaid-\_r_er\_ .labelText>tspan{fill:rgb(13, 13, 13);stroke:none;}#chatgpt-mermaid-\_r_er\_ .loopText,#chatgpt-mermaid-\_r_er\_ .loopText>tspan{fill:rgb(13, 13, 13);stroke:none;}#chatgpt-mermaid-\_r_er\_ .sectionTitle,#chatgpt-mermaid-\_r_er\_ .sectionTitle>tspan{fill:rgb(13, 13, 13);stroke:none;}#chatgpt-mermaid-\_r_er\_ .loopLine{stroke-width:2px;stroke-dasharray:2,2;stroke:rgba(0, 0, 0, 0.1);fill:rgba(0, 0, 0, 0.1);}#chatgpt-mermaid-\_r_er\_ .note{stroke:rgb(107, 198, 127);fill:rgb(243, 243, 243);}#chatgpt-mermaid-\_r_er\_ .noteText,#chatgpt-mermaid-\_r_er\_ .noteText>tspan{fill:rgb(13, 13, 13);stroke:none;font-weight:normal;}#chatgpt-mermaid-\_r_er\_ .activation0{fill:rgb(243, 243, 243);stroke:hsl(0, 0%, 85.2941176471%);}#chatgpt-mermaid-\_r_er\_ .activation1{fill:rgb(243, 243, 243);stroke:hsl(0, 0%, 85.2941176471%);}#chatgpt-mermaid-\_r_er\_ .activation2{fill:rgb(243, 243, 243);stroke:hsl(0, 0%, 85.2941176471%);}#chatgpt-mermaid-\_r_er\_ .actorPopupMenu{position:absolute;}#chatgpt-mermaid-\_r_er\_ .actorPopupMenuPanel{position:absolute;fill:rgb(222, 234, 251);box-shadow:0px 8px 16px 0px rgba(0,0,0,0.2);filter:drop-shadow(3px 5px 2px rgb(0 0 0 / 0.4));}#chatgpt-mermaid-\_r_er\_ .actor-man circle,#chatgpt-mermaid-\_r_er\_ line{fill:rgb(222, 234, 251);stroke-width:2px;}#chatgpt-mermaid-\_r_er\_ g rect.rect{filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));stroke:rgb(83, 154, 248);}#chatgpt-mermaid-\_r_er\_ .node .neo-node{stroke:rgb(83, 154, 248);}#chatgpt-mermaid-\_r_er\_ [data-look="neo"].node rect,#chatgpt-mermaid-\_r_er\_ [data-look="neo"].cluster rect,#chatgpt-mermaid-\_r_er\_ [data-look="neo"].node polygon{stroke:url(#chatgpt-mermaid-\_r_er\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_er\_ [data-look="neo"].swimlane.cluster rect{filter:none;}#chatgpt-mermaid-\_r_er\_ [data-look="neo"].node path{stroke:url(#chatgpt-mermaid-\_r_er\_-gradient);stroke-width:1px;}#chatgpt-mermaid-\_r_er\_ [data-look="neo"].node .outer-path{filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_er\_ [data-look="neo"].node .neo-line path{stroke:rgb(83, 154, 248);filter:none;}#chatgpt-mermaid-\_r_er\_ [data-look="neo"].node circle{stroke:url(#chatgpt-mermaid-\_r_er\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_er\_ [data-look="neo"].node circle .state-start{fill:#000000;}#chatgpt-mermaid-\_r_er\_ [data-look="neo"].icon-shape .icon{fill:url(#chatgpt-mermaid-\_r_er\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_er\_ [data-look="neo"].icon-shape .icon-neo path{stroke:url(#chatgpt-mermaid-\_r_er\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_er\_ :root{--mermaid-font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";}Logical milestone / submission commandOrganization RepresentativeEnter organization information1Save form section2Validate against pinned schema3Validation result4Save revision and audit record5Saved6Save successful7Submit completed section8Submit section and revision ID9Persist submission command10Signal section submitted11Load submitted revision12PATCH official request13Update accepted14Record synchronization result15Update synchronization status16Organization Representative

There are three distinct operations here:

A. Save form data

The Onboarding API saves the customer's data in your database.

This supports autosave, draft recovery, revision history and interrupted sessions.

B. Submit a logical section

The customer explicitly submits a completed section. This creates a meaningful business event.

The API checks completeness and permissions and then notifies the appropriate Workflow.

C. Synchronize with SO

Temporal coordinates the SO update through an Activity.

The important thing is that Temporal receives a reference to the submitted revision, not the entire JSON form.

For example:

```
{
  "onboardingCaseId": "10001",
  "revisionId": "revision-0042",
  "section": "organization-details",
  "schemaId": "company-schema",
  "schemaVersion": "3.2"
}
```

The Activity loads the appropriate revision from your database and updates SO.

### Should the data be written to both systems?

There is an important qualification.

I recommend that the application database retain its own durable working data and a read model of the SO request, but you must establish one authoritative owner for each piece of data at each lifecycle stage.

For example:

| Data                     | Before SO registration | After SO registration                                      |
| ------------------------ | ---------------------- | ---------------------------------------------------------- |
| Organization details     | Application DB         | SO is authoritative                                        |
| RM working notes         | Application DB         | Application DB                                             |
| Enrichment evidence      | Application DB         | Application DB                                             |
| Entity form draft        | Application DB         | Application DB for pending changes; accepted data is in SO |
| Official request status  | Not yet applicable     | SO                                                         |
| Workflow stage           | Temporal               | Temporal                                                   |
| SO synchronization state | Not yet applicable     | Application integration state                              |

The application database may maintain a projection of SO data for fast reads and frontend experiences.

However, do not independently modify the projection and pretend it is the official SO record.

I would use an explicit synchronization state:

```
PENDING_SYNC
     |
     v
SYNC_IN_PROGRESS
     |
     +-----> SYNCED
     |
     +-----> SYNC_FAILED
                    |
                    v
              RETRY / RECONCILE
```

This is particularly important when the SO API is unavailable.

The customer may have successfully saved a form revision in your application, but that does not necessarily mean the official Servicing Order has received it.

The frontend should distinguish between:

- Saved in the onboarding application.
- Submitted for synchronization.
- Accepted by Servicing Order.

### Do not invoke Temporal for every keystroke

This is worth emphasizing.

I would not send a Temporal Signal or schedule an Activity for every field change.

Instead:

- Save draft data through the Onboarding API.
- Persist revisions in the database.
- Validate field changes and form sections through the API.
- Trigger Temporal at meaningful milestones.
- Use a revision identifier to synchronize a stable snapshot.

This prevents workflow history from growing unnecessarily and reduces the number of calls to SO.

## 6. How I would implement Servicing Order Kafka integration

The SO Kafka integration is a particularly important part of this architecture.

My recommendation is:

Kafka Consumer → Inbox/Outbox → Temporal Signal → Onboarding Workflow.

I would not have the Workflow itself directly consume Kafka.

The Kafka Consumer and Temporal Worker have different responsibilities.

- Kafka Consumer: message ingestion, acknowledgement, deduplication and event routing.
- Temporal Worker: business process decisions and orchestration.

### Proposed architecture

\#chatgpt-mermaid-\_r_fd\_{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;fill:rgb(13, 13, 13);}@keyframes edge-animation-frame{from{stroke-dashoffset:0;}}@keyframes dash{to{stroke-dashoffset:0;}}#chatgpt-mermaid-\_r_fd\_ .edge-animation-slow{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 50s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-\_r_fd\_ .edge-animation-fast{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 20s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-\_r_fd\_ .error-icon{fill:rgb(243, 243, 243);}#chatgpt-mermaid-\_r_fd\_ .error-text{fill:rgb(13, 13, 13);stroke:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_fd\_ .edge-thickness-normal{stroke-width:1px;}#chatgpt-mermaid-\_r_fd\_ .edge-thickness-thick{stroke-width:3.5px;}#chatgpt-mermaid-\_r_fd\_ .edge-pattern-solid{stroke-dasharray:0;}#chatgpt-mermaid-\_r_fd\_ .edge-thickness-invisible{stroke-width:0;fill:none;}#chatgpt-mermaid-\_r_fd\_ .edge-pattern-dashed{stroke-dasharray:3;}#chatgpt-mermaid-\_r_fd\_ .edge-pattern-dotted{stroke-dasharray:2;}#chatgpt-mermaid-\_r_fd\_ .marker{fill:rgb(143, 143, 143);stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_fd\_ .marker.cross{stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_fd\_ svg{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;}#chatgpt-mermaid-\_r_fd\_ p{margin:0;}#chatgpt-mermaid-\_r_fd\_ .label{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";color:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_fd\_ .cluster-label text{fill:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_fd\_ .cluster-label span{color:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_fd\_ .cluster-label span p{background-color:transparent;}#chatgpt-mermaid-\_r_fd\_ .label text,#chatgpt-mermaid-\_r_fd\_ span{fill:rgb(13, 13, 13);color:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_fd\_ .node rect,#chatgpt-mermaid-\_r_fd\_ .node circle,#chatgpt-mermaid-\_r_fd\_ .node ellipse,#chatgpt-mermaid-\_r_fd\_ .node polygon,#chatgpt-mermaid-\_r_fd\_ .node path{fill:rgb(222, 234, 251);stroke:rgb(83, 154, 248);stroke-width:1px;}#chatgpt-mermaid-\_r_fd\_ .rough-node .label text,#chatgpt-mermaid-\_r_fd\_ .node .label text,#chatgpt-mermaid-\_r_fd\_ .image-shape .label,#chatgpt-mermaid-\_r_fd\_ .icon-shape .label{text-anchor:middle;}#chatgpt-mermaid-\_r_fd\_ .node .katex path{fill:#000;stroke:#000;stroke-width:1px;}#chatgpt-mermaid-\_r_fd\_ .rough-node .label,#chatgpt-mermaid-\_r_fd\_ .node .label,#chatgpt-mermaid-\_r_fd\_ .image-shape .label,#chatgpt-mermaid-\_r_fd\_ .icon-shape .label{text-align:center;}#chatgpt-mermaid-\_r_fd\_ .node.clickable{cursor:pointer;}#chatgpt-mermaid-\_r_fd\_ .root .anchor path{fill:rgb(143, 143, 143)!important;stroke-width:0;stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_fd\_ .arrowheadPath{fill:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_fd\_ .edgePath .path{stroke:rgb(143, 143, 143);stroke-width:1px;}#chatgpt-mermaid-\_r_fd\_ .flowchart-link{stroke:rgb(143, 143, 143);fill:none;}#chatgpt-mermaid-\_r_fd\_ .edgeLabel{background-color:rgb(252, 252, 252);text-align:center;}#chatgpt-mermaid-\_r_fd\_ .edgeLabel p{background-color:rgb(252, 252, 252);}#chatgpt-mermaid-\_r_fd\_ .edgeLabel rect{opacity:0.5;background-color:rgb(252, 252, 252);fill:rgb(252, 252, 252);}#chatgpt-mermaid-\_r_fd\_ .labelBkg{background-color:rgba(252, 252, 252, 0.5);}#chatgpt-mermaid-\_r_fd\_ .cluster rect{fill:rgb(243, 243, 243);stroke:rgba(0, 0, 0, 0.1);stroke-width:1px;}#chatgpt-mermaid-\_r_fd\_ .cluster text{fill:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_fd\_ .cluster span{color:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_fd\_ div.mermaidTooltip{position:absolute;text-align:center;max-width:200px;padding:2px;font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:12px;background:rgb(243, 243, 243);border:1px solid rgba(0, 0, 0, 0.1);border-radius:2px;pointer-events:none;z-index:100;}#chatgpt-mermaid-\_r_fd\_ .flowchartTitleText{text-anchor:middle;font-size:18px;fill:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_fd\_ rect.text{fill:none;stroke-width:0;}#chatgpt-mermaid-\_r_fd\_ .icon-shape,#chatgpt-mermaid-\_r_fd\_ .image-shape{background-color:rgb(252, 252, 252);text-align:center;}#chatgpt-mermaid-\_r_fd\_ .icon-shape p,#chatgpt-mermaid-\_r_fd\_ .image-shape p{background-color:rgb(252, 252, 252);padding:2px;}#chatgpt-mermaid-\_r_fd\_ .icon-shape .label rect,#chatgpt-mermaid-\_r_fd\_ .image-shape .label rect{opacity:0.5;background-color:rgb(252, 252, 252);fill:rgb(252, 252, 252);}#chatgpt-mermaid-\_r_fd\_ .label-icon{display:inline-block;height:1em;overflow:visible;vertical-align:-0.125em;}#chatgpt-mermaid-\_r_fd\_ .node .label-icon path{fill:currentColor;stroke:revert;stroke-width:revert;}#chatgpt-mermaid-\_r_fd\_ .node .neo-node{stroke:rgb(83, 154, 248);}#chatgpt-mermaid-\_r_fd\_ [data-look="neo"].node rect,#chatgpt-mermaid-\_r_fd\_ [data-look="neo"].cluster rect,#chatgpt-mermaid-\_r_fd\_ [data-look="neo"].node polygon{stroke:url(#chatgpt-mermaid-\_r_fd\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_fd\_ [data-look="neo"].swimlane.cluster rect{filter:none;}#chatgpt-mermaid-\_r_fd\_ [data-look="neo"].node path{stroke:url(#chatgpt-mermaid-\_r_fd\_-gradient);stroke-width:1px;}#chatgpt-mermaid-\_r_fd\_ [data-look="neo"].node .outer-path{filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_fd\_ [data-look="neo"].node .neo-line path{stroke:rgb(83, 154, 248);filter:none;}#chatgpt-mermaid-\_r_fd\_ [data-look="neo"].node circle{stroke:url(#chatgpt-mermaid-\_r_fd\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_fd\_ [data-look="neo"].node circle .state-start{fill:#000000;}#chatgpt-mermaid-\_r_fd\_ [data-look="neo"].icon-shape .icon{fill:url(#chatgpt-mermaid-\_r_fd\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_fd\_ [data-look="neo"].icon-shape .icon-neo path{stroke:url(#chatgpt-mermaid-\_r_fd\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_fd\_ .node text{font-size:14px;font-weight:600;letter-spacing:normal;fill:rgb(0, 79, 153);}#chatgpt-mermaid-\_r_fd\_ .edgeLabels text{font-size:13px;font-weight:600;letter-spacing:-0.08px;fill:rgb(0, 79, 153);}#chatgpt-mermaid-\_r_fd\_ .node tspan[font-weight="normal"],#chatgpt-mermaid-\_r_fd\_ .edgeLabels tspan[font-weight="normal"]{font-weight:600;}#chatgpt-mermaid-\_r_fd\_ .edgeLabel .label rect{opacity:1;rx:13px;ry:13px;fill:rgb(245, 250, 255);stroke:rgb(206, 219, 229);stroke-width:1px;}#chatgpt-mermaid-\_r_fd\_ .node rect,#chatgpt-mermaid-\_r_fd\_ .node circle,#chatgpt-mermaid-\_r_fd\_ .node ellipse,#chatgpt-mermaid-\_r_fd\_ .node polygon,#chatgpt-mermaid-\_r_fd\_ .node path{fill:rgb(229, 243, 255);stroke:rgba(0, 0, 0, 0.1);stroke-width:1px;}#chatgpt-mermaid-\_r_fd\_ .node rect{rx:16px;ry:16px;}#chatgpt-mermaid-\_r_fd\_ .mermaid-decision .label-container{fill:rgb(245, 250, 255);stroke:rgb(206, 219, 229);stroke-dasharray:2,2;}#chatgpt-mermaid-\_r_fd\_ .edgePaths .flowchart-link{stroke:rgb(143, 143, 143);stroke-width:1px;stroke-linecap:round;stroke-linejoin:round;}#chatgpt-mermaid-\_r_fd\_ .marker{fill:rgb(143, 143, 143);stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_fd\_ :root{--mermaid-font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";}Servicing OrderSO Kafka TopicKafka ConsumerEvent InboxSignal OutboxSO Read Model / ProjectionSignal DispatcherTemporal WorkflowSO Reconciliation Activity

### Example event processing

Suppose the entity completes their form and the SO system changes the status to:

```
ENTITY_SUBMITTED
```

The SO publishes:

```
{
  "eventId": "evt-12345",
  "eventType": "ServicingOrderUpdated",
  "eventVersion": "1.0",
  "servicingOrderId": "SO-98765",
  "onboardingCaseId": "10001",
  "aggregateVersion": 17,
  "status": "ENTITY_SUBMITTED",
  "occurredAt": "2026-11-04T10:15:00Z"
}
```

This is an illustrative event contract, not an assumption about the SO vendor's actual event payload.

The Kafka Consumer:

1. Reads the event.
2. Validates its event envelope.
3. Checks whether the `eventId` has already been processed.
4. Records the event in the inbox.
5. Updates the local SO projection if its aggregate version is newer.
6. Creates a signal-dispatch record.
7. Dispatches a signal to the appropriate onboarding Workflow.

The Workflow receives something like:

```
{
  "eventId": "evt-12345",
  "eventType": "ServicingOrderUpdated",
  "servicingOrderId": "SO-98765",
  "aggregateVersion": 17
}
```

The Workflow can then decide what to do.

For example:

```
SO status = ENTITY_SUBMITTED
            |
            v
Fetch latest SO request
            |
            v
Validate entity submission
            |
            v
Initiate bank review
            |
            v
Notify RM
            |
            v
Update onboarding stage
```

### Important: do not blindly trust event ordering

You must account for:

- Duplicate Kafka events.
- Events arriving out of order.
- Consumer restarts.
- Workflow signal retries.
- Temporal Worker restarts.
- SO events arriving before the API call that created the SO record has completed locally.

Use the following safeguards:

| Problem                             | Recommendation                               |
| ----------------------------------- | -------------------------------------------- |
| Duplicate events                    | Unique `eventId` and inbox deduplication     |
| Out-of-order events                 | `aggregateVersion` and stale-event rejection |
| Lost signal after inbox persistence | Transactional outbox and signal dispatcher   |
| Lost consumer availability          | Durable Kafka offsets and replay             |
| Event for unknown request           | Persist as unmatched and reconcile           |
| Duplicate Workflow signal           | Custom event ID deduplication                |
| Missing or inconsistent SO state    | Fetch authoritative state through SO API     |

Temporal Signals are asynchronous and do not return an application-level result to the sender. Use Updates where you need synchronous Workflow-side validation and a returned result.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://docs.temporal.io\&sz=32)

Temporal Documentation+1



The transactional outbox is especially important because a database commit and a Temporal Signal are not one atomic transaction. Do not assume that a successful database insert guarantees the signal was delivered.

### A critical correlation question

When your application creates an SO record, SO may publish its Kafka event before your create-request Activity has received and stored the SO ID.

You need a correlation strategy.

I would ask the SO vendor whether the create API supports an external reference such as:

```
{
  "externalReference": "10001",
  "correlationId": "onboarding-10001"
}
```

If the Kafka event includes that reference, you can associate it with the internal case immediately.

If it does not, you need a durable unmatched-event mechanism and subsequent reconciliation.

This is one of the most important third-party integration details to resolve before implementation.

### Another recommendation: distinguish commands from events

This is a simple but important architecture rule.

| Message            | Meaning | Direction                     |
| ------------------ | ------- | ----------------------------- |
| Create SO Request  | Command | Bank → SO                     |
| Update SO Request  | Command | Bank → SO                     |
| Change SO Status   | Command | Bank → SO                     |
| SO Request Created | Event   | SO → Bank                     |
| SO Request Updated | Event   | SO → Bank                     |
| Entity Submitted   | Event   | SO → Bank, if SO publishes it |

The bank sends commands using REST APIs.

The bank receives notifications of facts that have occurred through Kafka.

Avoid writing business logic that reacts to an SO update by issuing the same SO update again. This can create event feedback loops.

## 7. Organization-specific JSON Schema design

You have another important architectural concern: how to make the same organization-specific schema work consistently across:

- RM Copilot.
- Next.js entity forms.
- Onboarding API.
- Backend validation.
- SO REST API.
- SO Schema Registry.

I recommend establishing Servicing Order's Schema Registry as the canonical publication point, assuming the vendor allows schemas to be retrieved and versioned reliably.

Your Onboarding Application should have a Schema Service that retrieves and caches the schemas.

### Proposed design

```
                  SO Schema Registry
                          |
                          v
                    Schema Service
                          |
                 Versioned Schema Cache
                          |
             +------------+------------+
             |                         |
             v                         v
      Next.js Frontend          Onboarding API
             |                         |
      Client validation          Server validation
             |                         |
             +------------+------------+
                          |
                          v
                   Temporal Workflow
                          |
                          v
                    SO REST API
                          |
                   SO Validation
```

### A. Schema versioning

Suppose you have:

```
Company Schema       v3.2
Trust Schema         v2.1
Government Schema    v1.4
Partnership Schema   v1.0
```

When an onboarding case starts, pin its schema:

```
{
  "onboardingCaseId": "10001",
  "orgType": "COMPANY",
  "schemaId": "company-schema",
  "schemaVersion": "3.2",
  "schemaDialect": "2020-12"
}
```

This is very important.

Imagine that a Company Schema changes from v3.2 to v3.3 while an entity is halfway through onboarding.

You do not necessarily want an already-started onboarding request to suddenly acquire new mandatory fields.

My recommendation:

- Every case has a pinned schema version.
- Every form revision references that version.
- The frontend validates against that version.
- The backend validates against that version.
- SO receives the same version or an equivalent supported schema reference.
- A schema upgrade for an existing case requires an explicit migration decision.

Also establish what happens when a new schema version is published: existing cases should generally remain on their pinned version unless migration is required by policy.

The current JSON Schema specification is Draft 2020-12, but you must first verify that SO's registry and both validation implementations support the same dialect.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://json-schema.org\&sz=32)

Specification [#section]+1



### B. Avoid putting everything into JSON Schema

I would separate the data contract from the form presentation.

For example:

```
schemas/
    common/
        organization.json
        address.json
        contact.json
        identification.json

    company/
        company-data.schema.json
        company-ui.schema.json

    trust/
        trust-data.schema.json
        trust-ui.schema.json

    government/
        government-data.schema.json
        government-ui.schema.json
```

`company-data.schema.json` defines:

- Properties.
- Types.
- Required fields.
- Constraints.
- Conditional requirements.
- Valid values.
- References to shared definitions.

`company-ui.schema.json` defines:

- Form layout.
- Sections.
- Labels.
- Help text.
- Display conditions.
- Field ordering.
- Widget types.
- Which fields should be read-only.
- Which fields can be prepopulated.

JSON Schema is primarily a data contract; it should not be treated as the complete definition of the user experience.

### C. Partial form submissions versus complete validation

This is an issue I would resolve early.

An entity might save its company details before filling in its director information.

The entire Company Schema might require both sections for final submission.

Therefore, distinguish between:

Draft validation: Validate the structure and validity of fields that have been supplied, without requiring the entire organization profile to be complete.

Final submission validation: Enforce all mandatory fields and cross-field requirements.

Do not accidentally make every autosave require a fully completed organization profile.

You can implement this using draft/submission validation rules and, if appropriate, separate versioned schema profiles.

Also be careful with JSON Schema's `format` keyword. The specification allows format to function as annotation rather than assertion, and validation implementations may differ. Explicitly configure your validator and implement critical business checks separately.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://json-schema.org\&sz=32)

json-schema.org



### D. Avoid frontend/backend validation differences

I would establish automated contract tests that run the same valid and invalid JSON examples against:

1. Frontend validator.
2. Onboarding API validator.
3. SO's validator, where its behaviour can be tested.

Examples:

```
Valid Company
Invalid ABN
Missing registered address
Missing mandatory director
Invalid trust structure
Unsupported organization type
Invalid organization status
Incorrect date format
```

Backend validation must always be authoritative. Frontend validation improves usability but must never be the security or correctness boundary.

## 8. AI-driven data enrichment architecture

This is where your architecture can deliver substantial business value.

I would build enrichment as a separate, reusable capability rather than embedding individual source integrations inside the Copilot.

For example, create an Enrichment Service with a connector model:

```
Enrichment Service
    |
    +-- ABR Connector
    |
    +-- ASIC Connector
    |
    +-- ACNC Connector
    |
    +-- Organization Website Connector
    |
    +-- Government Data Connector
    |
    +-- Approved Third-party Connectors
    |
    +-- AI Extraction / Normalization
    |
    +-- Data Reconciliation
```

The Workflow coordinates these activities.

### Example enrichment process

The RM enters:

```
Organization Name: ABC Technologies Pty Ltd
Organization Type: Company
ACN: 123456789
ABN: 12345678901
Website: https://www.example.com.au
```

The onboarding Workflow initiates several enrichment Activities, potentially in parallel.

\#chatgpt-mermaid-\_r_i8\_{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;fill:rgb(13, 13, 13);}@keyframes edge-animation-frame{from{stroke-dashoffset:0;}}@keyframes dash{to{stroke-dashoffset:0;}}#chatgpt-mermaid-\_r_i8\_ .edge-animation-slow{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 50s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-\_r_i8\_ .edge-animation-fast{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 20s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-\_r_i8\_ .error-icon{fill:rgb(243, 243, 243);}#chatgpt-mermaid-\_r_i8\_ .error-text{fill:rgb(13, 13, 13);stroke:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_i8\_ .edge-thickness-normal{stroke-width:1px;}#chatgpt-mermaid-\_r_i8\_ .edge-thickness-thick{stroke-width:3.5px;}#chatgpt-mermaid-\_r_i8\_ .edge-pattern-solid{stroke-dasharray:0;}#chatgpt-mermaid-\_r_i8\_ .edge-thickness-invisible{stroke-width:0;fill:none;}#chatgpt-mermaid-\_r_i8\_ .edge-pattern-dashed{stroke-dasharray:3;}#chatgpt-mermaid-\_r_i8\_ .edge-pattern-dotted{stroke-dasharray:2;}#chatgpt-mermaid-\_r_i8\_ .marker{fill:rgb(143, 143, 143);stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_i8\_ .marker.cross{stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_i8\_ svg{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;}#chatgpt-mermaid-\_r_i8\_ p{margin:0;}#chatgpt-mermaid-\_r_i8\_ .label{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";color:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_i8\_ .cluster-label text{fill:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_i8\_ .cluster-label span{color:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_i8\_ .cluster-label span p{background-color:transparent;}#chatgpt-mermaid-\_r_i8\_ .label text,#chatgpt-mermaid-\_r_i8\_ span{fill:rgb(13, 13, 13);color:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_i8\_ .node rect,#chatgpt-mermaid-\_r_i8\_ .node circle,#chatgpt-mermaid-\_r_i8\_ .node ellipse,#chatgpt-mermaid-\_r_i8\_ .node polygon,#chatgpt-mermaid-\_r_i8\_ .node path{fill:rgb(222, 234, 251);stroke:rgb(83, 154, 248);stroke-width:1px;}#chatgpt-mermaid-\_r_i8\_ .rough-node .label text,#chatgpt-mermaid-\_r_i8\_ .node .label text,#chatgpt-mermaid-\_r_i8\_ .image-shape .label,#chatgpt-mermaid-\_r_i8\_ .icon-shape .label{text-anchor:middle;}#chatgpt-mermaid-\_r_i8\_ .node .katex path{fill:#000;stroke:#000;stroke-width:1px;}#chatgpt-mermaid-\_r_i8\_ .rough-node .label,#chatgpt-mermaid-\_r_i8\_ .node .label,#chatgpt-mermaid-\_r_i8\_ .image-shape .label,#chatgpt-mermaid-\_r_i8\_ .icon-shape .label{text-align:center;}#chatgpt-mermaid-\_r_i8\_ .node.clickable{cursor:pointer;}#chatgpt-mermaid-\_r_i8\_ .root .anchor path{fill:rgb(143, 143, 143)!important;stroke-width:0;stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_i8\_ .arrowheadPath{fill:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_i8\_ .edgePath .path{stroke:rgb(143, 143, 143);stroke-width:1px;}#chatgpt-mermaid-\_r_i8\_ .flowchart-link{stroke:rgb(143, 143, 143);fill:none;}#chatgpt-mermaid-\_r_i8\_ .edgeLabel{background-color:rgb(252, 252, 252);text-align:center;}#chatgpt-mermaid-\_r_i8\_ .edgeLabel p{background-color:rgb(252, 252, 252);}#chatgpt-mermaid-\_r_i8\_ .edgeLabel rect{opacity:0.5;background-color:rgb(252, 252, 252);fill:rgb(252, 252, 252);}#chatgpt-mermaid-\_r_i8\_ .labelBkg{background-color:rgba(252, 252, 252, 0.5);}#chatgpt-mermaid-\_r_i8\_ .cluster rect{fill:rgb(243, 243, 243);stroke:rgba(0, 0, 0, 0.1);stroke-width:1px;}#chatgpt-mermaid-\_r_i8\_ .cluster text{fill:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_i8\_ .cluster span{color:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_i8\_ div.mermaidTooltip{position:absolute;text-align:center;max-width:200px;padding:2px;font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:12px;background:rgb(243, 243, 243);border:1px solid rgba(0, 0, 0, 0.1);border-radius:2px;pointer-events:none;z-index:100;}#chatgpt-mermaid-\_r_i8\_ .flowchartTitleText{text-anchor:middle;font-size:18px;fill:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_i8\_ rect.text{fill:none;stroke-width:0;}#chatgpt-mermaid-\_r_i8\_ .icon-shape,#chatgpt-mermaid-\_r_i8\_ .image-shape{background-color:rgb(252, 252, 252);text-align:center;}#chatgpt-mermaid-\_r_i8\_ .icon-shape p,#chatgpt-mermaid-\_r_i8\_ .image-shape p{background-color:rgb(252, 252, 252);padding:2px;}#chatgpt-mermaid-\_r_i8\_ .icon-shape .label rect,#chatgpt-mermaid-\_r_i8\_ .image-shape .label rect{opacity:0.5;background-color:rgb(252, 252, 252);fill:rgb(252, 252, 252);}#chatgpt-mermaid-\_r_i8\_ .label-icon{display:inline-block;height:1em;overflow:visible;vertical-align:-0.125em;}#chatgpt-mermaid-\_r_i8\_ .node .label-icon path{fill:currentColor;stroke:revert;stroke-width:revert;}#chatgpt-mermaid-\_r_i8\_ .node .neo-node{stroke:rgb(83, 154, 248);}#chatgpt-mermaid-\_r_i8\_ [data-look="neo"].node rect,#chatgpt-mermaid-\_r_i8\_ [data-look="neo"].cluster rect,#chatgpt-mermaid-\_r_i8\_ [data-look="neo"].node polygon{stroke:url(#chatgpt-mermaid-\_r_i8\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_i8\_ [data-look="neo"].swimlane.cluster rect{filter:none;}#chatgpt-mermaid-\_r_i8\_ [data-look="neo"].node path{stroke:url(#chatgpt-mermaid-\_r_i8\_-gradient);stroke-width:1px;}#chatgpt-mermaid-\_r_i8\_ [data-look="neo"].node .outer-path{filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_i8\_ [data-look="neo"].node .neo-line path{stroke:rgb(83, 154, 248);filter:none;}#chatgpt-mermaid-\_r_i8\_ [data-look="neo"].node circle{stroke:url(#chatgpt-mermaid-\_r_i8\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_i8\_ [data-look="neo"].node circle .state-start{fill:#000000;}#chatgpt-mermaid-\_r_i8\_ [data-look="neo"].icon-shape .icon{fill:url(#chatgpt-mermaid-\_r_i8\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_i8\_ [data-look="neo"].icon-shape .icon-neo path{stroke:url(#chatgpt-mermaid-\_r_i8\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_i8\_ .node text{font-size:14px;font-weight:600;letter-spacing:normal;fill:rgb(0, 79, 153);}#chatgpt-mermaid-\_r_i8\_ .edgeLabels text{font-size:13px;font-weight:600;letter-spacing:-0.08px;fill:rgb(0, 79, 153);}#chatgpt-mermaid-\_r_i8\_ .node tspan[font-weight="normal"],#chatgpt-mermaid-\_r_i8\_ .edgeLabels tspan[font-weight="normal"]{font-weight:600;}#chatgpt-mermaid-\_r_i8\_ .edgeLabel .label rect{opacity:1;rx:13px;ry:13px;fill:rgb(245, 250, 255);stroke:rgb(206, 219, 229);stroke-width:1px;}#chatgpt-mermaid-\_r_i8\_ .node rect,#chatgpt-mermaid-\_r_i8\_ .node circle,#chatgpt-mermaid-\_r_i8\_ .node ellipse,#chatgpt-mermaid-\_r_i8\_ .node polygon,#chatgpt-mermaid-\_r_i8\_ .node path{fill:rgb(229, 243, 255);stroke:rgba(0, 0, 0, 0.1);stroke-width:1px;}#chatgpt-mermaid-\_r_i8\_ .node rect{rx:16px;ry:16px;}#chatgpt-mermaid-\_r_i8\_ .mermaid-decision .label-container{fill:rgb(245, 250, 255);stroke:rgb(206, 219, 229);stroke-dasharray:2,2;}#chatgpt-mermaid-\_r_i8\_ .edgePaths .flowchart-link{stroke:rgb(143, 143, 143);stroke-width:1px;stroke-linecap:round;stroke-linejoin:round;}#chatgpt-mermaid-\_r_i8\_ .marker{fill:rgb(143, 143, 143);stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_i8\_ :root{--mermaid-font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";}RM provides organizationdetailsOnboarding WorkflowABN / ABR LookupASIC / Company RegistryOrganization WebsiteOther Whitelisted SourcesAI Extraction andNormalizationData ReconciliationSave Enrichment Results andProvenanceGenerate RM ReviewSummaryRM Reviews and Accepts /Rejects Suggestions

### Data provenance is essential

I would never store an AI-enriched field as just a value.

For every enriched field, maintain its provenance.

For example:

```
{
  "field": "organization.registeredAddress",
  "value": {
    "street": "100 Example Street",
    "suburb": "Sydney",
    "state": "NSW",
    "postcode": "2000"
  },
  "source": {
    "type": "ABR",
    "reference": "source-record-123",
    "retrievedAt": "2026-11-04T10:00:00Z"
  },
  "confidence": 0.99,
  "verificationStatus": "SOURCE_CONFIRMED",
  "reviewStatus": "PENDING_RM_REVIEW"
}
```

The structure is illustrative.

I would distinguish at least these field states:

| State            | Meaning                                                    |
| ---------------- | ---------------------------------------------------------- |
| AI_SUGGESTED     | Suggested by AI, not independently verified                |
| SOURCE_CONFIRMED | Matched to an authoritative or approved source             |
| RM_CONFIRMED     | Reviewed and accepted by RM                                |
| ENTITY_CONFIRMED | Supplied or confirmed by the organization                  |
| BANK_VERIFIED    | Independently verified through the bank's required control |
| CONFLICTED       | Multiple sources disagree                                  |
| REJECTED         | Value explicitly rejected                                  |

These are different concepts: a value can be confirmed by a public source without having been independently verified for bank onboarding purposes.

### Source ranking

For each field, define which sources are authoritative.

For example:

| Information                  | Preferred source                                           |
| ---------------------------- | ---------------------------------------------------------- |
| ABN and ABN status           | ABR                                                        |
| ACN and company registration | ASIC, subject to access                                    |
| Registered company name      | Authoritative registry                                     |
| Public organization address  | Approved registry                                          |
| Organization website         | Official website, subject to verification                  |
| Organization description     | Website and approved public sources                        |
| Directors and officeholders  | Applicable authoritative registry and verification process |
| Beneficial owners            | Appropriate bank/customer verification process             |

Do not let AI select whichever source happens to provide the most convenient answer.

Where there are disagreements, retain both observations and let explicit reconciliation rules or an RM resolve the conflict.

### Important Australian data-source consideration

I would clarify what you mean by "IPO API". This is not sufficiently precise to identify an authoritative organization-information source.

For Australian organization onboarding, I would investigate these first:

- Australian Business Register (ABR) — its ABN Lookup Web Services support ABN validation and prepopulation of forms. Access to its web services is free but requires registration and an authentication GUID.&#x20;

  [image](https://www.google.com/s2/favicons?domain=https://abr.business.gov.au\&sz=32)

  ABN Lookup+1

- Australian Securities and Investments Commission (ASIC) — relevant to companies and business-name registry information. An important current access constraint is that ASIC's published API information says it is not accepting new company-register Digital Service Provider applications at present and expects to reopen applications in 2027. This means your source strategy should not assume that a new direct ASIC company-register integration is immediately available.&#x20;

  [image](https://www.google.com/s2/favicons?domain=https://www.asic.gov.au\&sz=32)

  ASIC+1

- Australian Charities and Not-for-profits Commission (ACNC) — relevant when verifying charity registration and associated public information.

- Official government websites and other specifically approved public registers where the organization type makes them relevant.

I would build source connectors behind a configurable catalogue so that sources can be added or replaced without modifying the main onboarding Workflow.

One significant control: publicly accessible information is not automatically permissible for every banking use. Each connector should have an approved purpose, access terms, data-retention policy and field-level provenance. Website retrieval should also enforce domain allowlists and protection against server-side request forgery.

And importantly, use the AI to prepopulate information, not to replace the bank's identity, beneficial ownership, KYC or other mandatory verification controls.

## 9. Recommended onboarding Workflow lifecycle

I would establish a single internal state machine for the business journey and a separate mapping for the official SO status.

For example:

\#chatgpt-mermaid-\_r_j1\_{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;fill:rgb(13, 13, 13);}@keyframes edge-animation-frame{from{stroke-dashoffset:0;}}@keyframes dash{to{stroke-dashoffset:0;}}#chatgpt-mermaid-\_r_j1\_ .edge-animation-slow{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 50s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-\_r_j1\_ .edge-animation-fast{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 20s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-\_r_j1\_ .error-icon{fill:rgb(243, 243, 243);}#chatgpt-mermaid-\_r_j1\_ .error-text{fill:rgb(13, 13, 13);stroke:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_j1\_ .edge-thickness-normal{stroke-width:1px;}#chatgpt-mermaid-\_r_j1\_ .edge-thickness-thick{stroke-width:3.5px;}#chatgpt-mermaid-\_r_j1\_ .edge-pattern-solid{stroke-dasharray:0;}#chatgpt-mermaid-\_r_j1\_ .edge-thickness-invisible{stroke-width:0;fill:none;}#chatgpt-mermaid-\_r_j1\_ .edge-pattern-dashed{stroke-dasharray:3;}#chatgpt-mermaid-\_r_j1\_ .edge-pattern-dotted{stroke-dasharray:2;}#chatgpt-mermaid-\_r_j1\_ .marker{fill:rgb(143, 143, 143);stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_j1\_ .marker.cross{stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_j1\_ svg{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;}#chatgpt-mermaid-\_r_j1\_ p{margin:0;}#chatgpt-mermaid-\_r_j1\_ defs [id$="-barbEnd"]{fill:rgb(143, 143, 143);stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_j1\_ g.stateGroup text{fill:rgb(83, 154, 248);stroke:none;font-size:10px;}#chatgpt-mermaid-\_r_j1\_ g.stateGroup text{fill:rgb(13, 13, 13);stroke:none;font-size:10px;}#chatgpt-mermaid-\_r_j1\_ g.stateGroup .state-title{font-weight:bolder;fill:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_j1\_ g.stateGroup rect{fill:rgb(222, 234, 251);stroke:rgb(83, 154, 248);}#chatgpt-mermaid-\_r_j1\_ g.stateGroup line{stroke:rgb(143, 143, 143);stroke-width:1;}#chatgpt-mermaid-\_r_j1\_ .transition{stroke:rgb(143, 143, 143);stroke-width:1;fill:none;}#chatgpt-mermaid-\_r_j1\_ .stateGroup .composit{fill:transparent;border-bottom:1px;}#chatgpt-mermaid-\_r_j1\_ .stateGroup .alt-composit{fill:#e0e0e0;border-bottom:1px;}#chatgpt-mermaid-\_r_j1\_ .state-note{stroke:rgb(107, 198, 127);fill:rgb(243, 243, 243);}#chatgpt-mermaid-\_r_j1\_ .state-note text{fill:rgb(13, 13, 13);stroke:none;font-size:10px;}#chatgpt-mermaid-\_r_j1\_ .stateLabel .box{stroke:none;stroke-width:0;fill:rgb(222, 234, 251);opacity:0.5;}#chatgpt-mermaid-\_r_j1\_ .edgeLabel .label rect{fill:rgb(222, 234, 251);opacity:0.5;}#chatgpt-mermaid-\_r_j1\_ .edgeLabel{background-color:rgb(252, 252, 252);text-align:center;}#chatgpt-mermaid-\_r_j1\_ .edgeLabel p{background-color:rgb(252, 252, 252);}#chatgpt-mermaid-\_r_j1\_ .edgeLabel rect{opacity:0.5;background-color:rgb(252, 252, 252);fill:rgb(252, 252, 252);}#chatgpt-mermaid-\_r_j1\_ .edgeLabel .label text{fill:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_j1\_ .label div .edgeLabel{color:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_j1\_ .stateLabel text{fill:rgb(13, 13, 13);font-size:10px;font-weight:bold;}#chatgpt-mermaid-\_r_j1\_ .node circle.state-start{fill:rgb(143, 143, 143);stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_j1\_ .node .fork-join{fill:rgb(143, 143, 143);stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_j1\_ .node circle.state-end{fill:rgb(83, 154, 248);stroke:transparent;stroke-width:1.5;}#chatgpt-mermaid-\_r_j1\_ .end-state-inner{fill:transparent;stroke-width:1.5;}#chatgpt-mermaid-\_r_j1\_ .node rect{fill:rgb(222, 234, 251);stroke:rgb(83, 154, 248);stroke-width:1px;}#chatgpt-mermaid-\_r_j1\_ .node polygon{fill:rgb(222, 234, 251);stroke:rgb(83, 154, 248);stroke-width:1px;}#chatgpt-mermaid-\_r_j1\_ [id$="-barbEnd"]{fill:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_j1\_ .statediagram-cluster rect{fill:rgb(222, 234, 251);stroke:rgb(83, 154, 248);stroke-width:1px;}#chatgpt-mermaid-\_r_j1\_ .cluster-label,#chatgpt-mermaid-\_r_j1\_ .nodeLabel{color:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_j1\_ .statediagram-cluster rect.outer{rx:5px;ry:5px;}#chatgpt-mermaid-\_r_j1\_ .statediagram-state .divider{stroke:rgb(83, 154, 248);}#chatgpt-mermaid-\_r_j1\_ .statediagram-state .title-state{rx:5px;ry:5px;}#chatgpt-mermaid-\_r_j1\_ .statediagram-cluster.statediagram-cluster .inner{fill:transparent;}#chatgpt-mermaid-\_r_j1\_ .statediagram-cluster.statediagram-cluster-alt .inner{fill:rgb(243, 243, 243);}#chatgpt-mermaid-\_r_j1\_ .statediagram-cluster .inner{rx:0;ry:0;}#chatgpt-mermaid-\_r_j1\_ .statediagram-state rect.basic{rx:5px;ry:5px;}#chatgpt-mermaid-\_r_j1\_ .statediagram-state rect.divider{stroke-dasharray:10,10;fill:rgb(243, 243, 243);}#chatgpt-mermaid-\_r_j1\_ .note-edge{stroke-dasharray:5;}#chatgpt-mermaid-\_r_j1\_ .statediagram-note rect{fill:rgb(243, 243, 243);stroke:rgb(107, 198, 127);stroke-width:1px;rx:0;ry:0;}#chatgpt-mermaid-\_r_j1\_ .statediagram-note rect{fill:rgb(243, 243, 243);stroke:rgb(107, 198, 127);stroke-width:1px;rx:0;ry:0;}#chatgpt-mermaid-\_r_j1\_ .statediagram-note text{fill:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_j1\_ .statediagram-note .nodeLabel{color:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_j1\_ .statediagram .edgeLabel{color:red;}#chatgpt-mermaid-\_r_j1\_ [id$="-dependencyStart"],#chatgpt-mermaid-\_r_j1\_ [id$="-dependencyEnd"]{fill:rgb(143, 143, 143);stroke:rgb(143, 143, 143);stroke-width:1;}#chatgpt-mermaid-\_r_j1\_ .statediagramTitleText{text-anchor:middle;font-size:18px;fill:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_j1\_ [data-look="neo"].statediagram-cluster rect{fill:rgb(222, 234, 251);stroke:url(#chatgpt-mermaid-\_r_j1\_-gradient);stroke-width:1;}#chatgpt-mermaid-\_r_j1\_ [data-look="neo"].statediagram-cluster rect.outer{rx:5px;ry:5px;filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_j1\_ .node .neo-node{stroke:rgb(83, 154, 248);}#chatgpt-mermaid-\_r_j1\_ [data-look="neo"].node rect,#chatgpt-mermaid-\_r_j1\_ [data-look="neo"].cluster rect,#chatgpt-mermaid-\_r_j1\_ [data-look="neo"].node polygon{stroke:url(#chatgpt-mermaid-\_r_j1\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_j1\_ [data-look="neo"].swimlane.cluster rect{filter:none;}#chatgpt-mermaid-\_r_j1\_ [data-look="neo"].node path{stroke:url(#chatgpt-mermaid-\_r_j1\_-gradient);stroke-width:1px;}#chatgpt-mermaid-\_r_j1\_ [data-look="neo"].node .outer-path{filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_j1\_ [data-look="neo"].node .neo-line path{stroke:rgb(83, 154, 248);filter:none;}#chatgpt-mermaid-\_r_j1\_ [data-look="neo"].node circle{stroke:url(#chatgpt-mermaid-\_r_j1\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_j1\_ [data-look="neo"].node circle .state-start{fill:#000000;}#chatgpt-mermaid-\_r_j1\_ [data-look="neo"].icon-shape .icon{fill:url(#chatgpt-mermaid-\_r_j1\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_j1\_ [data-look="neo"].icon-shape .icon-neo path{stroke:url(#chatgpt-mermaid-\_r_j1\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_j1\_ :root{--mermaid-font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";}DraftEnrichingRMReviewReadyToSubmitSORegistrationSORegistrationFailedAwaitingEntityEntitySubmittingValidationBankReviewAwaitingInformationApprovedRejectedCompletedCancelledExpiredMore enrichment requiredRM requests changesRM approvesSO API errorRetry / ReconcileValidation errorsValid submissionEntity responseRM / internal response

This is an illustrative state machine. Your actual SO statuses should be mapped to it, not necessarily copied directly.

For example:

| Internal workflow stage | Possible SO status        |
| ----------------------- | ------------------------- |
| Draft                   | Not registered / Draft    |
| ReadyToSubmit           | Pending registration      |
| AwaitingEntity          | Awaiting Customer         |
| BankReview              | Under Review              |
| AwaitingInformation     | More Information Required |
| Approved                | Approved                  |
| Rejected                | Rejected                  |
| Completed               | Completed                 |

The actual mapping depends on the third-party system.

I recommend that SO remains the authority for official request status after registration. Your application should not independently invent or overwrite official SO status.

A useful additional distinction:

- SO status: What is the official status of the servicing request?
- Workflow status: What step is the automation/business process currently executing?
- Application status: What should the RM or customer see in the interface?

These may be related, but they are not necessarily identical.

For example:

```
SO Status: AWAITING_CUSTOMER

Workflow Status: WAITING_FOR_ENTITY_RESPONSE

Customer UI Status: Action Required
```

That separation prevents a lot of future confusion.

## 10. Important Temporal implementation considerations

Since you are new to Temporal, there are some implementation details I would establish before development.

### A. Workflow code must be deterministic

A Temporal Workflow can be replayed to reconstruct its state.

Therefore, don't directly execute the following inside Workflow code:

- HTTP calls.
- Database queries.
- LLM invocations.
- Random number generation.
- Direct Kafka consumption.
- Other non-deterministic operations.

Put those operations inside Activities.

For example:

```
OrganizationOnboardingWorkflow
    |
    +-- Activity: GetOrganizationDraft
    |
    +-- Activity: EnrichUsingABR
    |
    +-- Activity: EnrichUsingASIC
    |
    +-- Activity: ExtractWebsiteInformation
    |
    +-- Activity: SaveEnrichmentResults
    |
    +-- Activity: CreateServicingOrder
    |
    +-- Activity: SendEntityInvitation
    |
    +-- Activity: UpdateServicingOrder
```

The Workflow decides what happens next. Activities interact with the outside world. Temporal explicitly recommends Activities for non-deterministic operations, including API calls, database queries and AI invocations.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://docs.temporal.io\&sz=32)

Temporal Documentation



### B. Activities must be idempotent

This is especially important for your SO integration.

Imagine:

1. Temporal calls `POST /servicing-orders`.
2. SO successfully creates the record.
3. The network connection drops before your Activity receives the response.
4. Temporal retries the Activity.
5. Another SO request is created.

You now have duplicate requests.

Therefore, every operation with external side effects needs an idempotency strategy.

For example:

```
Activity: CreateServicingOrder

Idempotency Key:
    onboarding-10001-create-so
```

Use the SO API's native idempotency support wherever available.

If it does not support idempotency keys, ask whether it supports a unique external reference that you can query before retrying a create operation.

The same applies to notifications: you do not want a retry sending five identical invitations.

### C. Be careful about Workflow history size

Do not store:

- Complete organization JSON.
- Complete entity form submissions.
- Documents.
- Large website extraction results.
- Entire LLM prompts and responses.
- Large enrichment datasets.

Keep only information necessary for orchestration:

```
{
  "onboardingCaseId": "10001",
  "orgType": "COMPANY",
  "soRequestId": "SO-98765",
  "currentStage": "AWAITING_ENTITY",
  "schemaVersion": "3.2",
  "latestRevisionId": "revision-0042"
}
```

Temporal stores Workflow and Activity input/output payloads in Event History. Its documented limits include 2 MB per individual payload and 50 MB per Workflow Event History. Temporal recommends storing large information externally and passing references through the Workflow instead.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://docs.temporal.io\&sz=32)

Temporal Documentation+1



This is another reason not to use Workflow state as your form-data database.

For longer-running requests, use Continue-As-New when the history grows sufficiently.

### D. Use the right Workflow messaging mechanism

Temporal has three useful messaging mechanisms:

| Mechanism | Use in your application                                                   |
| --------- | ------------------------------------------------------------------------- |
| Signal    | Kafka event, customer response, asynchronous RM action                    |
| Update    | A business command requiring synchronous Workflow validation and a result |
| Query     | Read small pieces of current Workflow execution state                     |

For example:

```
Signal:
    EntitySubmitted
    SOStatusChanged
    RMCancelledRequest

Update:
    ApproveEnrichment
    RequestAdditionalInformation
    ApproveSubmission

Query:
    GetWorkflowProgress
    GetCurrentWorkflowStage
```

I would not use Query as your main method of retrieving form data. Read form and request data through the Onboarding API and its database/read model.

Also, give every externally generated Signal a stable event or command ID and implement deduplication. Signals do not automatically provide exactly-once business processing.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://docs.temporal.io\&sz=32)

Temporal Documentation+1



### E. Separate Activities by responsibility

I would start with at least these logical Worker groups:

| Worker group           | Responsibilities                                     |
| ---------------------- | ---------------------------------------------------- |
| Onboarding Workers     | Main onboarding Workflow and orchestration           |
| Enrichment Workers     | ABR, ASIC, website, AI and data reconciliation       |
| SO Integration Workers | SO create, update, lookup, status and reconciliation |
| Notification Workers   | Invitations, status notifications and reminders      |

They can initially be deployed together if the team and infrastructure are small. Separate Task Queues and deployments become useful when workloads, permissions or scaling requirements diverge.

### F. Treat Workflow versioning as a production requirement

A company onboarding Workflow created in November may still be running after you release a new version in December.

Do not assume that all existing executions can automatically start using the new code.

Adopt Temporal Worker Versioning or a suitable patching strategy from the beginning. For your use case, I would favour Worker Versioning where the deployment environment supports it.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://docs.temporal.io\&sz=32)

Temporal Documentation+1



## 11. Data model I would recommend

I would separate the business entity from the onboarding request.

This is important because the same organization could have multiple onboarding requests over time, potentially for different banking products or servicing purposes.

A suggested logical data model:

| Entity                   | Purpose                                                                     |
| ------------------------ | --------------------------------------------------------------------------- |
| `OnboardingCase`         | The individual onboarding journey                                           |
| `Organization`           | The organization being onboarded                                            |
| `OrganizationIdentifier` | ABN, ACN or other identifiers                                               |
| `OrganizationParty`      | Directors, trustees, owners, authorized representatives and related parties |
| `PartyRelationship`      | The relationship between the organization and its people or other entities  |
| `OnboardingRevision`     | Immutable versions of submitted form data                                   |
| `EnrichmentObservation`  | Values obtained from external sources with provenance                       |
| `DocumentReference`      | Metadata and references to uploaded documents                               |
| `SORequestLink`          | Mapping between internal onboarding case and SO request ID                  |
| `OnboardingAuditEvent`   | Business-level audit history                                                |
| `IntegrationInbox`       | Received SO events and processed event IDs                                  |
| `IntegrationOutbox`      | Pending commands and Temporal dispatch operations                           |

### Why introduce OrganizationParty and PartyRelationship?

Because a company, trust and government organization have different structures.

For example:

```
Company
    |
    +-- Director
    +-- Shareholder
    +-- Beneficial Owner
    +-- Authorized Signatory

Trust
    |
    +-- Trustee
    +-- Appointor
    +-- Beneficiary
    +-- Settlor
    +-- Authorized Signatory

Government Organization
    |
    +-- Department
    +-- Agency / Division
    +-- Authorized Officer
```

These should not be represented as arbitrary extra fields within a single flat organization JSON object.

You are likely to need an organization graph or at least an explicit organization-and-party relationship model.

It will also make it easier to apply reusable due diligence workflows to the relevant people and related entities.

### Important database design recommendation

Maintain immutable form revisions.

For example:

```
OnboardingCase 10001

    revision-0001
        RM initial information

    revision-0002
        ABR enrichment accepted

    revision-0003
        RM corrected organization address

    revision-0004
        Entity submitted organization details

    revision-0005
        Entity corrected director information
```

Each revision should capture:

- Schema ID and version.
- Who created it.
- When it was created.
- Which fields changed.
- Original and updated values, subject to data-retention policy.
- Submission or approval reference.
- Synchronization status with SO.

This will be enormously useful for audit, dispute resolution and troubleshooting.

# 12. Ambiguity and gap analysis

You have described the core architecture well, but there are several important matters that need to be clarified or explicitly included.

I would consider the following part of the architecture, not optional future enhancements.

## A. Third-party Servicing Order capabilities

Critical dependency

This is the largest area of uncertainty.

| Question                                             | Why it matters                               | Recommendation                                           |
| ---------------------------------------------------- | -------------------------------------------- | -------------------------------------------------------- |
| Does SO support Draft status?                        | Determines Option A versus B                 | Confirm before finalizing data ownership                 |
| Does create support an external reference?           | Enables correlation and duplicate prevention | Require a unique bank onboarding ID                      |
| Does SO support idempotency keys?                    | Prevents duplicate requests                  | Require native support or an equivalent lookup mechanism |
| Does SO support partial updates?                     | Important for entity forms and enrichment    | Confirm PATCH semantics                                  |
| Does SO support optimistic concurrency?              | Prevents conflicting updates                 | Require ETags or version numbers                         |
| Does SO publish aggregate versions?                  | Allows event ordering protection             | Include monotonic version numbers                        |
| Does Kafka guarantee ordering per request?           | Affects event processing                     | Confirm partition key and ordering guarantees            |
| Can Kafka events be replayed?                        | Important for recovery                       | Confirm retention and replay arrangements                |
| Are events full snapshots or change events?          | Affects reconciliation                       | Prefer event notification plus authoritative API lookup  |
| Does SO expose GET by external reference?            | Enables reconciliation                       | Strongly recommend                                       |
| Can a schema version be pinned to a request?         | Prevents schema drift                        | Require explicit schema ID/version                       |
| Can an existing request be migrated to a new schema? | Important for future evolution               | Define migration processes                               |

I would make these requirements part of the third-party API integration agreement.

## B. Organization types and complex relationships

You mentioned Company, Trust and Government Organization.

I would clarify the full organization taxonomy.

For example:

- Proprietary Limited Company.
- Public Company.
- Partnership.
- Discretionary Trust.
- Unit Trust.
- Family Trust.
- Self-Managed Superannuation Fund.
- Incorporated Association.
- Registered Charity.
- Government Department.
- Statutory Authority.
- Local Government.
- Foreign Entity.

Each can require different questions, supporting documentation and party relationships.

My recommendation is to use an organization type registry rather than hardcoding `if/else` logic throughout the application.

A registry entry might contain:

```
{
  "orgType": "TRUST",
  "schemaId": "trust-schema",
  "schemaVersion": "2.1",
  "workflowProfile": "standard-organization-onboarding",
  "requiredPartyRoles": [
    "TRUSTEE",
    "APPOINTOR",
    "AUTHORIZED_SIGNATORY"
  ],
  "enrichmentProfile": [
    "ABR",
    "APPROVED_PUBLIC_SOURCES"
  ]
}
```

This also makes it possible to introduce a new organization type without rewriting your primary Workflow.

## C. Conflicting data from multiple sources

What happens when:

```
ABR:
    Organization name = ABC Pty Ltd

Website:
    Organization name = ABC Technologies

RM:
    Organization name = ABC Holdings Pty Ltd
```

You need an explicit resolution strategy.

I recommend:

- Source precedence by field.
- Field-level confidence.
- Source timestamps.
- Conflict detection.
- Manual resolution for material conflicts.
- Immutable history of the original observations.

Do not allow AI to silently select one value and overwrite the others.

## D. Human verification and approval

You should distinguish between:

- AI enrichment.
- RM acceptance.
- Customer confirmation.
- Independent bank verification.

These are not interchangeable.

For example, an ABR record might confirm that an ABN is active. It does not establish that a person submitting the onboarding form is authorized to act for that organization.

You will need appropriate identity, authority, beneficial ownership and applicable KYC/AML controls.

## E. Entity invitations and delegated access

There is an additional security question:

How does the bank know that the person completing the Next.js onboarding form is authorized to represent the organization?

I would introduce:

- Secure invitations linked to an onboarding case.
- Time-limited invitation tokens.
- Appropriate identity verification and MFA.
- RM-controlled invitation and revocation.
- Role-based or attribute-based access.
- Explicit organization-to-user relationships.
- Audit of customer access and submissions.

Never rely on possession of an onboarding URL alone as proof of authority.

## F. Document management

Documents should not be stored in Temporal Workflow history or directly embedded into Kafka events.

Use the bank's approved document management or object storage platform.

Store references in your application database:

```
{
  "documentId": "doc-123",
  "onboardingCaseId": "10001",
  "documentType": "COMPANY_EXTRACT",
  "storageReference": "approved-storage-reference",
  "status": "UPLOADED",
  "uploadedBy": "entity-user-123"
}
```

You will also need malware scanning, secure download authorization, document retention and potentially document extraction/verification workflows.

## G. Operational failures and manual intervention

Not every onboarding request will complete successfully through automation.

For example:

- ABR API is unavailable.
- An organization website is inaccessible.
- AI extraction has low confidence.
- Sources disagree.
- SO API is unavailable.
- Entity submission fails validation.
- A Kafka event cannot be matched to an onboarding case.
- Notifications repeatedly fail.

Establish explicit exception states and a bank operations work queue.

Temporal handles retries and durable waiting, but it should not replace human operational oversight.

## H. Security, privacy and audit

For a banking application, I would establish these controls from day one:

| Area              | Recommendation                                                     |
| ----------------- | ------------------------------------------------------------------ |
| API security      | Enterprise OAuth/OIDC, service authentication and authorization    |
| Data protection   | Encryption in transit and at rest                                  |
| Temporal          | Restrict Namespace access and Workflow visibility                  |
| PII in Temporal   | Pass references, not full customer records                         |
| Temporal payloads | Consider client-side payload encryption as an additional safeguard |
| Documents         | Approved encrypted document storage                                |
| AI                | Approved model, controlled data access and retention               |
| Audit             | Durable business audit log                                         |
| Public enrichment | Source allowlisting, provenance and retention controls             |
| Secrets           | Centralized secrets management and rotation                        |
| Access            | Least-privilege RM, customer and service permissions               |

Temporal provides payload codec mechanisms for encryption before Workflow payloads reach its service. However, given your data sensitivity, I would prioritize not placing unnecessary PII into Temporal in the first place.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub+1



Also, do not treat Temporal Event History as your sole regulatory/business audit record. The application needs its own audit model that captures business actors, changes, reasons, evidence and official SO acknowledgements.

## 13. Additional design decisions

Here are several decisions I would establish as architectural standards.

| Design area            | My recommendation                                       |
| ---------------------- | ------------------------------------------------------- |
| Workflow granularity   | One main Workflow per onboarding case                   |
| Workflow ID            | Stable internal onboarding case ID                      |
| Child Workflows        | Only for independently managed complex sub-processes    |
| Workflow persistence   | Temporal's own durable history, minimal business state  |
| Form data              | Onboarding database                                     |
| Official SO data       | Servicing Order after registration                      |
| Frontend communication | Onboarding API only                                     |
| SO communication       | SO Integration Adapter only                             |
| Kafka integration      | Separate Consumer and Signal Dispatcher                 |
| Kafka processing       | Inbox/outbox, deduplication and version checks          |
| Form autosave          | Database-backed, revision-based                         |
| SO synchronization     | Controlled logical submissions/checkpoints              |
| Schema ownership       | SO registry as canonical publisher, application cache   |
| Schema evolution       | Immutable versions and pinned active cases              |
| AI enrichment          | Activities using approved connectors                    |
| Source provenance      | Persist every meaningful source observation             |
| Human approval         | Explicit RM/customer approval where needed              |
| Notifications          | Temporal Activities and controlled notification service |
| Business audit         | Separate immutable application audit history            |
| Failure recovery       | Temporal retries, outbox/inbox and reconciliation       |

# 14. Putting everything together: recommended end-to-end journey

Here is the end-to-end design I would implement.

\#chatgpt-mermaid-\_r_p4\_{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;fill:rgb(13, 13, 13);}@keyframes edge-animation-frame{from{stroke-dashoffset:0;}}@keyframes dash{to{stroke-dashoffset:0;}}#chatgpt-mermaid-\_r_p4\_ .edge-animation-slow{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 50s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-\_r_p4\_ .edge-animation-fast{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 20s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-\_r_p4\_ .error-icon{fill:rgb(243, 243, 243);}#chatgpt-mermaid-\_r_p4\_ .error-text{fill:rgb(13, 13, 13);stroke:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_p4\_ .edge-thickness-normal{stroke-width:1px;}#chatgpt-mermaid-\_r_p4\_ .edge-thickness-thick{stroke-width:3.5px;}#chatgpt-mermaid-\_r_p4\_ .edge-pattern-solid{stroke-dasharray:0;}#chatgpt-mermaid-\_r_p4\_ .edge-thickness-invisible{stroke-width:0;fill:none;}#chatgpt-mermaid-\_r_p4\_ .edge-pattern-dashed{stroke-dasharray:3;}#chatgpt-mermaid-\_r_p4\_ .edge-pattern-dotted{stroke-dasharray:2;}#chatgpt-mermaid-\_r_p4\_ .marker{fill:rgb(143, 143, 143);stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_p4\_ .marker.cross{stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_p4\_ svg{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;}#chatgpt-mermaid-\_r_p4\_ p{margin:0;}#chatgpt-mermaid-\_r_p4\_ .label{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";color:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_p4\_ .cluster-label text{fill:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_p4\_ .cluster-label span{color:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_p4\_ .cluster-label span p{background-color:transparent;}#chatgpt-mermaid-\_r_p4\_ .label text,#chatgpt-mermaid-\_r_p4\_ span{fill:rgb(13, 13, 13);color:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_p4\_ .node rect,#chatgpt-mermaid-\_r_p4\_ .node circle,#chatgpt-mermaid-\_r_p4\_ .node ellipse,#chatgpt-mermaid-\_r_p4\_ .node polygon,#chatgpt-mermaid-\_r_p4\_ .node path{fill:rgb(222, 234, 251);stroke:rgb(83, 154, 248);stroke-width:1px;}#chatgpt-mermaid-\_r_p4\_ .rough-node .label text,#chatgpt-mermaid-\_r_p4\_ .node .label text,#chatgpt-mermaid-\_r_p4\_ .image-shape .label,#chatgpt-mermaid-\_r_p4\_ .icon-shape .label{text-anchor:middle;}#chatgpt-mermaid-\_r_p4\_ .node .katex path{fill:#000;stroke:#000;stroke-width:1px;}#chatgpt-mermaid-\_r_p4\_ .rough-node .label,#chatgpt-mermaid-\_r_p4\_ .node .label,#chatgpt-mermaid-\_r_p4\_ .image-shape .label,#chatgpt-mermaid-\_r_p4\_ .icon-shape .label{text-align:center;}#chatgpt-mermaid-\_r_p4\_ .node.clickable{cursor:pointer;}#chatgpt-mermaid-\_r_p4\_ .root .anchor path{fill:rgb(143, 143, 143)!important;stroke-width:0;stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_p4\_ .arrowheadPath{fill:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_p4\_ .edgePath .path{stroke:rgb(143, 143, 143);stroke-width:1px;}#chatgpt-mermaid-\_r_p4\_ .flowchart-link{stroke:rgb(143, 143, 143);fill:none;}#chatgpt-mermaid-\_r_p4\_ .edgeLabel{background-color:rgb(252, 252, 252);text-align:center;}#chatgpt-mermaid-\_r_p4\_ .edgeLabel p{background-color:rgb(252, 252, 252);}#chatgpt-mermaid-\_r_p4\_ .edgeLabel rect{opacity:0.5;background-color:rgb(252, 252, 252);fill:rgb(252, 252, 252);}#chatgpt-mermaid-\_r_p4\_ .labelBkg{background-color:rgba(252, 252, 252, 0.5);}#chatgpt-mermaid-\_r_p4\_ .cluster rect{fill:rgb(243, 243, 243);stroke:rgba(0, 0, 0, 0.1);stroke-width:1px;}#chatgpt-mermaid-\_r_p4\_ .cluster text{fill:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_p4\_ .cluster span{color:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_p4\_ div.mermaidTooltip{position:absolute;text-align:center;max-width:200px;padding:2px;font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:12px;background:rgb(243, 243, 243);border:1px solid rgba(0, 0, 0, 0.1);border-radius:2px;pointer-events:none;z-index:100;}#chatgpt-mermaid-\_r_p4\_ .flowchartTitleText{text-anchor:middle;font-size:18px;fill:rgb(13, 13, 13);}#chatgpt-mermaid-\_r_p4\_ rect.text{fill:none;stroke-width:0;}#chatgpt-mermaid-\_r_p4\_ .icon-shape,#chatgpt-mermaid-\_r_p4\_ .image-shape{background-color:rgb(252, 252, 252);text-align:center;}#chatgpt-mermaid-\_r_p4\_ .icon-shape p,#chatgpt-mermaid-\_r_p4\_ .image-shape p{background-color:rgb(252, 252, 252);padding:2px;}#chatgpt-mermaid-\_r_p4\_ .icon-shape .label rect,#chatgpt-mermaid-\_r_p4\_ .image-shape .label rect{opacity:0.5;background-color:rgb(252, 252, 252);fill:rgb(252, 252, 252);}#chatgpt-mermaid-\_r_p4\_ .label-icon{display:inline-block;height:1em;overflow:visible;vertical-align:-0.125em;}#chatgpt-mermaid-\_r_p4\_ .node .label-icon path{fill:currentColor;stroke:revert;stroke-width:revert;}#chatgpt-mermaid-\_r_p4\_ .node .neo-node{stroke:rgb(83, 154, 248);}#chatgpt-mermaid-\_r_p4\_ [data-look="neo"].node rect,#chatgpt-mermaid-\_r_p4\_ [data-look="neo"].cluster rect,#chatgpt-mermaid-\_r_p4\_ [data-look="neo"].node polygon{stroke:url(#chatgpt-mermaid-\_r_p4\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_p4\_ [data-look="neo"].swimlane.cluster rect{filter:none;}#chatgpt-mermaid-\_r_p4\_ [data-look="neo"].node path{stroke:url(#chatgpt-mermaid-\_r_p4\_-gradient);stroke-width:1px;}#chatgpt-mermaid-\_r_p4\_ [data-look="neo"].node .outer-path{filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_p4\_ [data-look="neo"].node .neo-line path{stroke:rgb(83, 154, 248);filter:none;}#chatgpt-mermaid-\_r_p4\_ [data-look="neo"].node circle{stroke:url(#chatgpt-mermaid-\_r_p4\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_p4\_ [data-look="neo"].node circle .state-start{fill:#000000;}#chatgpt-mermaid-\_r_p4\_ [data-look="neo"].icon-shape .icon{fill:url(#chatgpt-mermaid-\_r_p4\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_p4\_ [data-look="neo"].icon-shape .icon-neo path{stroke:url(#chatgpt-mermaid-\_r_p4\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_p4\_ .node text{font-size:14px;font-weight:600;letter-spacing:normal;fill:rgb(0, 79, 153);}#chatgpt-mermaid-\_r_p4\_ .edgeLabels text{font-size:13px;font-weight:600;letter-spacing:-0.08px;fill:rgb(0, 79, 153);}#chatgpt-mermaid-\_r_p4\_ .node tspan[font-weight="normal"],#chatgpt-mermaid-\_r_p4\_ .edgeLabels tspan[font-weight="normal"]{font-weight:600;}#chatgpt-mermaid-\_r_p4\_ .edgeLabel .label rect{opacity:1;rx:13px;ry:13px;fill:rgb(245, 250, 255);stroke:rgb(206, 219, 229);stroke-width:1px;}#chatgpt-mermaid-\_r_p4\_ .node rect,#chatgpt-mermaid-\_r_p4\_ .node circle,#chatgpt-mermaid-\_r_p4\_ .node ellipse,#chatgpt-mermaid-\_r_p4\_ .node polygon,#chatgpt-mermaid-\_r_p4\_ .node path{fill:rgb(229, 243, 255);stroke:rgba(0, 0, 0, 0.1);stroke-width:1px;}#chatgpt-mermaid-\_r_p4\_ .node rect{rx:16px;ry:16px;}#chatgpt-mermaid-\_r_p4\_ .mermaid-decision .label-container{fill:rgb(245, 250, 255);stroke:rgb(206, 219, 229);stroke-dasharray:2,2;}#chatgpt-mermaid-\_r_p4\_ .edgePaths .flowchart-link{stroke:rgb(143, 143, 143);stroke-width:1px;stroke-linecap:round;stroke-linejoin:round;}#chatgpt-mermaid-\_r_p4\_ .marker{fill:rgb(143, 143, 143);stroke:rgb(143, 143, 143);}#chatgpt-mermaid-\_r_p4\_ :root{--mermaid-font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";}RM starts onboarding in AICopilotOnboarding API creates caseDatabase persists draftStartOrganizationOnboardingWorkflowParallel data enrichmentPersist data and provenanceAI prepares enrichmentsummaryRM reviews and confirmsRM approves?Revise / enrich furtherValidate against pinnedschemaCreate official SO requestPersist SO Request IDNotify organization and RMOrganization opens Next.jsportalLoad organization-specificformSave form revisions indatabaseValidate completed sectionsSubmit section / completerequestTemporal coordinates SOupdateSO emits Kafka eventKafka Consumer processeseventSignal onboarding WorkflowFurther action required?Request more informationBank review / verificationDecisionApprovedRejectedComplete onboarding andnotify partiesNoYesYesNoApprovedRejected

The important point is that the entire journey is managed by one onboarding Workflow, while the actual information is stored in your application database and Servicing Order.

The workflow can wait for the customer, wait for the RM, react to SO events, schedule reminders, execute retries and coordinate internal review processes.

# 15. Suggested API design

I would expose business-oriented APIs rather than simply proxying the SO API.

For example:

| API                                                     | Purpose                                 |
| ------------------------------------------------------- | --------------------------------------- |
| `POST /onboarding-cases`                                | Create a draft onboarding case          |
| `GET /onboarding-cases/{id}`                            | Retrieve case details                   |
| `PATCH /onboarding-cases/{id}/draft`                    | Update draft information                |
| `POST /onboarding-cases/{id}/enrichment`                | Initiate enrichment                     |
| `GET /onboarding-cases/{id}/enrichment`                 | Retrieve enrichment results             |
| `POST /onboarding-cases/{id}/enrichment/accept`         | Accept reviewed enrichment              |
| `POST /onboarding-cases/{id}/submit`                    | Submit the request for SO registration  |
| `GET /onboarding-cases/{id}/schema`                     | Retrieve the pinned organization schema |
| `PUT /onboarding-cases/{id}/sections/{section}`         | Save an entity form section             |
| `POST /onboarding-cases/{id}/sections/{section}/submit` | Submit an entity form section           |
| `POST /onboarding-cases/{id}/documents`                 | Register document uploads               |
| `GET /onboarding-cases/{id}/status`                     | Retrieve business journey status        |

All mutating operations should support idempotency and appropriate optimistic concurrency.

For the database-to-Temporal boundary, use an outbox pattern:

```
Onboarding API
     |
     v
Database Transaction
     |
     +-- Save business data
     |
     +-- Save revision
     |
     +-- Write outbox command
              |
              v
       Outbox Dispatcher
              |
              v
          Temporal
```

This prevents the classic problem of successfully saving the business data but failing to start or signal the Workflow.

The same pattern should be applied to SO Kafka event processing.

# 16. What I would build first

I would avoid building every organization type and every external connector immediately.

Instead, deliver this in stages.

| Phase                            | What to build                                                           | Outcome                                     |
| -------------------------------- | ----------------------------------------------------------------------- | ------------------------------------------- |
| 1. Architecture foundation       | Onboarding API, database, Temporal, Workflow framework, SO Adapter      | Reliable orchestration foundation           |
| 2. Schema framework              | Schema Registry integration, versioning, frontend/backend validation    | Consistent organization-specific validation |
| 3. RM Copilot                    | Conversational intake, enrichment, review and approval                  | RM onboarding experience                    |
| 4. SO integration                | Create/update/status APIs, Kafka Consumer, inbox/outbox, reconciliation | Reliable official request management        |
| 5. Entity portal                 | Next.js forms, autosave, revisions, documents and submissions           | Customer onboarding experience              |
| 6. Lifecycle automation          | Notifications, reminders, escalations, bank review                      | End-to-end automation                       |
| 7. Additional organization types | Trusts, government bodies, partnerships, charities, etc.                | Extensible onboarding platform              |

For the first pilot, I would select Company onboarding because it provides a useful opportunity to test identifiers, registry enrichment, organization relationships, dynamic schemas and customer-submitted data.

I would start with ABR as an enrichment source, subject to obtaining the required service access, and add other registries as their availability and permissions are confirmed.

# 17. Final architectural recommendations

Here is my consolidated recommendation.

## Recommended architectural decisions

Workflow

One per case

One long-running `OrganizationOnboardingWorkflow` identified by the internal onboarding case ID.

Business data

Database + SO

Application DB for drafts and working data; SO for the official registered request and status.

Temporal state

Minimal state

Store identifiers, process stage and revision references, not complete organization forms or documents.

API architecture

Bank API intermediary

Copilot and Next.js never call SO directly.

Kafka integration

Consumer + Signals

Separate consumer, durable inbox/outbox and Temporal signaling.

Schema validation

Version pinned

Canonical versioned schemas with consistent frontend and backend validation.

AI enrichment

Activities

Reusable connectors, provenance, confidence, reconciliation and human approval.

Reliability

Idempotent

Outbox/inbox, API idempotency, event deduplication, retries and reconciliation.

## 18. Five decisions I would resolve before implementation

Although the overall architecture can be established now, these five questions have the most influence on the detailed design.

| Priority | Decision                                                                | Why it matters                                                                                      |
| -------- | ----------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| 1        | Does SO support creating incomplete Draft requests?                     | Determines when the official request is created and where pre-submission data lives                 |
| 2        | Does SO support external references, idempotency and versioned updates? | Determines whether reliable distributed synchronization is possible                                 |
| 3        | What is the SO Kafka event contract?                                    | Determines correlation, deduplication, event ordering and reconciliation                            |
| 4        | What JSON Schema dialect and versioning capabilities does SO support?   | Determines schema compatibility across frontend, backend and SO                                     |
| 5        | Does SO support partial entity submissions and section-level updates?   | Determines whether entity data must be staged in your database or can be synchronized incrementally |

I would specifically request the SO vendor's API specifications, Kafka event examples, schema registry documentation and lifecycle/status transition documentation before finalizing the integration contracts.

## My overall architectural position

There are three particularly important decisions I would not compromise on:

1\. Temporal is the process orchestration engine, not your application's database.

Use it to coordinate long-running onboarding journeys, external services, human decisions, timers, retries, event processing and notifications. Keep the organization data in durable application storage and SO.

2\. Your bank owns the onboarding experience and integration boundary.

The Copilot, Next.js portal, schema validation, enrichment and business rules should be independent of the third-party SO implementation. The SO Adapter should be the only application component responsible for communicating with SO.

3\. Treat the onboarding request as a long-running business entity.

One request, one main Workflow, a stable identity, controlled state transitions and explicit communication through Signals and Updates. Split out independent subprocesses only when there is a genuine lifecycle or scaling reason.

This architecture should give you a strong foundation for an AI-driven organization onboarding platform without coupling the bank's business processes too tightly to either Temporal or the third-party Servicing Order system.

### Useful technical references

These are the primary references I would use when implementing this architecture:

- [Temporal Entity Workflow Pattern](https://docs.temporal.io/design-patterns/entity-workflow?utm_source=chatgpt.com) — one Workflow per business entity.
- [Temporal Signals, Queries and Updates](https://docs.temporal.io/encyclopedia/workflow-message-passing?utm_source=chatgpt.com) — Workflow communication.
- [Temporal Worker and Event History Best Practices](https://docs.temporal.io/best-practices/worker?utm_source=chatgpt.com) — payload sizing and history management.
- [Temporal Child Workflows](https://docs.temporal.io/child-workflows?utm_source=chatgpt.com) — when to use independent subprocesses.
- [JSON Schema Specification](https://json-schema.org/specification?utm_source=chatgpt.com) — schema dialect and validation.
- [ABN Lookup Web Services](https://abr.business.gov.au/Tools/WebServices?utm_source=chatgpt.com) — Australian entity enrichment.
- [ASIC API documentation](https://www.asic.gov.au/online-services/information-for-intermediaries/application-programming-interfaces-apis?utm_source=chatgpt.com) — Australian company registry integration.

One particularly valuable next architectural exercise would be to turn this into a detailed technical design package: component responsibilities, database ERD, Temporal Workflow/Activity contracts, Kafka event contracts, SO API adapter contracts, schema-versioning strategy and sequence diagrams for the RM, entity and SO journeys. That would give your engineering team an implementation-ready blueprint rather than just a conceptual architecture.