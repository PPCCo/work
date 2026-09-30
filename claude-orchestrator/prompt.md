I have a `.claude/` folder with AI skills, agents, workflows, standards, scripts, rules, etc. I want to use ClaudeCode do full stack development in an automated and autonomous fashion.

The app that I'm working on is an existing app, that currently has NestJS Rest API, NextJS Frontend App, and Temporal workflow, all having separate existing repositories. JSON Schema is the source of truth that is used for backend API validation, as well as zod schema and Typescript types for frontend validation.

So I have three internal team projects (NextJS Frontend, NestJS API, and Temporal workflows) that are three separate github projects themselves. And I have a fourth project with claude folder with AI skills, agents, workflows, standards, scripts, rules, etc.

I want to use the project with `.claude/` folder as my main AI-tooling and AI development orchestrator repository named `claude-orchestrator`. I want to keep the three code repositories entirely separate and completely flat on my local drive, then map them using Symbolic Links (Symlinks).

This way all three can be independently maintained while the main repo works as AI development orchestrator. My app's backend is a orchestrator (Temporal workflows) that listens to Kafka topics, and based on the event+payload, the different workflow activities and uses postgresql to save data, and S3 buckets to store files, JSON Schema, etc. The Temporal workflow will also use the JSON Schema to call the IPO/ASIC API to fetch prospective organizations' data, and will also interact with a internal agentic/RAG agent that will fetch data from public websites. My team also uses other tools including pnpm, Turborepo, Docker, GithubActions, husky, prettier, etc.

dev-workspace/
|-- claude-orchestrator/ (My Git repo with `.claude/` skills)
| |-- .claude
| | |-- agents/
| | |-- rules/
| | |-- scripts/
| | |-- skills/
| | |-- standards/
| | |-- workspace.yaml
| |-- nextjs-frontend (Symlink to folder below)
| |-- nestjs-api (Symlink to folder below)
| |-- temporal-worker (Symlink to folder below)
|-- nextjs-frontend/ (Independent Git Repo)
|-- nestjs-api/ (Independent Git Repo)
|-- temporal-worker/ (Independent Git Repo)

I expect my `claude-orchestrator` orchestrator repository to look something like this

```text
claude-orchestrator/
|-- CLAUDE.md
|-- workspace.yaml
|
|-- .claude/
|   |-- agents/
|   |   |-- architect.md
|   |   |-- frontend-engineer.md
|   |   |-- api-engineer.md
|   |   |-- temporal-engineer.md    TODO
|   |   |-- contract-engineer.md    TODO
|   |   |-- reviewer.md           TODO
|   |   |-- test-engineer.md
|   |
|   |-- skills/
|   |   |-- understand-feature/
|   |   |-- plan-feature/
|   |   |-- implement-frontend/
|   |   |-- implement-api/    TODO
|   |   |-- implement-workflow/    TODO
|   |   |-- modify-json-schema/    TODO
|   |   |-- generate-contracts/
|   |   |-- validate-contracts/
|   |   |-- run-tests/
|   |   |-- review-changes/
|   |   |-- create-commits/
|   |   |-- prepare-pr/
|   |
|   |-- rules/
|   |   |-- architecture.md
|   |   |-- frontend.md
|   |   |-- nestjs.md    TODO
|   |   |-- temporal.md    TODO
|   |   |-- kafka.md    TODO
|   |   |-- postgres.md
|   |   |-- json-schema.md
|   |   |-- testing.md
|   |   |-- git.md    TODO
|   |
|   |-- workflows/
|   |   |-- feature.md
|   |   |-- bugfix.md
|   |   |-- schema-change.md    TODO
|   |   |-- refactor.md
```

# TASK

I have most of the `.claude/` files already created. I want you to think hard, and in the context of my symlink setup and the three repositories I mentioned (NextJS Frontend, NestJS API, and Temporal workflows), and create the files marked as `TODO`. Also think of any gaps or any files that I have missed, and generate a comprehensive (but concise) framework that would help me buid high quality, enterprise grade, fully tested applications comprising of the tools and technologies including Temporal workflows, Kafka topics, NextJS, NestJS, JSON Schema, zod, Postgresql, S3 buckets, agentic/RAG agent, pnpm, Turborepo, Docker, GithubActions, husky, prettier, etc.

