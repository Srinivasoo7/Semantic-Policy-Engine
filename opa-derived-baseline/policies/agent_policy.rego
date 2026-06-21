##############################################################
# agent_policy.rego
#
# OPA/Rego baseline — same five scenarios as the RDF/OWL/SHACL
# semantic baseline in semantic-agent-policy-mvp/.
#
# ─────────────────────────────────────────────────────────────
# KEY DESIGN CONTRAST
# ─────────────────────────────────────────────────────────────
# Semantic baseline encodes production-ness ONCE in the ontology:
#
#   :srv_123 a :Server ;
#       :belongsToEnvironment :production .          ← single fact
#
#   :ProductionServer owl:equivalentClass [          ← inference rule
#       owl:intersectionOf (:Server
#           [owl:onProperty :belongsToEnvironment ;
#            owl:hasValue :production]) ] .
#
#   OWL INFERS at runtime: :srv_123 a :ProductionServer
#   SHACL queries:         ?server a :ProductionServer
#
# Here in Rego we MANUALLY enumerate every production server.
# No inference bridges "has environment=production" to
# "is a ProductionServer". Every new server joining production
# must be added to the set below by a human.
# ─────────────────────────────────────────────────────────────
package agent_policy

import rego.v1

# ============================================================
# SECTION 1 — Enterprise knowledge base (DERIVED from data)
# ============================================================

# Instead of hardcoded sets, we derive these dynamically from the
# data.enterprise JSON document injected by the engine.

is_production_server(srv) if data.enterprise.servers[srv].environment == "production"
is_production_server(srv) if data.enterprise.servers[srv].criticality == "customer_facing"
is_production_server(srv) if "pci-dss" in data.enterprise.servers[srv].tags

is_staging_server(srv) if data.enterprise.servers[srv].environment == "staging"

is_unverified_finance_skill(skill) if {
    data.enterprise.skills[skill].verification_status == "unverified"
    "finance_write" in data.enterprise.skills[skill].permissions
}

# ============================================================
# SECTION 2 — Priority-ordered policy decision (else chain)
# ============================================================

# DENY  > REQUIRE_APPROVAL > ALLOW_WITH_OBLIGATION > ALLOW  > REQUIRE_CLARIFICATION
decision := "DENY"                 if _deny
else       := "REQUIRE_APPROVAL"   if _require_approval
else       := "ALLOW_WITH_OBLIGATION" if _allow_with_obligation
else       := "ALLOW"

# ============================================================
# SECTION 3 — DENY conditions
# ============================================================

# A skill invocation that is already loaded and contains a
# credential-exfiltration instruction must be blocked immediately.
#
# Semantic baseline: sh:severity sh:Violation fires on
#   (:hasDisclosureState :loaded) ∧ (:hasInstruction ?i) ∧ (?i a :CredentialExfiltrationInstruction)
# Here the same three-part conjunction is written directly in Rego.
_deny if {
    input.action_type == "SkillInvocation"
    input.disclosure_state == "loaded"
    some instr in input.instructions
    instr.type == "CredentialExfiltrationInstruction"
}

# ============================================================
# SECTION 4 — REQUIRE_APPROVAL conditions
# ============================================================

# Restarting a production server without an approved change ticket
# or an active break-glass exception escalates to human approval.
#
# Semantic baseline: RestartProductionServerShape queries
#   ?server a :ProductionServer     ← OWL-inferred class
# Rego:              we test membership in production_servers (manual).
_require_approval if {
    input.action_type == "RestartServerAction"
    is_production_server(input.targets)
    not _has_approved_ticket
    not _has_break_glass_exception
}

# Pre-loading an unverified skill that touches finance-write tools
# requires human review before the skill is executed.
#
# Semantic baseline: UnverifiedFinanceSkillPreloadShape queries
#   ?skill a :UnverifiedSkill       ← OWL-inferred class
#   ?tool :requiresPermission :FinanceWriteAccess
# Rego:              we check membership in unverified_finance_skills (manual).
_require_approval if {
    input.action_type == "SkillInvocation"
    input.disclosure_state == "advertised"
    is_unverified_finance_skill(input.targets)
}

_require_approval if {
    input.action_type == "DeployAction"
    is_production_server(input.targets)
    not _has_approved_ticket
}

# ============================================================
# SECTION 4.5 — ALLOW_WITH_OBLIGATION conditions
# ============================================================
_allow_with_obligation if {
    input.action_type == "QueryLogsAction"
    is_production_server(input.targets)
    not input.has_audit_obligation
}

# ============================================================
# SECTION 5 — ALLOW conditions
# ============================================================

# Staging server restarts have no approval requirements.
#
# Semantic baseline: :RestartProductionServerShape targets :ProductionServer.
# srv_456 is not a :ProductionServer (OWL does not infer it), so the SHACL
# shape never fires → ALLOW implicitly.
# Rego: we must make the staging membership check explicit.
_allow if {
    input.action_type == "RestartServerAction"
    is_staging_server(input.targets)
}

# Production server restart with a valid, approved change ticket is allowed.
_allow if {
    input.action_type == "RestartServerAction"
    is_production_server(input.targets)
    _has_approved_ticket
}

# ============================================================
# SECTION 6 — Helper rules
# ============================================================

_has_approved_ticket if {
    some ticket in input.change_tickets
    ticket.status == "Approved"
}

_has_break_glass_exception if {
    some ex in input.exceptions
    ex.type == "ActiveBreakGlassException"
}
