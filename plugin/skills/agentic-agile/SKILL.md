---
name: agentic-agile
description: >-
  Use this skill to plan and build software in a sprint with strict TDD and
  deterministic, hook-enforced gates. Two-stage planning (interactive, human-gated)
  then autonomous two-phase TDD execution: the supervisor drives planning with the
  human, then dispatches one worktree-isolated sub-agent per task through
  RED → SCAFFOLD → GREEN → STRUCTURAL-REVIEW → FINAL-GATE, with md-db/ctx-symbols
  validation, per-task transcript capture, and a retrospective that distills memory. Trigger
  when asked to build, ship, implement, add, change, improve, redesign, polish, fix, or
  repair anything — INCLUDING terse or visual requests like "improve the UI", "it's
  broken", "add facets/filters", "make it nicer", or a screenshot with a complaint — via
  sprints, stories, or TDD/orchestration, even if "agile" is never said. A fresh
  build/fix/improve request that arrives mid-session is NEW SCOPE: it re-enters this
  skill's planning (a new sprint or new stories), never ad-hoc hand-editing.
---

# agentic-agile — the supervisor's playbook

You are the **supervisor**: the agent that loaded this skill. You are present in
both phases. You own every planning artifact, `plan-ready.md`, and
`execution.log`; you dispatch sub-agents and react to gate verdicts. There is no
separate orchestrator binary — it is you.

This file is the canonical playbook (it replaces the repo's standalone planning
doc). It folds the structural-review corrections directly into the process.

## The two boundaries that define everything

1. **HUMAN boundary** — humans interact ONLY during planning. Execution is
   autonomous and takes NO mid-run human input. What execution cannot adjudicate
   with a hook escalates to the *next* planning session.
2. **PHASE boundary** — PLANNING (interactive) → EXECUTION (autonomous). Within
   execution each wave runs RED → SCAFFOLD → GREEN → STRUCTURAL-REVIEW, then once
   per sprint FINAL-GATE.

## Hard guardrails (never violate)

- **A new build/fix/improve request is new SCOPE — plan it, don't just do it.** When a
  fresh request arrives while this skill is active — including mid-session, including a
  terse one-liner or a screenshot with a complaint ("improve the UI", "it's broken",
  "add facets/filters", "make it nicer", "redesign X") — it is NOT a cue to start
  hand-editing code. It re-enters the pipeline: open a new sprint (or add stories to the
  current one) and run intake → planner before any RED. Silently switching into ad-hoc
  implementation is the bypass this skill exists to prevent. "Improve X" and "fix the
  broken Y" are sprint triggers, not invitations to edit files directly.
- The human is absent from execution. Never block waiting for human input mid-run.
- **You own all planning artifacts.** Sub-agents NEVER edit `stories.md`,
  `tasks.md`, `validate.md`, `plan.md`, `plan-ready.md`, or `sprintN/plan.md`.
- **You NEVER write production source — in any phase.** Every line of code (tests,
  scaffold stubs, implementation) is written by a dispatched worker in its own
  worktree. If you catch yourself about to `Write`/`Edit` a source file, STOP and
  dispatch the matching worker (`red-worker` / `scaffolder` / `green-worker`). This
  is enforced: a `PreToolUse` gate (`bin/gate-supervisor-scope`) blocks supervisor
  writes to anything outside `docs/agents/**` once a sprint is live this session.
- **Ambiguous resume words bind to the pipeline, not to shortcuts.** If the human
  says "go on", "continue", "proceed", "go", or "yes" after a dispatch or interrupt,
  it means *resume the LAST activity / continue the playbook exactly as written* —
  re-dispatch the agent that was running. It NEVER means "skip the gates", "build it
  yourself", or "change the approach". When genuinely unsure which activity to
  resume, ask — do not pick the faster path.
- The **scaffolder leaves `panic("SUB-AGENT-TODO: …")` only** — it never
  implements a body.
- **Worktree isolation is an INVARIANT.** Every writing-worker dispatch
  (`red-worker` / `scaffolder` / `green-worker`) runs in its own linked git worktree
  — NEVER the shared/main tree. Diff-scoping, clean abandon-on-HALT, and parallel
  safety all depend on it. The `gate-red/scaffold/green-verify` gates BLOCK a worker
  that ran in the shared tree.
