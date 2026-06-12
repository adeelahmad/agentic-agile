# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Versioning policy

`agentic-agile` versions the **plugin** (`plugin/.claude-plugin/plugin.json`) and the
bundled `ctx-symbols` crate together under one SemVer line:

- **MAJOR** — breaking changes to the gate contract (hook events/`agent_type`
  matchers, gate exit-code semantics), the on-disk artifact layout, the KDL schemas,
  or the `ctx-symbols` CLI surface.
- **MINOR** — backward-compatible additions (new gate, new check, new language in
  `ctx-symbols`, new optional env in the gate contract).
- **PATCH** — backward-compatible fixes (gate bug, false positive/negative, docs).

Keep `plugin.json` `version`, the `ctx-symbols` `Cargo.toml` `version`, and the git
tag in lockstep. Tag releases as `vMAJOR.MINOR.PATCH`.

## [0.5.0] - 2026-06-12

### Changed
- **Sprint-entry discipline.** A fresh build/fix/improve request mid-session was being
  treated as "just do the work" instead of opening a new sprint/stories. Broadened the
  skill trigger `description` to fire on terse/visual requests (improve/redesign/polish,
  "the UI is broken", "add facets/filters", a screenshot with a complaint), and added a
  Hard-guardrail: a new build/fix/improve request is NEW SCOPE — re-enter intake →
  planner, never switch into ad-hoc hand-editing.
- **Renamed `lineage` → `transcripts`, and it now records EVERYTHING.** The old
  `bin/lineage` captured only `tool_name` + `file_path` per event — not a transcript.
  Replaced by `bin/transcripts`, which captures:
  - `<task>/events.jsonl` — the FULL hook payload per tool call (tool_input +
    tool_response) plus every user prompt (new `UserPromptSubmit` hook).
  - `<task>/transcript.jsonl` — the complete session snapshot (every user/assistant
    message + thinking + tool result), copied from the session's `transcript_path` on
    each stop (new `Stop` hook + `SubagentStop`).
  - `global.jsonl` — a thin cross-task causal stream for the retrospective to scan.
  Retention keeps everything (no auto-compaction); `transcripts prune`
  (`AGENTIC_TRANSCRIPTS_KEEP`) is a manual, opt-in cap.
  Renamed throughout: the `bin/lineage`→`bin/transcripts` script, the
  `AGENTIC_LINEAGE_DIR`→`AGENTIC_TRANSCRIPTS_DIR` task.env var, the `.lineage/`→
  `.transcripts/` worktree slice, the store dir, hook wiring, schemas-adjacent docs,
  SKILL.md Part C, README/STRUCTURE/ARCHITECTURE/DESIGN, and the archivist
  agent/eval. No back-compat shim.

## [0.4.0] - 2026-06-12

### Fixed
- **`make install` failed on rustc < 1.95.** The committed `md-db` `Cargo.lock`
  pinned `kdl@6.7.1`, whose MSRV jumped to 1.95 at the 6.6.0 release, so the build
  died (`kdl@6.7.1 requires rustc 1.95`) on toolchains as recent as 1.94.1. Pinned
  `kdl` back to `6.5.0` (MSRV 1.82, still within the `kdl = "6"` range). Verified by a
  clean rebuild under rustc 1.94.1. Corrected the stale `install.sh` header comment
  (it claimed edition 2024 / rustc ≥ 1.85).

### Added
- **`gate-supervisor-scope`** (`PreToolUse · Write|Edit|MultiEdit`) — blocks the
  supervisor from writing production source while a sprint is live in the current
  session, forcing all code through dispatched workers. Uses a session-scoped,
  self-arming lock (armed on the first `docs/agents/**` write) so a stale lock from an
  abandoned sprint never blocks unrelated future sessions. Honors `SKIP_HOOKS=1`.
- **`gate-tooling`** (`SubagentStart` on execution roles + a manual supervisor
  preflight) — BLOCKS the first worker dispatch unless `md-db` and `ctx-symbols` are
  on PATH. Execution no longer starts silently grep-degraded; planning may still run
  degraded. `selfcheck tooling` runs it. Honors `SKIP_HOOKS=1`.

