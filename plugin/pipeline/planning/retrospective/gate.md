# Gate — retrospective (supervisor + human curation)

Not a hook gate — a human-present curation step at planning.

Checks:
- [ ] Each kept memory is 1-2 lines and role-tagged.
- [ ] Each reflects a RECURRING pattern (>= 2 occurrences) or an explicit human keep.
- [ ] No memory relaxes an invariant (no-suppression, human-only-planning,
      scaffolder-leaves-panic, the gates). Such candidates are DISCARDED.
- [ ] memory.md stays bounded (stale/low-value entries pruned; deduped).

Failure verb:
  DISCARD — a candidate that is a one-off, an essay, or would weaken a gate.
Enforced by: the supervisor + the human at the planning retrospective; memory.md is
validated structurally by md-db (schemas/memory.kdl).

Self-check (v0.2): the worker runs `bin/selfcheck` (this same gate) BEFORE reporting
done — nothing advances past a failing self-check. The SubagentStop hook runs the same
gate as the backstop.
