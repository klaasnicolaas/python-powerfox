"""Tests for the PowerfoxLocal client."""

# pylint: disable=protected-access
import asyncio
from unittest.mock import patch

import pytest
from aiohttp import ClientError, ClientResponse, ClientSession
from aresponses import Response, ResponsesMockServer

from powerfox import PowerfoxLocal
from powerfox.exceptions import (
    PowerfoxAuthenticationError,
    PowerfoxConnectionError,
    PowerfoxError,
)

from . import load_fixtures


async def test_value(
    aresponses: ResponsesMockServer,
    powerfox_local_client: PowerfoxLocal,
) -> None:
    """Test getting value from local poweropti."""
    aresponses.add(
        "192.168.1.50",
        "/value",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("local_value.json"),
        ),
    )
    response = await powerfox_local_client.value()
    assert response.power == 228
    assert response.energy_usage == 17784955
    assert response.energy_usage_high_tariff == 17784955
    assert response.energy_usage_low_tariff == 0
    assert response.energy_return == 181


async def test_value_snapshot(
    aresponses: ResponsesMockServer,
    powerfox_local_client: PowerfoxLocal,
    snapshot: ...,
) -> None:
    """Test value response matches snapshot."""
    aresponses.add(
        "192.168.1.50",
        "/value",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("local_value.json"),
        ),
    )
    response = await powerfox_local_client.value()
    assert response == snapshot


async def test_internal_session(aresponses: ResponsesMockServer) -> None:
    """Test internal session is handled correctly."""
    aresponses.add(
        "192.168.1.50",
        "/value",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("local_value.json"),
        ),
    )
    async with PowerfoxLocal(host="192.168.1.50", api_key="1097bd725557") as client:
        await client._request("value")


async def test_authentication_error(
    aresponses: ResponsesMockServer,
    powerfox_local_client: PowerfoxLocal,
) -> None:
    """Test authentication error handling."""
    aresponses.add(
        "192.168.1.50",
        "/value",
        "GET",
        aresponses.Response(status=401),
    )
    with pytest.raises(PowerfoxAuthenticationError):
        await powerfox_local_client._request("value")


async def test_timeout(aresponses: ResponsesMockServer) -> None:
    """Test request timeout from the local poweropti."""

    async def response_handler(_: ClientResponse) -> Response:
        await asyncio.sleep(0.2)
        return aresponses.Response(
            body="Goodmorning!",
            text=load_fixtures("local_value.json"),
        )

    aresponses.add(
        "192.168.1.50",
        "/value",
        "GET",
        response_handler,
    )

    async with ClientSession() as session:
        client = PowerfoxLocal(
            host="192.168.1.50",
            api_key="1097bd725557",
            session=session,
            request_timeout=0.1,
        )
        with pytest.raises(PowerfoxConnectionError):
            await client._request("value")


async def test_content_type(
    aresponses: ResponsesMockServer,
    powerfox_local_client: PowerfoxLocal,
) -> None:
    """Test content type is handled correctly."""
    aresponses.add(
        "192.168.1.50",
        "/value",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
        ),
    )
    with pytest.raises(PowerfoxError):
        await powerfox_local_client._request("value")


async def test_client_error() -> None:
    """Test client error is handled correctly."""
    async with ClientSession() as session:
        client = PowerfoxLocal(
            host="192.168.1.50",
            api_key="1097bd725557",
            session=session,
        )
        with (
            patch.object(
                session,
                "request",
                side_effect=ClientError,
            ),
            pytest.raises(PowerfoxConnectionError),
        ):
            await client._request("value")


async def test_response_status_404(
    aresponses: ResponsesMockServer,
    powerfox_local_client: PowerfoxLocal,
) -> None:
    """Test HTTP 404 response handling."""
    aresponses.add(
        "192.168.1.50",
        "/value",
        "GET",
        aresponses.Response(status=404),
    )
    with pytest.raises(PowerfoxConnectionError):
        await powerfox_local_client._request("value")
