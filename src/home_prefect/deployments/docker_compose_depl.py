"""Deployment definitions for Docker Compose maintenance flows.

Run this script once to register deployments with the Prefect server.

Static deployments for a single stack:
    python -m home_prefect.deployments.docker_compose_depl

Auto-discovery of all compose stacks under a directory:
    python -m home_prefect.deployments.docker_compose_depl /path/to/docker
"""

import socket
import sys
from pathlib import Path

from prefect import serve

from home_prefect.flows.docker_compose_flows import (
    compose_down,
    compose_pull_up,
    compose_restart,
    compose_update,
    compose_up,
)

COMPOSE_FILE_NAMES = frozenset(
    {"docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"}
)


def _make_deployments_for_dir(
    compose_dir: Path,
    name_prefix: str,
    tags: list[str],
) -> list:
    """Return the five standard deployment objects for a single compose directory."""
    path_str = str(compose_dir)
    return [
        compose_down.to_deployment(
            name=f"{name_prefix}-compose_down",
            parameters={"compose_dir": path_str},
            tags=tags,
        ),
        compose_up.to_deployment(
            name=f"{name_prefix}-compose_up",
            parameters={"compose_dir": path_str},
            tags=tags,
        ),
        compose_restart.to_deployment(
            name=f"{name_prefix}-compose_restart",
            parameters={"compose_dir": path_str},
            tags=tags,
        ),
        compose_update.to_deployment(
            name=f"{name_prefix}-compose_update",
            parameters={"compose_dir": path_str},
            tags=tags,
        ),
        compose_pull_up.to_deployment(
            name=f"{name_prefix}-compose_pull_up",
            parameters={"compose_dir": path_str},
            tags=tags,
        ),
    ]


def discover_and_serve(
    search_path: str | Path,
    hostname: str | None = None,
) -> None:
    """Discover all docker-compose directories under *search_path* and serve deployments.

    For every immediate subdirectory that contains a compose file, five deployments
    are registered:

        <hostname>-docker-<dirname>-compose_down
        <hostname>-docker-<dirname>-compose_up
        <hostname>-docker-<dirname>-compose_restart
        <hostname>-docker-<dirname>-compose_update
        <hostname>-docker-<dirname>-compose_pull_up

    Deployment names are fully deterministic, so re-running this function is
    idempotent – existing deployments are updated, not duplicated.
    """
    search_path = Path(search_path)
    if hostname is None:
        hostname = socket.gethostname()

    tags = ["docker", "maintenance", hostname]
    all_deployments = []

    for candidate in sorted(search_path.iterdir()):
        if not candidate.is_dir():
            continue
        if not any((candidate / f).exists() for f in COMPOSE_FILE_NAMES):
            continue
        name_prefix = f"{hostname}-docker-{candidate.name}"
        all_deployments.extend(_make_deployments_for_dir(candidate, name_prefix, tags))

    if not all_deployments:
        raise ValueError(f"No docker-compose directories found under {search_path}")

    serve(*all_deployments)


def register_docker_deployments(compose_dir: str | Path = "docker/prefect_tester") -> None:
    """Register deployments for a single, explicitly named Docker Compose stack."""
    hostname = socket.gethostname()
    tags = ["docker", "maintenance", hostname]
    name_prefix = f"{hostname}-docker-{Path(compose_dir).name}"
    serve(*_make_deployments_for_dir(Path(compose_dir), name_prefix, tags))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        discover_and_serve(sys.argv[1])
    else:
        register_docker_deployments(compose_dir="docker/prefect_tester")
