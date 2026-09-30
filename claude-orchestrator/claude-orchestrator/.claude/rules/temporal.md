# Temporal rules (`temporal-worker`)

Assumes the TypeScript SDK. If the worker uses another SDK, keep the principles and adapt the APIs.

## Workflow code is deterministic
- No I/O, network, DB, S3, file, env, or random access inside workflow code. All of that belongs in activities.
- No `Date.now()`, `Math.random()`, or iteration-order-dependent logic on unordered data. Use `workflow.sleep`, `workflow.uuid4()` and Temporal time.
- Workflow files import only from `@temporalio/workflow`, pure helpers, and type-only imports. Activity implementations are never imported into workflow code.
- Keep workflows thin: orchestration, branching, signals, timers. Logic that needs libraries or I/O is an activity.

## Activities
- Idempotent by construction: derive an idempotency key from `workflowId + activity name + business key`, and use upserts (`ON CONFLICT`) or conditional writes.
- Always set `startToClose`. Add `heartbeatTimeout` and heartbeat for anything over ~30 seconds.
- Retry policy is explicit: backoff, max attempts where appropriate, and a list of `nonRetryableErrorTypes`. Validation and "not found in registry" errors are non-retryable (`ApplicationFailure.nonRetryable`). Network, 429 and 5xx are retryable.
- Return small results. Anything large goes to S3 and the activity returns a reference (claim-check pattern). Keep payloads well under the 2 MB limit.
- Activities translate third-party errors into typed application failures. Never leak raw vendor errors into workflow state.

## Workflow design
- Workflow ID is a business key (for example `org-onboarding:<eventId>`). Choose a `WorkflowIdReusePolicy` deliberately.
- Long-running or looping workflows call `continueAsNew` before history approaches the limits (50K events). Use `workflowInfo().continueAsNewSuggested`.
- Use signals for fire-and-forget input, queries for read-only state, updates for validated request/response.
- Compensation (saga) steps are explicit activities, registered as you go and run on failure. Compensations are idempotent too.
- Fan-out with bounded concurrency; never unbounded `Promise.all` over user-sized lists.
- Child workflows for independently retryable or long units; set the parent close policy on purpose.

## Versioning (never break in-flight executions)
Any change to workflow code that alters command order, adds or removes activities, changes timers, or renames activity types must be protected:
1. Wrap in `patched('<id>')`; later `deprecatePatch('<id>')`, then remove once no old executions remain. Or introduce a new workflow type and route new starts to it.
2. Add or refresh a replay test using exported histories of real executions.
3. Note the change in the PR under "Workflow versioning".
Renaming a workflow or activity type, or changing signal/query names or argument shapes, is a breaking change.

## Kafka to Temporal
See `kafka.md`. Consumers only validate, map and start workflows; they contain no business logic.

## Observability
Propagate correlation ID via Temporal headers/interceptors. Set search attributes for business keys so operators can find executions. Log through the workflow logger inside workflows.

## Testing
- Workflow logic: `TestWorkflowEnvironment` (time-skipping) with activities mocked.
- Activities: `MockActivityEnvironment`, real PostgreSQL and S3-compatible containers for integration.
- Replay: `Worker.runReplayHistories` over `test/histories/*.json` in CI.
- Every non-retryable and compensation path has a test. Test retries by making the mock fail N times.
