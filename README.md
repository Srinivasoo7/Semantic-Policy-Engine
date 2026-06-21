# Semantic Policy Agent Governance

A comparative study of **RDF/OWL/SHACL**, **OPA-set**, and **OPA-derived** baselines for governing AI agent actions.

> **Paper title (working):** *When Do Semantic-Web Policies Help Govern AI Agent Actions? A Comparative Study of RDF/OWL/SHACL, OPA/Rego, and Runtime Guardrails*

---

## Repository Structure

```
semantic-policy-agent-governance/
├── semantic-mvp/           # RDF/OWL/SHACL baseline
├── opa-set-baseline/       # OPA baseline using static production-server sets
├── opa-derived-baseline/   # OPA baseline using derived is_production_server() predicates
├── benchmark/
│   ├── scenarios/          # Shared JSON scenario inputs
│   ├── expected/           # Ground-truth expected decisions
│   └── schemas/            # JSON Schema definitions for scenarios and results
├── experiments/
│   ├── run_all_experiments.py
│   ├── latency.py
│   ├── explanation_quality.py
│   └── maintainability.py
├── results/
│   ├── raw/                # Raw JSON/CSV outputs from each run
│   ├── tables/             # Rendered markdown/LaTeX tables
│   └── figures/            # Generated charts and diagrams
├── paper/
│   └── research_claims.md  # Frozen scope — do not change without explicit revision
├── README.md
├── LICENSE
└── CITATION.cff
```

---

## What This Repository Compares

| System           | Classification strategy                                    | Policy strategy                     |
|------------------|------------------------------------------------------------|-------------------------------------|
| RDF/OWL/SHACL    | OWL `equivalentClass` + `unionOf` → inferred type         | SHACL shapes targeting inferred class |
| OPA-set          | Static set `production_servers := {...}`                   | Rego allow/deny rules over set membership |
| OPA-derived      | Dynamic predicates `is_production_server(srv) if ...`      | Rego allow/deny rules over derived predicates |

All three systems reach **behavioural parity** on the same scenario suite. The key difference is where maintenance occurs when the definition of a domain class (e.g. `ProductionServer`) evolves.

---

## Quick Start

### Prerequisites

- Python 3.8+
- Windows or Linux/macOS
- Install all baselines in editable mode:
  ```bash
  pip install -e semantic-mvp/
  pip install -e opa-set-baseline/
  pip install -e opa-derived-baseline/
  ```

### Run all tests

You can run individual test suites cleanly:
```bash
python -m pytest semantic-mvp/tests/ -q
python -m pytest opa-set-baseline/tests/ -q
python -m pytest opa-derived-baseline/tests/ -q
```

### Run the measurement harnesses & aggregate tables

```bash
# Run accuracy, maintainability, explanation quality, and latency measurements
python experiments/run_all_experiments.py
python experiments/maintainability.py
python experiments/explanation_quality.py
python experiments/latency.py --iterations 10

# Generate Markdown/LaTeX tables under results/tables/
python experiments/generate_tables.py
```

---

## Benchmark Tiers and Scenarios (32 Scenarios)

Our expanded benchmark contains 32 curated scenarios spanning 8 different validation tiers. The table below presents theaggregated accuracy, average latency, and average explanation quality scores:

| Tier | Tier Name | System | Accuracy | Avg Latency (ms) | Avg Explanation Score |
| :---: | :--- | :--- | :---: | :---: | :---: |
| **1** | Flat access | `rdf_owl_shacl` | 2/2 (100.0%) | ~728.38 ms | 4.00/5 |
| **1** | Flat access | `opa_set` | 2/2 (100.0%) | ~8.51 ms | 2.00/5 |
| **1** | Flat access | `opa_derived` | 2/2 (100.0%) | ~91.90 ms | 4.00/5 |
| **2** | Attribute-based | `rdf_owl_shacl` | 4/4 (100.0%) | ~600.03 ms | 4.00/5 |
| **2** | Attribute-based | `opa_set` | 4/4 (100.0%) | ~10.04 ms | 2.00/5 |
| **2** | Attribute-based | `opa_derived` | 4/4 (100.0%) | ~84.46 ms | 4.00/5 |
| **4** | Relationship-dependent | `rdf_owl_shacl` | 5/5 (100.0%) | ~628.59 ms | 4.80/5 |
| **4** | Relationship-dependent | `opa_set` | 5/5 (100.0%) | ~7.88 ms | 2.60/5 |
| **4** | Relationship-dependent | `opa_derived` | 5/5 (100.0%) | ~80.79 ms | 4.60/5 |
| **5** | State-dependent | `rdf_owl_shacl` | 4/4 (100.0%) | ~630.42 ms | 4.50/5 |
| **5** | State-dependent | `opa_set` | 4/4 (100.0%) | ~7.55 ms | 2.25/5 |
| **5** | State-dependent | `opa_derived` | 4/4 (100.0%) | ~75.00 ms | 4.25/5 |
| **6** | Exception/break-glass | `rdf_owl_shacl` | 4/4 (100.0%) | ~619.80 ms | 5.00/5 |
| **6** | Exception/break-glass | `opa_set` | 4/4 (100.0%) | ~7.40 ms | 2.50/5 |
| **6** | Exception/break-glass | `opa_derived` | 4/4 (100.0%) | ~73.79 ms | 4.50/5 |
| **7** | Obligation | `rdf_owl_shacl` | 4/4 (100.0%) | ~578.55 ms | 4.50/5 |
| **7** | Obligation | `opa_set` | 4/4 (100.0%) | ~7.52 ms | 2.00/5 |
| **7** | Obligation | `opa_derived` | 4/4 (100.0%) | ~79.27 ms | 4.00/5 |
| **8** | Skill composition/provenance | `rdf_owl_shacl` | 5/5 (100.0%) | ~691.46 ms | 4.60/5 |
| **8** | Skill composition/provenance | `opa_set` | 5/5 (100.0%) | ~8.74 ms | 2.60/5 |
| **8** | Skill composition/provenance | `opa_derived` | 5/5 (100.0%) | ~87.24 ms | 4.60/5 |
| **9** | Adversarial skill proposer | `rdf_owl_shacl` | 4/4 (100.0%) | ~711.19 ms | 5.00/5 |
| **9** | Adversarial skill proposer | `opa_set` | 4/4 (100.0%) | ~8.36 ms | 3.00/5 |
| **9** | Adversarial skill proposer | `opa_derived` | 4/4 (100.0%) | ~126.54 ms | 5.00/5 |

See `results/tables/comparison_table.md` for individual scenario results.

---

## Citation

See `CITATION.cff` for machine-readable citation metadata.

---

## License

MIT — see `LICENSE`.
