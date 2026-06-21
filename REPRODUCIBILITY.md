# Reproducibility Notes

This document provides guidelines for reproducing the benchmark results and outlines historical changes to the tooling environment.

## Execution Environment

All tables in the repository were generated using Python 3.8+ on the benchmark code at the recorded commit hash. 

### Latency Measurement Strategy
Latency benchmarks are executed via `experiments/latency.py`. For each scenario:
1. A single warm-up evaluation of the policy engine is run to compile the rules and load initial graphs into memory.
2. The engine is then run for `N` timed iterations (default `100`, configured to `10` or more for verification).
3. The median and 95th percentile (p95) times are calculated and saved under `results/raw/latency.csv`.

To regenerate the results tables:
```bash
# Run all accuracy, maintainability, and explanation metrics
python experiments/run_all_experiments.py
python experiments/maintainability.py
python experiments/explanation_quality.py

# Run the latency benchmarks (e.g. 100 iterations)
python experiments/latency.py --iterations 100

# Aggregates results into results/tables/
python experiments/generate_tables.py
```

## OPA Package-Name Collision Fix

> [!NOTE]
> Earlier development versions of the benchmark code used the same Python distribution name (`opa-policy-baseline`) in `pyproject.toml` for both the `opa-set-baseline` and `opa-derived-baseline` sub-packages.
>
> The artifact now uses distinct package names, `opa-set-baseline` and `opa-derived-baseline`, to avoid editable-install contamination where one installation would silently overwrite the other. Ensure you reinstall the updated packages:
> ```bash
> pip install -e opa-set-baseline/
> pip install -e opa-derived-baseline/
> ```

---

## Results Snapshot

The benchmark results in the tables were generated and verified using the following system parameters:

- **Commit**: `c29a76b` (with subsequent documentation polish commits)
- **Python Version**: `3.8.19 (AuthenticAMD, Windows 64-bit)`
- **OS / CPU**: `Windows 11 (build 26200) / AMD64 Family 23 Model 96 Stepping 1`
- **Latency Iterations**: `10` or `100` timed runs after `1` warm-up call
- **Generated Outputs**:
  - Raw Metrics: `results/raw/decision_accuracy.csv`, `results/raw/maintainability.csv`, `results/raw/explanation_quality.csv`, `results/raw/latency.csv`
  - Rendered Markdown Tables: `results/tables/comparison_table.md`, `results/tables/tier_summary.md`
  - LaTeX Output: `results/tables/comparison_table.tex`