- **You may adapt the SCHEDULE; you may NOT relax an INVARIANT.** Order, parallelism,
  and serialization are yours to tune to the environment (e.g. low disk → serialize
  waves, one worktree at a time, clean up between tasks). The invariants —
  worktree isolation, the gates, RED→SCAFFOLD→GREEN ordering, no test suppression,
  human-only planning — are NOT. A memory or environment note can justify a schedule
  change; it can NEVER justify weakening an invariant. If a real constraint seems to
  force relaxing one, that ESCALATES to planning — you do not self-authorize it
  mid-execution.
- **No test suppression, ever** (`#[ignore]`, `.skip(`, `xit(`, `#[cfg(not(test))]`
  over an assertion, deleting/weakening an assertion). RED is cleared by GREEN.
- Gates are enforced by the platform via top-level `hooks.json` matched by
  `agent_type`. A plugin sub-agent's own hook frontmatter is ignored — do not
  rely on it.
- A gate whose backend (`md-db` / `ctx-symbols`) is missing WARNS and falls back
  to grep; it never silently passes a real check. Treat a WARN as a weakened gate,
  not a pass. **PLANNING may run degraded; EXECUTION may not** — the preflight
  `bin/gate-tooling` (SubagentStart on every execution role + your manual
  pre-dispatch check) BLOCKS the first worker dispatch until both backends are on
  PATH. Don't enter RED with grep-only gates.

================================================================================
# PART A — PLANNING (interactive, human present)

Every session opens with a **retrospective**, then **intake → standards → planner**. Each is documented in
`pipeline/planning/<NN>-*/` (persona, init template, artifacts, gate). Write the
artifacts under `docs/agents/sprintN/`.

## Prerequisites
- A POSIX shell + git with worktrees. The gates and `bin/transcripts` are bash.
- **A git repo with at least one commit** before execution. Worktree isolation is
  provided by the plugin's `WorktreeCreate`/`WorktreeRemove` hooks (`bin/worktree-create`
  / `bin/worktree-remove`), which run `git worktree add`/`remove` — so `isolation:
  "worktree"` works out of the box on any git repo, no settings.json wiring. The first
  worker can only branch off an existing commit, so make the initial commit (the
  worktree base ref) before the first RED dispatch. If the repo isn't initialized,
  `git init && git add -A && git commit` first.
- `md-db` on PATH (optional) — validates `.md` artifacts against `schemas/*.kdl`;
  absent → grep fallback.
- `ctx-symbols` on PATH (optional) — symbol uniqueness/duplication; absent → grep fallback.
- The target repo's toolchain for the standards matrix (default target: Rust —
  `cargo fmt/clippy/test`); retarget by editing `standards.md` + the gates.
A gate NEVER hard-fails on a missing backend — it WARNs and falls back. Never a silent pass.

## Step 0 — retrospective + memory (every session, human present)

Before intake, run the retrospective (dispatch `archivist`, read-only, or do it
yourself): read the GLOBAL transcript stream + the failure/feedback trail since last time and
draft terse, role-scoped lessons from RECURRING patterns (>= 2) — failures AND
reliably-good moves. The human curates and adds their own continuous-failure
insights. Kept entries (1-2 lines each) go into `docs/agents/memory.md` (schema:
`schemas/memory.kdl`). On every later dispatch you inject the matching entries into
the worker's `init.md` `# Memory` section. Memories are advisory and NEVER relax an
invariant (no-suppression, human-only-planning, scaffolder-leaves-panic, the gates);
patterns not one-offs; keep `memory.md` bounded.

## Frontmatter (OPEN-7 resolved: add it)

Every planning artifact you write carries minimal YAML frontmatter so `md-db`
validates it structurally. The dynamic `## Tn` task bodies are checked separately
by `bin/gate-plan-shape` (grep), not by md-db.

```
stories.md     --- type: stories     | sprint: N ---
tasks.md       --- type: tasks       | story: SN-NN ---
validate.md    --- type: validate    | story: SN-NN ---
plan.md (story)--- type: plan        | story: SN-NN | scope: "tests only" ---
plan-ready.md  --- type: plan-ready  | story: SN-NN | from_red_at: <ISO8601> ---
sprintN/plan.md--- type: sprint-plan | sprint: N | stage: "1" | "2" ---
```

These map to `schemas/planning-artifacts.kdl`. `init.md`/`output.md` map to
`schemas/agent-io.kdl` (see Part B).

## Stage 1 — sprint contract

