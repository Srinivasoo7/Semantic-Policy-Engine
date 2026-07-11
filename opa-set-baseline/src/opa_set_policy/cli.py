from __future__ import annotations

import argparse
from pathlib import Path

from opa_set_policy.engine import run_policy_check, PolicyResult


SCENARIOS: dict[str, str] = {
    "restart_denied":          "restart_denied.json",
    "restart_allowed":         "restart_allowed.json",
    "restart_staging_allowed": "restart_staging_allowed.json",
    "skill_preload_review":    "skill_preload_review.json",
    "skill_postload_denied":   "skill_postload_denied.json",
    "restart_new_prod_server": "restart_new_prod_server.json",
    "restart_customer_facing": "restart_customer_facing.json",
    "deploy_prod": "deploy_prod.json",
    "query_logs_prod": "query_logs_prod.json",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def print_result(result: PolicyResult, show_contrast: bool = True) -> None:
    print("=" * 80)
    print(f"Scenario : {result.scenario}")
    print(f"Decision : {result.decision}")

    if result.messages:
        print("Messages :")
        for msg in result.messages:
            print(f"  - {msg}")

    if show_contrast and result.contrast_notes:
        print("Contrast (Rego manual vs. OWL inferred):")
        for note in result.contrast_notes:
            print(f"  - {note}")

    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run OPA/Rego policy validation scenarios."
    )
    parser.add_argument(
        "--scenario",
        choices=sorted(SCENARIOS),
        help="Run one scenario by name.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all scenarios.",
    )
    parser.add_argument(
        "--no-contrast",
        action="store_true",
        help="Suppress the manual-vs-inferred contrast notes.",
    )

    args = parser.parse_args()
    root = repo_root()

    if not args.all and not args.scenario:
        parser.error("Use --all or --scenario <name>")

    selected = list(SCENARIOS) if args.all else [args.scenario]

    for name in selected:
        scenario_file = root / "input" / SCENARIOS[name]
        result = run_policy_check(scenario_file, root=root)
        print_result(result, show_contrast=not args.no_contrast)


if __name__ == "__main__":
    main()
