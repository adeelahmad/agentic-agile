#!/usr/bin/env python3
"""Turn a `claude -p --output-format json` envelope into result.md + timing.json.

Usage:  _extract.py <claude-json-file> <arm-dir>
Writes  <arm-dir>/outputs/result.md  and  <arm-dir>/timing.json
"""
import json
import sys
from pathlib import Path


def main(argv):
    if len(argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    env = json.loads(Path(argv[1]).read_text())
    arm = Path(argv[2])
    (arm / "outputs").mkdir(parents=True, exist_ok=True)

    (arm / "outputs" / "result.md").write_text(str(env.get("result", "")))

    usage = env.get("usage", {}) or {}
    total = sum(v for v in usage.values() if isinstance(v, int))
    timing = {"total_tokens": total or None, "duration_ms": env.get("duration_ms")}
    (arm / "timing.json").write_text(json.dumps(timing, indent=2) + "\n")
    print(f"  tokens={timing['total_tokens']} duration_ms={timing['duration_ms']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
