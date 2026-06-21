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

All three systems reach **behavioural parity** on the same scenario suite. The key difference is where maintenance occurs when the definition of a domain class (e.g. `ProductionServer`) evolves. All modular systems can fan out a centralized abstraction, but the semantic system natively localises this definition in the ontology rather than in enforcement policy code.

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

Our expanded benchmark contains 32 curated scenarios spanning 8 different validation tiers. 

To prevent stale results duplication, the generated benchmark metric tables are located under the results directory:
- **Aggregated Results**: [results/tables/tier_summary.md](file:///d:/Finance_Stocks/semantic-policy-agent-governance/results/tables/tier_summary.md) (Tier-wise aggregated summary)
- **Detailed Scenario Results**: [results/tables/comparison_table.md](file:///d:/Finance_Stocks/semantic-policy-agent-governance/results/tables/comparison_table.md) (Individual results per system and scenario)

---

## Citation

See `CITATION.cff` for machine-readable citation metadata.

---

## License

MIT — see `LICENSE`.