package all files as a single zip file.

---

# RESPONSE

Tooling is ready (jq and yq fetched for testing the scripts), so I'm now writing the agent files, then skills, rules, workflows, standards and scripts before zipping.The `cd` failed (the shell doesn't expand braces), so the six agent files landed in `/`. I'll fix the directory layout and move them into place.Layout is fixed. Now the rules.Now the skills.Now workflows and standards.Scripts next, along with the workspace schema they read. I'll test them against a simulated `dev-workspace`.I'll test the scripts in a simulated `dev-workspace`.Every script behaves as intended. Now the README and merge guide, then I'll package the zip.The zip has your `TODO` files plus gap-fillers, all designed for the symlink setup. I tested the scripts and the guard hook in a simulated `dev-workspace`. I haven't run any of it against your real repos, and the agent, skill and rule files themselves are untested.

**Your TODOs, now done**

- **Agents:** `temporal-engineer`, `contract-engineer`, `reviewer`
- **Skills:** `implement-api`, `implement-workflow`, `modify-json-schema`
- **Rules:** `nestjs`, `temporal`, `kafka`, `git`
- **Workflow:** `schema-change`, as an expand/migrate/contract rollout rather than a simple edit

**Gaps I filled**

- **Ownership of shared things:** `data-engineer` owns the Postgres schema, since two services write to it. `devops-engineer` owns CI, Docker, husky and Turborepo. `security-reviewer` covers the regulated-data and untrusted-RAG concerns.
- **Skills for repeatable jobs:** `kafka-event`, `db-migration`, `diagnose-failure`, `workspace-sync`.
- **Rules:**
  - `s3`, `security` and `observability` (one correlation ID from HTTP through Kafka to Temporal).
  - `integrations` (ASIC/IPO API and the RAG agent: validate responses, keep provenance, route low-confidence results to a human).
  - `devops` and `typescript`.
- **Workflows:** `kafka-event-change`, `db-migration`, and `release` (readers deploy before writers: migration, then worker, then API, then frontend).
- **Standards:**
  - `definition-of-done`, with an evidence block for PRs.
  - `agent-operating-protocol`: risk tiers 0–3, stop conditions, and a handoff format.
  - `event-catalog` and `adr-template`.
- **Guardrails for autonomous runs:**
  - `scripts/verify.sh` runs each repo's gates and reports only failures.
  - `workspace-status.sh` and `link-repos.sh` manage the symlinks and `.gitignore`.
  - A hook in `settings.recommended.json` blocks force-push, `--no-verify`, `.env` access and hand-edits to lockfiles and generated files.

**Needs a few minutes from you**

- **Merge by hand:** `FRAMEWORK-README.md` has the install steps, a `CLAUDE.md` routing block, and notes on merging `workspace.recommended.yaml` and `settings.recommended.json` into yours. I didn't overwrite any existing file.
- **Assumptions to confirm:**
  - The worker uses the Temporal TypeScript SDK.
  - Kafka consumers run in `temporal-worker` and the API produces with an outbox.
  - I don't know where your schemas live or which Postgres migration tool you use.
  - The gate commands in `workspace.recommended.yaml` (like `pnpm test:replay` and `pnpm contracts:check`) are placeholders until they match your `package.json` scripts. An undefined gate shows as `SKIP`, never as pass.
- **Dependencies:** the scripts and hook need `yq` and `jq` (`brew install yq jq`).
- **Symlinks:** Claude Code's search may not follow them, so the framework tells agents to search and edit through the real sibling paths (`../nestjs-api` etc.). I couldn't confirm this against Claude Code itself; `additionalDirectories` and `--add-dir` are there as the fallback.

Files are in the zip:

- `claude-orchestrator-framework.zip`
