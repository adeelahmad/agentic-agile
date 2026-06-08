---
type: init
agent_role: red-worker
task_id: S<N>-<NN>/T<k>
attempt: 1
wave: <K>
issued_by: "@supervisor"
issued_at: <ISO8601>
allowed_tools: [read, write]
allowed_paths: ["<test-file-path>", "tests/common/**"]
---
# Mandate
Write task T<k>'s tests from plan.md; confirm each one fails.

# Scope
## May
Write the named test file and mod common shims.
## May Not
Write production code; make a test that passes.

# Inputs
- sN-NN-<slug>/plan.md  (this task's section only)

# Acceptance
Every new test is FAIL; no prior test regressed; diff touches only test + shim.
