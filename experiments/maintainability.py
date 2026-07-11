"""
maintainability.py
==================
Compute maintainability metrics for three explicit change experiments
(E1–E3), not per-scenario zero-filled annotations.

E1  Add a new production server (data / set / predicate impact)
E2  Expand the ProductionServer definition
E3  One abstraction reused by N dependent enforcement policies

Outputs:
    results/raw/maintainability.csv
    results/raw/maintainability_e1_e3.json
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS_RAW = ROOT / "results" / "raw"
RESULTS_RAW.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# E1–E3 are audited edit-site counts derived from the frozen artifact design.
# They are *not* runtime measurements of the 32-scenario harness.
# ---------------------------------------------------------------------------

EXPERIMENTS = [
    {
        "experiment_id": "E1",
        "name": "Add new production server",
        "description": (
            "Introduce srv_new with belongsToEnvironment=production. "
            "RDF/OPA-derived classify from facts; OPA-set must update the set."
        ),
        "systems": {
            "rdf_owl_shacl": {
                "m1_enforcement_policy_edits": 0,
                "m2_semantic_edits": 0,
                "m3_data_edits": 1,
                "m4_classification_code_edits": 0,
                "m5_dependent_policies_affected": 3,
                "notes": "One enterprise fact; OWL class definition unchanged; restart/deploy/logs shapes reuse ProductionServer.",
            },
            "opa_set": {
                "m1_enforcement_policy_edits": 0,
                "m2_semantic_edits": 0,
                "m3_data_edits": 1,
                "m4_classification_code_edits": 1,
                "m5_dependent_policies_affected": 3,
                "notes": "Must add srv_new to production_servers set (classification-code edit).",
            },
            "opa_derived": {
                "m1_enforcement_policy_edits": 0,
                "m2_semantic_edits": 0,
                "m3_data_edits": 1,
                "m4_classification_code_edits": 0,
                "m5_dependent_policies_affected": 3,
                "notes": "One JSON server record; is_production_server predicate unchanged.",
            },
        },
    },
    {
        "experiment_id": "E2",
        "name": "Expand ProductionServer definition",
        "description": (
            "Add a new disjunct (e.g. tag prod-like) to the ProductionServer class."
        ),
        "systems": {
            "rdf_owl_shacl": {
                "m1_enforcement_policy_edits": 0,
                "m2_semantic_edits": 1,
                "m3_data_edits": 0,
                "m4_classification_code_edits": 0,
                "m5_dependent_policies_affected": 3,
                "notes": "One OWL equivalentClass edit; SHACL shapes untouched.",
            },
            "opa_set": {
                "m1_enforcement_policy_edits": 0,
                "m2_semantic_edits": 0,
                "m3_data_edits": 0,
                "m4_classification_code_edits": 1,
                "m5_dependent_policies_affected": 3,
                "notes": "Must recompute/extend membership set or set-generation logic.",
            },
            "opa_derived": {
                "m1_enforcement_policy_edits": 0,
                "m2_semantic_edits": 0,
                "m3_data_edits": 0,
                "m4_classification_code_edits": 1,
                "m5_dependent_policies_affected": 3,
                "notes": "One additional is_production_server rule head; allow/deny rules untouched.",
            },
        },
    },
    {
        "experiment_id": "E3",
        "name": "Abstraction reused by three policies",
        "description": (
            "Restart, deploy, and query-logs policies all depend on ProductionServer. "
            "Shows fan-out is representation-neutral; location differs."
        ),
        "systems": {
            "rdf_owl_shacl": {
                "m1_enforcement_policy_edits": 0,
                "m2_semantic_edits": 1,
                "m3_data_edits": 0,
                "m4_classification_code_edits": 0,
                "m5_dependent_policies_affected": 3,
                "notes": "Shared OWL class; three SHACL shapes target inferred class.",
            },
            "opa_set": {
                "m1_enforcement_policy_edits": 0,
                "m2_semantic_edits": 0,
                "m3_data_edits": 0,
                "m4_classification_code_edits": 1,
                "m5_dependent_policies_affected": 3,
                "notes": "Shared production_servers set referenced by three rule groups.",
            },
            "opa_derived": {
                "m1_enforcement_policy_edits": 0,
                "m2_semantic_edits": 0,
                "m3_data_edits": 0,
                "m4_classification_code_edits": 1,
                "m5_dependent_policies_affected": 3,
                "notes": "Shared is_production_server predicate referenced by three rule groups.",
            },
        },
    },
]


def flatten_records() -> list[dict]:
    rows: list[dict] = []
    for exp in EXPERIMENTS:
        for system, metrics in exp["systems"].items():
            rows.append(
                {
                    "experiment_id": exp["experiment_id"],
                    "experiment_name": exp["name"],
                    "system": system,
                    "m1_enforcement_policy_edits": metrics["m1_enforcement_policy_edits"],
                    "m2_semantic_edits": metrics["m2_semantic_edits"],
                    "m3_data_edits": metrics["m3_data_edits"],
                    "m4_classification_code_edits": metrics["m4_classification_code_edits"],
                    "m5_dependent_policies_affected": metrics["m5_dependent_policies_affected"],
                    "notes": metrics["notes"],
                }
            )
    return rows


def main() -> None:
    rows = flatten_records()
    csv_path = RESULTS_RAW / "maintainability.csv"
    fieldnames = list(rows[0].keys())
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"[OK] Wrote {len(rows)} E1–E3 records -> {csv_path}")

    json_path = RESULTS_RAW / "maintainability_e1_e3.json"
    json_path.write_text(json.dumps(EXPERIMENTS, indent=2) + "\n", encoding="utf-8")
    print(f"[OK] Wrote structured experiments -> {json_path}")


if __name__ == "__main__":
    main()
