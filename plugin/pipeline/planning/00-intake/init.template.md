---
type: init
agent_role: intake
task_id: <sprint-or-request-id>
attempt: 1
issued_by: "@orchestrator"
issued_at: <ISO8601>
allowed_tools: [read, ask-human]
---
# Mandate
Restate <request>; run the question protocol; deliver intake.md carrying the FIVE
parts of Intent (below). Intent is the outcome in the user's terms — no stack.

# Scope
## May
Ask the human clarifying questions; read repo README/CLAUDE.md/specs.
## May Not
Write plan artifacts or code; name a stack/implementation; assume an unstated scope.

# Inputs
- The raw user request
- README.md, CLAUDE.md

# Intent — the five parts (all required)
1. What's wanted     — the outcome, in the user's terms
2. Constraints       — the limits it must stay inside
3. Failure scenarios — the cases where the result does NOT count as done
4. Success scenarios — the cases where it DOES
5. Connections       — what else this touches (price/inventory/checkout/...), so a
                       change here is traceable to what it affects

# Acceptance
All five parts present; outcome is testable and stack-free; in/out-of-scope explicit;
zero blocking open questions. Hand to someone NOT in your head and ask where an agent
would still have to guess — close those holes.
