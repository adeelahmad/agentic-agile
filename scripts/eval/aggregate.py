#!/usr/bin/env python3
"""Aggregate one iteration's grading + timing into benchmark.json.

Walks <iteration-dir>/eval-*/{with_skill,without_skill}/ reading grading.json and
timing.json, then computes per-config pass_rate / time / tokens (mean + stddev) and
the with-minus-without delta. Pure file I/O — no model calls, safe to run anytime.

Usage:  aggregate.py <iteration-dir>
"""
import json
import math
import sys
from pathlib import Path

CONFIGS = ("with_skill", "without_skill")


def _mean_std(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return {"mean": None, "stddev": None, "n": 0}
    mean = sum(xs) / len(xs)
    var = sum((x - mean) ** 2 for x in xs) / len(xs) if len(xs) > 1 else 0.0
    return {"mean": round(mean, 4), "stddev": round(math.sqrt(var), 4), "n": len(xs)}


def _read_json(p):
    try:
        return json.loads(Path(p).read_text())
    except (OSError, ValueError):
        return None


def _config_stats(iteration: Path, config: str):
    pass_rates, times, tokens = [], [], []
    for eval_dir in sorted(iteration.glob("eval-*")):
        grading = _read_json(eval_dir / config / "grading.json")
        if grading and "summary" in grading:
            pass_rates.append(grading["summary"].get("pass_rate"))
        timing = _read_json(eval_dir / config / "timing.json")
        if timing:
            ms = timing.get("duration_ms")
            times.append(ms / 1000.0 if ms is not None else None)
            tokens.append(timing.get("total_tokens"))
    return {
        "pass_rate": _mean_std(pass_rates),
        "time_seconds": _mean_std(times),
        "tokens": _mean_std(tokens),
    }


def main(argv):
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    iteration = Path(argv[1])
    if not iteration.is_dir():
        print(f"not a directory: {iteration}", file=sys.stderr)
        return 2

    summary = {c: _config_stats(iteration, c) for c in CONFIGS}

    def delta(metric):
        w = summary["with_skill"][metric]["mean"]
        wo = summary["without_skill"][metric]["mean"]
        return round(w - wo, 4) if (w is not None and wo is not None) else None

    out = {
        "run_summary": {
            **summary,
            "delta": {
                "pass_rate": delta("pass_rate"),
                "time_seconds": delta("time_seconds"),
                "tokens": delta("tokens"),
            },
        }
    }
    dest = iteration / "benchmark.json"
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {dest}")
    print(json.dumps(out["run_summary"]["delta"], indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
