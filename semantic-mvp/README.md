# Semantic Agent Policy MVP

A small, local, GitHub-ready prototype for testing the core paper idea:

> Agent action → RDF action graph → OWL inference → SHACL validation → runtime decision.

This repo demonstrates a standards-based semantic policy validation layer for AI agent actions using:

- **RDF** for action and enterprise facts
- **OWL** for inferred semantic classes
- **SHACL** for executable policy validation

The demo focuses on two scenarios:

1. **Tool action:** Restarting a production server.
2. **Skill action:** Invoking a payment-related Agent Skill under partial disclosure.

---

## Quick start

```bash
cd semantic-agent-policy-mvp

python -m venv .venv
source .venv/bin/activate      # macOS/Linux
# .venv\Scripts\activate     # Windows PowerShell

pip install -r requirements.txt
python run_validation.py --all
```

Expected high-level output:

```text
restart_denied           -> REQUIRE_APPROVAL
restart_allowed          -> ALLOW
restart_staging_allowed  -> ALLOW
skill_preload_review     -> REQUIRE_APPROVAL
skill_postload_denied    -> DENY
```

---

## Why this repo matters

This repo proves the technical core of the paper:

| Paper concept | Local implementation |
|---|---|
| RDF action graph | `data/scenarios/*.ttl` |
| Enterprise RDF graph | `data/enterprise.ttl` |
| OWL inference | `data/ontology.ttl` |
| SHACL validation | `shapes/policy_shapes.ttl` |
| Runtime decision | `src/semantic_policy/engine.py` |
| Explanations | SHACL result messages + inferred class checks |

The important example is this:

```text
srv_123 is asserted as:
  a Server
  belongsToEnvironment production

OWL infers:
  srv_123 a ProductionServer

SHACL validates:
  RestartServerAction targeting a ProductionServer requires approved change ticket
  or active break-glass exception.
```

So SHACL is not just querying raw properties. It depends on OWL-inferred semantic class membership.

---

## Run individual scenarios

```bash
python run_validation.py --scenario restart_denied
python run_validation.py --scenario restart_allowed
python run_validation.py --scenario restart_staging_allowed
python run_validation.py --scenario skill_preload_review
python run_validation.py --scenario skill_postload_denied
```

---

## Run tests

```bash
pytest -q
```

---

## Repo structure

```text
semantic-agent-policy-mvp/
├── README.md
├── requirements.txt
├── run_validation.py
├── data/
│   ├── ontology.ttl
│   ├── enterprise.ttl
│   └── scenarios/
│       ├── restart_denied.ttl
│       ├── restart_allowed.ttl
│       ├── restart_staging_allowed.ttl
│       ├── skill_preload_review.ttl
│       └── skill_postload_denied.ttl
├── shapes/
│   └── policy_shapes.ttl
├── src/
│   └── semantic_policy/
│       ├── __init__.py
│       ├── cli.py
│       └── engine.py
├── tests/
│   └── test_scenarios.py
└── examples/
    └── expected_outputs.md
```

---

## Scenario summary

| Scenario | Expected decision |
|---|---|
| `restart_denied` | `REQUIRE_APPROVAL` |
| `restart_allowed` | `ALLOW` |
| `restart_staging_allowed` | `ALLOW` |
| `skill_preload_review` | `REQUIRE_APPROVAL` |
| `skill_postload_denied` | `DENY` |

---

## Notes

This is an MVP, not the final experimental system. It is intentionally small so you can validate the core RDF/OWL/SHACL pipeline locally before building the full benchmark comparison.
