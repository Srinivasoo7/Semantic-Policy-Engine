# Maintainability Experiments E1–E3

Edit-site counts for explicit change experiments (not per-scenario annotations).

| Experiment | System | M1 Enforcement | M2 Semantic | M3 Data | M4 Classification code | M5 Dependent policies | Notes |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | :--- |
| E1: Add new production server | `rdf_owl_shacl` | 0 | 0 | 1 | 0 | 3 | One enterprise fact; OWL class definition unchanged; restart/deploy/logs shapes reuse ProductionServer. |
| E1: Add new production server | `opa_set` | 0 | 0 | 1 | 1 | 3 | Must add srv_new to production_servers set (classification-code edit). |
| E1: Add new production server | `opa_derived` | 0 | 0 | 1 | 0 | 3 | One JSON server record; is_production_server predicate unchanged. |
| E2: Expand ProductionServer definition | `rdf_owl_shacl` | 0 | 1 | 0 | 0 | 3 | One OWL equivalentClass edit; SHACL shapes untouched. |
| E2: Expand ProductionServer definition | `opa_set` | 0 | 0 | 0 | 1 | 3 | Must recompute/extend membership set or set-generation logic. |
| E2: Expand ProductionServer definition | `opa_derived` | 0 | 0 | 0 | 1 | 3 | One additional is_production_server rule head; allow/deny rules untouched. |
| E3: Abstraction reused by three policies | `rdf_owl_shacl` | 0 | 1 | 0 | 0 | 3 | Shared OWL class; three SHACL shapes target inferred class. |
| E3: Abstraction reused by three policies | `opa_set` | 0 | 0 | 0 | 1 | 3 | Shared production_servers set referenced by three rule groups. |
| E3: Abstraction reused by three policies | `opa_derived` | 0 | 0 | 0 | 1 | 3 | Shared is_production_server predicate referenced by three rule groups. |
