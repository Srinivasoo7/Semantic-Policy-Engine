from __future__ import annotations

import argparse
from pathlib import Path

from semantic_policy.engine import run_policy_check


SCENARIOS = {
    "restart_denied": "restart_denied.ttl",
    "restart_allowed": "restart_allowed.ttl",
    "restart_staging_allowed": "restart_staging_allowed.ttl",
    "skill_preload_review": "skill_preload_review.ttl",
    "skill_postload_denied": "skill_postload_denied.ttl",
    "restart_new_prod_server": "restart_new_prod_server.ttl",
    "restart_customer_facing": "restart_customer_facing.ttl",
    "deploy_prod": "deploy_prod.ttl",
    "query_logs_prod": "query_logs_prod.ttl",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def print_result(result) -> None:
    print("=" * 80)
    print(f"Scenario: {result.scenario}")
    print(f"Conforms: {result.conforms}")
    print(f"Decision: {result.decision}")

    if result.inferred_types:
        print("Key inferred/visible semantic types:")
        for item in result.inferred_types:
            print(f"  - {item}")

    if result.messages:
        print("Policy messages:")
        for message in result.messages:
            print(f"  - {message}")

    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run RDF/OWL/SHACL policy validation scenarios."
    )
    parser.add_argument(
        "--scenario",
        choices=sorted(SCENARIOS.keys()),
        help="Run one scenario by name.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all scenarios.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable pySHACL debug output.",
    )

    args = parser.parse_args()
    root = repo_root()

    if not args.all and not args.scenario:
        parser.error("Use --all or --scenario <name>")

    selected = SCENARIOS.keys() if args.all else [args.scenario]

    for name in selected:
        scenario_file = root / "data" / "scenarios" / SCENARIOS[name]
        result = run_policy_check(scenario_file, root=root, debug=args.debug)
        print_result(result)


if __name__ == "__main__":
    main()
