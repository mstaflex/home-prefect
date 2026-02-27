"""Network-related Prefect tasks (ping, HTTP checks, etc.)."""

import asyncio

import httpx
from prefect import get_run_logger, task


@task(name="ping-host", retries=2, retry_delay_seconds=5)
async def ping_host(host: str, count: int = 3) -> bool:
    """Return True if *host* is reachable via ICMP ping.

    Uses the OS `ping` command so no root privileges are required.
    """
    logger = get_run_logger()
    cmd = ["ping", "-c", str(count), "-W", "2", host]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    returncode = await proc.wait()
    reachable = returncode == 0
    logger.info("ping %s → %s", host, "OK" if reachable else "UNREACHABLE")
    return reachable


@task(name="http-check", retries=2, retry_delay_seconds=10)
async def http_check(url: str, timeout: float = 10.0) -> int:
    """Return the HTTP status code for *url*.

    Raises on network errors so Prefect can retry.
    """
    logger = get_run_logger()
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        response = await client.get(url)
    logger.info("GET %s → %d", url, response.status_code)
    return response.status_code
