"""Auth tests for PowerFox."""
# pylint: disable=protected-access
# ruff: noqa: S106
import pytest
from aiohttp import ClientSession
from aresponses import ResponsesMockServer

from powerfox import Powerfox
from powerfox.exceptions import PowerfoxAuthenticationError


async def test_authentication_error(aresponses: ResponsesMockServer) -> None:
    """Test authentication error is handled correctly."""
    aresponses.add(
        "backend.powerfox.energy",
        "/api/2.0/test",
        "GET",
        aresponses.Response(status=401),
    )
    async with ClientSession() as session:
        client = Powerfox(username="user", password="pass", session=session)
        with pytest.raises(PowerfoxAuthenticationError):
            assert await client._request("test")
