# Expected Outputs

Run:

```bash
python run_validation.py --all
```

Expected decisions:

```text
restart_denied           -> REQUIRE_APPROVAL
restart_allowed          -> ALLOW
restart_staging_allowed  -> ALLOW
skill_preload_review     -> REQUIRE_APPROVAL
skill_postload_denied    -> DENY
```

The exact SHACL report text can vary slightly by `pyshacl` version.

## Why `restart_denied` is blocked

The data asserts:

```text
srv_123 a Server
srv_123 belongsToEnvironment production
```

OWL infers:

```text
srv_123 a ProductionServer
srv_123 a CriticalInfrastructureAsset
```

SHACL sees a `RestartServerAction` targeting a `ProductionServer` without an approved change ticket or active break-glass exception.

Decision:

```text
REQUIRE_APPROVAL
```

## Why `restart_allowed` passes

Same production target, but the action has:

```text
hasChangeTicket CHG_001
CHG_001 hasStatus Approved
```

Decision:

```text
ALLOW
```

## Why `skill_preload_review` needs approval

The skill is only advertised/pre-load, has unverified provenance, and declares a finance-write tool.

Decision:

```text
REQUIRE_APPROVAL
```

## Why `skill_postload_denied` is denied

The fully loaded skill action contains a credential-exfiltration instruction.

Decision:

```text
DENY
```
