# OPA-derived Policy Baseline

Companion project to [`semantic-mvp`](../semantic-mvp/).
Runs the validation scenarios using [OPA](https://www.openpolicyagent.org/)
Rego policies (evaluated in-process via [regopy](https://pypi.org/project/regopy/)),
so you can compare the approaches side-by-side.

---

## Quick start

```bash
cd opa-derived-baseline

python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate

pip install -r requirements.txt
python run_validation.py --all
```

Expected output:

```
Scenario : restart_denied
Decision : REQUIRE_APPROVAL

Scenario : restart_allowed
Decision : ALLOW

Scenario : restart_staging_allowed
Decision : ALLOW

Scenario : skill_preload_review
Decision : REQUIRE_APPROVAL

Scenario : skill_postload_denied
Decision : DENY
```

---

## The core comparison

| Concept | Semantic baseline (RDF/OWL/SHACL) | OPA-derived Baseline (OPA/Rego) |
|---|---|---|
| Production-ness | Encoded **once** as ontology equivalentClass rule; OWL **infers** `srv_123 a ProductionServer` from `belongsToEnvironment :production` | Dynamically evaluated at runtime via `is_production_server(srv)` Rego rules over `data.enterprise` JSON |
| Staging-ness | OWL infers `srv_456 a StagingServer` | Dynamically evaluated via `is_staging_server(srv)` rule |
| Unverified skill | OWL infers `a UnverifiedSkill` from `hasVerificationStatus :Unverified` | Dynamically evaluated via `is_unverified_finance_skill(skill)` rule |
| Finance-write check | SHACL queries `?tool :requiresPermission :FinanceWriteAccess` separately | Dynamically evaluated via properties in JSON database |
| Adding a new prod server | Add one triple: `:srv_999 :belongsToEnvironment :production` | Add server and its metadata to `enterprise.json` |
| Reusability | OWL class hierarchy is globally reusable across shapes | Custom predicates are defined globally in Rego helper package |

### Why this matters

In the semantic baseline, production-ness is an **ontological property**:

```turtle
# data/enterprise.ttl — one fact
:srv_123 :belongsToEnvironment :production .

# data/ontology.ttl — one reusable rule
:ProductionServer owl:equivalentClass [
    owl:intersectionOf (:Server
        [owl:onProperty :belongsToEnvironment ;
         owl:hasValue   :production]) ] .
```

OWL inference **materialises** `:srv_123 a :ProductionServer` at runtime.
The SHACL shape then simply asks `?server a :ProductionServer` — no hardcoded IDs anywhere.

In this OPA-derived baseline, the same rules are dynamically derived from input enterprise JSON data rather than hardcoded sets:

```rego
# policies/agent_policy.rego — dynamic classification rule
is_production_server(srv) if data.enterprise.servers[srv].environment == "production"
is_production_server(srv) if data.enterprise.servers[srv].criticality == "customer_facing"
is_production_server(srv) if "pci-dss" in data.enterprise.servers[srv].tags
```

This avoids manual set enumeration, but still encodes the schema translation rules directly in policy code rather than a centralized ontology layer.

---

## Repo structure

```
opa-policy-baseline/
├── README.md
├── requirements.txt
├── run_validation.py
├── pyproject.toml
├── policies/
│   └── agent_policy.rego        ← the Rego policy (with contrast comments)
├── input/
│   ├── restart_denied.json
│   ├── restart_allowed.json
│   ├── restart_staging_allowed.json
│   ├── skill_preload_review.json
│   └── skill_postload_denied.json
├── src/
│   └── opa_derived_policy/
│       ├── __init__.py
│       ├── engine.py             ← uses regopy.Interpreter
│       └── cli.py
├── tests/
│   └── test_scenarios.py
└── .github/
    └── workflows/
        └── tests.yml
```

---

## Run tests

```bash
pytest -q
```

---

## Scenario summary

| Scenario | Decision |
|---|---|
| `restart_denied` | `REQUIRE_APPROVAL` |
| `restart_allowed` | `ALLOW` |
| `restart_staging_allowed` | `ALLOW` |
| `skill_preload_review` | `REQUIRE_APPROVAL` |
| `skill_postload_denied` | `DENY` |

---

## Run individual scenarios

```bash
python run_validation.py --scenario restart_denied
python run_validation.py --scenario skill_postload_denied
python run_validation.py --all --no-contrast   # suppress contrast notes
```
