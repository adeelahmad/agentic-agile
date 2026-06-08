---
type: init
agent_role: scaffolder
task_id: S<N>-<NN>
attempt: 1
wave: <K>
issued_by: "@supervisor"
issued_at: <ISO8601>
allowed_tools: [read, write, delete]
allowed_paths: ["<production source dirs from tasks.md>"]
---
# Mandate
Stub every production symbol referenced by the verified RED tests, once each.

# Scope
## May
Create stub files/types/fns with panic("SUB-AGENT-TODO: ..."); delete mod common shims.
## May Not
Implement any body; create a symbol twice; edit a test file.

# Inputs
- sN-NN-<slug>/plan-ready.md
- the verified RED test files

# Acceptance
Every referenced symbol stubbed exactly once; all bodies panic+TODO; shims gone;
each action recorded in `# Scaffold` and execution.log.
