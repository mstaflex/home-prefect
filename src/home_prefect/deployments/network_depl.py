"""Deployment definitions for network flows.

Run this script once to register deployments with the Prefect server:

    python -m home_prefect.deployments.network
"""

from prefect import serve

from home_prefect.flows.network_health_flows import network_health_check


def main() -> None:
    """Register all network-related deployments."""
    health_deployment = network_health_check.to_deployment(
        name="network-health-check-hourly",
        cron="0 * * * *",  # every hour
        parameters={
            "hosts": ["192.168.1.1"],
            "endpoints": [],
        },
        tags=["network", "monitoring"],
    )
    serve(health_deployment)


if __name__ == "__main__":
    main()
