"""Basic tests for Powerfox."""

import asyncio
from unittest.mock import patch

import pytest
from aiohttp import ClientError, ClientResponse, ClientSession
from aresponses import Response, ResponsesMockServer

from powerfox import Powerfox
from powerfox.exceptions import (
    PowerfoxAuthenticationError,
    PowerfoxConnectionError,
    PowerfoxError,
)

from . import load_fixtures


async def test_json_request(
    aresponses: ResponsesMockServer,
    powerfox_client: Powerfox,
) -> None:
    """Test JSON response is handled correctly."""
    aresponses.add(
        "backend.powerfox.energy",
        "/api/2.0/test",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("all_devices.json"),
        ),
    )
    await powerfox_client._request("test")
    await powerfox_client.close()


async def test_internal_session(aresponses: ResponsesMockServer) -> None:
    """Test internal session is handled correctly."""
    aresponses.add(
        "backend.powerfox.energy",
        "/api/2.0/test",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("all_devices.json"),
        ),
    )
    async with Powerfox(username="user", password="pass") as client:
        await client._request("test")


async def test_timeout(aresponses: ResponsesMockServer) -> None:
    """Test request timeout from the Powerfox API."""

    # Faking a timeout by sleeping
    async def response_handler(_: ClientResponse) -> Response:
        await asyncio.sleep(0.2)
        return aresponses.Response(
            body="Goodmorning!",
            text=load_fixtures("all_devices.json"),
        )

    aresponses.add(
        "backend.powerfox.energy",
        "/api/2.0/test",
        "GET",
        response_handler,
    )

    async with ClientSession() as session:
        client = Powerfox(
            username="user",
            password="pass",
            session=session,
            request_timeout=0.1,
        )
        with pytest.raises(PowerfoxConnectionError):
            await client._request("test")


async def test_content_type(
    aresponses: ResponsesMockServer,
    powerfox_client: Powerfox,
) -> None:
    """Test content type is handled correctly."""
    aresponses.add(
        "backend.powerfox.energy",
        "/api/2.0/test",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
        ),
    )
    with pytest.raises(PowerfoxError):
        assert await powerfox_client._request("test")


async def test_client_error() -> None:
    """Test client error is handled correctly."""
    async with ClientSession() as session:
        client = Powerfox(username="user", password="pass", session=session)
        with (
            patch.object(
                session,
                "request",
                side_effect=ClientError,
            ),
            pytest.raises(PowerfoxConnectionError),
        ):
            assert await client._request("test")


async def test_response_status_404(
    aresponses: ResponsesMockServer,
    powerfox_client: Powerfox,
) -> None:
    """Test HTTP 404 response handling."""
    aresponses.add(
        "backend.powerfox.energy",
        "/api/2.0/test",
        "GET",
        aresponses.Response(status=404),
    )
    with pytest.raises(PowerfoxConnectionError):
        assert await powerfox_client._request("test")


@pytest.mark.parametrize("failures", [1, 2])
async def test_transient_unauthorized_retry(
    aresponses: ResponsesMockServer,
    powerfox_client: Powerfox,
    failures: int,
) -> None:
    """Retry intermittent HTTP 401 responses before accepting a valid response."""
    for _ in range(failures):
        aresponses.add(
            "backend.powerfox.energy",
            "/api/2.0/test",
            "GET",
            aresponses.Response(status=401),
        )
    aresponses.add(
        "backend.powerfox.energy",
        "/api/2.0/test",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("all_devices.json"),
        ),
    )
    with patch("powerfox.powerfox.asyncio.sleep", return_value=None):
        assert await powerfox_client._request("test") == load_fixtures(
            "all_devices.json"
        )


async def test_persistent_unauthorized(
    aresponses: ResponsesMockServer,
    powerfox_client: Powerfox,
) -> None:
    """Preserve authentication errors after bounded HTTP 401 retries."""
    for _ in range(3):
        aresponses.add(
            "backend.powerfox.energy",
            "/api/2.0/test",
            "GET",
            aresponses.Response(status=401),
        )
    with (
        patch("powerfox.powerfox.asyncio.sleep", return_value=None),
        pytest.raises(PowerfoxAuthenticationError),
    ):
        await powerfox_client._request("test")


async def test_unauthorized_non_get_not_retried(
    aresponses: ResponsesMockServer,
    powerfox_client: Powerfox,
) -> None:
    """Do not retry methods that might have side effects."""
    aresponses.add(
        "backend.powerfox.energy",
        "/api/2.0/test",
        "POST",
        aresponses.Response(status=401),
    )
    with pytest.raises(PowerfoxAuthenticationError):
        await powerfox_client._request("test", method="POST")
