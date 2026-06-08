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
