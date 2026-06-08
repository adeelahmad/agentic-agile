---
type: init
agent_role: archivist
task_id: retrospective/sprint-<N>
attempt: 1
issued_by: "@supervisor"
issued_at: <ISO8601>
allowed_tools: [read]
---
# Mandate
Distill recurring failures and reliably-good patterns since the last retrospective
into terse, role-scoped candidate memories.

# Scope
## May
Read the global lineage, attempt feedback, and execution.log; write a candidate list.
## May Not
Edit code, plans, or memory.md directly; relax any invariant.

# Inputs
- <lineage store> (global lineage.jsonl + per-task transcripts)
- docs/agents/sprint*/**/attempt-*/   (feedback + findings)

# Acceptance
Each candidate is 1-2 lines, role-tagged, recurrence >= 2 (or a human keep), and
violates no invariant.
