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
# 1) Build + install the gate backends (ctx-symbols; tells you how to get md-db)
./plugin/tools/install.sh
#    ensure ~/.local/bin (or ~/.cargo/bin) is on PATH

# 2) Add this repo as a marketplace and install the plugin
#    (inside Claude Code)
/plugin marketplace add /path/to/this/repo
/plugin install agentic-agile@agentic-agile-marketplace
```

Then run the planning skill interactively in your project; once Stage-2 is complete,
trigger the autonomous execution run.

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
| **md-db** | recommended | validates `.md` artifacts against `plugin/schemas/*.kdl` | external: `cargo install --path /path/to/md-db/crates/md-db-cli` |
| **Rust toolchain** | for the gates | the target repo's fmt/clippy/test/coverage matrix | rustup |

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
make install        # build + install ctx-symbols to ~/.local/bin (+ md-db guidance)
make link           # register THIS repo as a local marketplace and install the plugin
make ci             # everything CI runs: fmt-check · lint · test
make test           # ctx-symbols tests
make lint           # clippy -D warnings + shellcheck + JSON sanity
make validate       # claude plugin validate ./plugin --strict
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
