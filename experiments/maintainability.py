"""
maintainability.py
==================
Compute M1–M5 maintainability metrics for each experiment.

Reads benchmark/expected/*.json and aggregates the metric annotations
into results/raw/maintainability.csv.

Run after populating benchmark/expected/ with ground-truth records.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPECTED_DIR = ROOT / "benchmark" / "expected"
RESULTS_RAW  = ROOT / "results" / "raw"
RESULTS_RAW.mkdir(parents=True, exist_ok=True)


SYSTEMS = ["rdf_owl_shacl", "opa_set", "opa_derived"]

METRIC_KEYS = [
    "m1_enforcement_policy_edits",
    "m2_semantic_edits",
    "m3_data_edits",
    "m4_classification_code_edits",
    "m5_dependent_policies_affected",
]


def load_maintainability_records() -> list[dict]:
    records = []
    for f in sorted(EXPECTED_DIR.glob("*.json")):
        expected = json.loads(f.read_text(encoding="utf-8"))
        scenario_id = expected["scenario_id"]
        for system in SYSTEMS:
            system_key = f"maintainability_{system}"
            m = expected.get(system_key, {})
            records.append({
                "scenario_id":   scenario_id,
                "tier":          expected.get("tier", 0),
                "tier_name":     expected.get("tier_name", ""),
                "system":        system,
                **{k: m.get(k, 0) for k in METRIC_KEYS},
            })
    return records


def write_csv(records: list[dict], path: Path) -> None:
    if not records:
        print(f"[WARN] No maintainability records found.")
        return
    fieldnames = list(records[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    print(f"[OK] Wrote {len(records)} records -> {path}")


if __name__ == "__main__":
    records = load_maintainability_records()
    write_csv(records, RESULTS_RAW / "maintainability.csv")
