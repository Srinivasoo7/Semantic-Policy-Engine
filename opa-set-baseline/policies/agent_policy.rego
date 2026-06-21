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
# SECTION 1 — Enterprise knowledge base (MANUALLY encoded)
# ============================================================

# Semantic baseline: :srv_123 :belongsToEnvironment :production
#                    OWL infers → :srv_123 a :ProductionServer
# Rego:              we hard-code the membership here.
production_servers := {"srv_123", "srv_999", "srv_888", "srv_777"}

# Semantic baseline: :srv_456 :belongsToEnvironment :staging
#                    OWL infers → :srv_456 a :StagingServer
# Rego:              we hard-code the membership here.
staging_servers := {"srv_456"}

# Semantic baseline:
#   :expense_reconciler :hasVerificationStatus :Unverified .
#   :UnverifiedSkill owl:equivalentClass [
#       owl:onProperty :hasVerificationStatus ; owl:hasValue :Unverified ] .
#   OWL infers → :expense_reconciler a :UnverifiedSkill
#   SHACL then checks :declaresTool/:requiresPermission :FinanceWriteAccess
#
# Rego: we collapse BOTH inference steps into one hand-maintained set.
# The single set encodes the conjunction that OWL+SHACL derives in two
# separate, reusable layers.
unverified_finance_skills := {"expense_reconciler"}

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
    input.targets in production_servers
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
    input.targets in unverified_finance_skills
}

_require_approval if {
    input.action_type == "DeployAction"
    input.targets in production_servers
    not _has_approved_ticket
}

# ============================================================
# SECTION 4.5 — ALLOW_WITH_OBLIGATION conditions
# ============================================================
_allow_with_obligation if {
    input.action_type == "QueryLogsAction"
    input.targets in production_servers
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
    input.targets in staging_servers
}

# Production server restart with a valid, approved change ticket is allowed.
_allow if {
    input.action_type == "RestartServerAction"
    input.targets in production_servers
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