- **Worktree-isolation enforcement** in the writing-worker gates. `_gatelib.sh` gains
  `assert_worktree_isolation`, called by `gate-red/scaffold/green-verify`: a worker
  that ran in the shared/main tree (detected via `.git` being a directory rather than
  a worktree's `gitdir:` file) is BLOCKED. Stops the supervisor from silently dropping
  isolation as an "environmental adaptation". Honors `SKIP_HOOKS=1`.

### Changed
- `SKILL.md`: added the "supervisor never writes production source" guardrail and an
  ambiguous-resume rule ("go on"/"continue" = re-dispatch the last activity, never
  "build it directly"); documented the execution tooling preflight. Added the
  **schedule-vs-invariant** rule (adapt order/parallelism freely; never relax
  worktree isolation, gates, TDD ordering, or no-suppression — those escalate to
  planning) and the sanctioned disk-pressure path (serialize worktrees, don't share).

## [0.3.1] - 2026-06-08

### Changed
- **Tool allowlists on the non-building agents** (subagents-doc audit). The five agents
  that read/verify/produce-artifacts only — `intake`, `standards`, `structural-reviewer`,
  `final-gate`, `archivist` — now declare `tools: Read, Grep, Glob, Bash, Write`, omitting
  `Edit`/`MultiEdit` so they can't patch source/tests in place. This is defense-in-depth:
  `Bash`/`Write` can still touch files, so the deterministic gates remain the real
  enforcement (noted inline). The 3 builders (`red`/`scaffold`/`green-worker`) and the
  `planner` intentionally keep full tools — they must edit code or revise `.md` artifacts;
  `planner.md` documents why. Confirmed all agent `name`s still match the `hooks.json`
  `SubagentStop` matchers, and no agent uses the plugin-ignored `hooks`/`mcpServers`/
  `permissionMode` fields.
- `archivist` now drafts memory candidates to its `output.md` only and never writes
  `docs/agents/memory.md` directly — the supervisor + human curate it.

## [0.3.0] - 2026-06-08

### Added
- **`init` entry-point skill** (`plugin/skills/init/`): a thin, explicit-only alias
  (`disable-model-invocation: true`) invoked as `/agentic-agile:init`. It points at the
  canonical `agentic-agile` playbook rather than duplicating it, so the two never drift.
  The main `agentic-agile` skill still auto-triggers on natural-language build/TDD asks.

## [0.2.1] - 2026-06-08

### Fixed
- **Plugin failed to load: duplicate hooks file.** `plugin.json` declared
  `"hooks": "./hooks/hooks.json"`, but Claude Code auto-loads the standard
  `hooks/hooks.json` by convention — the manifest declaration loaded it a second time
  and the plugin refused to load. Removed the redundant `manifest.hooks` entry. Caught
  by a live `claude plugin install` smoke test; static `claude plugin validate` passes
  either way.

### Added
- **Eval suites** (agentskills.io style): expanded the skill suite to 7 cases
  (`plugin/skills/agentic-agile/evals/`) and added per-agent suites for all 9 agents
  (`plugin/evals/agents/*.json`) plus a shared harness (`scripts/eval/`) and
  `make eval-validate` / `make eval`.
- **Vendored `md-db`** (`plugin/tools/md-db/`, AGPL-3.0): `make install` now builds
  both gate backends from source; md-db is no longer an external prerequisite.

### Changed
- `make test` runs both Rust crates; `make ci` now includes `eval-validate`.
- Marketplace gained a `description`; plugin manifest gained `homepage`/`repository`.

## [0.2.0]

### Added
- **Per-task lineage** (`bin/lineage`, file-based, no FUSE): a global append-only
  `lineage.jsonl` + per-task transcripts. Each sub-agent gets a READ-ONLY task slice
  staged into its worktree (`.lineage/`); the supervisor reads the global store. Wired
  via `SubagentStart` (stage-in), `PostToolUse *` (record), `SubagentStop *` (stage-out);
  lineage hooks never block.
- **Planning retrospective + memory** (`pipeline/planning/retrospective/`, the
  `archivist` agent, `schemas/memory.kdl`): every planning session distills recurring
  failures + reliably-good patterns (plus human insight) into terse, role-scoped
  entries in `docs/agents/memory.md`, injected into each `init.md` `# Memory` section.
- **Manifests**: `plugin/.claude-plugin/plugin.json` and root `.claude-plugin/marketplace.json`.
- **Per-worktree task contract** `.agentic/task.env` (supervisor-written), read by the gates.
- **Fix (found by end-to-end dry run): executable bits** — all `bin/gate-*` and
  `log-execution` are now shipped `+x`; previously several were `0644`, so the hooks
  would have failed to exec them at runtime (exit 126).
- **Fix: diff-scope excludes `.agentic/`** — the plugin's own per-task control files
  (`task.env`, `scaffold-symbols`, lineage) no longer count against a GREEN task's
  scope check (joining `target/`, `Cargo.lock`, `.git/` in the filter).
- **Self-check at EVERY step**: added `gate-intake` (five-part intent) and `gate-memory`
  (valid + never relaxes an invariant) so intake and the archivist self-check too;
  `gate-stage2-complete` auto-discovers the sprint dir; SubagentStop now backstops every
  dispatched role (intake/standards/planner/archivist + the 5 execution gates). Nothing
  advances past a failing self-check.
- **Self-check loop** (`bin/selfcheck`): workers run their own gate (the same script the
  hook enforces) + `md-db validate` BEFORE reporting done — layered determinism, fewer
  re-spawns. SKILL.md gains a "Validate before you report" + "Available scripts" section.
- **Skill-quality artifacts** (agentskills.io standards): `skills/agentic-agile/evals/` (evals.json + eval_queries.json), `bin/README.md` (gate usage + exit-code catalog), `lineage --help`, a Prerequisites section and a triggering-optimized description in SKILL.md.

### Fixed
- `final-gate` fires on `SubagentStop` (matcher `final-gate`), not `Stop` — it is a
  dispatched sub-agent.
- `gate-scaffold-verify` resolves production symbols from `.agentic/scaffold-symbols`
  (scaffolder-written) instead of mis-reading test paths from `plan-ready.md`, and flags
  only marked shim files (`// agentic:shim`) instead of any `mod common` (which collided
  with the standard Rust `tests/common` convention).

### Changed
- `agent-io.kdl` `agent_role` enum gains `archivist`.

## [Unreleased]

## [0.1.0] - 2026-06-08

Initial release.

### Added
- **Plugin manifest + marketplace** — `plugin/.claude-plugin/plugin.json` and a
  root `.claude-plugin/marketplace.json` (install via
  `/plugin install agentic-agile@agentic-agile-marketplace`).
- **Supervisor playbook** — canonical `skills/agentic-agile/SKILL.md`: two-stage
  planning (intake → standards → planner) + two-phase TDD execution
  (RED → SCAFFOLD → GREEN → STRUCTURAL-REVIEW → FINAL-GATE), per-task attempt dirs,
  the revision/feedback loop, cause-specific escalation, and the data-plane writers.
- **8 dispatchable agent personas** (`agents/`) assembled from `pipeline/`.
- **Deterministic gates** (`bin/`) wired in `hooks/hooks.json` by `agent_type`:
  `gate-red-verify`, `gate-scaffold-verify`, `gate-green-verify`,
  `gate-structural-integrity`, `gate-final`, `gate-stage2-complete`,
  `gate-validate-artifact`, `gate-standards-cited`, `gate-plan-shape`,
  `gate-ledger-format`, plus `log-execution` and the shared `_gatelib.sh`.
  GREEN/FINAL matrix is read from `standards.md`, not hardcoded.
- **ctx-symbols** (`tools/ctx-symbols`) — minimal tree-sitter symbol resolver
  (`count`/`locate`/`search`/`conflicts`) harvested from the MIT `ctxconfig`
  code-intelligence layer; backs the scaffold/structural gates with grep fallback.
- **md-db KDL schemas** (`schemas/`) — `agent-io`, `planning-artifacts`, `ledger`.
- **Tooling** — `tools/install.sh`, `Makefile`, git hooks (`.githooks/`),
  GitHub Actions CI (`.github/workflows/ci.yml`), and linter configs.

### Known limitations
- Gate bodies are verified offline (positive + negative); the live hook wiring
  should be smoke-tested in a real Claude Code session.
- Suppression detection is syntactic (see SKILL.md "Known gate limitations").

[Unreleased]: https://github.com/adeelahmad/agentic-agile/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/adeelahmad/agentic-agile/releases/tag/v0.1.0
