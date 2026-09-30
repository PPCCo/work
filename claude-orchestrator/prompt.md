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
