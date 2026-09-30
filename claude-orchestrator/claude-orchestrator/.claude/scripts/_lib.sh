#!/usr/bin/env bash
# Shared helpers. Requires: yq (mikefarah v4), git.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CFG=""
for c in "$ROOT/workspace.yaml" "$ROOT/.claude/workspace.yaml"; do
  if [[ -f "$c" ]] && yq -e '.repos' "$c" >/dev/null 2>&1; then CFG="$c"; break; fi
done
need() { command -v "$1" >/dev/null 2>&1 || { echo "missing dependency: $1 (brew install $1)" >&2; exit 2; }; }
need yq; need git
[[ -n "$CFG" ]] || { echo "no workspace.yaml with a 'repos:' section found (see .claude/workspace.recommended.yaml)" >&2; exit 2; }

repo_names() { yq -r '.repos | keys | .[]' "$CFG"; }
repo_field() { yq -r ".repos[\"$1\"].$2 // \"\"" "$CFG"; }
repo_real()  { local p; p="$(repo_field "$1" path)"; (cd "$ROOT" && cd "$p" 2>/dev/null && pwd -P) || true; }
