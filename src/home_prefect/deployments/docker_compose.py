"""Deployment definitions for Docker Compose maintenance flows.

Run this script once to register deployments with the Prefect server:

    python -m home_prefect.deployments.docker_compose
"""

from prefect import serve

from home_prefect.flows.docker_compose import (
    compose_down,
    compose_pull_up,
    compose_restart,
    compose_update,
    compose_up,
)

COMPOSE_DIR = "docker/prefect_tester"


def main() -> None:
    """Register all Docker Compose deployments for the prefect_tester stack."""
    down = compose_down.to_deployment(
        name="prefect-tester-down",
        parameters={"compose_dir": COMPOSE_DIR},
        tags=["docker", "maintenance"],
    )
    up = compose_up.to_deployment(
        name="prefect-tester-up",
        parameters={"compose_dir": COMPOSE_DIR},
        tags=["docker", "maintenance"],
    )
    restart = compose_restart.to_deployment(
        name="prefect-tester-restart",
        parameters={"compose_dir": COMPOSE_DIR},
        tags=["docker", "maintenance"],
    )
    update = compose_update.to_deployment(
        name="prefect-tester-update",
        parameters={"compose_dir": COMPOSE_DIR},
        tags=["docker", "maintenance"],
    )
    pull_up = compose_pull_up.to_deployment(
        name="prefect-tester-pull-up",
        parameters={"compose_dir": COMPOSE_DIR},
        tags=["docker", "maintenance"],
    )
    serve(down, up, restart, update, pull_up)


if __name__ == "__main__":
    main()
