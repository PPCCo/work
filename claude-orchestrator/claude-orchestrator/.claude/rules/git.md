# Git rules (multi-repo)

The workspace has four git repos: `claude-orchestrator` and three code repos. They share nothing in git; the symlinks are local only.

## Golden rules
1. Commit in the repo that owns the file. Code changes are committed in the code repo, never in the orchestrator. Use `git -C <real-repo-path> ...` so you are always certain which repo you are in.
2. The orchestrator ignores the symlinks (`.gitignore`). Never add a symlinked repo to the orchestrator index.
3. Never force-push, rewrite published history, or push to `main`/`master`/`develop`. Never use `--no-verify` or disable husky hooks; if a hook fails, fix the cause.
4. Start from a clean tree (`.claude/scripts/workspace-status.sh`). Do not stash or discard the human's uncommitted work; stop and ask.

## Branches
One branch name per task, identical in every repo touched: `<type>/<ticket>-<short-slug>` with type in `feat|fix|refactor|chore|docs|test|perf`. Example: `feat/ONB-142-asic-lookup`.

## Commits
- Conventional Commits: `type(scope): imperative summary` (<= 72 chars), body explains why. Scope is the module or area.
- Small, atomic, each one building and passing tests. Separate commits for: contract change, migration, implementation, tests, docs.
- Generated files are committed in the same commit as the schema change that produced them.
- Breaking change: `!` after scope and a `BREAKING CHANGE:` footer.
- Never commit secrets, `.env`, build output, or local files.

## Pull requests
- One PR per repo, all linked to each other and to the ticket, with the same title prefix.
- Description template: Summary, Why, Changes, Contract impact, DB/migration impact, Workflow versioning, Test evidence (commands and results), Rollout order, Rollback.
- State the merge/deploy order at the top when more than one PR is involved (see `workflows/release.md`). Draft until every gate is green.
- Do not merge; a human merges.

## Conflicts
Rebase the task branch on the latest base before opening the PR. Resolve conflicts preserving both sides' intent; re-run gates afterwards. If a conflict is in a generated file, regenerate instead of merging by hand.
