Our Bank is building an entity onboarding application, where entities are different types of organizations (Company, Trust, Government Org, etc) who submit onboarding requests. Each organization type has different data requirements so we use JSON Schema validation for each orgType, which will be used by both the frontend and the backend to validate the data submitted by the entity.

We are using a third party Servicing Order (SO) System (with an API and database) that maintains all the requests and the status changes. Only the Rest API is exposed to us. We will need to call the API to change the request status, and add in more data provided by different sources or the RM or the customer. The Servicing Order will create a Kafka event every time a record is created or updated. The temporal worker would listen to that Kafka topic and for example send notification to RM and entity, etc. Servicing Order also has a schema registry where we can add orgType specific JSON Schema that will then be used to validate the submitted data.

The journey starts when Bank's Relationship Manager (RM) submits a Servicing Order Request through a AI-driven (co-pilot) chat-like interface, where RM provides initial data for the org that needs to be onboarded, like the Org Name, Org Type, ABN/ACN number, the AI Agent will fetch additional data from different sources, like fetch the data from IPO API, organization website, and other public whitelisted sources. The more data we collect from publicly available sources the better, as it provides convenience to the organizations by prepopulation a lot of data when they are asked to fill in and submit the form.

We want to use Temporal workflows for orchestrating, but we are new to Temporal, and not sure what would be the best design for what we are trying to build, for example whether to have one workflow per request, or have different ones for different things. Also, I'm thinking, maybe we should keep the data in Temporal which RM is using copilot, and data is being enriched from the different sources (IPO, website, etc) and only POST to Servicing Order when RM is ready to submit. The alternative would be to submit the the data directly to Servicing Order and update the data and status there. Not sure what would be better and why.

There are some other design decisions that I am not sure of:

- When the RM is ready to submit the request via co-pilot, should our app have its own API as intermediary that calls the ServicingOrder API to update the data or should co-pilot directly post the data to ServicingOrder API
- When the entity fills in NextJS frontend should the transient data be stored in the durable request specific workflow or updated directly in Servicing order, or both?

## TASK

Act as a System Architect and Temporal Expert and suggest what would be a good design and reasons for your decisions? Also create a high level system design and diagram(s) that explains the system.

Also do ambiguity and gap analysis and fill in any info that I may have missed, or any gaps or ambiguities, and give best recommendations.

---

There will be one long-running Temporal workflow per onboarding case, with activities and child workflows for specific work such as data enrichment, document collection, validation and notifications.

Documents will be stored in Documentum. The OrgType specific JSON Schema will specify which documents are required. The Temporal workflow will maintain which documents have been submitted, along with their status (eg submitted, in-review, approved, rejected, etc) and the link to specific documentum location where they are stored. The case handler can request additional documents for a specific case, which will be tracked in the same manner by the workflow.

Redis cache will be used to latency reduction and performance.

The request form will have multiple steps/pages. Each step will have soft validation. The final submission will have hard validation and would fail to submit the request if validation fails