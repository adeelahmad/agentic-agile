#!/usr/bin/env python3
"""Grade one eval arm's outputs against its assertions -> grading.json.

Reads the outputs produced by run-evals.sh (result.md + any files) for a single
arm directory, then evaluates each assertion PASS/FAIL with evidence and writes
grading.json into that arm directory.

Two modes:
  --dry-run   write an ungraded template (passed=null) — no model call, no tokens.
              Use this to verify the file plumbing before spending credits.
  (default)   call `claude -p` as an LLM judge to grade each assertion.

Usage:
  grade.py --suite <evals.json> --eval-id <N> --arm-dir <dir> [--dry-run]
  grade.py --assertions-file <json-list> --arm-dir <dir> [--dry-run]

The judge is instructed to require concrete evidence for a PASS (quote/reference the
output), per the agentskills.io grading principles.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

JUDGE_SYSTEM = (
    "You are a strict eval grader. For each assertion, decide PASS or FAIL based ONLY "
    "on the provided outputs. Require concrete evidence for a PASS — quote or reference "
    "the output; if the substance is missing even when a label is present, FAIL it. "
    "Do not give the benefit of the doubt. Return ONLY JSON."
)


def _load_assertions(args):
    if args.assertions_file:
        return json.loads(Path(args.assertions_file).read_text())
    suite = json.loads(Path(args.suite).read_text())
    for e in suite["evals"]:
        if e["id"] == args.eval_id:
            return e["assertions"]
    raise SystemExit(f"eval id {args.eval_id} not found in {args.suite}")


def _collect_outputs(arm_dir: Path) -> str:
    out = arm_dir / "outputs"
    parts = []
    result = out / "result.md"
    if result.exists():
        parts.append("## result.md\n" + result.read_text())
    files = [p for p in sorted(out.rglob("*")) if p.is_file() and p.name != "result.md"]
    if files:
        listing = "\n".join(f"- {p.relative_to(out)} ({p.stat().st_size} bytes)" for p in files)
        parts.append("## files produced\n" + listing)
        for p in files:
            if p.suffix in (".md", ".rs", ".txt", ".json", ".toml", ".py", ".ts", ".yaml", ".yml"):
                try:
                    parts.append(f"### {p.relative_to(out)}\n" + p.read_text()[:8000])
                except OSError:
                    pass
    return "\n\n".join(parts) if parts else "(no outputs were produced)"


def _template(assertions):
    return {
        "assertion_results": [
            {"text": a, "passed": None, "evidence": ""} for a in assertions
        ],
        "summary": {"passed": 0, "failed": 0, "total": len(assertions), "pass_rate": None},
    }


def _summarize(results):
    passed = sum(1 for r in results if r.get("passed") is True)
    total = len(results)
    failed = sum(1 for r in results if r.get("passed") is False)
    return {
        "passed": passed,
        "failed": failed,
        "total": total,
        "pass_rate": round(passed / total, 4) if total else None,
    }


def _grade_with_claude(assertions, outputs):
    prompt = (
        "Grade these assertions against the outputs.\n\n"
        f"ASSERTIONS:\n{json.dumps(assertions, indent=2)}\n\n"
        f"OUTPUTS:\n{outputs}\n\n"
        'Return JSON of the exact shape: {"assertion_results":[{"text":"...",'
        '"passed":true|false,"evidence":"..."}]}. One entry per assertion, same order.'
    )
    proc = subprocess.run(
        ["claude", "-p", "--output-format", "json", "--append-system-prompt", JUDGE_SYSTEM, prompt],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        raise SystemExit(f"claude judge failed: {proc.stderr.strip()}")
    envelope = json.loads(proc.stdout)
    text = envelope.get("result", proc.stdout)
    start, end = text.find("{"), text.rfind("}")
    graded = json.loads(text[start:end + 1])
    return graded["assertion_results"]


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--suite")
    ap.add_argument("--eval-id", type=int)
    ap.add_argument("--assertions-file")
    ap.add_argument("--arm-dir", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv[1:])

    assertions = _load_assertions(args)
    arm_dir = Path(args.arm_dir)
    arm_dir.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        grading = _template(assertions)
    else:
        results = _grade_with_claude(assertions, _collect_outputs(arm_dir))
        grading = {"assertion_results": results, "summary": _summarize(results)}

    dest = arm_dir / "grading.json"
    dest.write_text(json.dumps(grading, indent=2) + "\n")
    print(f"wrote {dest} (pass_rate={grading['summary']['pass_rate']})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
