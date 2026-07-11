# Benchmark Suite Notes (post-repair)

## Suites

| Suite | N | Purpose |
|-------|--:|---------|
| core | 21 | Long-standing classification, ticket, obligation, and skill policies |
| extension | 11 | State, break-glass, provenance, admin-secret, prompt-injection |

## Causal policies implemented in all three systems

| Feature | Decision effect |
|---------|-----------------|
| ProductionServer (env / criticality / pci-dss) | Drives restart/deploy/logs gates |
| Approved change ticket | Clears production restart/deploy approval |
| Active break-glass | Allows production restart/deploy without ticket |
| Expired break-glass | Does **not** clear approval |
| Active deployment freeze | **DENY** production deploy (no break-glass) |
| Open SEV1 incident | **REQUIRE_APPROVAL** for production restart even with ticket |
| Active maintenance window | Allows production restart without ticket |
| Unverified + finance-write skill (advertised) | REQUIRE_APPROVAL |
| Unknown provenance + privileged tool (advertised) | REQUIRE_APPROVAL |
| Admin-secret skill (advertised) | REQUIRE_APPROVAL |
| Loaded credential-exfil instruction | DENY |
| Loaded prompt-injection instruction | DENY |
| Production log query without audit obligation | ALLOW_WITH_OBLIGATION |

## Decision vocabulary (evaluated)

`ALLOW` | `DENY` | `REQUIRE_APPROVAL` | `ALLOW_WITH_OBLIGATION`

## Expected record schema (key fields)

```json
{
  "scenario_id": "...",
  "tier": 1,
  "tier_name": "...",
  "suite": "core|extension",
  "expected_decision": "...",
  "causal_features": ["..."]
}
```
