# agentic-agile

A Claude Code plugin that packages **two-stage agile planning** (interactive,
human-gated) and **two-phase TDD execution** (autonomous, hook-enforced) into one
install. Determinism comes from hooks, not from model goodwill: every sub-agent
stop is intercepted by a gate that can block the stop and feed the failure reason
back to the supervisor.

- **Planning** (human present): intake → standards → planner produce the sprint
  contract + per-story `tasks.md` / `validate.md` / `plan.md`.
- **Execution** (human absent): per wave, RED → SCAFFOLD → GREEN →
  STRUCTURAL-REVIEW, then once per sprint a FINAL-GATE. One worktree-isolated
  sub-agent per task; merge on pass, abandon the chain on a foundation-poisoning halt.

See `skills/agentic-agile/SKILL.md` for the full supervisor playbook and
`STRUCTURE.md` for the design source layout.

## Prerequisites

| Tool | Required? | What it does | Install |
|------|-----------|--------------|---------|
| **ctx-symbols** | recommended | symbol uniqueness (`count==1`) + duplicate/parallel/orphan detection for the scaffold & structural gates | built from `tools/ctx-symbols` (see below) |
| **md-db** | recommended | validates `.md` artifacts against `schemas/*.kdl` | built from vendored `tools/md-db` (AGPL-3.0; see below) |
| **Rust toolchain** | required to install | builds both backends + runs the target repo's `cargo fmt/clippy/test/coverage` matrix | rustup (>= 1.85) |

Both backends are **optional**: if absent, the gates WARN and fall back to grep —
they never falsely block and never silently pass a real check. A run with WARNs has
*weaker*, not *absent*, gates. Install both for full enforcement.

### Install the backends

```bash
./tools/install.sh            # builds + installs ctx-symbols AND md-db to ~/.local/bin
                              # (both from source; needs a Rust toolchain >= 1.85)
# ensure ~/.local/bin (or ~/.cargo/bin) is on PATH
```

## Install the plugin

From a marketplace (this repo ships `.claude-plugin/marketplace.json` at its root):

```
/plugin marketplace add /path/to/this/repo
/plugin install agentic-agile@agentic-agile-marketplace
```

Then in a project, run the planning skill interactively; once Stage-2 is complete,
trigger the autonomous execution run.

## Targeting your repo

The execution gates ship wired for a **Rust** target (cargo fmt/clippy/test). The
GREEN and FINAL matrix is **read from your `standards.md`**, not hardcoded — so the
fastest way to retarget is to declare your matrix there. For a non-Rust stack, adapt
the language-specific bits of `bin/gate-red-verify` (compile-then-fail check) and the
default matrix in `bin/_gatelib.sh`.

### Gate contract (env the supervisor sets per dispatch)

All optional, each with a safe fallback (see `bin/_gatelib.sh`):
`ATTEMPT_DIR`, `REPO_DIR`, `STANDARDS_FILE`, `BASE_REF`, `TEST_GLOBS`,
`SCOPE_GLOBS`, `SCAFFOLD_SYMBOLS`, `GATE_RUN_TESTS`, `GATE_RUN_MATRIX`.

## What's in here

```
.claude-plugin/plugin.json   manifest
skills/agentic-agile/SKILL.md the supervisor playbook (canonical)
agents/<role>.md             8 dispatchable personas
hooks/hooks.json             gate wiring by agent_type (SubagentStop/Stop/PostToolUse)
bin/                         gate bodies + _gatelib.sh + log-execution
schemas/*.kdl                md-db schemas (agent-io / planning-artifacts / ledger)
tools/ctx-symbols/           the symbol backend (Rust source) + install.sh
pipeline/                    design source of truth (persona/init/artifacts/gate per activity)
```

## Status & limitations

- Gate bodies are **verified offline** (positive + negative) against a sample
  one-story sprint. The hook *wiring* should be smoke-tested in a live Claude Code
  session before relying on it in anger.
- Suppression detection is syntactic; a test weakened by deleting an assertion is
  caught by the RED-invariant + diff-scope, not by grep. See SKILL.md
  "Known gate limitations."

## License

MIT — see `LICENSE`.

## Lineage & memory (v0.2)

- `bin/lineage` keeps a global append-only `lineage.jsonl` + per-task transcripts.
  `SubagentStart` stages a READ-ONLY task slice into the worktree (`.lineage/`),
  `PostToolUse *` records every call, `SubagentStop *` removes the slice. These hooks
  never block. The supervisor reads the global store; the planning **retrospective**
  (the `archivist`) distills it into `docs/agents/memory.md`, which is injected
  (role-scoped) into each `init.md` `# Memory` section.
- The gates read their per-task contract (`TASK_ID`, `SCOPE_GLOBS`, `SCAFFOLD_SYMBOLS`,
  `BASE_REF`, `AGENTIC_LINEAGE_DIR`) from `.agentic/task.env`, written by the supervisor
  into each worktree at dispatch. `.agentic/` and `.lineage/` are git-ignored and never
  merged.
