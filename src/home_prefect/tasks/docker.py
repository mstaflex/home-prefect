"""Docker Compose Prefect tasks.

Requirements
------------
The worker process must be able to run ``docker compose`` commands without
elevated privileges.  On Linux that means the OS user running the Prefect
worker must be a member of the ``docker`` group::

    sudo usermod -aG docker <worker-user>
    # log out / back in (or: newgrp docker) for the change to take effect

No ``sudo`` is needed or used here.
"""

import asyncio
from pathlib import Path

from prefect import get_run_logger, task


async def _run_compose(
    args: list[str],
    compose_dir: str | Path,
    timeout: float,
) -> tuple[bool, str]:
    """Run ``docker compose <args>`` in *compose_dir*.

    Returns ``(success, combined_output)``.
    """
    logger = get_run_logger()
    cwd = Path(compose_dir).expanduser().resolve()

    cmd = ["docker", "compose", *args]
    logger.info("Running %s in %s", " ".join(cmd), cwd)

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=cwd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,  # merge so order is preserved
    )

    try:
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        logger.error("docker compose %s timed out after %ss", args[0], timeout)
        return False, ""

    output = stdout.decode(errors="replace").strip()
    if output:
        logger.info(output)

    success = proc.returncode == 0
    if not success:
        logger.error("docker compose %s exited with code %d", args[0], proc.returncode)
    return success, output


@task(name="docker-compose-up", retries=2, retry_delay_seconds=10)
async def docker_compose_up(
    compose_dir: str | Path,
    services: list[str] | None = None,
    timeout: float = 180.0,
) -> bool:
    """Start a Docker Compose stack (detached).

    Parameters
    ----------
    compose_dir:
        Directory that contains the ``docker-compose.yml`` (or
        ``compose.yaml``) file.
    services:
        Optional list of service names to start.  When omitted all services
        defined in the compose file are started.
    timeout:
        Seconds to wait for the command to finish before giving up.

    Returns
    -------
    bool
        ``True`` if the command exited with return code 0.
    """
    args = ["up", "-d", "--remove-orphans"]
    if services:
        args.extend(services)

    success, _ = await _run_compose(args, compose_dir, timeout)
    return success


@task(name="docker-compose-down")
async def docker_compose_down(
    compose_dir: str | Path,
    remove_volumes: bool = False,
    timeout: float = 120.0,
) -> bool:
    """Stop and remove a Docker Compose stack.

    Parameters
    ----------
    compose_dir:
        Directory that contains the ``docker-compose.yml`` (or
        ``compose.yaml``) file.
    remove_volumes:
        When ``True`` also remove named volumes (``--volumes`` flag).
        Use with caution – data will be lost.
    timeout:
        Seconds to wait for the command to finish before giving up.

    Returns
    -------
    bool
        ``True`` if the command exited with return code 0.
    """
    args = ["down"]
    if remove_volumes:
        args.append("--volumes")

    success, _ = await _run_compose(args, compose_dir, timeout)
    return success


@task(name="docker-compose-pull", retries=2, retry_delay_seconds=10)
async def docker_compose_pull(
    compose_dir: str | Path,
    timeout: float = 300.0,
) -> bool:
    """Pull a Docker Compose stack (detached).

    Parameters
    ----------
    compose_dir:
        Directory that contains the ``docker-compose.yml`` (or
        ``compose.yaml``) file.
    timeout:
        Seconds to wait for the command to finish before giving up.

    Returns
    -------
    bool
        ``True`` if the command exited with return code 0.
    """
    args = ["pull"]

    success, _ = await _run_compose(args, compose_dir, timeout)
    return success
