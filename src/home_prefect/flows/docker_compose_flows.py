"""Docker Compose maintenance flows."""

from pathlib import Path

from prefect import flow
from prefect.logging import get_run_logger

from home_prefect.tasks.docker_tasks import (
    docker_compose_down,
    docker_compose_pull,
    docker_compose_up,
)


@flow(name="compose-down", log_prints=True)
async def compose_down(
    compose_dir: str | Path,
    remove_volumes: bool = False,
) -> bool:
    """Stop and remove a Docker Compose stack."""
    logger = get_run_logger()
    success = await docker_compose_down(compose_dir, remove_volumes=remove_volumes)
    logger.info("compose down %s", "succeeded" if success else "FAILED")
    return success


@flow(name="compose-up", log_prints=True)
async def compose_up(
    compose_dir: str | Path,
    services: list[str] | None = None,
) -> bool:
    """Start a Docker Compose stack."""
    logger = get_run_logger()
    success = await docker_compose_up(compose_dir, services=services)
    logger.info("compose up %s", "succeeded" if success else "FAILED")
    return success


@flow(name="compose-restart", log_prints=True)
async def compose_restart(
    compose_dir: str | Path,
    services: list[str] | None = None,
    remove_volumes: bool = False,
) -> bool:
    """Stop then start a Docker Compose stack."""
    logger = get_run_logger()

    down_ok = await docker_compose_down(compose_dir, remove_volumes=remove_volumes)
    if not down_ok:
        logger.error("compose down failed – aborting restart")
        return False

    up_ok = await docker_compose_up(compose_dir, services=services)
    logger.info("compose restart %s", "succeeded" if up_ok else "FAILED")
    return up_ok


@flow(name="compose-update", log_prints=True)
async def compose_update(
    compose_dir: str | Path,
    services: list[str] | None = None,
    remove_volumes: bool = False,
) -> bool:
    """Pull new images, then stop and restart the stack.

    Sequence: down → pull → up
    """
    logger = get_run_logger()

    down_ok = await docker_compose_down(compose_dir, remove_volumes=remove_volumes)
    if not down_ok:
        logger.error("compose down failed – aborting update")
        return False

    pull_ok = await docker_compose_pull(compose_dir)
    if not pull_ok:
        logger.error("compose pull failed – aborting update")
        return False

    up_ok = await docker_compose_up(compose_dir, services=services)
    logger.info("compose update %s", "succeeded" if up_ok else "FAILED")
    return up_ok


@flow(name="compose-pull-up", log_prints=True)
async def compose_pull_up(
    compose_dir: str | Path,
    services: list[str] | None = None,
) -> bool:
    """Pull new images and start the stack without taking it down first.

    Sequence: pull → up

    Useful when you want zero-downtime updates for services that support it,
    or when the stack is already stopped.
    """
    logger = get_run_logger()

    pull_ok = await docker_compose_pull(compose_dir)
    if not pull_ok:
        logger.error("compose pull failed – aborting")
        return False

    up_ok = await docker_compose_up(compose_dir, services=services)
    logger.info("compose pull-up %s", "succeeded" if up_ok else "FAILED")
    return up_ok
