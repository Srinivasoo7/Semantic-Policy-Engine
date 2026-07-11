"""Generate Markdown/LaTeX result tables from results/raw/."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "results" / "raw"
TABLES_DIR = ROOT / "results" / "tables"
TABLES_DIR.mkdir(parents=True, exist_ok=True)

# Main explanation score is c1–c4 only (max 4)
EXPL_MAX = 4


def load_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> None:
    accuracy = load_csv(RAW_DIR / "decision_accuracy.csv")
    maintainability = load_csv(RAW_DIR / "maintainability.csv")
    explanation = load_csv(RAW_DIR / "explanation_quality.csv")
    latency = load_csv(RAW_DIR / "latency.csv")

    if not accuracy or not explanation:
        print("[ERROR] Missing decision_accuracy.csv or explanation_quality.csv in results/raw/.")
        return

    data: dict[tuple[str, str], dict] = {}
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
            "explanation_score": 0,
            "latency_median": "PENDING",
            "latency_p95": "PENDING",
        }

    for row in explanation:
        key = (row["scenario_id"], row["system"])
        if key in data:
            data[key]["explanation_score"] = int(float(row["total_score"]))

    for row in latency:
        key = (row["scenario_id"], row["system"])
        if key in data:
            data[key].update(
                {
                    "latency_median": row["latency_median_ms"],
                    "latency_p95": row["latency_p95_ms"],
                }
            )

    system_order = {"rdf_owl_shacl": 0, "opa_set": 1, "opa_derived": 2}
    sorted_keys = sorted(
        data.keys(),
        key=lambda k: (
            data[k]["tier"],
            data[k]["scenario_id"],
            system_order.get(data[k]["system"], 9),
        ),
    )

    # 1. Scenario comparison (no per-scenario M1–M5; those are E1–E3 only)
    md_lines = [
        "# Benchmark Results Comparison",
        "",
        "Explanation score is runtime field-export completeness over **c1–c4** "
        f"(asserted facts, inferred/derived facts, violated policy, decision reason); max {EXPL_MAX}.",
        "Maintainability is reported separately in `maintainability_e1_e3.md` (experiments E1–E3).",
        "",
        "| Scenario | Tier | System | Decision | Correct | Latency Median (ms) | Explanation Score |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]
    for k in sorted_keys:
        d = data[k]
        md_lines.append(
            f"| `{d['scenario_id']}` | {d['tier']} | `{d['system']}` | "
            f"{d['expected_decision']} | {d['correct']} | {d['latency_median']} | "
            f"{d['explanation_score']}/{EXPL_MAX} |"
        )

    (TABLES_DIR / "comparison_table.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    print("[OK] Wrote results/tables/comparison_table.md")

    tex_lines = [
        "\\begin{table}[h!]",
        "\\centering",
        "\\caption{Comprehensive Benchmark Results}",
        "\\label{tab:benchmark_results}",
        "\\begin{tabular}{l c l l c r c}",
        "\\hline",
        "Scenario & Tier & System & Decision & Correct & Lat. (ms) & Expl. \\\\",
        "\\hline",
    ]
    for k in sorted_keys:
        d = data[k]
        sys_name = d["system"].replace("_", "\\_")
        scen_id = d["scenario_id"].replace("_", "\\_")
        tex_lines.append(
            f"{scen_id} & {d['tier']} & \\texttt{{{sys_name}}} & "
            f"{d['expected_decision']} & {d['correct']} & {d['latency_median']} & "
            f"{d['explanation_score']}/{EXPL_MAX} \\\\"
        )
    tex_lines.extend(["\\hline", "\\end{tabular}", "\\end{table}"])
    (TABLES_DIR / "comparison_table.tex").write_text("\n".join(tex_lines) + "\n", encoding="utf-8")
    print("[OK] Wrote results/tables/comparison_table.tex")

    # 2. Tier summary
    tiers_summary: dict = {}
    for k in sorted_keys:
        d = data[k]
        t_key = (d["tier"], d["tier_name"])
        tiers_summary.setdefault(t_key, {})
        sys = d["system"]
        tiers_summary[t_key].setdefault(
            sys,
            {
                "latency_vals": [],
                "expl_sum": 0,
                "expl_count": 0,
                "correct_count": 0,
                "total_count": 0,
            },
        )
        stats = tiers_summary[t_key][sys]
        try:
            stats["latency_vals"].append(float(d["latency_median"]))
        except ValueError:
            pass
        stats["expl_sum"] += d["explanation_score"]
        stats["expl_count"] += 1
        if d["correct"]:
            stats["correct_count"] += 1
        stats["total_count"] += 1

    md_summary = [
        "# Tier-wise Aggregated Summary",
        "",
        f"| Tier | Tier Name | System | Accuracy | Median Latency (ms) | Avg Explanation Score (/{EXPL_MAX}) |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |",
    ]
    for t_val, t_name in sorted(tiers_summary.keys()):
        for sys in ["rdf_owl_shacl", "opa_set", "opa_derived"]:
            stats = tiers_summary[(t_val, t_name)].get(sys)
            if not stats:
                continue
            acc = (
                f"{stats['correct_count']}/{stats['total_count']} "
                f"({stats['correct_count']/stats['total_count']:.1%})"
            )
            if stats["latency_vals"]:
                vals = sorted(stats["latency_vals"])
                mid = vals[len(vals) // 2]
                avg_lat = f"{mid:.2f}"
            else:
                avg_lat = "N/A"
            avg_expl = (
                f"{stats['expl_sum']/stats['expl_count']:.2f}/{EXPL_MAX}"
                if stats["expl_count"]
                else "N/A"
            )
            md_summary.append(
                f"| {t_val} | {t_name} | `{sys}` | {acc} | {avg_lat} | {avg_expl} |"
            )

    (TABLES_DIR / "tier_summary.md").write_text("\n".join(md_summary) + "\n", encoding="utf-8")
    print("[OK] Wrote results/tables/tier_summary.md")

    # 3. Maintainability E1–E3 table
    if maintainability and "experiment_id" in maintainability[0]:
        md_m = [
            "# Maintainability Experiments E1–E3",
            "",
            "Edit-site counts for explicit change experiments (not per-scenario annotations).",
            "",
            "| Experiment | System | M1 Enforcement | M2 Semantic | M3 Data | M4 Classification code | M5 Dependent policies | Notes |",
            "| :--- | :--- | ---: | ---: | ---: | ---: | ---: | :--- |",
        ]
        for row in maintainability:
            md_m.append(
                f"| {row['experiment_id']}: {row['experiment_name']} | `{row['system']}` | "
                f"{row['m1_enforcement_policy_edits']} | {row['m2_semantic_edits']} | "
                f"{row['m3_data_edits']} | {row['m4_classification_code_edits']} | "
                f"{row['m5_dependent_policies_affected']} | {row.get('notes', '')} |"
            )
        (TABLES_DIR / "maintainability_e1_e3.md").write_text(
            "\n".join(md_m) + "\n", encoding="utf-8"
        )
        print("[OK] Wrote results/tables/maintainability_e1_e3.md")
    else:
        print("[WARN] maintainability.csv is not in E1–E3 format; skip maintainability table")

    # 4. Suite summary if expected JSON has suite field
    expected_dir = ROOT / "benchmark" / "expected"
    suite_counts = {"core": 0, "extension": 0}
    for p in expected_dir.glob("*.json"):
        exp = json.loads(p.read_text(encoding="utf-8"))
        suite_counts[exp.get("suite", "core")] = suite_counts.get(exp.get("suite", "core"), 0) + 1
    print(f"[INFO] Suite sizes: {suite_counts}")


if __name__ == "__main__":
    main()