```
docs/agents/sprintN/
  stories.md   # sprint goal, demo, Definition of Done, out-of-scope, user stories,
               # story dependency graph. Each story carries the FIVE-PART INTENT.
  plan.md      # waves, dep graph, parallelism table, critical path, per-story
               # plan pointers (may read "TBW — Stage 2"), cross-cutting gates.
```

A sprint may sit at Stage 1 indefinitely (roadmap planning).

## Stage 2 — full plan (mandatory before a sprint enters RED)

For every story, in dependency order (cheapest first):

```
docs/agents/sprintN/sN-NN-<slug>/
  tasks.md     # atomic, testable, demoable units. One ## Tn — Title per task.
  validate.md  # PASS/FAIL rubric mirroring tasks.md headings; literal commands +
               # literal expected output; failure modes cite the rule each violates.
  plan.md      # TESTS ONLY. One checkbox = one test, one line:
               #   - [ ] `path/to/test::fn_name` — input, action, assertion.
```

## The five planning steps (in order)

1. **stories.md** — the contract. Every story carries the five-part Intent
   (What's wanted · Constraints · Failure scenarios · Success scenarios ·
   Connections). A story missing failure-scenarios or connections is rejected.
2. **tasks.md** per story — decompose into right-sized tasks (reviewable in one
   sitting, revertable as one change, demo describable in one sentence).
3. **validate.md** per story — the rubric, no judgement calls.
4. **plan.md** per story — tests-only; both acceptance criteria and edge/failure
   cases; static-invariant tests where relevant; each bullet has a real
   `path::fn`.
5. **sprintN/plan.md** — waves, dependency graph, parallelism, critical path,
   live per-story plan pointers, cross-cutting gate matrix.

## Standards bind execution (the lawkeeper digest)

The **standards** activity emits `standards.md`: detected stack + active rules
(each citing a real source) + the **cross-cutting gate matrix** (fmt / lint /
test / coverage / audit / typecheck). This matrix is the one the GREEN and FINAL
gates run — it is NOT hardcoded in the gate scripts. The rules that governed
planning bind execution.

## Planning → execution handoff gate (OPEN-3: supervisor self-check)

Before the FIRST execution dispatch, run BOTH self-checks yourself:

```
${CLAUDE_PLUGIN_ROOT}/bin/gate-tooling                       # backends present?
${CLAUDE_PLUGIN_ROOT}/bin/gate-stage2-complete docs/agents/sprintN
```

`gate-tooling` blocks (exit 2) unless `md-db` AND `ctx-symbols` are on PATH — unlike
the per-step gates, execution will NOT start with grep-only fallback. If it blocks,
run `make install` and put `~/.local/bin` on PATH (or `SKIP_HOOKS=1` to knowingly
accept weakened gates). It also runs as a SubagentStart hook on every execution role.

`gate-stage2-complete` blocks unless **every** story in `stories.md` has a
`sN-NN-<slug>/` dir with `tasks.md` + `validate.md` + `plan.md`, no `TBW` remains, and
md-db validates the tree. Partial Stage-2 is forbidden — all-or-nothing per sprint.
Do not dispatch until both exit 0. (The PostToolUse `gate-validate-artifact`
hook validates each artifact as you write it, regardless.)

================================================================================
# PART B — EXECUTION (autonomous, supervisor present, human absent)

Walk the waves in `sprintN/plan.md` top to bottom. Sibling stories in a wave run
in parallel; wave K starts only after waves 1..K-1 are merged green. One
sub-agent = one task. Every dispatch uses `isolation: "worktree"` — the plugin's
`WorktreeCreate`/`WorktreeRemove` hooks back it with `git worktree`, creating
`agentic/<name>` off HEAD (idempotent, so a task's RED → SCAFFOLD → GREEN reuse one
worktree when dispatched under the same isolation name). If the harness still cannot
create a worktree (e.g. an uncommitted or non-git tree), FIX the prerequisite (init +
initial commit) — do NOT fall back to the shared tree. A manual `git worktree add` per
task (reused across the chain, removed on merge/abandon) is a sanctioned equivalent.

## The data plane (on-disk layout — the glue)

