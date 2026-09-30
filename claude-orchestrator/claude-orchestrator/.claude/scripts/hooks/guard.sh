#!/usr/bin/env bash
# Claude Code PreToolUse hook. Reads the tool call as JSON on stdin; exit 2 blocks it and
# sends stderr back to Claude. Requires jq (fails closed if missing).
command -v jq >/dev/null 2>&1 || { echo "guard.sh: jq is required (brew install jq)" >&2; exit 2; }

input="$(cat)"
tool="$(jq -r '.tool_name // ""' <<<"$input")"
ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)}"
block() { echo "BLOCKED by workspace guard: $1" >&2; exit 2; }

case "$tool" in
  Edit|Write|MultiEdit|NotebookEdit)
    path="$(jq -r '.tool_input.file_path // .tool_input.notebook_path // ""' <<<"$input")"
    base="$(basename "$path")"
    [[ "$base" == ".env.example" ]] || { [[ "$base" == .env || "$base" == .env.* ]] && block "$path is an environment file; agents must not edit secrets."; }
    [[ "$base" == "pnpm-lock.yaml" ]] && block "never hand-edit pnpm-lock.yaml; change package.json and run pnpm install."
    [[ "$base" == *.pem || "$base" == *.key ]] && block "$path looks like key material."
    if [[ -f "$ROOT/.claude/protected-paths.txt" ]]; then
      while IFS= read -r glob; do
        [[ -z "$glob" || "$glob" == \#* ]] && continue
        # shellcheck disable=SC2053
        [[ "$path" == $glob ]] && block "$path matches protected pattern '$glob' (generated or protected). Regenerate via the owning skill."
      done < "$ROOT/.claude/protected-paths.txt"
    fi
    ;;
  Bash)
    cmd="$(jq -r '.tool_input.command // ""' <<<"$input")"
    shopt -s nocasematch
    [[ "$cmd" =~ git[[:space:]]+push.*(--force|--force-with-lease|[[:space:]]-f([[:space:]]|$)) ]] && block "force-push is not allowed."
    [[ "$cmd" =~ git[[:space:]]+push[[:space:]]+[^\;\&\|]*[[:space:]](main|master|develop)([[:space:]]|$) ]] && block "direct push to a protected branch; push a task branch and open a PR."
    [[ "$cmd" =~ --no-verify|--no-gpg-sign ]] && block "bypassing hooks or signing is not allowed; fix the cause."
    [[ "$cmd" =~ git[[:space:]]+(reset[[:space:]]+--hard|clean[[:space:]]+-[a-z]*f|checkout[[:space:]]+--[[:space:]]+\.) ]] && block "destructive git command could discard the human's work."
    [[ "$cmd" =~ (cat|less|more|head|tail|grep|source|printenv|env)[^\;\&\|]*\.env([[:space:]]|$|\.) && ! "$cmd" =~ \.env\.example ]] && block "reading environment files is not allowed."
    [[ "$cmd" =~ (drop[[:space:]]+(database|table|schema)|truncate[[:space:]]+table) ]] && block "destructive SQL needs a human (Tier 3)."
    [[ "$cmd" =~ rm[[:space:]]+-[a-z]*r[a-z]*f?[[:space:]]+(/|~|\$HOME|\.\.)([[:space:]]|$) ]] && block "unsafe recursive delete."
    [[ "$cmd" =~ (terraform|tofu|pulumi)[[:space:]]+(apply|destroy|up) || "$cmd" =~ kubectl[[:space:]]+(apply|delete) ]] && block "infrastructure changes are Tier 3: prepare a proposal for a human."
    ;;
esac
exit 0
