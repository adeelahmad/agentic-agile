---
type: init
agent_role: final-gate
task_id: sprint<N>
attempt: 1
issued_by: "@supervisor"
issued_at: <ISO8601>
allowed_tools: [read, run, grep]
---
# Mandate
Certify sprint <N>: full matrix green, zero suppressions, all plan-ready.md ticked.

# Scope
## May
Run the full gate matrix; grep for suppressions; read all plan-ready.md.
## May Not
Edit code; ignore/skip/weaken any test.

# Inputs
- sprintN/plan.md (Cross-cutting gates)
- every sN-NN-<slug>/plan-ready.md

# Acceptance
Zero failures/skips/ignores/suppressions; every plan-ready.md fully [x]; all green.
