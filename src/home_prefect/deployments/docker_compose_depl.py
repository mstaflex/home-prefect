"""Deployment definitions for Docker Compose maintenance flows.

Run this script once to register deployments with the Prefect server.

Auto-discovery of all compose stacks under a directory:
    python -m home_prefect.deployments.docker_compose_depl /path/to/docker
"""

import socket
import sys
from pathlib import Path

from prefect import serve

from home_prefect.flows.docker_compose_flows import docker_compose

COMPOSE_FILE_NAMES = frozenset(
    {"docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"}
)


def discover_and_serve(
    search_path: str | Path,
    hostname: str | None = None,
) -> None:
    """Discover all docker-compose directories under *search_path* and serve deployments.

    For every immediate subdirectory that contains a compose file, one deployment
    is registered:

        <hostname>-docker-<dirname>

    The ``action`` parameter is chosen at runtime when triggering the flow run.
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
        all_deployments.append(
            docker_compose.to_deployment(
                name=f"{hostname}-docker-{candidate.name}",
                parameters={"compose_dir": str(candidate)},
                tags=tags,
            )
        )

    if not all_deployments:
        raise ValueError(f"No docker-compose directories found under {search_path}")

    serve(*all_deployments)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        discover_and_serve(sys.argv[1])
    else:
        raise SystemExit("Usage: python -m home_prefect.deployments.docker_compose_depl <path>")
