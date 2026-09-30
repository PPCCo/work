---
name: diagnose-failure
description: Systematically diagnose a failing test, build, CI job, Temporal workflow execution, Kafka consumer, or runtime error across the three repos, finding the root cause before changing code. Use whenever something is red, flaky, stuck, retrying, or "not working", or when the same fix has failed twice.
---

# Diagnose failure

Root cause first, fix second. Never make a failure disappear by skipping, loosening or retrying it.

## Procedure
1. **Reproduce** with the smallest command: `.claude/scripts/verify.sh <repo> <gate>` or the single failing test. Capture the exact error and the first failing line (not the last).
2. **Locate the layer** and follow the matching path:
   - *Type/lint/build*: read the first error; check for contract drift (`validate-contracts`), stale generated files, Node/pnpm version mismatch, lockfile changes.
   - *Unit/integration test*: is the test wrong or the code? Check recent diff (`git -C <repo> log -p -n 5 -- <file>`); check test isolation and time/randomness; check container services are up.
   - *CI only*: compare the CI environment with local (Node version, env vars, service containers, cache, filter). Reproduce with the same command CI runs.
   - *Temporal*: look for non-determinism errors (replay a history), activity timeout vs retry policy, non-retryable classification, payload size, workflow ID collisions, worker not on the expected task queue or build.
   - *Kafka*: consumer lag, rebalances, poison message in DLQ, schema validation failure, offset committed before handoff, duplicate delivery.
   - *DB*: migration applied? lock contention, constraint violation, missing index, pool exhaustion.
3. **Form one hypothesis**, predict what you would see if it is true, and check it with a read-only probe or a log. Do not change code to "see what happens".
4. **Fix the cause**, add a test that fails before and passes after, then run the full relevant gate.
5. **Escalate** after three failed hypotheses on the same problem: stop, and write a diagnosis note (symptom, evidence, hypotheses tried, what is ruled out, suggested next probe) for a human.

## Flaky tests
Do not retry-until-green. Find the shared state, ordering, clock or network dependency and remove it; if not fixable now, quarantine with a ticket and a reason, never silently.

## Output
Root cause in one sentence, evidence, the fix, the regression test, and the gate output.
