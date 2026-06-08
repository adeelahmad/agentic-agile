# agentic-agile plugin — Dev Log

## Working State
**Session:** 1 | **Date:** 2026-06-07

### Active Task
Build the `agentic-agile` Claude Code plugin from the DESIGN package.
- [x] Resolve OPEN-1/2/3/4/7/8 (all at recommended defaults)
- [x] TARGET = new Rust workspace at `./target-demo` (per user: "create new dir here")
- [x] Extract + install `ctx-symbols` (OPEN-8)
- [x] Populate `plugin/skills/agentic-agile/SKILL.md` (OPEN-2)
- [x] Fill 4 gate bodies + shared `bin/_gatelib.sh` (Rust commands)
- [x] Fix manifest (`skills` key); confirm hooks.json per OPEN-3
- [x] Dry-run one-story sprint through RED→SCAFFOLD→GREEN→STRUCTURAL→FINAL (pos+neg)
- [x] code review (rust-reviewer + code-reviewer) → fixed all CRITICAL/HIGH

### Key Files (current shape)
- **`plugin/skills/agentic-agile/SKILL.md`** — canonical supervisor playbook: 2-stage
  planning, 2-phase TDD, data-plane writers, §12 corrections, escalation, guardrails.
- **`plugin/tools/ctx-symbols/`** — harvested Rust CLI (`count`/`locate`/`search`/`conflicts`).
  17 tests green, clippy clean, pinned to Rust 1.77. Installed at `~/.local/bin`.
- **`plugin/bin/_gatelib.sh`** — shared gate helpers (md-db fallback, standards-matrix
  runner, ctx-symbols detection, diff-scope, suppression grep).
- **`plugin/bin/gate-{red,scaffold,green,structural-integrity,final}-verify`** — filled
  for Rust; matrix read from standards.md, not hardcoded.
- **`target-demo/`** — Rust crate + `docs/agents/sprint1/` sample sprint used for the dry-run.

### Decisions (resolved OPENs, all defaults)
- OPEN-2 replace · OPEN-1 dispatched scaffolder + body-guard · OPEN-3 supervisor
  self-check (`gate-stage2-complete`) · OPEN-4 per-task `T<k>/attempt-K/` · OPEN-5 fresh
  output.md/attempt · OPEN-6 MAX=3 · OPEN-7 add frontmatter · OPEN-8 extract ctx-symbols.

### Verified (dry-run, target-demo)
- RED: exit 0 (compiles vs mod-common shim, fails by assertion); exit 2 on vacuous RED.
- SCAFFOLD: exit 0 (count==1, panic+TODO, no shim); exit 2 on duplicate def and on a real body.
- GREEN: exit 0 (standards matrix fmt+clippy+test green, in scope); exit 2 on suppression and out-of-scope.
- STRUCTURAL: exit 0 clean; exit 2 on HIGH duplicate (foundation-poisoning → HALT).
- FINAL: exit 0 (matrix + all ticked + no suppression); exit 2 on unticked box.
- stage2 / plan-shape / validate-artifact / ledger / standards-cited: all pass; md-db
  absent → WARN+fallback (never a false block, never a silent pass).

### Watch Out
- `md-db` is now **vendored** at `plugin/tools/md-db/` (AGPL-3.0) and built by
  `install.sh`; no longer an external prereq. `make install` builds both backends.
- Build now needs **Rust >= 1.85** (vendored md-db deps use edition 2024). Local
  toolchain upgraded 1.77.2 → 1.96.0 (Homebrew) this session.
- ctx-symbols must be on the hook's PATH (`~/.local/bin` or `~/.cargo/bin`).

---

### Session 2 — 2026-06-08: Vendor md-db so `make install` is self-contained
**What:** `make install` failed (cargo 1.77 couldn't read a v4 Cargo.lock; md-db was an
unbuildable external prereq). Vendored `decisiongraph/md-db-rs` into `plugin/tools/md-db/`
(AGPL-3.0, own LICENSE), wired `install.sh` + `Makefile` to build+install it from source.
Upgraded Rust 1.77.2→1.96.0 (vendored deps need edition 2024); pinning to MSRV 1.77 was
whack-a-mole, so upgrade was the durable fix. All 4 plugin KDL schemas parse + validate
under the vendored binary; md-db unit tests green; shellcheck/json clean.
**Files:** plugin/tools/md-db/ (new, vendored), plugin/tools/install.sh, Makefile,
README.md, plugin/README.md.
**License note:** repo is MIT + one vendored AGPL-3.0 subtree (disclosed in README).
- Gate diff-scope uses the working tree unless `BASE_REF` is set; the supervisor should
  set `BASE_REF`, `SCOPE_GLOBS`, `TEST_GLOBS`, `SCAFFOLD_SYMBOLS`, `STANDARDS_FILE`,
  `ATTEMPT_DIR`, `REPO_DIR` per dispatch (contract documented in `bin/_gatelib.sh`).

---

## Review findings — disposition
**Fixed (all CRITICAL + HIGH):** impl-block over-count in `count` (broke count==1);
panicking `Default` impl removed; JS/TS const+function double-count; unguarded byte-slice;
`--tree` with no value now errors; `gate-standards-cited` `set -e` foot-gun + silent pass
(now a real citation check); `changed_paths_filter` pipefail `|| true`; `symbol_count`
fallback guard; awk heading-match consistency; `type:` checks scoped to the frontmatter block.
**Deferred (MEDIUM/LOW, non-blocking):** per-symbol source clone perf (small trees);
`is_excluded` substring on dirs named dist/build/target (documented); body-slice standalone
re-parse stability; JSON path sed escaping (impossible on unix paths). assert_no_suppression
syntactic gap is documented as a known limitation in SKILL.md.

## Milestones
- [x] Plugin builds, ctx-symbols installs, all gates verified pos+neg on a dry-run sprint.
- [ ] Install `md-db` and re-verify artifact validation with the real backend.
- [ ] Live Claude Code session test of the hook wiring (offline gate tests done).

## v0.2 — lineage, retrospective/memory, review fixes

Review dispositions (from the gap analysis):
- Added the two missing manifests (plugin.json + marketplace.json) — the install blocker.
- Rewired final-gate to SubagentStop (was Stop; it is dispatched as a sub-agent).
- gate-scaffold-verify: symbols now come from .agentic/scaffold-symbols, and shim
  detection uses the `// agentic:shim` marker (no longer collides with tests/common).
- Added .agentic/task.env so the gates get their per-task contract for real (closes the
  env-injection gap; _gatelib sources it).

New capability:
- Task-scoped lineage (bin/lineage) + the every-planning retrospective/memory loop
  (archivist + memory.kdl). Lineage feeds memory; memory feeds init.md.

## End-to-end self-check dry run (v0.2)
Walked a throwaway `calc` crate through the full lifecycle, running each gate twice —
on good work (expect PASS) and on planted bad work (expect BLOCK). 18/18 matched.
Two real defects caught and fixed: (1) gate scripts shipped non-executable; (2) the
diff-scope filter counted the plugin's `.agentic/` control dir as worker scope.
Dynamic cargo/md-db/ctx-symbols branches WARN-degrade (no toolchain in the harness);
all structural checks ran for real.
