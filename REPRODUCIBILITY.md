# Reproducibility Notes

## Execution Environment

Regenerate all tables from a clean editable install:

```bash
pip install -e semantic-mvp/
pip install -e opa-set-baseline/
pip install -e opa-derived-baseline/

python3 -m pytest opa-set-baseline/tests/ -q
python3 -m pytest opa-derived-baseline/tests/ -q
python3 -m pytest semantic-mvp/tests/ -q

python3 experiments/run_all_experiments.py
python3 experiments/maintainability.py
python3 experiments/explanation_quality.py
python3 experiments/latency.py --iterations 10
python3 experiments/generate_tables.py
```

Use `python3` if `python` is not on PATH.

### Latency Measurement Strategy

`experiments/latency.py` for each scenario:

1. One warm-up evaluation  
2. `N` timed iterations (default often 10 for author snapshots)  
3. Median and p95 written to `results/raw/latency.csv`

Latency is **environment-dependent** and measures a **cold-evaluation prototype** (graph load + OWL-RL + SHACL each call unless otherwise stated). Absolute milliseconds must not be mixed across machines.

## OPA Package-Name Collision Fix

Earlier versions used the same distribution name for both OPA baselines. The artifact now uses distinct names:

- `opa-set-baseline`
- `opa-derived-baseline`

Reinstall both after pull.

## Pytest note

Run each baseline’s tests in a **separate** pytest invocation. The three packages historically shared a `tests` package basename; separate invocations avoid import collisions.

## Suite integrity

- **32 scenarios**, each with `causal_features` and `suite` (`core` | `extension`) in `benchmark/expected/`
- Extension policies (freeze, incident, maintenance, break-glass, unknown provenance, admin-secret, prompt-injection) are implemented in **all three** systems
- Decision algebra: `DENY ≻ REQUIRE_APPROVAL ≻ ALLOW_WITH_OBLIGATION ≻ ALLOW`
- Maintainability is **E1–E3 only** (not per-scenario zero rows)
- Explanation main score is **c1–c4 only** (max 4); reconstructability annotations are metadata only

## Results Snapshot (post-repair)

- **Decision conformance:** 96/96 (32 scenarios × 3 systems) after P0 repair  
- **Unit tests:** 32 per system (96 total)  
- **Generated outputs:**
  - `results/raw/decision_accuracy.csv`
  - `results/raw/maintainability.csv` / `maintainability_e1_e3.json`
  - `results/raw/explanation_quality.csv`
  - `results/raw/latency.csv`
  - `results/tables/comparison_table.md`
  - `results/tables/tier_summary.md`
  - `results/tables/maintainability_e1_e3.md`
  - `results/tables/comparison_table.tex`

Record the git commit SHA and `pip freeze` in the paper’s experimental-setup section before submission.

See `paper/research_claims.md` for frozen claims.
