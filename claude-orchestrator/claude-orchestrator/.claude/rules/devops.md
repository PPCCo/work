# DevOps rules: pnpm, Turborepo, Docker, GitHub Actions, husky, prettier

## pnpm and Node
- Node version pinned in `.nvmrc`/`engines` and identical in CI and Docker. pnpm version pinned via `packageManager`.
- `pnpm install --frozen-lockfile` in CI and agents. Never hand-edit `pnpm-lock.yaml`; change `package.json` and run `pnpm install`.
- Dependencies: exact or caret ranges per repo policy; dev vs prod correctly separated; no unused packages. Internal scripts are run through `pnpm <script>`, not global tools.

## Turborepo
- Every task that can be cached declares `inputs` and `outputs` in `turbo.json`. Pipelines: `lint`, `typecheck`, `test`, `build`, plus `contracts:check` where present.
- CI uses `turbo run ... --filter=...[origin/main]` for affected-only runs. Env vars that change output are listed in `env`/`globalEnv` or caches lie.
- For Docker, use `turbo prune <app> --docker` to keep layers small and cache-friendly.

## Docker
- Multi-stage builds: deps, build, runtime. Runtime image is minimal, non-root, read-only filesystem where feasible, with a `HEALTHCHECK`.
- Pin base images by tag and digest. No secrets in build args or layers. `.dockerignore` excludes `.git`, `node_modules`, `.env*`.
- `docker-compose` for local dev starts PostgreSQL, Kafka-compatible broker, Temporal dev server, and an S3-compatible store with the same config keys as real environments.

## GitHub Actions
- Workflows: `ci.yml` (lint, typecheck, test, build, contracts check, audit), `docker.yml` (build and scan on merge), optional `release.yml`.
- Top-level `permissions: contents: read`, widen per job only. `concurrency` cancels superseded runs on branches. Timeouts on every job.
- Actions pinned to SHAs. Cache via `actions/setup-node` with `cache: pnpm`. Secrets only in the jobs that need them; never echo them.
- Required status check names are a contract with branch protection: renaming a job is a breaking change for humans to coordinate.
- Service containers (PostgreSQL, Kafka-compatible, S3-compatible, Temporal dev server) for integration tests; no shared environments.

## husky, lint-staged, commitlint, prettier
- `pre-commit`: lint-staged (prettier + eslint --fix on staged files). `commit-msg`: commitlint (Conventional Commits). `pre-push`: typecheck and affected tests.
- Hooks are never bypassed (`--no-verify` is forbidden, see `git.md`). A hook that is slow or flaky is a bug to fix with `devops-engineer`.
- One prettier config per repo, shared via a package if the team has one. Do not reformat files you are not otherwise changing.

## Contract drift gate
Each consuming repo has `contracts:check` in CI: regenerate from the source-of-truth schema and fail if the working tree changes.
