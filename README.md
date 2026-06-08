<div align="center">
  
  # 🤖 agentic-agile
  
  ### Agentic agile + autonomous TDD for Claude Code — AI coding agents that plan your sprint, then write the code with hook-enforced, deterministic gates.
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
  [![CI](https://github.com/adeelahmad/agentic-agile/actions/workflows/ci.yml/badge.svg)](https://github.com/adeelahmad/agentic-agile/actions/workflows/ci.yml)
  [![Claude Code](https://img.shields.io/badge/Claude%20Code-plugin-D97757)](https://docs.anthropic.com/en/docs/claude-code)
  [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
  [![Stars](https://img.shields.io/github/stars/adeelahmad/agentic-agile?style=social)](https://github.com/adeelahmad/agentic-agile/stargazers)
  
  *Determinism comes from hooks, not model goodwill.*
  
  </div>
  
  ---
  
  # agentic-agile

A Claude Code **plugin marketplace** containing the `agentic-agile` plugin:
**two-stage agile planning** (interactive, human-gated) followed by **two-phase TDD
execution** (autonomous, hook-enforced). Determinism comes from hooks, not model
goodwill — every sub-agent stop is intercepted by a deterministic gate that can
block the stop and feed the failure reason back to the supervisor.

> This repository is self-contained and publishable as-is. The plugin lives in
> [`plugin/`](plugin/); the marketplace catalog is
> [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json).

## Quick start

```bash
# 1) Build + install the gate backends (ctx-symbols + md-db, both from source)
#    requires a Rust toolchain >= 1.85 (rustup.rs or `brew install rust`)
./plugin/tools/install.sh
#    ensure ~/.local/bin (or ~/.cargo/bin) is on PATH

# 2) Add the marketplace and install the plugin (inside Claude Code)
/plugin marketplace add adeelahmad/agentic-agile
/plugin install agentic-agile@agentic-agile-marketplace
#    (for local dev, point marketplace add at your checkout instead: ./path/to/repo)
```

## Using it

The plugin ships one skill — **`agentic-agile`** — which acts as the *supervisor*. You
don't invoke the 9 sub-agents or the gates directly; the skill dispatches them and
reacts to gate verdicts. Two ways to start it inside Claude Code:

- **Just ask.** The skill is model-invoked, so it auto-triggers on build / ship /
  implement / add-a-feature / fix-via-TDD requests — even if you never say "agile":

  ```
  Build a rate limiter as a sprint with strict TDD.
  Plan and implement the CSV export feature — tests first, with gates.
  ```

- **Explicitly**, via the namespaced entry-point command:

  ```
  /agentic-agile:init
  ```

  (`init` is a thin alias that loads the same supervisor playbook; the underlying
  skill is also directly invokable as `/agentic-agile:agentic-agile`.)

Once started:

1. **Planning (you're in the loop):** intake → standards → planner produce the sprint
   contract + per-story `tasks.md` / `validate.md` / `plan.md`. The skill **stops for
   your approval** — it will not start building until Stage-2 is approved.
2. **Execution (autonomous):** after approval it runs RED → SCAFFOLD → GREEN →
   STRUCTURAL-REVIEW per wave, then a once-per-sprint FINAL-GATE, each enforced by a
   deterministic hook gate.

The gate backends (`ctx-symbols`, `md-db`) must be on PATH — see step 1 above. Without
them the gates WARN and fall back to grep (never a false block, never a silent pass).

## What it does

- **Planning** (human present): intake → standards → planner produce the sprint
  contract + per-story `tasks.md` / `validate.md` / `plan.md`.
- **Execution** (human absent): per wave, RED → SCAFFOLD → GREEN →
  STRUCTURAL-REVIEW, then once per sprint a FINAL-GATE. One worktree-isolated
  sub-agent per task; merge on pass, abandon the chain on a foundation-poisoning halt.

- **Lineage** (v0.2): every tool call is recorded to a global `lineage.jsonl` +
  per-task transcripts; each sub-agent gets a READ-ONLY task slice in its worktree;
  the supervisor reads the whole stream.
- **Retrospective + memory** (v0.2): every planning session distills recurring
  failures (and your own insights) into `docs/agents/memory.md`, injected into each
  sub-agent's contract.

Full operator playbook: [`plugin/skills/agentic-agile/SKILL.md`](plugin/skills/agentic-agile/SKILL.md).

## Prerequisites

| Tool | Required? | Purpose | Install |
|------|-----------|---------|---------|
| **ctx-symbols** | recommended | symbol uniqueness (`count==1`) + duplicate/orphan detection | `./plugin/tools/install.sh` (builds from `plugin/tools/ctx-symbols`) |
| **md-db** | recommended | validates `.md` artifacts against `plugin/schemas/*.kdl` | `./plugin/tools/install.sh` (builds from vendored `plugin/tools/md-db`, AGPL-3.0) |
| **Rust toolchain** | required to install | builds both backends; also runs the target repo's fmt/clippy/test/coverage matrix | rustup (>= 1.85) |

Both backends are optional: absent → gates WARN and fall back to grep (never a false
block, never a silent pass). See [`plugin/README.md`](plugin/README.md) for the gate
env-contract and how to retarget a non-Rust repo.

## Layout

```
.claude-plugin/marketplace.json   marketplace catalog (source: ./plugin)
plugin/                           the installable plugin (see plugin/README.md)
docs/                             design + architecture docs for this plugin
  ARCHITECTURE.md DESIGN.md PLATFORM-NOTES.md KICKSTART.md
  agentic-agile-design.html diagrams/
DEVLOG.md                         build journal + review dispositions
```

## Development (Makefile)

`make` (no target) prints all targets. Common ones:

```bash
make install        # build + install ctx-symbols and md-db to ~/.local/bin
make link           # register THIS repo as a local marketplace and install the plugin
make ci             # everything CI runs: fmt-check · lint · test · eval-validate
make test           # ctx-symbols + md-db unit tests
make lint           # clippy -D warnings + shellcheck + JSON sanity
make validate       # claude plugin validate ./plugin --strict
make eval-validate  # validate every eval suite's JSON (no tokens)
make eval SUITE=…   # run one eval suite live (YES=1 spends tokens; see scripts/eval/)
make hooks          # install the tracked git hooks (.githooks → core.hooksPath)
make smoke          # offline gate smoke test
make release        # verify (ci+validate+version-check) then tag vX.Y.Z
make publish        # push branch + tags to origin
```

Git hooks (opt in with `make hooks`): **pre-commit** runs `fmt-check · json ·
shellcheck`; **pre-push** runs `lint · test`. Bypass with `SKIP_HOOKS=1`.

## Versioning & changelog

[SemVer](https://semver.org); see [`CHANGELOG.md`](CHANGELOG.md). Keep the version in
`plugin/.claude-plugin/plugin.json`, `plugin/tools/ctx-symbols/Cargo.toml`, and the
top `CHANGELOG.md` entry in lockstep — `make version-check` (and `make release`)
enforce this. Tag releases `vMAJOR.MINOR.PATCH`.

## First publish

```bash
git init && git add -A && git commit -m "agentic-agile v0.1.0"
git remote add origin <your-repo-url>
make hooks          # optional: enable local git hooks
make ci             # green before tagging
make release        # tags v0.1.0
make publish        # pushes branch + tags
```

## Continuous integration

`.github/workflows/ci.yml` runs on every push/PR:

- **ctx-symbols** — `cargo fmt --check`, `cargo clippy -D warnings`, `cargo test`.
- **shellcheck** — lints every gate script (`plugin/bin/*`), errors fail the build.
- **plugin validate** — JSON sanity on the manifest + marketplace, then
  `claude plugin validate ./plugin --strict` (installs the Claude Code CLI).

## Status

Plugin implemented for a **Rust** target; gate bodies verified offline (positive +
negative) against a sample one-story sprint. Before relying on it: smoke-test the
hook wiring in a live Claude Code session (CI runs `plugin validate` but not a live
session). Set the real `repository` URL in `plugin/.claude-plugin/plugin.json` when
you create the public repo.

## License

MIT — see [`LICENSE`](LICENSE). `ctx-symbols` is harvested from the MIT-licensed
`ctxconfig` code-intelligence layer (see `plugin/tools/ctx-symbols/README.md`).

`plugin/tools/md-db/` is **vendored third-party source under AGPL-3.0-or-later**
([decisiongraph/md-db-rs](https://github.com/decisiongraph/md-db-rs)), kept under its
own [`LICENSE`](plugin/tools/md-db/LICENSE). It is built into a standalone `md-db`
binary the gates shell out to — the MIT plugin code links to none of it — but anyone
redistributing this repository must honor AGPL-3.0 terms for that subtree.