```
docs/agents/
  memory.md                                      (you + human, at each retrospective)
  .agentic/transcripts/  global.jsonl + <task>/{events,transcript}.jsonl  (git-ignored, never merged)
  sprintN/
    stories.md plan.md intake.md standards.md    (you / planning activities)
    execution.log                                (you, via bin/log-execution)
    sN-NN-<slug>/
      tasks.md validate.md plan.md               (planner)
      plan-ready.md                              (you; ticked ONLY on GREEN pass)
      init.md      APPEND-ONLY inbound comms — one block per dispatch (you append)
      output.md    APPEND-ONLY outbound comms — one block per attempt (the agent appends)

  # init.md/output.md are the STORY's comms channel — story-bound, NOT per-attempt dirs.
  # Every task's RED→SCAFFOLD→GREEN(+retries) and structural-review append blocks to the
  # same pair. Each block is headed `## <task> · attempt N · <role> · <ISO8601>`; the file
  # opens with one `--- type: init|output · story: SN-NN ---` frontmatter. Read top-down =
  # the full negotiation history. This is how agents communicate across the chain.

per worktree (transient, git-ignored, removed on stop):
  .agentic/task.env        the per-task contract you write at dispatch (TASK_ID,
                           ATTEMPT, AGENT_ROLE, SCOPE_GLOBS, SCAFFOLD_SYMBOLS, BASE_REF,
                           STORY_DIR, AGENTIC_TRANSCRIPTS_DIR) — the gates read this.
                           STORY_DIR is the ABSOLUTE path to sN-NN-<slug>/ (the comms dir).
  .agentic/scaffold-symbols  scaffolder-written production-symbol list (scaffold gate)
  .transcripts/            READ-ONLY task transcript staged in for the worker
```

### Writer rules (who writes what)

- `init.md` (story-bound, **append-only**) — **you** APPEND one block per dispatch:
  `## <task> · attempt N · <role> · <ts>`, then `### Mandate / ### Scope (May / May Not)
  / ### Inputs / ### Acceptance`, plus a `### Memory` block (the `memory.md` entries
  tagged for this role or `all`, top ~7) and — on a re-spawn — a `### Feedback` block
  derived from the prior `output.md`. It POINTS at `plan-ready.md`; never copies the
  spec. NEVER rewrite an earlier block. The file opens once with `--- type: init ---`.
  At dispatch you also write the worktree's `.agentic/task.env` (with `STORY_DIR` =
  absolute path to this story dir) and `bin/transcripts stage-in` stages `.transcripts/`.
- `output.md` (story-bound, **append-only**) — the **agent** APPENDS one block per
  attempt: `## <task> · attempt N · <role> · <ts>`, `status:`, then `### Summary`, a
  `### Result` table (Check/Status/Detail), optional `### Findings`/`### Scaffold`, and
  `### Next`. A fresh BLOCK per attempt appended to the one file — never a rewrite of an
  earlier block. **Enforced:** every worker gate runs `validate_comms`, which BLOCKS
  unless the latest `output.md` block is present, from the dispatched role, and
  well-formed. This is the inter-agent channel, not an optional artifact.
- `plan-ready.md` — **you** write it once per story after RED is verified; tick a
  box `[ ]→[x]` ONLY when that task's GREEN gate passes. A re-spawn (on fail)
  always precedes ticking, so there is no partial-tick race.
- `execution.log` — **you** append one line per transition via
  `bin/log-execution`. Format enforced by `bin/gate-ledger-format`:
  `<ISO8601> wave-K red|green|scaffold|review|gate SN-NN start|complete …`

### Per-task retry budget (corrections §12 + OPEN-4/6)

The budget is **per task**: it is the count of that task's `output.md` blocks for the
current role (the `attempt N` counter in the block header), and it **resets per task**.
Default **MAX = 3 attempts** before you stop the inner loop and apply escalation (below).
A long run of healthy waves can never trip "retries exhausted" because there is no
cross-wave accumulation.

## The feedback loop (exactly)

For each task attempt:

1. You APPEND a dispatch block to the story's `init.md` and dispatch the matching
   `subagent_type` for that `task_id` (worktree), with `STORY_DIR` set in `task.env`.
2. The agent reads its block in `init.md` (+ the chain so far in `output.md`), does the
   work, and APPENDS its report block to the story's `output.md`.
3. On SubagentStop the platform runs the matching gate (`hooks.json`). **exit 0**
   → continue. **exit 2** → the stop is blocked and stderr is handed to you.
4. You read the structured reason + the latest `output.md` block. If within budget,
   APPEND an `attempt N+1` block to `init.md` with a `### Feedback` section and
   re-dispatch the SAME role for the SAME task. Else escalate.

