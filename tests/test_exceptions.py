"""Auth tests for PowerFox."""

# pylint: disable=protected-access
import pytest
from aresponses import ResponsesMockServer

from powerfox import Powerfox
from powerfox.exceptions import (
    PowerfoxAuthenticationError,
    PowerfoxNoDataError,
    PowerfoxUnsupportedDeviceError,
)


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


async def test_no_poweropti_devices(
    aresponses: ResponsesMockServer,
    powerfox_client: Powerfox,
) -> None:
    """Test no Poweropti devices are found."""
    aresponses.add(
        "backend.powerfox.energy",
        "/api/2.0/my/all/devices",
        "GET",
        aresponses.Response(
            text="[]",
            headers={"Content-Type": "application/json"},
        ),
    )
    with pytest.raises(PowerfoxNoDataError):
        assert await powerfox_client.all_devices()


@pytest.mark.parametrize("method_name", ["device", "raw_device_data", "report"])
async def test_no_poweropti_data(
    aresponses: ResponsesMockServer,
    powerfox_client: Powerfox,
    method_name: str,
) -> None:
    """Test no Poweropti data is found."""
    path = "/api/2.0/my/test/current"
    if method_name == "report":
        path = "/api/2.0/my/test/report"
    aresponses.add(
        "backend.powerfox.energy",
        path,
        "GET",
        aresponses.Response(
            text="{}",
            headers={"Content-Type": "application/json"},
        ),
    )
    method = getattr(powerfox_client, method_name)
    with pytest.raises(PowerfoxNoDataError):
        await method("test")


async def test_unsupported_poweropti_device(
    aresponses: ResponsesMockServer,
    powerfox_client: Powerfox,
) -> None:
    """Test unsupported Poweropti device error is raised."""
    # Simulate a FLOW response with Division: 4 (unsupported)
    aresponses.add(
        "backend.powerfox.energy",
        "/api/2.0/my/unsupported_device/current",
        "GET",
        aresponses.Response(
            text='{"Division": 4, "Timestamp": 1718812800, "Outdated": false}',
            headers={"Content-Type": "application/json"},
        ),
    )
    with pytest.raises(PowerfoxUnsupportedDeviceError) as exc:
        await powerfox_client.device("unsupported_device")
    assert "Division=4" in str(exc.value)
