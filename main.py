"""Command-line entry point for the PassKit Python quickstart."""

from __future__ import annotations

import argparse

from quickstarts.api import PassKitApi
from quickstarts.client import ConnectionPool
from quickstarts.config import Config
from quickstarts.workflows.coupons import CouponsWorkflow
from quickstarts.workflows.event_tickets import EventTicketsWorkflow
from quickstarts.workflows.flights import FlightsWorkflow
from quickstarts.workflows.membership import MembershipWorkflow

WORKFLOWS = {
    "membership": MembershipWorkflow,
    "loyalty": MembershipWorkflow,
    "coupons": CouponsWorkflow,
    "event-tickets": EventTicketsWorkflow,
    "tickets": EventTicketsWorkflow,
    "flights": FlightsWorkflow,
}


def pass_url(config: Config, identifier: str) -> str:
    region = "pub2" if "pub2" in config.address else "pub1"
    return f"https://{region}.pskt.io/{identifier}"


def run(command: str) -> None:
    if command == "operations":
        operations = PassKitApi.operations()
        total = sum(len(methods) for methods in operations.values())
        for service, methods in operations.items():
            print(f"{service} ({len(methods)}): {', '.join(methods)}")
        print(f"\n{total} SDK operations are available through PassKitApi.")
        return

    config = Config.load()
    config.validate(require_flights=command == "flights")
    pool = ConnectionPool(config)
    workflow = WORKFLOWS[command](pool, config)
    try:
        results = workflow.execute()
        print("Created resources:")
        for label, value in results.items():
            output = value if label.lower().endswith("url") else pass_url(config, value)
            print(f"  {label}: {output}")
    finally:
        try:
            workflow.cleanup()
        finally:
            pool.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a PassKit Python quickstart")
    parser.add_argument(
        "command",
        choices=[
            "membership",
            "loyalty",
            "coupons",
            "event-tickets",
            "tickets",
            "flights",
            "operations",
        ],
        help="product workflow or SDK operation listing",
    )
    args = parser.parse_args()
    run(args.command)


if __name__ == "__main__":
    main()
