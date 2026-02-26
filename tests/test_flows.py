"""Tests for home_prefect flows."""

from unittest.mock import AsyncMock, patch

import pytest

from home_prefect.flows.network_health_flows import network_health_check


@pytest.mark.asyncio
async def test_network_health_check_all_reachable() -> None:
    with (
        patch(
            "home_prefect.flows.network_health.ping_host",
            new_callable=AsyncMock,
            return_value=True,
        ),
        patch(
            "home_prefect.flows.network_health.http_check",
            new_callable=AsyncMock,
            return_value=200,
        ),
    ):
        result = await network_health_check.fn(
            hosts=["192.168.1.1"],
            endpoints=["http://nas.local"],
        )

    assert result == {"192.168.1.1": True, "http://nas.local": True}


@pytest.mark.asyncio
async def test_network_health_check_host_down() -> None:
    with patch(
        "home_prefect.flows.network_health.ping_host",
        new_callable=AsyncMock,
        return_value=False,
    ):
        result = await network_health_check.fn(hosts=["10.0.0.99"], endpoints=[])

    assert result == {"10.0.0.99": False}
