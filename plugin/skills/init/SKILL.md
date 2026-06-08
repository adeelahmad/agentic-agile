---
name: init
description: >-
  Explicit entry point for the agentic-agile workflow — start a sprint with two-stage
  human-gated planning then autonomous, hook-enforced TDD execution. Invoke with
  /agentic-agile:init. This is a thin alias; the canonical playbook is the
  agentic-agile skill.
disable-model-invocation: true
---

# agentic-agile — init (entry point)

This is the explicit entry point for the **agentic-agile** workflow. It does not
restate the playbook; it points at the canonical one so the two never drift.

**Do this now:**

1. Load the canonical supervisor playbook — the `agentic-agile` skill in this plugin.
   If its full text is not already in your context, read it from this plugin's
   directory: `${CLAUDE_PLUGIN_ROOT}/skills/agentic-agile/SKILL.md` (run
   `echo "$CLAUDE_PLUGIN_ROOT"` first if you need the absolute path).
2. Adopt the supervisor role it defines and begin **Stage-1 planning** with the human:
   confirm the request, run intake, then standards, then the planner.
3. Honor every invariant from that playbook — most importantly, **do not start the
   autonomous RED → SCAFFOLD → GREEN → STRUCTURAL-REVIEW → FINAL-GATE execution run
   until the human approves the completed Stage-2 plan.**

Everything else — the gate contract, artifact layout, lineage, retrospective — is
defined in `agentic-agile/SKILL.md`. Follow it as written.
