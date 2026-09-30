# Definition of done

A change is done only when every applicable box is true **and** the evidence is in the handoff or PR description. "Should work" is not evidence.

## All repos
- [ ] Gates pass via `.claude/scripts/verify.sh <repo>`: install (frozen lockfile), format check, lint, typecheck, unit tests, build.
- [ ] New behaviour has tests that fail without the change. Error paths and edge cases covered. No skipped, weakened or deleted tests.
- [ ] No `any`, suppressions or disabled lint rules without a reason (`rules/typescript.md`).
- [ ] No secrets, PII in logs, debug code, or unrelated edits (`rules/security.md`).
- [ ] Generated files are current and untouched by hand; `validate-contracts` passes.
- [ ] Conventional commits, branch name per `rules/git.md`, hooks not bypassed.
- [ ] Docs updated where behaviour, config, topics, or runbooks changed.

## nextjs-frontend
- [ ] Forms and responses validated with generated zod; loading, empty, error states handled.
- [ ] Accessibility checks pass; component and e2e tests for the changed user flow.

## nestjs-api
- [ ] Guard and ownership check on every route; problem+json errors; idempotency where required.
- [ ] Integration tests against real PostgreSQL; contract tests per endpoint; health/readiness updated.

## temporal-worker
- [ ] Workflow code deterministic; activities idempotent with timeouts and retry policy.
- [ ] Workflow, activity and replay tests pass; versioning handled for changed workflows.
- [ ] Consumers: duplicate, malformed (DLQ) and crash-before-commit tests.

## Cross-cutting
- [ ] Compatibility class stated; deploy order stated (`workflows/release.md`).
- [ ] Observability: correlation ID, logs, metrics or alerts for new failure modes.
- [ ] `reviewer` verdict APPROVE (and `security-reviewer` for Tier 2+).

## Evidence block (paste into PR)
```
Repo: <name>  Branch: <branch>
verify.sh: lint PASS | typecheck PASS | test PASS (N tests) | build PASS
Contract check: PASS   Replay tests: PASS / n/a
Migration: <file> stage <expand|migrate|contract> / n/a
Known gaps: <none or list>
```
