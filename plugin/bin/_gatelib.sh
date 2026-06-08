#!/usr/bin/env bash
# _gatelib.sh — shared helpers for the agentic-agile gate bodies (Rust target).
#
# Gates are wired in hooks.json (SubagentStop / Stop) matched by agent_type. The
# supervisor sets the per-dispatch contract via environment variables; every var
# has a safe fallback so a gate degrades to a WARN rather than a false pass.
#
# Contract (supervisor-set; all optional, with fallbacks):
#   ATTEMPT_DIR     dir holding this attempt's init.md + output.md
#   REPO_DIR        worktree root with source + tests        (default: git toplevel or PWD)
#   STANDARDS_FILE  path to standards.md (the gate matrix)   (default: auto-discovered)
#   BASE_REF        git ref to diff scope against            (default: working-tree diff)
#   TEST_GLOBS      space-sep globs for test files (RED scope)  (default: rust test conventions)
#   SCOPE_GLOBS     space-sep globs this task may touch (GREEN scope) (default: unset → skip)
#   SCAFFOLD_SYMBOLS  space-sep symbols the RED tests reference (scaffold count==1)
#   GATE_RUN_TESTS  1 to actually run cargo (default: 1 if a Cargo.toml is found)
#   GATE_RUN_MATRIX 1 to run the standards matrix (default: 1)
#
# Exit-code contract for callers: 0 pass · 2 block+feedback (stderr) · other = error.

set -uo pipefail

warn() { echo "WARN[$GATE_NAME]: $*" >&2; }
fail() { echo "BLOCK[$GATE_NAME]: $*" >&2; exit 2; }
note() { echo "[$GATE_NAME] $*" >&2; }

# Resolve REPO_DIR.
repo_dir() {
  if [ -n "${REPO_DIR:-}" ]; then echo "$REPO_DIR"; return; fi
  git rev-parse --show-toplevel 2>/dev/null || pwd
}

# Per-worktree task contract the supervisor writes at dispatch (.agentic/task.env):
# TASK_ID, ATTEMPT, AGENT_ROLE, SCOPE_GLOBS, SCAFFOLD_SYMBOLS, BASE_REF, ATTEMPT_DIR,
# AGENTIC_LINEAGE_DIR. Real env still overrides (load is non-clobbering only for unset).
load_task_env() {
  local te; te="$(repo_dir)/.agentic/task.env"
  [ -f "$te" ] || return 0
  # shellcheck source=/dev/null
  set -a; . "$te"; set +a
}
load_task_env

# Find an artifact file by name, preferring $ATTEMPT_DIR.
find_in_attempt() {
  local name="$1"
  if [ -n "${ATTEMPT_DIR:-}" ] && [ -f "$ATTEMPT_DIR/$name" ]; then
    echo "$ATTEMPT_DIR/$name"; return 0
  fi
  return 1
}

# Validate an attempt dir's .md against agent-io.kdl via md-db; WARN-fallback if absent.
validate_agent_io() {
  local dir="${1:-${ATTEMPT_DIR:-}}"
  [ -z "$dir" ] && { warn "no ATTEMPT_DIR; skipping md-db validation"; return 0; }
  if command -v md-db >/dev/null 2>&1; then
    md-db validate "$dir" --schema "${CLAUDE_PLUGIN_ROOT}/schemas/agent-io.kdl" \
      || fail "md-db: $dir failed agent-io.kdl"
  else
    warn "md-db absent; init.md/output.md structure UNVALIDATED (weaker check)"
    # Minimal fallback: output.md must at least exist and carry required sections.
    local out="$dir/output.md"
    [ -f "$out" ] || fail "output.md missing in $dir"
    grep -q '^#\+ *Result' "$out"  || fail "output.md missing # Result section"
    grep -q '^#\+ *Summary' "$out" || fail "output.md missing # Summary section"
    # type: must live INSIDE the frontmatter block (between the first two --- lines).
    awk 'NR==1&&/^---/{f=1;next} f&&/^---/{exit} f' "$out" | grep -qE '^type:[[:space:]]*output' \
      || fail "output.md frontmatter missing 'type: output'"
  fi
}

# True if ctx-symbols is available.
have_ctx_symbols() { command -v ctx-symbols >/dev/null 2>&1; }

