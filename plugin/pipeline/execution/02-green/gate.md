# Gate — 02-green  (supervisor verification)

Checks (bin/gate-green-verify):
- [ ] Every test in the task's plan-ready.md section now passes.
- [ ] No previously-passing test regressed.
- [ ] git diff --stat touches only tasks.md-named files + the RED test file.
- [ ] fmt / lint / full test suite / dependency audit / coverage all green.
- [ ] No suppression pattern introduced.

Failure verbs:
  REJECT — new test, unforced refactor, out-of-scope file, or suppression
  RETRY  — tests still failing; re-spawn with feedback appended to init.md
Enforced by: SubagentStop(green-worker) -> bin/gate-green-verify (exit 2 blocks).

Standards binding (added): the fmt/lint/test/coverage matrix this gate runs is the
one declared in standards.md (the lawkeeper's digest), not a hardcoded list — so the
rules that governed planning also bind execution.

Self-check (v0.2): the worker runs `bin/selfcheck` (this same gate) BEFORE reporting
done. A PASS there means this hook will pass — the hook is the backstop, not the first
line of defense.
