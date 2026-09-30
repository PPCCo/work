#!/usr/bin/env bash
# Create/repair the symlinks from the orchestrator to the real repos and keep .gitignore correct.
# Idempotent. Never deletes real files or directories.
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

status=0
touch "$ROOT/.gitignore"
add_ignore() { grep -qxF "$1" "$ROOT/.gitignore" || echo "$1" >> "$ROOT/.gitignore"; }

for r in $(repo_names); do
  real="$(repo_real "$r")"; link="$(repo_field "$r" link)"; link="${link:-$r}"
  if [[ -z "$real" ]]; then echo "FAIL  $r: path '$(repo_field "$r" path)' does not exist"; status=1; continue; fi
  if [[ ! -d "$real/.git" && ! -f "$real/.git" ]]; then echo "WARN  $r: $real is not a git repo root"; fi
  target="$ROOT/$link"
  if [[ -L "$target" ]]; then
    if [[ "$(cd "$target" && pwd -P)" == "$real" ]]; then echo "OK    $link -> $real"; else ln -sfn "$real" "$target"; echo "FIXED $link -> $real"; fi
  elif [[ -e "$target" ]]; then
    echo "FAIL  $link exists and is not a symlink; move it away manually"; status=1; continue
  else
    ln -s "$real" "$target"; echo "MADE  $link -> $real"
  fi
  add_ignore "/$link"
done
add_ignore "/.claude/.verify-logs/"
exit $status
