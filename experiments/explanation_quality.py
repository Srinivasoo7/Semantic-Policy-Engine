"""
explanation_quality.py
=======================
Evaluate the explanation completeness (field-completeness scoring) produced by each system against five mechanical criteria:

  1. asserted_facts    — does the explanation list raw input facts used?
  2. inferred_facts    — does it list OWL-inferred / Rego-derived facts?
  3. violated_policy   — does it name the SHACL shape or Rego rule that fired?
  4. decision_reason   — does it provide a free-text justification?
  5. reconstructable   — can a human reconstruct the decision from the explanation alone?
     (mechanical completeness score 0/1, pre-populated in benchmark/expected/*.json)

Score per criterion: 1 if present/non-empty, 0 otherwise.
Total score: sum of 5 criteria (max 5).

Outputs:
    results/raw/explanation_quality.csv
"""

from __future__ import annotations

import csv
import json
import sys
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


def _get_explanation(system_name: str, system_root: Path, scenario_id: str) -> dict:
    import sys
    for key in list(sys.modules.keys()):
        if key.startswith(("opa_policy", "opa_set_policy", "opa_derived_policy", "semantic_policy")):
            del sys.modules[key]

    src = system_root / "src"
    if str(src) in sys.path:
        sys.path.remove(str(src))
    sys.path.insert(0, str(src))
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

        result = run_policy_check(scenario_file, root=system_root)
        return {
            "decision":        getattr(result, "decision", ""),
            "asserted_facts":  getattr(result, "asserted_facts", []),
            "inferred_facts":  getattr(result, "inferred_types", []),
            "violated_policy": getattr(result, "violated_policy", ""),
            "decision_reason": getattr(result, "messages", [""])[-1] if getattr(result, "messages", []) else "",
        }
    except Exception as exc:
        print(f"  [ERROR] {system_name}/{scenario_id}: {exc}")
        return {"decision": "", "asserted_facts": [], "inferred_facts": [], "violated_policy": "", "decision_reason": ""}
    finally:
        if str(src) in sys.path:
            sys.path.remove(str(src))


def score_explanation(expl: dict, reconstructable: int = 0) -> dict:
    """Score runtime-exported explanation *fields*.

    Main score (total_score) uses only runtime-observable fields c1–c4.
    c5_reconstructable is retained as an optional pre-registered annotation
    and is NOT included in total_score (avoids circular scoring).
    """
    decision = expl.get("decision", "ALLOW")

    # c3: for ALLOW, empty violated_policy is correct; otherwise non-empty required.
    if decision == "ALLOW":
        has_violated_policy = 1 if not expl.get("violated_policy") else 0
    else:
        has_violated_policy = 1 if expl.get("violated_policy") else 0

    c1 = 1 if expl.get("asserted_facts") else 0
    c2 = 1 if expl.get("inferred_facts") else 0
    c3 = has_violated_policy
    c4 = 1 if expl.get("decision_reason") else 0

    return {
        "c1_asserted_facts": c1,
        "c2_inferred_facts": c2,
        "c3_violated_policy": c3,
        "c4_decision_reason": c4,
        "c5_reconstructable_annotation": reconstructable,
        "total_score": c1 + c2 + c3 + c4,  # max 4 — runtime fields only
        "total_score_with_annotation": c1 + c2 + c3 + c4 + reconstructable,
    }


def run() -> list[dict]:
    if not EXPECTED_DIR.exists():
        print("[WARN] benchmark/expected/ not yet populated.")
        return []

    records = []
    for f in sorted(EXPECTED_DIR.glob("*.json")):
        expected = json.loads(f.read_text(encoding="utf-8"))
        scenario_id = expected["scenario_id"]
        for system_name, system_root in SYSTEMS:
            reconstructable = expected.get(f"reconstructable_{system_name}", 0)
            expl = _get_explanation(system_name, system_root, scenario_id)
            scores = score_explanation(expl, reconstructable)
            records.append({
                "scenario_id": scenario_id,
                "system":      system_name,
                **scores,
            })
    return records


if __name__ == "__main__":
    print("=== Explanation quality scoring ===")
    records = run()
    if records:
        out = RESULTS_RAW / "explanation_quality.csv"
        with open(out, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(records[0].keys()))
            writer.writeheader()
            writer.writerows(records)
        print(f"[OK] Wrote {len(records)} records -> {out}")