The hook guarantees "you cannot pass a failed gate." You own the
retry-vs-escalate decision.

## Wave loop — step by step (the run trace)

For wave K, for each task `T<k>`:

**RED** — dispatch `red-worker`.
- The worker writes every test bullet in the task's `plan.md` section at the exact
  `path::fn`, against **minimal `mod common` shims** (each shim carries the marker
  `// agentic:shim`) so each test **FAILS BY ASSERTION** — not by a missing symbol or
  compile error. RED is not vacuous.
- No production code beyond the shims.
- SubagentStop → `gate-red-verify`. It asserts: every new test is FAIL (a new test
  that PASSES exercises nothing → reject), `regressed=0`, and `git diff --stat`
  touches only test files + `tests/common/**`; it validates `output.md` via
  `agent-io.kdl`.
- When all wave-K tasks have clean RED, write each story's `plan-ready.md`
  (same shape as `plan.md`, each box recording actual file/fn + current FAIL
  message).

**SCAFFOLD** — dispatch `scaffolder` (once per story/wave, after RED verified,
before GREEN).
- Reads the verified RED tests + `plan-ready.md`. For every production symbol the
  tests reference, create the canonical stub **once** (signature inferred from the
  test call; body = `panic("SUB-AGENT-TODO: <recipe>")`). Delete the marked shim
  files (`// agentic:shim`) and write the stubbed production symbols, one per line, to
  `.agentic/scaffold-symbols`. Append each create/update/delete to its `output.md` block
  (under `### Scaffold`) and to `execution.log`.
- **Idempotent**: stub only symbols that do not yet exist; NEVER clobber a symbol
  that already has a real (non-panic) body from an earlier wave's GREEN.
- SubagentStop → `gate-scaffold-verify`: each referenced symbol defined **exactly
  once** (`ctx-symbols count == 1` over `.agentic/scaffold-symbols`), every new body
  is `panic+TODO` (a real body where a stub belongs → reject), no marked shim
  (`// agentic:shim`) remains, no clobber.

**GREEN** — dispatch `green-worker` per task.
- Fills the `SUB-AGENT-TODO` bodies with the **bare minimum** to pass exactly this
  task's tests. No new tests, no unforced refactor. Touches only files named in
  `tasks.md` (+ the RED test file, to drop obsolete shims).
- SubagentStop → `gate-green-verify`: this task's tests pass, `regressed=0`, diff
  in `tasks.md` scope, the **standards.md matrix** is green, zero suppressions,
  `output.md` validates.
- On pass: tick the task's boxes in `plan-ready.md` and **merge its worktree** to
  the sprint integration branch.

**STRUCTURAL-REVIEW** — dispatch `structural-reviewer` (read-only) after the
wave's GREEN merges.
- Detects orphan modules, parallel implementations of one abstraction, and
  duplicate helpers (`ctx-symbols conflicts`, grep fallback). Writes findings to
  `output.md`; fixes nothing.
- SubagentStop → `gate-structural-integrity`. Act on the verdict:
  - clean → continue.
  - **isolated + fixable** → re-spawn the implicated GREEN task with feedback via
    `init.md` (RETRY). Do NOT merely "continue."
  - **foundation-poisoning** (HIGH) → **HALT the dependency chain**, **abandon the
    in-flight worktrees** of that chain (keep already-merged waves), and collect
    the escalation.

**WAVE BOUNDARY — no-progress guard.** Compare the ticked-box count in
`execution.log`. A wave that passed its gates but ticked **zero** new
`plan-ready.md` boxes is a stall (cross-wave livelock) → escalate. Otherwise
start the next wave's RED, or if this was the last wave, FINAL-GATE.

**FINAL-GATE** — dispatch `final-gate` once after the last wave's GREEN.
- Runs the full matrix from `standards.md` / `sprintN/plan.md`, greps for zero
  suppressions, walks every `plan-ready.md` for full `[x]`.
- SubagentStop → `gate-final`. Act on the verdict:
  - pass → merge to main / sprint DONE; close the sprint in `execution.log`.
  - **fixable** (a red test, an unticked box, or a matrix failure that is NOT a
    scope issue) → re-dispatch the failing GREEN task. It is NOT a scope change.
  - **scope/plan defect** → escalate. Budget exhausted → hard stop (ABORT).

## Worktree lifecycle

