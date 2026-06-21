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

- Python 3.9+
- Windows or Linux/macOS
- `pip install -r semantic-mvp/requirements.txt`
- `pip install -r opa-set-baseline/requirements.txt`
- `pip install -r opa-derived-baseline/requirements.txt`

### Run all tests

```bash
# Semantic MVP
cd semantic-mvp && pytest tests/ -q

# OPA-set baseline
cd ../opa-set-baseline && pytest tests/ -q

# OPA-derived baseline
cd ../opa-derived-baseline && pytest tests/ -q
```

### Run individual scenarios

```bash
cd semantic-mvp
python -m semantic_policy.cli restart_denied
python -m semantic_policy.cli --all
```

---

## Maintainability Results (Experiments 1–3)

| Experiment | RDF/OWL/SHACL edit | SHACL edits | OPA-set edit | OPA-derived edit | Result |
|---|---:|---:|---:|---:|---|
| Add `srv_999` | 1 RDF fact | 0 | 1 set update | 0 if JSON contains environment | Semantic and OPA-derived generalize; OPA-set needs set update |
| Expand `ProductionServer` | 1 OWL definition edit | 0 | 1 set update | 1 Rego predicate update | Semantic keeps enforcement rules unchanged |
| 3 policies depend on `ProductionServer` | 1 OWL edit + 1 fact | 0 across 3 policies | 1 classification update | 1 Rego predicate update | All systems match behavior; maintenance layer differs |

### Edit type definitions

| Edit type | Meaning |
|---|---|
| Data edit | Add or change enterprise facts |
| Semantic edit | Change the definition of a domain class like `ProductionServer` |
| Enforcement-policy edit | Change SHACL shape or Rego allow/deny rule |
| Classification-code edit | Change Rego predicate such as `is_production_server()` |

---

## Core Scenarios (9)

| Scenario | Expected Decision | Tier |
|---|---|---|
| `restart_denied` | `REQUIRE_APPROVAL` | 4 |
| `restart_allowed` | `ALLOW` | 4 |
| `restart_staging_allowed` | `ALLOW` | 2 |
| `skill_preload_review` | `REQUIRE_APPROVAL` | 8 |
| `skill_postload_denied` | `DENY` | 8 |
| `restart_new_prod_server` | `REQUIRE_APPROVAL` | 4 |
| `restart_customer_facing` | `REQUIRE_APPROVAL` | 4 |
| `deploy_prod` | `REQUIRE_APPROVAL` | 4 |
| `query_logs_prod` | `ALLOW_WITH_OBLIGATION` | 7 |

---

## Citation

See `CITATION.cff` for machine-readable citation metadata.

---

## License

MIT — see `LICENSE`.
