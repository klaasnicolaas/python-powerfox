"""Auth tests for PowerFox."""
# pylint: disable=protected-access
import pytest
from aresponses import ResponsesMockServer

from powerfox import Powerfox
from powerfox.exceptions import PowerfoxAuthenticationError


async def test_authentication_error(
    aresponses: ResponsesMockServer,
    powerfox_client: Powerfox,
) -> None:
    """Test authentication error is handled correctly."""
    aresponses.add(
        "backend.powerfox.energy",
        "/api/2.0/test",
        "GET",
        aresponses.Response(status=401),
    )
    with pytest.raises(PowerfoxAuthenticationError):
        assert await powerfox_client._request("test")
