from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "results" / "raw"
TABLES_DIR = ROOT / "results" / "tables"
TABLES_DIR.mkdir(parents=True, exist_ok=True)

def load_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))

def main():
    accuracy = load_csv(RAW_DIR / "decision_accuracy.csv")
    maintainability = load_csv(RAW_DIR / "maintainability.csv")
    explanation = load_csv(RAW_DIR / "explanation_quality.csv")
    latency = load_csv(RAW_DIR / "latency.csv")

    if not (accuracy and maintainability and explanation):
        print("[ERROR] Missing raw files in results/raw/.")
        return

    # Index data by (scenario_id, system)
    data = {}
    for row in accuracy:
        key = (row["scenario_id"], row["system"])
        data[key] = {
            "scenario_id": row["scenario_id"],
            "tier": int(row["tier"]),
            "tier_name": row["tier_name"],
            "system": row["system"],
            "expected_decision": row["expected_decision"],
            "actual_decision": row["actual_decision"],
            "correct": row["correct"] == "True",
            "m1": 0, "m2": 0, "m3": 0, "m4": 0, "m5": 0,
            "explanation_score": 0,
            "latency_median": "PENDING", "latency_p95": "PENDING"
        }

    for row in maintainability:
        key = (row["scenario_id"], row["system"])
        if key in data:
            data[key].update({
                "m1": int(row["m1_enforcement_policy_edits"]),
                "m2": int(row["m2_semantic_edits"]),
                "m3": int(row["m3_data_edits"]),
                "m4": int(row["m4_classification_code_edits"]),
                "m5": int(row["m5_dependent_policies_affected"])
            })

    for row in explanation:
        key = (row["scenario_id"], row["system"])
        if key in data:
            data[key]["explanation_score"] = int(row["total_score"])

    for row in latency:
        key = (row["scenario_id"], row["system"])
        if key in data:
            data[key].update({
                "latency_median": row["latency_median_ms"],
                "latency_p95": row["latency_p95_ms"]
            })

    # Sort scenarios by tier, then scenario_id, then system in order: rdf_owl_shacl, opa_set, opa_derived
    system_order = {"rdf_owl_shacl": 0, "opa_set": 1, "opa_derived": 2}
    sorted_keys = sorted(data.keys(), key=lambda k: (data[k]["tier"], data[k]["scenario_id"], system_order.get(data[k]["system"], 9)))

    # 1. Generate full Markdown comparison table
    md_lines = [
        "# Benchmark Results Comparison",
        "",
        "| Scenario | Tier | System | Decision | Correct | Latency Median (ms) | Explanation Score | M1 | M2 | M3 | M4 | M5 |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
    ]
    for k in sorted_keys:
        d = data[k]
        md_lines.append(
            f"| `{d['scenario_id']}` | {d['tier']} | `{d['system']}` | {d['expected_decision']} | {d['correct']} | {d['latency_median']} | {d['explanation_score']}/5 | {d['m1']} | {d['m2']} | {d['m3']} | {d['m4']} | {d['m5']} |"
        )
    
    (TABLES_DIR / "comparison_table.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    print(f"[OK] Wrote results/tables/comparison_table.md")

    # 2. Generate LaTeX comparison table
    tex_lines = [
        "\\begin{table}[h!]",
        "\\centering",
        "\\caption{Comprehensive Benchmark Results}",
        "\\label{tab:benchmark_results}",
        "\\begin{tabular}{l c l l c r c c c c c c}",
        "\\hline",
        "Scenario & Tier & System & Decision & Correct & Lat. (ms) & Expl. & M1 & M2 & M3 & M4 & M5 \\\\",
        "\\hline"
    ]
    for k in sorted_keys:
        d = data[k]
        sys_name = d["system"].replace("_", "\\_")
        scen_id = d["scenario_id"].replace("_", "\\_")
        tex_lines.append(
            f"{scen_id} & {d['tier']} & \\texttt{{{sys_name}}} & {d['expected_decision']} & {d['correct']} & {d['latency_median']} & {d['explanation_score']}/5 & {d['m1']} & {d['m2']} & {d['m3']} & {d['m4']} & {d['m5']} \\\\"
        )
    tex_lines.extend([
        "\\hline",
        "\\end{tabular}",
        "\\end{table}"
    ])
    (TABLES_DIR / "comparison_table.tex").write_text("\n".join(tex_lines) + "\n", encoding="utf-8")
    print(f"[OK] Wrote results/tables/comparison_table.tex")

    # 3. Generate Tier Summary Table
    tiers_summary = {}
    for k in sorted_keys:
        d = data[k]
        t_key = (d["tier"], d["tier_name"])
        if t_key not in tiers_summary:
            tiers_summary[t_key] = {}
        sys = d["system"]
        if sys not in tiers_summary[t_key]:
            tiers_summary[t_key][sys] = {"latency_sum": 0.0, "latency_count": 0, "expl_sum": 0, "expl_count": 0, "correct_count": 0, "total_count": 0}
        
        # Latency
        try:
            val = float(d["latency_median"])
            tiers_summary[t_key][sys]["latency_sum"] += val
            tiers_summary[t_key][sys]["latency_count"] += 1
        except ValueError:
            pass
        
        # Expl score
        tiers_summary[t_key][sys]["expl_sum"] += d["explanation_score"]
        tiers_summary[t_key][sys]["expl_count"] += 1
        
        # Correctness
        if d["correct"]:
            tiers_summary[t_key][sys]["correct_count"] += 1
        tiers_summary[t_key][sys]["total_count"] += 1

    md_summary = [
        "# Tier-wise Aggregated Summary",
        "",
        "| Tier | Tier Name | System | Accuracy | Median Latency (ms) | Avg Explanation Score |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |"
    ]
    for (t_val, t_name) in sorted(tiers_summary.keys()):
        for sys in ["rdf_owl_shacl", "opa_set", "opa_derived"]:
            stats = tiers_summary[(t_val, t_name)].get(sys)
            if not stats:
                continue
            acc = f"{stats['correct_count']}/{stats['total_count']} ({stats['correct_count']/stats['total_count']:.1%})"
            avg_lat = f"{stats['latency_sum']/stats['latency_count']:.2f}" if stats["latency_count"] > 0 else "N/A"
            avg_expl = f"{stats['expl_sum']/stats['expl_count']:.2f}/5" if stats["expl_count"] > 0 else "N/A"
            md_summary.append(
                f"| {t_val} | {t_name} | `{sys}` | {acc} | {avg_lat} | {avg_expl} |"
            )
            
    (TABLES_DIR / "tier_summary.md").write_text("\n".join(md_summary) + "\n", encoding="utf-8")
    print(f"[OK] Wrote results/tables/tier_summary.md")

if __name__ == "__main__":
    main()
