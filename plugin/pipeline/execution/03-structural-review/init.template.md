---
type: init
agent_role: structural-reviewer
task_id: S<N>-<NN>
attempt: 1
wave: <K>
issued_by: "@supervisor"
issued_at: <ISO8601>
allowed_tools: [read, grep, build]
---
# Mandate
Audit the merged green tree for orphan modules, parallel implementations, and
duplicate helpers. Report findings with severity.

# Scope
## May
Read, grep, build/vet the tree.
## May Not
Edit any source file.

# Inputs
- the merged green worktree for wave <K>

# Acceptance
Findings table is complete; each finding cites file:line and a severity.

# Feedback
(blank on first attempt)
