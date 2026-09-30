# Framework add-on for `claude-orchestrator`

Fills the `TODO` files from your layout and adds the pieces that were missing for enterprise-grade, autonomous, multi-repo work across `nextjs-frontend`, `nestjs-api` and `temporal-worker`.

## 1. Install

```bash
cd dev-workspace/claude-orchestrator
unzip -n ../claude-orchestrator-framework.zip -d ..    # -n = never overwrite an existing file
brew install yq jq                                     # used by scripts and the guard hook
.claude/scripts/link-repos.sh                          # creates symlinks, updates .gitignore
.claude/scripts/workspace-status.sh
```

Then do the three merges in section 3. Everything else is new files and will not collide with yours unless a name matches (the `-n` flag protects you; diff any file it skipped).

## 2. What is in the box

**Your TODOs (now done)**
| Type | Files |
|---|---|
| Agents | `temporal-engineer`, `contract-engineer`, `reviewer` |
| Skills | `implement-api`, `implement-workflow`, `modify-json-schema` |
| Rules | `nestjs`, `temporal`, `kafka`, `git` |
| Workflow | `schema-change` |

**Gaps I filled**
| Gap | Added | Why it matters here |
|---|---|---|
| Two services write one database | `data-engineer` agent, `db-migration` skill, `workflows/db-migration.md` | API and worker deploy independently, so every change must be expand/contract; one owner avoids conflicting migrations |
| Kafka was a rule but no procedure | `kafka-event` skill, `workflows/kafka-event-change.md`, `standards/event-catalog.md` | Topics are contracts; a catalog plus consumer-first rollout prevents silent breakage |
| CI, Docker, husky, Turborepo had no owner | `devops-engineer` agent, `rules/devops.md` | Pipelines and hooks fail in agent loops more than anything else |
| Regulated data and untrusted RAG output | `security-reviewer` agent, `rules/security.md`, `rules/integrations.md` | ASIC/IPO data and web-scraped content need validation, provenance and human-review paths |
| S3 had no rules | `rules/s3.md` | Immutable versioned schemas, claim-check payloads, presigned URLs |
| Tracing one request across HTTP, Kafka, Temporal | `rules/observability.md` | Correlation ID propagation end to end |
| Shared TS standards | `rules/typescript.md` | One bar for all three repos |
| Cross-repo release order | `workflows/release.md` | Reader-before-writer deploy order, rollback rules |
| "Done" was undefined | `standards/definition-of-done.md` | Evidence-based completion and PR evidence block |
| Autonomy had no guardrails | `standards/agent-operating-protocol.md` | Risk tiers, stop conditions, handoff format, prohibitions |
| Decisions unrecorded | `standards/adr-template.md` | Tier 2+ decisions are reviewable later |
| Debugging was ad hoc | `diagnose-failure` skill | Root cause before fix; three-strikes escalation |
| Multi-repo hygiene | `workspace-sync` skill + `scripts/` | Clean-tree check, consistent branch names, baseline gates |
| Safety net for autonomous runs | `scripts/hooks/guard.sh`, `settings.recommended.json`, `protected-paths.txt` | Mechanically blocks force-push, `--no-verify`, `.env` access, lockfile and generated-file edits |

## 3. Merge steps (do by hand)

**a) `workspace.yaml`**: copy the keys from `.claude/workspace.recommended.yaml` into your existing file (root or `.claude/`). The scripts read `repos.*.path|link|gates`, `gate_order`, and the `contracts`, `database`, `kafka` blocks. Fill in `contracts.schema_dir` and `database.migration_tool`, and match each `gates.*` command to your real `package.json` scripts.

**b) `.claude/settings.json`**: merge `settings.recommended.json` into it (or rename it if you have none). It adds `additionalDirectories` for the three repos, a conservative allow/deny list, and the guard hook. Review `deny` (it blocks `curl`/`wget`; remove if agents need them).

**c) `CLAUDE.md`**: append the block below.

