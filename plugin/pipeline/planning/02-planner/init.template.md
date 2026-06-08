---
type: init
agent_role: planner
task_id: <sprint-id>
attempt: 1
issued_by: "@orchestrator"
issued_at: <ISO8601>
allowed_tools: [read, write]
allowed_paths: ["docs/agents/sprint<N>/**"]
---
# Mandate
Produce Stage-1 then Stage-2 artifacts for sprint <N> per the five steps.

# Scope
## May
Write only under docs/agents/sprint<N>/.
## May Not
Write production code or tests; start RED; leave any story at "TBW" in Stage 2.

# Inputs
- intake.md
- standards.md

# Acceptance
Stage-2 complete for EVERY story; plan.md bullets carry real path + fn; waves
respect the dependency graph; planning-artifacts.kdl + gate-plan-shape pass.
