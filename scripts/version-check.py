#!/usr/bin/env python3
"""Assert plugin.json, ctx-symbols Cargo.toml, and CHANGELOG top entry agree."""
import json
import re
import sys

pj = json.load(open("plugin/.claude-plugin/plugin.json"))["version"]
cargo = re.search(
    r'(?m)^version\s*=\s*"([^"]+)"',
    open("plugin/tools/ctx-symbols/Cargo.toml").read(),
).group(1)
ch = re.search(
    r"(?m)^## \[([0-9]+\.[0-9]+\.[0-9]+)\]",
    open("CHANGELOG.md").read(),
).group(1)

ok = pj == cargo == ch
status = "OK" if ok else "MISMATCH"
print(f"plugin.json={pj}  cargo={cargo}  changelog={ch}  ->  {status}")
sys.exit(0 if ok else 1)