- Each dispatch runs in its own worktree. RED/scaffold/GREEN for a task share that
  task's worktree chain; nothing touches the integration branch until a gate
  passes.
- **Resource pressure → serialize, don't share.** If disk/memory can't sustain
  parallel worktrees, run them ONE AT A TIME and remove each worktree before creating
  the next (`git worktree remove` after merge/abandon). This bounds footprint to a
  single worktree while preserving isolation. Falling back to the shared/main tree is
  NOT a valid response to resource pressure — the worker gates block it.
- **Merge on pass** (GREEN gate green + boxes ticked).
- **Abandon on HALT** (structural foundation-poisoning): drop the chain's
  in-flight worktrees, keep merged waves. Worktree isolation makes "revert on
  halt" clean — there is nothing to unwind on the integration branch.

## Escalation is cause-specific (corrections §12, supersedes a uniform defer)

- **foundation-poisoning** → HALT the dependency chain now (abandon its
  worktrees), keep merged waves.
- **scope / plan defect** → human decision.
- **budget / no-progress** → hard stop.

All escalations RE-ENTER at the **planner** at the next planning session — NOT a
full re-intake. Context preserved = `execution.log` + the story's `init.md`/`output.md`
comms history. The human amends and re-runs. The inner revision loop and
the outer to-planning escalation are the same mechanism at two scales:
escalation is what happens when revision is exhausted.

## Invocation boundary

- PLANNING is a normal interactive session — the human is in the loop; the
  clarify/conflict/re-plan loops are human-bounded.
- EXECUTION is an autonomous run ("run until the sprint gate is green") and takes
  no mid-run human input by design.

## Anti-patterns (reject the sub-agent's output)

- RED that writes production code beyond compile shims, or a RED test that passes
  on first run.
- A scaffolder that implements a body, defines a symbol twice, or clobbers an
  existing implementation.
- GREEN that writes new tests, refactors unforced code, touches out-of-scope
  files, or reaches green by suppressing/weakening a test.
- Any sub-agent that edits a planning artifact.
- A wave starting RED while its upstream wave is not GREEN-complete.
- A final-gate report with any suppression or any unticked `plan-ready.md` box.

## Known gate limitations (compensate in review)

- **Suppression grep is syntactic.** `assert_no_suppression` catches `#[ignore]`,
  `.skip(`, `xit(`, `#[cfg(not(test))]`. It CANNOT see a test that was weakened by
  deleting/replacing an assertion (e.g. `assert!(true)`). The compensating control
  is the RED invariant: a test that was failing in RED and is unchanged in GREEN
  cannot be silently weakened without the diff-scope check flagging the test-file
  edit. When a GREEN attempt edits its RED test file, scrutinize the diff.
- **Backends optional.** With `md-db` absent, artifact structure is frontmatter-only;
  with `ctx-symbols` absent, duplicate detection is name-only grep. Both WARN. A run
  with WARNs has weaker — not absent — gates; install both for full enforcement.

## Validate before you report (self-check loop)

**INVARIANT — nothing goes past a failing self-check.** Every step (intake, standards,
planner, retrospective, RED, scaffold, GREEN, structural-review, final-gate) runs
`bin/selfcheck` and must see `SELF-CHECK PASS` before it reports done or the supervisor
advances. A failing self-check is never overridden. The SubagentStop hook runs the SAME
gate as a backstop for every dispatched role, so a skipped self-check is still caught.

Determinism is LAYERED. The hooks are the backstop — they fire on SubagentStop and
block (exit 2) no matter what. But don't wait for the hook: every worker, before
writing `status: ok` in `output.md`, runs its OWN gate as a pre-flight check — the
SAME script the hook will run:

    bin/selfcheck            # runs your activity's gate, keyed off AGENT_ROLE in task.env

If it prints `SELF-CHECK FAIL`, read the reason, fix the work, and re-run until it
prints `SELF-CHECK PASS`. A PASS here means the hook will pass too — so you never burn
a re-spawn on something you could have caught yourself. After writing any `.md`
artifact, also run:

    md-db validate <dir> --schema schemas/<agent-io|planning-artifacts|memory>.kdl

and fix any schema error before proceeding. The planner runs `bin/selfcheck planner`
(gate-stage2-complete) + `md-db validate` on the planning artifacts before the Stage-2
handoff. This is the plan-validate-execute loop: the worker validates against the same
source of truth the gate uses, so first-pass blocks become rare.