# Count definitions of a symbol; echoes an integer. Uses ctx-symbols, else grep.
symbol_count() {
  local sym="$1" root="$2"
  if have_ctx_symbols; then
    ctx-symbols count "$sym" --tree "$root"
  else
    # grep fallback (fragile: matches fn/struct/etc. definitions only, name-anchored)
    { grep -rohE "\\b(fn|struct|enum|trait|type|const|static|mod)\\s+$sym\\b" \
        --include='*.rs' "$root" 2>/dev/null | wc -l | tr -d ' '; } || echo 0
  fi
}

# Build artifacts that are never "worker edits" — excluded from diff-scope checks.
# `|| true` so an all-artifacts diff (grep -v matches nothing) is success, not exit 1.
changed_paths_filter() { grep -vE '(^|/)(target/|Cargo\.lock$|\.git/|\.agentic/)' || true; }

# Changed paths in REPO_DIR (one per line). Uses BASE_REF if set, else working tree.
changed_paths() {
  local root; root="$(repo_dir)"
  if [ -n "${BASE_REF:-}" ]; then
    git -C "$root" diff --name-only "$BASE_REF" 2>/dev/null | changed_paths_filter
  else
    { git -C "$root" diff --name-only 2>/dev/null
      git -C "$root" diff --name-only --cached 2>/dev/null
      git -C "$root" ls-files --others --exclude-standard 2>/dev/null; } | sort -u | changed_paths_filter
  fi
}

# True if $1 matches any space-separated glob in $2.
path_matches_any() {
  local path="$1" globs="$2" g
  for g in $globs; do
    case "$path" in $g) return 0;; esac
  done
  return 1
}

# Suppression patterns that must never appear in source. exit 2 if found.
assert_no_suppression() {
  local root; root="$(repo_dir)"
  if grep -rEn '#\[ignore\]|\.skip\(|(^|[^A-Za-z])xit\(|#\[cfg\(not\(test\)\)\]' \
      --include='*.rs' "$root" 2>/dev/null \
      | grep -v '/target/' >/dev/null 2>&1; then
    fail "test-suppression pattern present (no #[ignore]/.skip/xit/cfg(not(test)))"
  fi
}

# Run the gate matrix declared in standards.md (standards-bind-gates). Falls back
# to a default Rust matrix with a WARN if standards.md / its matrix is not found.
run_standards_matrix() {
  [ "${GATE_RUN_MATRIX:-1}" = "1" ] || { note "matrix skipped (GATE_RUN_MATRIX=0)"; return 0; }
  local root; root="$(repo_dir)"
  local sf="${STANDARDS_FILE:-}"
  if [ -z "$sf" ]; then
    sf="$(find "$root" -maxdepth 6 -name standards.md 2>/dev/null | head -1)"
  fi

  local -a cmds=()
  if [ -n "$sf" ] && [ -f "$sf" ]; then
    # Extract fenced command lines under a "Gate matrix" / "Cross-cutting gates" heading.
    mapfile -t cmds < <(awk '
      /^#+.*([Gg]ate matrix|[Cc]ross-cutting gates)/ {insec=1; next}
      insec && /^#+[[:space:]]/                        {insec=0}
      insec && /^```/                                  {infence=!infence; next}
      insec && infence && NF                           {print}
    ' "$sf")
  fi

  if [ "${#cmds[@]}" -eq 0 ]; then
    warn "no matrix found in standards.md; using DEFAULT Rust matrix (weaker: not standards-bound)"
    cmds=(
      "cargo fmt --all -- --check"
      "cargo clippy --workspace --all-targets -- -D warnings"
      "cargo test --workspace"
    )
  else
    note "running ${#cmds[@]} gate command(s) from $(basename "$sf")"
  fi

  local c
  for c in "${cmds[@]}"; do
    note "matrix: $c"
    ( cd "$root" && eval "$c" ) || fail "matrix command failed: $c"
  done
}

# Detect a cargo project under REPO_DIR.
is_cargo_repo() { [ -f "$(repo_dir)/Cargo.toml" ] || find "$(repo_dir)" -maxdepth 2 -name Cargo.toml 2>/dev/null | head -1 | grep -q .; }
