"""Auth tests for PowerFox."""

# pylint: disable=protected-access
import pytest
from aresponses import ResponsesMockServer

from powerfox import Powerfox
from powerfox.exceptions import (
    PowerfoxAuthenticationError,
    PowerfoxError,
    PowerfoxNoDataError,
    PowerfoxPrivacyError,
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


async def test_embedded_invalid_json_payload(
    aresponses: ResponsesMockServer,
    powerfox_client: Powerfox,
) -> None:
    """Test that an unparsable embedded payload is silently ignored."""
    aresponses.add(
        "backend.powerfox.energy",
        "/api/2.0/test",
        "GET",
        aresponses.Response(
            text='{"StatusCode": }',
            headers={"Content-Type": "application/json"},
        ),
    )
    # Malformed JSON -> decode raises ValueError -> guard returns, raw text returned
    result = await powerfox_client._request("test")
    assert '"StatusCode"' in result


async def test_embedded_low_status_code_payload(
    aresponses: ResponsesMockServer,
    powerfox_client: Powerfox,
) -> None:
    """Test that an embedded StatusCode below 400 is silently ignored."""
    aresponses.add(
        "backend.powerfox.energy",
        "/api/2.0/test",
        "GET",
        aresponses.Response(
            text='{"StatusCode": 200}',
            headers={"Content-Type": "application/json"},
        ),
    )
    # StatusCode < 400 -> guard returns, raw text returned
    result = await powerfox_client._request("test")
    assert result == '{"StatusCode": 200}'


async def test_embedded_generic_error_payload(
    aresponses: ResponsesMockServer,
    powerfox_client: Powerfox,
) -> None:
    """Test that an unknown embedded error status code raises PowerfoxError."""
    aresponses.add(
        "backend.powerfox.energy",
        "/api/2.0/my/test/current",
        "GET",
        aresponses.Response(
            text='{"StatusCode": 500, "ReasonPhrase": "Internal Server Error"}',
            headers={"Content-Type": "application/json"},
        ),
    )
    with pytest.raises(PowerfoxError):
        await powerfox_client.device("test")


async def test_embedded_precondition_failed_payload(
    aresponses: ResponsesMockServer,
    powerfox_client: Powerfox,
) -> None:
    """Test embedded API 412 in a HTTP 200 response is handled correctly."""
    aresponses.add(
        "backend.powerfox.energy",
        "/api/2.0/my/test/current",
        "GET",
        aresponses.Response(
            text=(
                '{"Version":"1.1","Content":{"Headers":[{"Key":"Content-Type",'
                '"Value":["text/plain; charset=utf-8"]}]},"StatusCode":412,'
                '"ReasonPhrase":"Precondition Failed","Headers":[],'
                '"TrailingHeaders":[]}'
            ),
            headers={"Content-Type": "application/json"},
        ),
    )
    with pytest.raises(PowerfoxPrivacyError):
        await powerfox_client.device("test")


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
