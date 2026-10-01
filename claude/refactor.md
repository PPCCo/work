# A Framework for Planning a Module Refactor

The core principle: **every step should leave the system working and shippable.** If you can't stop after any step and deploy, the steps are too big.

## Stage 0: Define the goal and boundaries

Before touching code, write down:

- **Why** you're refactoring (testability, coupling, performance, readability). This tells you when you're done.
- **What stays the same**: the public behavior and contracts callers depend on.
- **What's in and out of scope**. Resist bundling feature work or bug fixes into the refactor, since they make regressions impossible to attribute.

**Test at this stage:** nothing yet, but write down the success criteria (e.g. "no public signature changes," "p95 latency unchanged").

## Stage 1: Map the module

- List the public surface: exported functions, classes, types, events, config, and any side effects (DB writes, files, network calls).
- Find all callers and dependencies (static search, dependency graphs, runtime logs/traces for dynamic usage).
- Identify hidden contracts: ordering assumptions, error types callers catch, global state, implicit timing.

**Test at this stage:** review whether existing tests cover each item you listed. Mark the gaps.

## Stage 2: Build a safety net

This is the most skipped stage and the most important one.

- Write **characterization tests** that pin down current behavior, including quirks and bugs. You're recording what it does, not what it should do.
- Cover the public surface first, then the riskiest internals.
- Add **golden/snapshot tests** for complex outputs.
- For hard-to-test code, add integration-level tests around the module's edges rather than unit tests on its guts.
- If feasible, capture real production inputs and outputs for replay.

**Test at this stage:** run the suite against the _unchanged_ code. It must be green and deterministic. Fix flakiness now, because you can't distinguish flaky failures from regressions later.

## Stage 3: Create seams

Make the code changeable without changing its behavior:

- Introduce interfaces or wrapper functions at the boundaries.
- Inject dependencies instead of reaching for globals or singletons.
- Extract pure logic away from I/O.
- Add a facade so callers depend on a stable entry point, not internals.

These changes should be mechanical and tiny.

**Test at this stage:** the full characterization suite, unchanged. Any test edits here are a red flag that you changed behavior.

## Stage 4: Sequence the changes

Order work by risk and dependency:

1. **Pure renames, moves, and dead-code removal** (lowest risk, and they clarify what's left)
2. **Extract and isolate** pure logic into new units, with unit tests for each
3. **Restructure internals** behind the stable facade
4. **Change data structures or schemas** (use expand/contract: add new alongside old, migrate, then remove old)
5. **Swap implementations** (for risky swaps, use the parallel-run or strangler pattern below)
6. **Migrate callers** to the new API incrementally
7. **Delete the old path** once nothing uses it

Rules of thumb: one kind of change per commit/PR, keep PRs reviewable, and never mix behavior changes with structural ones.

**Test at each step:**

- Characterization suite plus the new unit tests
- Type checks, linting, and build
- Contract tests on the public surface

## Stage 5: Handle risky swaps safely

For changes where tests alone don't give enough confidence:

- **Feature flag** the new implementation so rollback is a config change.
- **Parallel run / shadow mode**: run old and new side by side, return the old result, and log discrepancies.
- **Strangler pattern**: route traffic to the new path gradually (one caller, one endpoint, or a percentage at a time).
- **Expand/contract migrations** for data: write to both, backfill, verify, switch reads, then drop the old.

**Test at this stage:**

- Diff old vs. new outputs on real inputs
- Performance and load comparison against your Stage 0 criteria
- Error-path and failure-mode behavior (timeouts, partial failures, bad input)
- Rollback: actually exercise it

## Stage 6: Migrate callers and clean up

- Move callers over in small batches, with the facade or an adapter bridging old and new.
- Deprecate the old API with clear warnings and a removal date if others consume it.
- Remove adapters, flags, and old code only after the new path has run in production long enough to trust.

**Test at this stage:**

- Integration and end-to-end tests across migrated callers
- Production monitoring (error rates, latency, business metrics)
- A check that nothing still references the removed code

## Stage 7: Verify and close out

- Re-check the Stage 0 success criteria.
- Delete temporary scaffolding (characterization tests that pinned known bugs may be replaced by real expectations).
- Update docs and write down what changed and why.

## Test checklist by layer

| Layer                 | Purpose                 | When it matters most |
| --------------------- | ----------------------- | -------------------- |
| Characterization      | Detect behavior changes | Every step           |
| Unit                  | Verify extracted logic  | Stages 3-4           |
| Contract              | Protect the public API  | Stages 4-6           |
| Integration           | Verify wiring and I/O   | Stages 5-6           |
| Performance           | Catch regressions       | Stage 5              |
| Production monitoring | Catch what tests missed | Stages 5-7           |

## Common pitfalls

- Refactoring without tests, then "testing by clicking around"
- Big-bang rewrites instead of incremental steps
- Mixing bug fixes into refactor commits
- Changing tests and code in the same step, which removes your safety net
- Skipping the plan for rollback
- Deleting the old path too early

If you tell me the language, module size, and how many callers it has, I can tailor this into a concrete step list with PR-sized chunks.
