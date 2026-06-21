"""
run_all_experiments.py
======================
Top-level experiment runner skeleton for the benchmark suite.

Usage:
    python experiments/run_all_experiments.py

Outputs (written to results/raw/):
    decision_accuracy.csv
    maintainability.csv
    latency.csv       (populated by latency.py)
    explanation_quality.csv  (populated by explanation_quality.py)
"""

from __future__ import annotations

import csv
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SYSTEMS = [
    ("rdf_owl_shacl", ROOT / "semantic-mvp"),
    ("opa_set",       ROOT / "opa-set-baseline"),
    ("opa_derived",   ROOT / "opa-derived-baseline"),
]

RESULTS_RAW = ROOT / "results" / "raw"
RESULTS_RAW.mkdir(parents=True, exist_ok=True)

SCHEMA_PATH = ROOT / "benchmark" / "schemas" / "result_schema.json"
EXPECTED_DIR = ROOT / "benchmark" / "expected"


# ---------------------------------------------------------------------------
# Decision accuracy
# ---------------------------------------------------------------------------

def run_decision_accuracy() -> list[dict]:
    """Run all three systems against all scenarios in benchmark/expected/ and
    collect decision accuracy records."""
    records: list[dict] = []

    if not EXPECTED_DIR.exists():
        print(f"[WARN] No expected/ dir found at {EXPECTED_DIR}. Skipping accuracy run.")
        return records

    for expected_file in sorted(EXPECTED_DIR.glob("*.json")):
        with open(expected_file) as f:
            expected = json.load(f)

        scenario_id = expected["scenario_id"]
        expected_decision = expected["expected_decision"]

        for system_name, system_root in SYSTEMS:
            # Each baseline engine is invoked via its run_policy_check API.
            # We dynamically import to avoid coupling this file to any one engine.
            decision, latency_ms = _evaluate_system(
                system_name, system_root, scenario_id
            )

            records.append({
                "scenario_id": scenario_id,
                "tier": expected.get("tier", 0),
                "tier_name": expected.get("tier_name", ""),
                "system": system_name,
                "expected_decision": expected_decision,
                "actual_decision": decision,
                "correct": decision == expected_decision,
                "latency_ms": latency_ms,
                # Maintainability metrics are filled in by maintainability.py
                "m1_enforcement_policy_edits": expected.get("m1", 0),
                "m2_semantic_edits": expected.get("m2", 0),
                "m3_data_edits": expected.get("m3", 0),
                "m4_classification_code_edits": expected.get("m4", 0),
                "m5_dependent_policies_affected": expected.get("m5", 0),
            })

    return records


def _evaluate_system(
    system_name: str, system_root: Path, scenario_id: str
) -> tuple[str, float]:
    """Dispatch to the correct engine and return (decision, latency_ms)."""
    import sys
    for key in list(sys.modules.keys()):
        if key.startswith("opa_policy") or key.startswith("semantic_policy"):
            del sys.modules[key]
            
    src = system_root / "src"
    if str(src) in sys.path:
        sys.path.remove(str(src))
    sys.path.insert(0, str(src))

    t0 = time.perf_counter()
    try:
        if system_name == "rdf_owl_shacl":
            from semantic_policy.engine import run_policy_check
            scenario_file = system_root / "data" / "scenarios" / f"{scenario_id}.ttl"
        else:
            from opa_policy.engine import run_policy_check
            scenario_file = system_root / "input" / f"{scenario_id}.json"

        result = run_policy_check(scenario_file, root=system_root)
        decision = result.decision
    except Exception as exc:
        print(f"[ERROR] {system_name}/{scenario_id}: {exc}")
        decision = "REQUIRE_CLARIFICATION"
    finally:
        # ensure sys.path doesn't accumulate across calls
        if str(src) in sys.path:
            sys.path.remove(str(src))

    latency_ms = (time.perf_counter() - t0) * 1000
    return decision, round(latency_ms, 2)


# ---------------------------------------------------------------------------
# CSV output
# ---------------------------------------------------------------------------

def write_csv(records: list[dict], output_path: Path) -> None:
    if not records:
        print(f"[WARN] No records to write to {output_path}.")
        return
    fieldnames = list(records[0].keys())
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    print(f"[OK] Wrote {len(records)} records -> {output_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== Running decision accuracy ===")
    accuracy_records = run_decision_accuracy()
    write_csv(accuracy_records, RESULTS_RAW / "decision_accuracy.csv")

    print("\nDone. Run latency.py and explanation_quality.py for remaining metrics.")
