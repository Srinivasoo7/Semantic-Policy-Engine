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
