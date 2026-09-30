#!/usr/bin/env bash
# Run quality gates for one repo or all. Usage:
#   verify.sh <repo|all> [gate ...]     gates: install format lint typecheck test replay integration build contracts
#   verify.sh <repo> baseline           shorthand for: format lint typecheck test
# Output is compact: a result table, and the tail of the log for each failure (full logs in .claude/.verify-logs/).
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

target="${1:-}"; shift || true
[[ -n "$target" ]] || { echo "usage: verify.sh <repo|all> [gate ...]" >&2; exit 2; }
gates=("$@")
if [[ "${gates[*]:-}" == "baseline" ]]; then gates=(format lint typecheck test); fi
if [[ ${#gates[@]} -eq 0 ]]; then mapfile -t gates < <(yq -r '.gate_order[]' "$CFG" 2>/dev/null || true); fi
if [[ ${#gates[@]} -eq 0 ]]; then gates=(format lint typecheck test build contracts); fi

if [[ "$target" == "all" ]]; then repos=$(repo_names); else repos="$target"; fi
logdir="$ROOT/.claude/.verify-logs"; mkdir -p "$logdir"
overall=0; summary=()

for r in $repos; do
  real="$(repo_real "$r")"
  if [[ -z "$real" ]]; then echo "unknown or missing repo: $r" >&2; overall=1; continue; fi
  for g in "${gates[@]}"; do
    cmd="$(repo_field "$r" "gates.$g")"
    if [[ -z "$cmd" ]]; then summary+=("$r|$g|SKIP (not defined)"); continue; fi
    log="$logdir/$r-$g.log"
    if (cd "$real" && bash -c "$cmd") >"$log" 2>&1; then
      summary+=("$r|$g|PASS")
    else
      summary+=("$r|$g|FAIL  ($cmd)"); overall=1
      echo "---- $r $g FAILED: last 40 lines of $log ----"; tail -n 40 "$log"; echo
    fi
  done
done

echo "== verify summary =="
printf '%-18s %-12s %s\n' REPO GATE RESULT
for s in "${summary[@]}"; do IFS='|' read -r a b c <<<"$s"; printf '%-18s %-12s %s\n' "$a" "$b" "$c"; done
exit $overall
