"""Full-suite unit tests for the OPA-derived baseline."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from opa_policy.engine import run_policy_check

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
EXPECTED_DIR = REPO / "benchmark" / "expected"


def _all_expected() -> list[dict]:
    return [
        json.loads(p.read_text(encoding="utf-8"))
        for p in sorted(EXPECTED_DIR.glob("*.json"))
    ]


@pytest.mark.parametrize(
    "expected",
    _all_expected(),
    ids=lambda e: e["scenario_id"],
)
def test_scenario_matches_expected(expected: dict) -> None:
    sid = expected["scenario_id"]
    path = ROOT / "input" / f"{sid}.json"
    result = run_policy_check(path, root=ROOT)
    assert result.decision == expected["expected_decision"], (
        f"{sid}: got {result.decision}, want {expected['expected_decision']}"
    )
