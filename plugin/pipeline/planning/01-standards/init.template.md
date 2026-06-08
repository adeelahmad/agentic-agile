---
type: init
agent_role: standards
task_id: <sprint-id>
attempt: 1
issued_by: "@orchestrator"
issued_at: <ISO8601>
allowed_tools: [read]
---
# Mandate
Detect stack; load the rule sources; emit standards.md with source refs.

# Scope
## May
Read CLAUDE.md, docs/agents/*.md, rules/<lang>/*.
## May Not
Add a rule not present in a source; write plan or code.

# Inputs
- CLAUDE.md
- docs/agents/clean-code.md, testing.md, no-assumptions.md
- rules/<detected-lang>/

# Acceptance
Every digest line cites a real source; detected language matches the repo.
