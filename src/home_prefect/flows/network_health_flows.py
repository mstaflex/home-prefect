"""Example flow: check reachability of home-network devices."""

from prefect import flow
from prefect.logging import get_run_logger

from home_prefect.tasks.network_tasks import http_check, ping_host


@flow(name="network-health-check", log_prints=True)
async def network_health_check(
    hosts: list[str] | None = None,
    endpoints: list[str] | None = None,
) -> dict[str, bool]:
    """Ping a list of hosts and perform HTTP checks on a list of URLs.

    Args:
        hosts:     IP addresses or hostnames to ping (e.g. router, NAS, …).
        endpoints: HTTP(S) URLs to probe (e.g. internal services).

    Returns:
        A dict mapping each target to a boolean indicating reachability.
    """
    logger = get_run_logger()
    hosts = hosts or ["192.168.1.1"]
    endpoints = endpoints or []

    results: dict[str, bool] = {}

    for host in hosts:
        results[host] = await ping_host(host)

    for url in endpoints:
        status = await http_check(url)
        results[url] = 200 <= status < 400

    healthy = sum(v for v in results.values())
    logger.info("Health check done: %d/%d targets reachable", healthy, len(results))
    return results


if __name__ == "__main__":
    import asyncio

    asyncio.run(network_health_check.fn())