```markdown
## Workspace
Orchestrator repo with three independent code repos symlinked in: `nextjs-frontend`, `nestjs-api`, `temporal-worker`.
Paths are defined in `workspace.yaml`. **Search and edit using the real sibling paths (`../<repo>`)**; search tools may not traverse symlinks. Commit inside the repo that owns the file (`git -C ../<repo> ...`), never in the orchestrator.
JSON Schema is the source of truth; never hand-edit generated zod/types.

## How to work
Follow `.claude/standards/agent-operating-protocol.md` (risk tiers, stop conditions, handoff block) and `.claude/standards/definition-of-done.md`.
Start every task with the `workspace-sync` skill. Verify with `.claude/scripts/verify.sh <repo|all>`; do not trust "tests pass" without running it.

## Routing
| Task | Lead agent | Skills | Read |
|---|---|---|---|
| New/changed schema, payload | contract-engineer | modify-json-schema, generate-contracts, validate-contracts | json-schema, kafka |
| REST endpoint / API logic | api-engineer | implement-api | nestjs, security, postgres |
| Workflow / consumer / integration | temporal-engineer | implement-workflow, kafka-event | temporal, kafka, integrations |
| DB or S3 layout change | data-engineer | db-migration | postgres, s3 |
| UI | frontend-engineer | implement-frontend | frontend |
| CI, Docker, hooks, deps | devops-engineer | - | devops, git |
| Failing test/build/run | (any) | diagnose-failure | - |
| Review before PR | reviewer (+ security-reviewer for Tier 2+) | review-changes | definition-of-done |
| Multi-repo rollout | architect | plan-feature | workflows/release, schema-change |
```

## 4. Assumptions to verify (edit the files if wrong)

1. **Temporal TypeScript SDK** in `temporal-worker`. If not, keep the principles in `rules/temporal.md` and adapt API names.
2. **Kafka consumers run in `temporal-worker`**; the API produces (with an outbox). If consumers also live in NestJS, update `kafka.consumers_in` and `rules/nestjs.md`.
3. **Where schemas live** (`contracts.schema_dir`) and that CI publishes versioned schemas to S3. The framework says agents must not publish by hand.
4. **Migration tool and owner** are unspecified (`database.*`). Fill in; `data-engineer` relies on them.
5. **Gate commands** (`pnpm lint`, `pnpm test:replay`, `pnpm contracts:check`, ...) are placeholders until they match your scripts. A gate that is undefined is reported as `SKIP`, not silently passed.
6. Some rules are opinionated defaults (RFC 9457 errors, UUID v7, `Idempotency-Key`, `.dlq` topics). Change them to your house style once; agents follow what is written.

## 5. Symlink notes

- Keep `path:` in `workspace.yaml` pointing at the real repo; use symlinks for human convenience.
- The symlinks are git-ignored by `link-repos.sh`; never commit them.
- If Claude Code asks permission for files outside the orchestrator, that is what `additionalDirectories` is for; alternatively launch with `claude --add-dir ../nestjs-api --add-dir ../nextjs-frontend --add-dir ../temporal-worker`.
- Each code repo may keep its own short `CLAUDE.md` for repo-local commands; the orchestrator's rules hold the cross-repo standards.
- Rules are referenced explicitly by agents and skills on purpose (not path-scoped), because path-matching through symlinks is unreliable. If your Claude Code version auto-loads everything in `.claude/rules/`, expect all rule files in context each session; if that is too heavy, move rarely needed ones (`s3`, `integrations`, `devops`) under `standards/` and keep the references.

## 6. Suggested next steps

1. Run `workspace-sync` on a throwaway task and confirm the status table is right.
2. Run a Tier 0/1 feature end to end (`workflows/feature.md`) and tune the gate commands.
3. Try a compatible schema change with `modify-json-schema` to exercise contracts and all three repos.
4. Only then allow longer unattended runs, and review the first few PRs closely.
