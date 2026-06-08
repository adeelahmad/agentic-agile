# Artifacts — retrospective

READS
- the global lineage (lineage.jsonl + per-task transcripts)
- docs/agents/sprint*/**/attempt-*/{init.md,output.md}   (feedback + findings)
- docs/agents/sprint*/execution.log                       (escalations, halts)

WRITES
- candidate memories (output.md)   -> supervisor + human curate
- docs/agents/memory.md            (supervisor commits the kept entries)

VALIDATES
- memory.md   <- schemas/memory.kdl    (md-db)
- output.md   <- schemas/agent-io.kdl  (agent_role: archivist)
