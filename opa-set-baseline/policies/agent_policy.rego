##############################################################
# agent_policy.rego — OPA-set baseline
#
# Classifications are explicit membership sets maintained by hand.
# Decision algebra: DENY ≻ REQUIRE_APPROVAL ≻ ALLOW_WITH_OBLIGATION ≻ ALLOW
##############################################################
package agent_policy

import rego.v1

# ============================================================
# SECTION 1 — Explicit classification sets (manual maintenance)
# ============================================================

# Must be updated when a new production-class server is introduced.
production_servers := {"srv_123", "srv_999", "srv_888", "srv_777"}
staging_servers := {"srv_456"}

# Collapses UnverifiedSkill + finance_write into one hand-maintained set.
unverified_finance_skills := {"expense_reconciler"}

# Unknown provenance skills with privileged tools
unknown_provenance_privileged_skills := {"unknown_provenance_skill"}

# Skills that declare admin-secret tools
admin_secret_skills := {"admin_ops_skill", "credential_harvester"}

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

_deny if {
	input.action_type == "DeployAction"
	input.targets in production_servers
	input.is_deployment_freeze == true
	not _has_break_glass_exception
}

# ============================================================
# SECTION 4 — REQUIRE_APPROVAL
# ============================================================

_require_approval if {
	input.action_type == "RestartServerAction"
	input.targets in production_servers
	not _has_approved_ticket
	not _has_break_glass_exception
	not _in_maintenance_window
}

_require_approval if {
	input.action_type == "RestartServerAction"
	input.targets in production_servers
	input.has_active_incident == true
	not _has_break_glass_exception
}

_require_approval if {
	input.action_type == "DeployAction"
	input.targets in production_servers
	not _has_approved_ticket
	not _has_break_glass_exception
}

_require_approval if {
	input.action_type == "SkillInvocation"
	input.disclosure_state == "advertised"
	input.targets in unverified_finance_skills
}

_require_approval if {
	input.action_type == "SkillInvocation"
	input.disclosure_state == "advertised"
	input.targets in unknown_provenance_privileged_skills
}

_require_approval if {
	input.action_type == "SkillInvocation"
	input.disclosure_state == "advertised"
	input.targets in admin_secret_skills
}

# ============================================================
# SECTION 5 — ALLOW_WITH_OBLIGATION
# ============================================================

_allow_with_obligation if {
	input.action_type == "QueryLogsAction"
	input.targets in production_servers
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
