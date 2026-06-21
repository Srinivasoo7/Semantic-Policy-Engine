from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

try:
    from regopy import Interpreter
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "regopy is required.  Install with: pip install -r requirements.txt"
    ) from exc


# ─────────────────────────────────────────────────────────────────────────────
# Result dataclass
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class PolicyResult:
    scenario: str
    decision: str
    messages: List[str]
    contrast_notes: List[str]
    raw_query: str
    asserted_facts: List[str] = field(default_factory=list)
    violated_policy: str = ""


# ─────────────────────────────────────────────────────────────────────────────
# Contrast notes — shown alongside each result to highlight the key
# difference between manual Rego encoding and OWL-inferred semantics.
# ─────────────────────────────────────────────────────────────────────────────

_CONTRAST: dict[str, List[str]] = {
    "restart_denied": [
        "Rego:     srv_123 in production_servers  (hand-maintained set)",
        "Semantic: :srv_123 :belongsToEnvironment :production",
        "          OWL infers -> :srv_123 a :ProductionServer",
        "          SHACL queries ?server a :ProductionServer (inferred type)",
    ],
    "restart_allowed": [
        "Same manual production_servers check as restart_denied.",
        "ALLOW because input.change_tickets contains an Approved ticket.",
        "Semantic: SHACL shape exempts if :hasChangeTicket/:hasStatus :Approved.",
    ],
    "restart_staging_allowed": [
        "Rego:     srv_456 in staging_servers  (hand-maintained set)",
        "Semantic: :srv_456 :belongsToEnvironment :staging",
        "          OWL infers -> :srv_456 a :StagingServer (not ProductionServer)",
        "          RestartProductionServerShape never fires -> ALLOW implicitly.",
        "Rego:     must add an explicit _allow branch for staging targets.",
    ],
    "skill_preload_review": [
        "Rego:     expense_reconciler in unverified_finance_skills (hand-maintained)",
        "Semantic: :expense_reconciler :hasVerificationStatus :Unverified",
        "          OWL infers -> :expense_reconciler a :UnverifiedSkill",
        "          SHACL separately checks :declaresTool/:requiresPermission :FinanceWriteAccess",
        "Rego:     collapses BOTH inference steps into one manually maintained set.",
    ],
    "skill_postload_denied": [
        "Rego:     checks instruction.type == 'CredentialExfiltrationInstruction' directly.",
        "Semantic: LoadedSkillCredentialExfiltrationShape (sh:Violation) fires,",
        "          engine maps sh:Violation severity -> DENY.",
    ],
}


# ─────────────────────────────────────────────────────────────────────────────
# OPA evaluation
# ─────────────────────────────────────────────────────────────────────────────

_QUERY = "x = data.agent_policy.decision"
_POLICY_PATH = "policies/agent_policy.rego"


def _evaluate(policy_text: str, input_data: dict) -> str:
    """Run the Rego policy against *input_data* and return the decision string."""
    rego = Interpreter()
    rego.add_module("agent_policy", policy_text)
    rego.set_input(input_data)

    result = rego.query(_QUERY)

    # regopy 1.x returns an Output object instead of a dict.
    if result:
        x_node = result.binding("x")
        if x_node is not None:
            return json.loads(str(x_node))

    return "REQUIRE_CLARIFICATION"


# ─────────────────────────────────────────────────────────────────────────────
# Human-readable policy messages (mirrors SHACL result messages)
# ─────────────────────────────────────────────────────────────────────────────

def _build_messages(decision: str, input_data: dict) -> List[str]:
    action_type = input_data.get("action_type", "")
    msgs: List[str] = []

    if decision == "DENY":
        msgs.append(
            "Loaded skill contains credential exfiltration or malicious "
            "instruction. Invocation must be denied."
        )
    elif decision == "REQUIRE_APPROVAL":
        if action_type == "RestartServerAction":
            msgs.append(
                "Restarting a production server requires an approved change "
                "ticket or an active break-glass exception."
            )
        elif action_type == "SkillInvocation":
            msgs.append(
                "Pre-load invocation of an unverified skill that declares "
                "finance-write tools requires approval or clarification."
            )

    return msgs


def _extract_asserted_facts(input_data: dict) -> List[str]:
    """Return key input fields as human-readable strings."""
    facts: List[str] = []
    for key in ("action_type", "targets", "requested_by", "performed_by",
                "disclosure_state", "linked_to_ticket", "reason"):
        val = input_data.get(key)
        if val:
            facts.append(f"{key}={val}")
    # Include non-empty lists
    for key in ("change_tickets", "exceptions", "instructions"):
        val = input_data.get(key)
        if val:
            facts.append(f"{key}={val}")
    return facts


def _extract_violated_policy(decision: str) -> str:
    """Map decision back to the Rego rule that caused it."""
    mapping = {
        "DENY": "_deny",
        "REQUIRE_APPROVAL": "_require_approval",
        "ALLOW_WITH_OBLIGATION": "_allow_with_obligation",
        "ALLOW": "_allow",
    }
    return mapping.get(decision, "")


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def run_policy_check(
    scenario_file: Path,
    root: Optional[Path] = None,
) -> PolicyResult:
    """Evaluate *scenario_file* (JSON) against the Rego policy and return a result."""
    if root is None:
        root = Path(__file__).resolve().parents[2]

    policy_text = (root / _POLICY_PATH).read_text(encoding="utf-8")
    input_data = json.loads(scenario_file.read_text(encoding="utf-8"))

    decision = _evaluate(policy_text, input_data)
    messages = _build_messages(decision, input_data)
    contrast_notes = _CONTRAST.get(scenario_file.stem, [])
    asserted_facts = _extract_asserted_facts(input_data)
    violated_policy = _extract_violated_policy(decision)

    return PolicyResult(
        scenario=scenario_file.stem,
        decision=decision,
        messages=messages,
        contrast_notes=contrast_notes,
        raw_query=_QUERY,
        asserted_facts=asserted_facts,
        violated_policy=violated_policy,
    )
