# bin/ — gate scripts & tools

Gates are bash, invoked by hooks (`hooks/hooks.json`) by `agent_type`; the agent
never calls them directly. Shared helpers live in `_gatelib.sh`.

## Exit-code convention (gates)
- `0`  PASS (allow the event)
- `2`  BLOCK the event + write the reason to stderr (fed back to the supervisor)
- other non-zero  error
Transcripts hooks (`transcripts`) ALWAYS exit `0` — they must never block an agent.

## Per-task contract
Gates read `.agentic/task.env` (the supervisor writes it into each worktree at
dispatch): `TASK_ID, ATTEMPT, AGENT_ROLE, SCOPE_GLOBS, SCAFFOLD_SYMBOLS, BASE_REF,
ATTEMPT_DIR, AGENTIC_TRANSCRIPTS_DIR`. Real env overrides. A missing backend (md-db /
ctx-symbols) → WARN + grep fallback; never a silent pass.

## Gates (which hook fires each)
| script | event · matcher | checks | exit 2 when |
|--------|-----------------|--------|-------------|
| gate-supervisor-scope     | PreToolUse · Write\|Edit\|MultiEdit | supervisor writes only docs/agents/** while a sprint is live this session (session-scoped self-arming lock); workers exempt | supervisor writes production source mid-sprint |
| gate-tooling              | SubagentStart · exec roles + supervisor self-check | md-db + ctx-symbols on PATH (execution may not run grep-degraded) | a backend is missing |
| gate-validate-artifact    | PostToolUse · Write         | md-db-validate the written artifact | artifact malformed |
| gate-red-verify           | SubagentStop · red-worker   | worktree-isolated; every new test FAILS BY ASSERTION; no regression; diff = tests+shims | shared-tree run / a new test passes / prod code / regression |
| gate-scaffold-verify      | SubagentStop · scaffolder   | worktree-isolated; one def per symbol (`.agentic/scaffold-symbols`); panic+TODO; no marked shim; no clobber | shared-tree run / impl body / dup / shim remains |
| gate-green-verify         | SubagentStop · green-worker | worktree-isolated; tests pass; in-scope diff; standards matrix; zero suppressions | shared-tree run / failing test / out-of-scope / suppression |
| gate-structural-integrity | SubagentStop · structural-reviewer | orphan/parallel/duplicate via ctx-symbols | foundation-poisoning finding |
| gate-final                | SubagentStop · final-gate   | full matrix; zero suppressions; all plan-ready ticked | matrix red / suppression / unticked |
| gate-standards-cited      | SubagentStop · standards    | standards.md citations resolve | dangling citation |
| gate-stage2-complete      | supervisor self-check       | every story Stage-2 valid; no TBW | incomplete planning |
| gate-plan-shape           | called by gates             | each plan checkbox carries `path::fn` | malformed plan |
| gate-ledger-format        | called by gates             | execution.log line shape | malformed ledger |

## Tools
| script | purpose |
|--------|---------|
| `transcripts`       | full capture: stage-in / record / prompt / snapshot / stop / view / prune (`transcripts --help`) |
| `worktree-create` | `WorktreeCreate` hook — `git worktree add` for `isolation: "worktree"`; prints the path, exit 2 blocks |
| `worktree-remove` | `WorktreeRemove` hook — `git worktree remove` cleanup; always exit 0 (cannot block) |
| `log-execution` | append a transition line to `execution.log` |

## v0.2 — self-check at every step

Every dispatched role now has BOTH a `bin/selfcheck` mapping (run it before you report
done) AND a `SubagentStop` hook backstop running the same gate:

| role | gate | event · matcher |
|---|---|---|
| intake | `gate-intake` (five-part intent present) | SubagentStop · `intake` |
| standards | `gate-standards-cited` | SubagentStop · `standards` |
| planner | `gate-stage2-complete` (auto-discovers sprint dir) | SubagentStop · `planner` |
| archivist | `gate-memory` (valid + never relaxes an invariant) | SubagentStop · `archivist` |
| red/scaffold/green/structural/final | as above | SubagentStop · role |

`bin/selfcheck [role]` resolves the role from `$AGENT_ROLE` (task.env) and runs that
gate; exit `0` PASS · `2` FAIL · `64` unknown role. A PASS here means the hook passes.
