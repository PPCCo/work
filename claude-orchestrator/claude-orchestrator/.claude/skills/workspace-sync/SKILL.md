---
name: workspace-sync
description: Check and prepare the multi-repo workspace - verify symlinks, git status and branches of nextjs-frontend, nestjs-api and temporal-worker, install dependencies, and create a consistent task branch in each repo. Use at the start of any task, before any implementation, when paths look wrong, when a repo seems missing, or when the user says "set up", "sync", "start a new task" or "check the workspace".
---

# Workspace sync

Uses `.claude/scripts/link-repos.sh`, `workspace-status.sh` and `verify.sh`; repo paths come from `workspace.yaml`.

## Procedure
1. `.claude/scripts/workspace-status.sh` shows, per repo: real path, symlink OK/broken, current branch, clean/dirty, ahead/behind upstream.
2. If a symlink is missing or broken: `.claude/scripts/link-repos.sh` (idempotent; it also keeps `.gitignore` correct in the orchestrator).
3. **Dirty tree in any repo**: stop and report. Do not stash, reset or discard the human's work.
4. Fetch and fast-forward the base branch only if the tree is clean; otherwise report the drift.
5. For a new task, create `<type>/<ticket>-<slug>` in **each repo that the plan touches** (same name everywhere, see `rules/git.md`).
6. Install dependencies with `pnpm install --frozen-lockfile` in repos that need it.
7. Run the baseline: `.claude/scripts/verify.sh <repo> baseline` (or the fast gates) so pre-existing failures are recorded and not blamed on the task.

## Output
A status table plus any blockers (dirty repo, failing baseline, missing branch) stated plainly.

## Notes
Search tools may not follow symlinks; use the real sibling paths printed by the status script for grep/glob, and the symlink paths only for convenience.
