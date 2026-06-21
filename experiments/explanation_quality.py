"""
explanation_quality.py
=======================
Score the explanation quality produced by each system against five criteria:

  1. asserted_facts    — does the explanation list raw input facts used?
  2. inferred_facts    — does it list OWL-inferred / Rego-derived facts?
  3. violated_policy   — does it name the SHACL shape or Rego rule that fired?
  4. decision_reason   — does it provide a free-text justification?
  5. reconstructable   — can a human reconstruct the decision from the explanation alone?
     (manual score 0/1, pre-populated in benchmark/expected/*.json)

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
        if key.startswith("opa_policy") or key.startswith("semantic_policy"):
            del sys.modules[key]
            
    src = system_root / "src"
    if str(src) in sys.path:
        sys.path.remove(str(src))
    sys.path.insert(0, str(src))
    try:
        if system_name == "rdf_owl_shacl":
            from semantic_policy.engine import run_policy_check
            scenario_file = system_root / "data" / "scenarios" / f"{scenario_id}.ttl"
        else:
            from opa_policy.engine import run_policy_check
            scenario_file = system_root / "input" / f"{scenario_id}.json"

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
    decision = expl.get("decision", "ALLOW")
    
    # c3 is violated_policy. For ALLOW decisions, it is high quality (1) if it is correctly empty.
    # For non-ALLOW decisions, it is high quality (1) if it is non-empty.
    if decision == "ALLOW":
        has_violated_policy = 1 if not expl.get("violated_policy") else 0
    else:
        has_violated_policy = 1 if expl.get("violated_policy") else 0

    return {
        "c1_asserted_facts":   1 if expl.get("asserted_facts") else 0,
        "c2_inferred_facts":   1 if expl.get("inferred_facts") else 0,
        "c3_violated_policy":  has_violated_policy,
        "c4_decision_reason":  1 if expl.get("decision_reason") else 0,
        "c5_reconstructable":  reconstructable,
        "total_score":         (
            (1 if expl.get("asserted_facts") else 0) +
            (1 if expl.get("inferred_facts") else 0) +
            has_violated_policy +
            (1 if expl.get("decision_reason") else 0) +
            reconstructable
        ),
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
