# Semantic Policy Agent Governance

A comparative study of **RDF/OWL/SHACL**, **OPA-set**, and **OPA-derived** baselines for governing AI agent actions.

> **Paper title (working):** *When Do Semantic-Web Policies Help Govern AI Agent Actions? A Comparative Study of RDF/OWL/SHACL, OPA/Rego, and Runtime Guardrails*

---

## Repository Structure

```
Semantic-Policy-Engine/
├── semantic-mvp/           # RDF/OWL/SHACL baseline
├── opa-set-baseline/       # OPA baseline using static classification sets
├── opa-derived-baseline/   # OPA baseline using derived is_* predicates
├── benchmark/
│   ├── expected/           # Ground-truth decisions + causal_features + suite
│   └── schemas/            # JSON Schema definitions
├── experiments/
│   ├── run_all_experiments.py
│   ├── latency.py
│   ├── explanation_quality.py
│   ├── maintainability.py  # E1–E3 edit-site experiments
│   └── generate_tables.py
├── results/
│   ├── raw/
│   └── tables/
├── paper/
│   └── research_claims.md  # Frozen scope
├── README.md
├── LICENSE
└── CITATION.cff
```

---

## What This Repository Compares

| System        | Classification strategy                               | Policy strategy                               |
|---------------|--------------------------------------------------------|-----------------------------------------------|
| RDF/OWL/SHACL | OWL `equivalentClass` + `unionOf` → inferred type     | SHACL shapes targeting inferred class         |
| OPA-set       | Static set `production_servers := {...}`              | Rego allow/deny rules over set membership     |
| OPA-derived   | Dynamic predicates `is_production_server(srv) if ...` | Rego allow/deny rules over derived predicates |

**Frozen `ProductionServer` definition (identical across systems):**

- environment = production, **or**
- criticality = customer_facing, **or**
- tag `pci-dss`

**Shared decision algebra:**

```
DENY ≻ REQUIRE_APPROVAL ≻ ALLOW_WITH_OBLIGATION ≻ ALLOW
```

All three systems reach **configured behavioral parity** on the same 32-scenario suite. The key difference is **where** maintenance occurs when a domain class evolves.

---

## Benchmark (32 scenarios)

| Suite | Count | Contents |
|-------|------:|----------|
| **core** | 21 | Flat/attribute access, production classification, tickets, obligations, finance skill, credential exfil |
| **extension** | 11 | Deployment freeze, SEV1 incident, maintenance window, break-glass valid/expired, unknown provenance, admin-secret skill, prompt injection |

Each `benchmark/expected/*.json` record includes:

- `expected_decision`
- `suite` (`core` | `extension`)
- `causal_features` — features that **actually** drive the decision

---

## Quick Start

### Prerequisites

- Python 3.8+
- Install baselines in editable mode:

```bash
pip install -e semantic-mvp/
pip install -e opa-set-baseline/
pip install -e opa-derived-baseline/
```

### Run tests

Run each suite separately (avoids `tests` package name collisions):

```bash
python3 -m pytest opa-set-baseline/tests/ -q
python3 -m pytest opa-derived-baseline/tests/ -q
python3 -m pytest semantic-mvp/tests/ -q
```

### Run measurement harnesses

```bash
python3 experiments/run_all_experiments.py
python3 experiments/maintainability.py
python3 experiments/explanation_quality.py
python3 experiments/latency.py --iterations 10
python3 experiments/generate_tables.py
```

### Generated outputs

- `results/raw/decision_accuracy.csv`
- `results/raw/maintainability.csv` (E1–E3)
- `results/raw/maintainability_e1_e3.json`
- `results/raw/explanation_quality.csv` (score max **4**, runtime fields only)
- `results/raw/latency.csv`
- `results/tables/comparison_table.md`
- `results/tables/tier_summary.md`
- `results/tables/maintainability_e1_e3.md`

---

## Metrics (honest definitions)

| Metric | What it measures |
|--------|------------------|
| **Behavioral conformance** | Exact match to configured expected decisions |
| **Maintainability E1–E3** | Edit-site counts for add-server, expand-class, multi-policy fan-out |
| **Explanation field-export** | Presence of asserted facts, inferred/derived facts, violated rule, reason (max 4) |
| **Latency** | Cold-path prototype timing (environment-dependent) |

See `paper/research_claims.md` for frozen claims and non-claims.

---

## Citation

See `CITATION.cff`.

## License

MIT — see `LICENSE`.
