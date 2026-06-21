# Research Claims — Frozen Scope

**Version:** 1.0  
**Status:** Frozen — do not change without explicit revision and re-sign-off.

---

## Main Claim

> RDF/OWL/SHACL does not necessarily improve decision accuracy over strong rule-based baselines (OPA-set, OPA-derived). In terms of latency, RDF/OWL/SHACL is roughly two orders of magnitude slower than the lightweight OPA-set baseline, but only single-digit multiples slower than the stronger OPA-derived baseline in the current cold-evaluation prototype. In terms of explanation, RDF/OWL/SHACL produces substantially richer explanations than OPA-set, but OPA-derived can approach or match RDF/OWL/SHACL explanation completeness when explicitly engineered to export derived predicate traces. The strongest remaining distinction is maintainability location: RDF/OWL/SHACL localizes semantic class definitions in OWL, OPA-derived localizes them in Rego predicates over JSON, and OPA-set localizes them in explicit classification sets.

This is a **maintainability and explanation completeness** claim, not a raw accuracy superiority claim.

---

## Supported Hypotheses

| ID  | Hypothesis                                                                                                 | Evidence strategy                                                             |
|-----|------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|
| H3  | RDF/OWL/SHACL produces substantially richer explanations than OPA-set; OPA-derived can approach or match RDF/OWL/SHACL explanation completeness when explicitly engineered to export derived predicate traces | Explanation-completeness (field-completeness) metric across all 3 systems      |
| H4  | RDF/OWL/SHACL requires fewer enforcement-policy edits when semantic class definitions change               | Maintainability metrics M1–M5 across E1–E3                                    |
| RQ6 | The latency overhead of OWL inference + SHACL validation is roughly two orders of magnitude slower than the lightweight OPA-set baseline, but only single-digit multiples slower than the stronger OPA-derived baseline in the current cold-evaluation prototype, supporting feasibility for high-impact, non-realtime action gates rather than high-frequency realtime tool-call filtering | Latency benchmark across 100/500/1000 iterations on all 8 core scenarios      |

---

## What We Claim

- Semantic system localises domain-class changes in the OWL layer; SHACL shapes remain untouched when the class definition evolves.
- When a domain abstraction (e.g. `ProductionServer`) is reused across N enforcement policies, a single semantic edit propagates automatically to all N policies.
- Explanations from the semantic system trace fact → inference → violated policy, which is more auditable than set-membership or predicate-evaluation traces.
- All three systems (RDF/OWL/SHACL, OPA-set, OPA-derived) can reach **behavioural parity** given appropriate configuration.

---

## What We Do NOT Claim

- That RDF/OWL/SHACL is universally superior to OPA in all dimensions.
- That OPA is unsafe or unsuitable for AI agent governance.
- That the semantic system is novel as a runtime action firewall (related work already exists).
- That the semantic system beats all baselines in decision accuracy.
- That the benchmark is representative of real enterprise production systems (it is synthetic).
- Anything about NVIDIA SkillSpector, Agent Skills in the Wild, SoK Agentic Skills, or Governance-as-a-Service without verified citations.

---

## Maintainability Metrics

| Metric | Name                            | Definition                                                                   |
|--------|---------------------------------|------------------------------------------------------------------------------|
| M1     | Enforcement-policy edits        | Number of SHACL shape or Rego allow/deny rule edits required                 |
| M2     | Semantic-definition edits       | Number of OWL equivalentClass / unionOf definition edits required            |
| M3     | Data edits                      | Number of enterprise fact additions or changes required                      |
| M4     | Classification-code edits       | Number of Rego predicate edits (e.g. `is_production_server()`) required      |
| M5     | Dependent policies affected     | Number of dependent enforcement policies affected by one centralized abstraction edit |

---

## Decision Vocabulary

| Decision               | Meaning                                                                   |
|------------------------|---------------------------------------------------------------------------|
| `ALLOW`                | Action permitted without restriction                                      |
| `DENY`                 | Action blocked; must not proceed                                          |
| `REQUIRE_APPROVAL`     | Human approval required before action proceeds                            |
| `ALLOW_WITH_OBLIGATION`| Action permitted but must be logged / audited (obligation policy)         |
| `REQUIRE_CLARIFICATION`| Insufficient information to make a decision; action is paused             |

---

## Benchmark Target

- **Minimum:** 30 scenarios
- **Ideal:** 36–40 scenarios
- **Maximum for first submission:** 50 scenarios (only if time allows)

Scenario distribution: see `benchmark/schemas/` for tier definitions.

---

## Risky References to Verify Before Submission

The following references must be verified against actual released papers or specifications before inclusion:

- NVIDIA SkillSpector
- Agent Skills in the Wild
- SoK Agentic Skills
- Governance-as-a-Service
- AARM

If unverifiable, move to future work or remove entirely.
