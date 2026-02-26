"""Docker Compose maintenance flow."""

from enum import Enum
from pathlib import Path

from prefect import flow
from prefect.logging import get_run_logger

from home_prefect.tasks.docker_tasks import (
    docker_compose_down,
    docker_compose_pull,
    docker_compose_up,
)


class ComposeAction(str, Enum):
    up = "up"
    down = "down"
    restart = "restart"
    update = "update"   # down → pull → up
    pull_up = "pull_up"  # pull → up  (no prior down)


@flow(name="docker-compose", log_prints=True)
async def docker_compose(
    compose_dir: str | Path,
    action: ComposeAction,
    services: list[str] | None = None,
    remove_volumes: bool = False,
) -> bool:
    """Generic Docker Compose maintenance flow.

    Parameters
    ----------
    compose_dir:
        Directory containing the compose file.
    action:
        What to do: up | down | restart | update | pull_up.
    services:
        Optional subset of services (used by up/restart/update/pull_up).
    remove_volumes:
        Remove named volumes on down (used by down/restart/update).
    """
    logger = get_run_logger()

    match action:
        case ComposeAction.up:
            ok = await docker_compose_up(compose_dir, services=services)

        case ComposeAction.down:
            ok = await docker_compose_down(compose_dir, remove_volumes=remove_volumes)

        case ComposeAction.restart:
            ok = await docker_compose_down(compose_dir, remove_volumes=remove_volumes)
            if not ok:
                logger.error("compose down failed – aborting restart")
                return False
            ok = await docker_compose_up(compose_dir, services=services)

        case ComposeAction.update:
            ok = await docker_compose_down(compose_dir, remove_volumes=remove_volumes)
            if not ok:
                logger.error("compose down failed – aborting update")
                return False
            ok = await docker_compose_pull(compose_dir)
            if not ok:
                logger.error("compose pull failed – aborting update")
                return False
            ok = await docker_compose_up(compose_dir, services=services)

        case ComposeAction.pull_up:
            ok = await docker_compose_pull(compose_dir)
            if not ok:
                logger.error("compose pull failed – aborting")
                return False
            ok = await docker_compose_up(compose_dir, services=services)

    logger.info("compose %s %s", action.value, "succeeded" if ok else "FAILED")
    return ok
