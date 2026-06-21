from pathlib import Path

import pytest

from opa_policy.engine import run_policy_check


ROOT = Path(__file__).resolve().parents[1]


def scenario(name: str) -> Path:
    return ROOT / "input" / f"{name}.json"


def test_restart_denied_requires_approval():
    result = run_policy_check(scenario("restart_denied"), root=ROOT)
    assert result.decision == "REQUIRE_APPROVAL"


def test_restart_allowed():
    result = run_policy_check(scenario("restart_allowed"), root=ROOT)
    assert result.decision == "ALLOW"


def test_restart_staging_allowed():
    result = run_policy_check(scenario("restart_staging_allowed"), root=ROOT)
    assert result.decision == "ALLOW"


def test_skill_preload_review_requires_approval():
    result = run_policy_check(scenario("skill_preload_review"), root=ROOT)
    assert result.decision == "REQUIRE_APPROVAL"


def test_skill_postload_denied():
    result = run_policy_check(scenario("skill_postload_denied"), root=ROOT)
    assert result.decision == "DENY"

def test_restart_new_prod_server():
    result = run_policy_check(scenario("restart_new_prod_server"), root=ROOT)
    assert result.decision == "REQUIRE_APPROVAL"

def test_restart_customer_facing():
    result = run_policy_check(scenario("restart_customer_facing"), root=ROOT)
    assert result.decision == "REQUIRE_APPROVAL"

def test_deploy_prod():
    result = run_policy_check(scenario("deploy_prod"), root=ROOT)
    assert result.decision == "REQUIRE_APPROVAL"

def test_query_logs_prod():
    result = run_policy_check(scenario("query_logs_prod"), root=ROOT)
    assert result.decision == "ALLOW_WITH_OBLIGATION"

