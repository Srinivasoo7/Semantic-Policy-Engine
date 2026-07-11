##############################################################
# agent_policy.rego — OPA-derived baseline
#
# Classifications are derived from enterprise JSON via reusable
# predicates (is_production_server, is_unverified_finance_skill, ...).
# Decision algebra: DENY ≻ REQUIRE_APPROVAL ≻ ALLOW_WITH_OBLIGATION ≻ ALLOW
#
# ProductionServer definition (frozen, matches OWL):
#   environment == "production"
#   OR criticality == "customer_facing"
#   OR "pci-dss" in tags
##############################################################
package agent_policy

import rego.v1

# ============================================================
# SECTION 1 — Derived classifications from enterprise JSON
# ============================================================

is_production_server(srv) if data.enterprise.servers[srv].environment == "production"
is_production_server(srv) if data.enterprise.servers[srv].criticality == "customer_facing"
is_production_server(srv) if "pci-dss" in data.enterprise.servers[srv].tags

is_staging_server(srv) if data.enterprise.servers[srv].environment == "staging"

is_unverified_finance_skill(skill) if {
	data.enterprise.skills[skill].verification_status == "unverified"
	"finance_write" in data.enterprise.skills[skill].permissions
}

is_unknown_provenance_skill(skill) if {
	data.enterprise.skills[skill].verification_status == "unknown"
}

is_admin_secret_skill(skill) if {
	"admin_secret" in data.enterprise.skills[skill].permissions
}

# ============================================================
# SECTION 2 — Priority-ordered decision
# ============================================================

decision := "DENY" if _deny
else := "REQUIRE_APPROVAL" if _require_approval
else := "ALLOW_WITH_OBLIGATION" if _allow_with_obligation
else := "ALLOW"

# ============================================================
# SECTION 3 — DENY
# ============================================================

_deny if {
	input.action_type == "SkillInvocation"
	input.disclosure_state == "loaded"
	some instr in input.instructions
	instr.type == "CredentialExfiltrationInstruction"
}

_deny if {
	input.action_type == "SkillInvocation"
	input.disclosure_state == "loaded"
	some instr in input.instructions
	instr.type == "PromptInjectionInstruction"
}

# Production deploy during active freeze without break-glass
_deny if {
	input.action_type == "DeployAction"
	is_production_server(input.targets)
	input.is_deployment_freeze == true
	not _has_break_glass_exception
}

# ============================================================
# SECTION 4 — REQUIRE_APPROVAL
# ============================================================

# Restart production without ticket / break-glass / maintenance
_require_approval if {
	input.action_type == "RestartServerAction"
	is_production_server(input.targets)
	not _has_approved_ticket
	not _has_break_glass_exception
	not _in_maintenance_window
}

# Restart production during open SEV1 incident (ticket insufficient)
_require_approval if {
	input.action_type == "RestartServerAction"
	is_production_server(input.targets)
	input.has_active_incident == true
	not _has_break_glass_exception
}

# Deploy production without ticket or break-glass
_require_approval if {
	input.action_type == "DeployAction"
	is_production_server(input.targets)
	not _has_approved_ticket
	not _has_break_glass_exception
}

# Unverified finance skill preload
_require_approval if {
	input.action_type == "SkillInvocation"
	input.disclosure_state == "advertised"
	is_unverified_finance_skill(input.targets)
}

# Unknown provenance skill with privileged permissions
_require_approval if {
	input.action_type == "SkillInvocation"
	input.disclosure_state == "advertised"
	is_unknown_provenance_skill(input.targets)
	_skill_has_privileged_permission(input.targets)
}

# Admin-secret skill preload
_require_approval if {
	input.action_type == "SkillInvocation"
	input.disclosure_state == "advertised"
	is_admin_secret_skill(input.targets)
}

# ============================================================
# SECTION 5 — ALLOW_WITH_OBLIGATION
# ============================================================

_allow_with_obligation if {
	input.action_type == "QueryLogsAction"
	is_production_server(input.targets)
	not input.has_audit_obligation
}

# ============================================================
# SECTION 6 — Helpers
# ============================================================

_has_approved_ticket if {
	some ticket in input.change_tickets
	ticket.status == "Approved"
}

_has_break_glass_exception if {
	some ex in input.exceptions
	ex.type == "ActiveBreakGlassException"
}

_has_break_glass_exception if {
	some ex in input.exceptions
	ex.type == "BreakGlassException"
	ex.status == "active"
}

_in_maintenance_window if {
	input.in_maintenance_window == true
}

_skill_has_privileged_permission(skill) if {
	"finance_write" in data.enterprise.skills[skill].permissions
}

_skill_has_privileged_permission(skill) if {
	"admin_secret" in data.enterprise.skills[skill].permissions
}
