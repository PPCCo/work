#!/usr/bin/env bash
# One-screen status of every repo: real path, symlink health, branch, cleanliness, ahead/behind.
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

printf '%-18s %-8s %-28s %-10s %-12s %s\n' REPO LINK BRANCH TREE "AHEAD/BEHIND" REAL_PATH
rc=0
for r in $(repo_names); do
  real="$(repo_real "$r")"; link="$(repo_field "$r" link)"; link="${link:-$r}"
  if [[ -z "$real" ]]; then printf '%-18s %-8s %s\n' "$r" "-" "MISSING: $(repo_field "$r" path)"; rc=1; continue; fi
  if [[ -L "$ROOT/$link" && "$(cd "$ROOT/$link" && pwd -P)" == "$real" ]]; then l=ok; else l=BROKEN; rc=1; fi
  branch="$(git -C "$real" rev-parse --abbrev-ref HEAD 2>/dev/null || echo '?')"
  if [[ -n "$(git -C "$real" status --porcelain 2>/dev/null)" ]]; then tree=DIRTY; rc=1; else tree=clean; fi
  ab="$(git -C "$real" rev-list --left-right --count '@{upstream}...HEAD' 2>/dev/null | awk '{print "+"$2"/-"$1}' || true)"
  printf '%-18s %-8s %-28s %-10s %-12s %s\n' "$r" "$l" "$branch" "$tree" "${ab:-no-upstream}" "$real"
done
echo
echo "Search and edit using REAL_PATH; symlinks are a convenience only."
exit $rc
