#!/usr/bin/env bash
# run-evals.sh — execute one eval suite, both arms (with_skill / without_skill).
#
# For each eval in the suite it runs `claude -p` twice: once with the agent/skill
# instructions injected via --append-system-prompt (with_skill), once bare
# (without_skill). Outputs + timing land in a per-eval workspace dir. Grading and
# aggregation are separate steps (grade.py, aggregate.py) so you can dry-run first.
#
# THIS SPENDS MODEL TOKENS: 2 `claude -p` calls per eval. It refuses to run until you
# pass --yes (or set EVAL_CONFIRM=1); without that it prints the plan and the call
# count, then exits 0.
#
# Usage:
#   run-evals.sh --suite <evals.json> [--iteration N] [--workspace DIR] [--yes]
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
PLUGIN="$REPO/plugin"

SUITE=""
ITER=1
WORKSPACE=""
CONFIRM="${EVAL_CONFIRM:-0}"

while [ $# -gt 0 ]; do
  case "$1" in
    --suite)     SUITE="$2"; shift 2 ;;
    --iteration) ITER="$2"; shift 2 ;;
    --workspace) WORKSPACE="$2"; shift 2 ;;
    --yes)       CONFIRM=1; shift ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

[ -n "$SUITE" ] && [ -f "$SUITE" ] || { echo "ERROR: --suite <evals.json> required and must exist" >&2; exit 2; }

# Resolve the instruction file to inject for the with_skill arm.
read -r KIND NAME MD < <(python3 - "$SUITE" "$PLUGIN" <<'PY'
import json, sys, os
suite, plugin = sys.argv[1], sys.argv[2]
d = json.load(open(suite))
if "agent_role" in d:
    role = d["agent_role"]
    print("agent", role, os.path.join(plugin, "agents", role + ".md"))
elif "skill_name" in d:
    name = d["skill_name"]
    print("skill", name, os.path.join(plugin, "skills", name, "SKILL.md"))
else:
    print("unknown", "?", "")
PY
)
[ "$KIND" = "unknown" ] && { echo "ERROR: suite has neither agent_role nor skill_name" >&2; exit 2; }
[ -f "$MD" ] || { echo "ERROR: instruction file not found: $MD" >&2; exit 2; }

[ -n "$WORKSPACE" ] || WORKSPACE="$REPO/eval-workspace/$(basename "$SUITE" .json)"
ITER_DIR="$WORKSPACE/iteration-$ITER"

# Number of evals -> call count.
N_EVALS="$(python3 -c "import json,sys;print(len(json.load(open(sys.argv[1]))['evals']))" "$SUITE")"
CALLS=$(( N_EVALS * 2 ))

echo "Suite      : $SUITE  ($KIND: $NAME)"
echo "Injecting  : $MD  (with_skill arm only)"
echo "Workspace  : $ITER_DIR"
echo "Evals      : $N_EVALS  ->  $CALLS  'claude -p' calls"

if [ "$CONFIRM" != "1" ]; then
  echo
  echo "DRY PLAN ONLY — this run would spend tokens. Re-run with --yes (or EVAL_CONFIRM=1) to execute."
  exit 0
fi

command -v claude >/dev/null 2>&1 || { echo "ERROR: claude CLI not on PATH" >&2; exit 1; }
MD_TEXT="$(cat "$MD")"

# Drive each eval through both arms.
python3 -c "
import json,sys
for e in json.load(open(sys.argv[1]))['evals']:
    print('\t'.join([str(e['id']), e['prompt'].replace(chr(10),' '), ';'.join(e.get('files',[]))]))
" "$SUITE" | while IFS=$'\t' read -r ID PROMPT FILES; do
  echo
  echo "── eval $ID ──"
  SUITE_DIR="$(cd "$(dirname "$SUITE")" && pwd)"
  # Input files are relative to the skill/suite root (parent of an `evals/` dir).
  if [ "$(basename "$SUITE_DIR")" = "evals" ]; then FILE_BASE="$(dirname "$SUITE_DIR")"; else FILE_BASE="$SUITE_DIR"; fi
  for ARM in with_skill without_skill; do
    ARM_DIR="$ITER_DIR/eval-$ID/$ARM"
    OUT="$ARM_DIR/outputs"
    mkdir -p "$OUT"
    # Stage any input files into the run CWD so the agent can read them.
    if [ -n "$FILES" ]; then
      IFS=';' read -ra FS <<< "$FILES"
      for f in "${FS[@]}"; do
        [ -f "$FILE_BASE/$f" ] && cp "$FILE_BASE/$f" "$OUT/$(basename "$f")"
      done
    fi
    echo "  [$ARM] running…"
    if [ "$ARM" = "with_skill" ]; then
      ( cd "$OUT" && claude -p --output-format json \
          --append-system-prompt "$MD_TEXT" "$PROMPT" ) > "$ARM_DIR/claude.json" || true
    else
      ( cd "$OUT" && claude -p --output-format json "$PROMPT" ) > "$ARM_DIR/claude.json" || true
    fi
    python3 "$HERE/_extract.py" "$ARM_DIR/claude.json" "$ARM_DIR"
  done
done

echo
echo "Done. Outputs under $ITER_DIR"
echo "Next:"
echo "  # grade each arm (LLM judge — spends tokens; add --dry-run to test plumbing):"
echo "  for d in $ITER_DIR/eval-*/*/; do python3 $HERE/grade.py --suite $SUITE --eval-id \"\$(basename \$(dirname \$d) | sed 's/eval-//')\" --arm-dir \"\$d\" --dry-run; done"
echo "  # aggregate:"
echo "  python3 $HERE/aggregate.py $ITER_DIR"