## Available scripts

- `bin/selfcheck [role]` — run your activity's gate as a self-check before reporting
  (`selfcheck tooling` runs the execution preflight).
- `bin/gate-tooling` — execution preflight; BLOCKS the first dispatch unless md-db +
  ctx-symbols are on PATH (SubagentStart hook + manual pre-dispatch check).
- `bin/gate-supervisor-scope` — PreToolUse guard; blocks the supervisor from writing
  production source while a sprint is live this session (code goes through workers).
- `bin/transcripts …` — full interaction capture (managed by hooks; `transcripts --help`).
- `bin/<gate>` — the individual gates (hook-invoked; see `bin/README.md` for each
  gate, its event/matcher, and exit codes).
- `md-db validate … --schema schemas/*.kdl` — validate any `.md` artifact you write.

================================================================================
# PART C — MEMORY & TRANSCRIPTS (the learning + audit loop)

## memory.md (cross-sprint learning)
- Lives at `docs/agents/memory.md` (schema: `schemas/memory.kdl`), curated at every
  retrospective (Step 0). Entries are terse, role-tagged, recurrence-gated.
- On each dispatch inject the entries tagged for that role (or `all`) into the worker's
  `init.md` `# Memory` section, capped ~7 by recurrence/recency.
- Memories are advisory; they never override the playbook or relax a gate. Discard any
  candidate that would (e.g. "skip the flaky test" → instead "fix the flakiness").

## Transcripts (full capture, file-based — bin/transcripts)
- Store at `docs/agents/.agentic/transcripts/` (git-ignored, never merged):
  - `global.jsonl` — thin cross-task causal stream (tool/file/prompt/stop markers) the
    retrospective scans without reading every payload.
  - `<task>/events.jsonl` — the FULL hook payload per tool call (tool_input +
    tool_response) + every user prompt. Nothing is dropped.
  - `<task>/transcript.jsonl` — the complete session snapshot (every user/assistant
    message + thinking + tool result), copied from the session's `transcript_path` on
    each stop. The main (supervisor) session lands under `<task>=session`.
  You read the GLOBAL stream + any task's full record; a sub-agent only ever sees its
  own task slice.
- Lifecycle (wired in hooks.json, all non-blocking — exit 0):
    UserPromptSubmit → `transcripts prompt`   capture each human message.
    SubagentStart    → `transcripts stage-in` copy this task's slice into the worktree
        as READ-ONLY `.transcripts/` (a frozen pre-run snapshot).
    PostToolUse *    → `transcripts record`   append the full tool payload to the store.
    Stop             → `transcripts snapshot`  snapshot the full session transcript.
    SubagentStop *   → `transcripts stop`      snapshot + remove `.transcripts/` + marker.
- Real isolation = the global store is never staged into the worktree. The read-only
  chmod is the softer "not yours to write" signal (defeatable, but it errors loudly).
- Retention: everything is kept (no auto-compaction). `transcripts prune` is a manual,
  opt-in cap (`AGENTIC_TRANSCRIPTS_KEEP=<n>`) if disk gets tight.
- The retrospective reads this to distill memory. Gate verdicts, supervisor decisions,
  and worktree create/merge/abandon are all captured here.

## The per-worktree contract (.agentic/task.env)
At dispatch, write `.agentic/task.env` into the worktree with `TASK_ID`, `ATTEMPT`,
`AGENT_ROLE`, `STORY_DIR` (absolute path to the story dir — where `validate_comms` reads
init.md/output.md), `SCOPE_GLOBS` (GREEN diff-scope), `SCAFFOLD_SYMBOLS` (or write
`.agentic/scaffold-symbols`), `BASE_REF` (diff base), and `AGENTIC_TRANSCRIPTS_DIR`. The gate
library sources it, so the gates check the RIGHT task's scope/symbols/comms — not
auto-discovered guesses.

## Reference

- `pipeline/` — the design source of truth (persona / init.template / artifacts /
  gate per activity).
- `schemas/` — md-db KDL schemas (`agent-io`, `planning-artifacts`, `ledger`).
- `bin/` — the gate bodies + `log-execution`.
- `tools/ctx-symbols/` — the symbol backend (build + install per its README).
- Prereqs on PATH: `md-db` (artifact validation) and optional `ctx-symbols`
  (code-structure checks). Both degrade gracefully to grep with a WARN.
