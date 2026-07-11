"""
latency.py
==========
Benchmark the evaluation latency of all three systems.

For each scenario in benchmark/expected/, runs each system N times and
records median + p95 wall-clock time in milliseconds.

Usage:
    python experiments/latency.py --iterations 100

Outputs:
    results/raw/latency.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPECTED_DIR = ROOT / "benchmark" / "expected"
RESULTS_RAW  = ROOT / "results" / "raw"
RESULTS_RAW.mkdir(parents=True, exist_ok=True)

SYSTEMS = [
    ("rdf_owl_shacl", ROOT / "semantic-mvp"),
    ("opa_set",       ROOT / "opa-set-baseline"),
    ("opa_derived",   ROOT / "opa-derived-baseline"),
]


def benchmark(iterations: int = 100) -> list[dict]:
    if not EXPECTED_DIR.exists():
        print(f"[WARN] benchmark/expected/ not populated yet.")
        return []

    records = []
    for f in sorted(EXPECTED_DIR.glob("*.json")):
        expected = json.loads(f.read_text(encoding="utf-8"))
        scenario_id = expected["scenario_id"]
        for system_name, system_root in SYSTEMS:
            print(f"  Benchmarking {system_name}/{scenario_id} × {iterations}...")
            
            # Setup imports once per system-scenario
            import sys
            for key in list(sys.modules.keys()):
                if key.startswith(("opa_policy", "opa_set_policy", "opa_derived_policy", "semantic_policy")):
                    del sys.modules[key]
            src = system_root / "src"
            if str(src) in sys.path:
                sys.path.remove(str(src))
            sys.path.insert(0, str(src))

            times = []
            try:
                if system_name == "rdf_owl_shacl":
                    from semantic_policy.engine import run_policy_check
                    scenario_file = system_root / "data" / "scenarios" / f"{scenario_id}.ttl"
                elif system_name == "opa_set":
                    from opa_set_policy.engine import run_policy_check
                    scenario_file = system_root / "input" / f"{scenario_id}.json"
                elif system_name == "opa_derived":
                    from opa_derived_policy.engine import run_policy_check
                    scenario_file = system_root / "input" / f"{scenario_id}.json"
                else:
                    raise ValueError(f"Unknown system: {system_name}")
                
                # Warm up once
                run_policy_check(scenario_file, root=system_root)
                
                # Run iterations
                for _ in range(iterations):
                    t0 = time.perf_counter()
                    run_policy_check(scenario_file, root=system_root)
                    times.append((time.perf_counter() - t0) * 1000)
            except Exception as exc:
                print(f"  [ERROR] {system_name}/{scenario_id}: {exc}")
                times = [float("nan")] * iterations
            finally:
                if str(src) in sys.path:
                    sys.path.remove(str(src))
            
            valid = [t for t in times if t == t]  # filter NaN
            if not valid:
                median, p95 = float("nan"), float("nan")
            else:
                median = statistics.median(valid)
                p95    = sorted(valid)[int(len(valid) * 0.95)]
            records.append({
                "scenario_id":    scenario_id,
                "system":         system_name,
                "iterations":     iterations,
                "latency_median_ms": round(median, 3),
                "latency_p95_ms":    round(p95, 3),
            })
    return records


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=100)
    args = parser.parse_args()

    print(f"=== Latency benchmark ({args.iterations} iterations each) ===")
    records = benchmark(args.iterations)
    if records:
        out = RESULTS_RAW / "latency.csv"
        with open(out, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(records[0].keys()))
            writer.writeheader()
            writer.writerows(records)
        print(f"[OK] Wrote {len(records)} records -> {out}")
