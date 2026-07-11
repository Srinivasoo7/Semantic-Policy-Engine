# Research Claims — Frozen Scope

**Version:** 1.1  
**Status:** Frozen for post-repair artifact — update only with suite/results re-freeze.

---

## Main Claim

> RDF/OWL/SHACL does not necessarily improve decision accuracy over strong rule-based baselines (OPA-set, OPA-derived). Under **configured behavioral parity** on a shared 32-scenario suite, the systems differ in (1) **where semantic abstractions live**, (2) **which explanation fields are exported at runtime**, and (3) **cold-path latency**. RDF/OWL/SHACL localizes class definitions in OWL; OPA-derived localizes them in Rego predicates over JSON; OPA-set localizes them in explicit membership sets. OPA-derived can approach RDF/OWL/SHACL explanation field-export completeness when engineered to export derived traces. Semantic validation is slower on the current cold-evaluation Python prototype.

This is a **maintainability-location, explanation field-export, and latency** claim — not an accuracy-superiority claim.

---

## Decision Algebra (shared)

```
DENY ≻ REQUIRE_APPROVAL ≻ ALLOW_WITH_OBLIGATION ≻ ALLOW
```

Outcomes evaluated in this paper: `ALLOW`, `DENY`, `REQUIRE_APPROVAL`, `ALLOW_WITH_OBLIGATION`.

The semantic engine maps violated SHACL shapes to this algebra via an explicit decision adapter; Rego uses an `else` priority chain.

---

## ProductionServer definition (frozen, identical across systems)

A server is a `ProductionServer` if it is a `Server` and any of:

1. `belongsToEnvironment` / `environment` = `production`
2. `hasCriticality` / `criticality` = `customer_facing`
3. tag / tags contains `pci-dss`

---

## Supported Hypotheses

| ID  | Hypothesis | Evidence strategy |
|-----|------------|-------------------|
| H1  | All three systems can reproduce expected decisions after configuration | Decision match on 32 scenarios |
| H2  | RDF/OWL/SHACL incurs higher cold-path latency than OPA baselines | Latency harness |
| H3  | RDF/OWL/SHACL exports richer structured fields than OPA-set; OPA-derived can approach it when traces are exported | Explanation field-export score c1–c4 (max 4) |
| H4  | When class definitions evolve, edit location differs: OWL vs Rego predicate vs set | Maintainability experiments E1–E3 |

---

## What We Claim

- Semantic system localises domain-class changes in the OWL layer; SHACL shapes remain untouched when the class definition evolves (E2).
- Modular OPA-derived achieves similar fan-out via shared predicates; the distinction is **location**, not exclusive fan-out ability (E3).
- Runtime explanation artifacts can include asserted facts, inferred/derived classifications, violated rule/shape, and reason text.
- All three systems reach **configured behavioral parity** on the frozen suite.

## What We Do NOT Claim

- That RDF/OWL/SHACL is universally superior to OPA.
- That OPA is unsafe or unsuitable for agent governance.
- That the semantic path is a novel runtime interceptor architecture.
- Accuracy or generalization beyond the curated suite.
- That the benchmark represents real enterprise production traffic.
- Human explanation quality (no blinded reconstruction study yet).
- That a hybrid OPA+semantic router was empirically evaluated (deployment recommendation only).

---

## Benchmark Structure

- **Total:** 32 scenarios
- **Core suite:** scenarios whose causal features match long-standing production/ticket/skill/obligation rules
- **Extension suite:** state, break-glass, unknown provenance, admin-secret, prompt-injection — **implemented in all three systems** with causal features recorded in `benchmark/expected/*.json`

Each expected record includes:

- `expected_decision`
- `suite` (`core` | `extension`)
- `causal_features` (what actually drives the decision)

---

## Maintainability Metrics (E1–E3 only)

| Metric | Name | Definition |
|--------|------|------------|
| M1 | Enforcement-policy edits | SHACL shape or Rego allow/deny rule edits |
| M2 | Semantic-definition edits | OWL equivalentClass / unionOf edits |
| M3 | Data edits | Enterprise fact / JSON record edits |
| M4 | Classification-code edits | Rego set membership or `is_*` predicate edits |
| M5 | Dependent policies affected | Enforcement policies that reuse the abstraction |

Experiments:

- **E1** Add new production server  
- **E2** Expand ProductionServer definition  
- **E3** Abstraction reused by three policies (restart, deploy, query-logs)

---

## Explanation Metric

Runtime field-export completeness (main score, max 4):

1. asserted facts  
2. inferred / derived facts  
3. violated policy / rule  
4. decision reason  

`reconstructable_*` annotations in expected JSON are **optional metadata only** and are **not** part of the main score.

---

## Risky References to Verify Before Submission

- NVIDIA SkillSpector  
- Agent Skills in the Wild  
- SoK Agentic Skills  
- Governance-as-a-Service  
- AARM  

If unverifiable, remove or move to future work.
