"""Test the models for Powerfox."""

from aresponses import ResponsesMockServer
from syrupy.assertion import SnapshotAssertion

from powerfox import Device, DeviceType, Powerfox, PowerMeter, Poweropti, WaterMeter

from . import load_fixtures


async def test_all_devices_data(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    powerfox_client: Powerfox,
) -> None:
    """Test devices data function."""
    aresponses.add(
        "backend.powerfox.energy",
        "/api/2.0/my/all/devices",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("all_devices.json"),
        ),
    )
    devices: list[Device] = await powerfox_client.all_devices()
    assert devices == snapshot

    # Validate the human-readable property for each device
    for device in devices:
        assert isinstance(device.type, DeviceType)
        assert device.type.human_readable


async def test_power_meter_full_data(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    powerfox_client: Powerfox,
) -> None:
    """Test power meter full data function."""
    aresponses.add(
        "backend.powerfox.energy",
        "/api/2.0/my/power_device_id/current",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("power_meter_full.json"),
        ),
    )
    power_meter: Poweropti = await powerfox_client.device("power_device_id")
    assert power_meter == snapshot
    assert isinstance(power_meter, PowerMeter)


async def test_power_meter_data(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    powerfox_client: Powerfox,
) -> None:
    """Test power meter data function."""
    aresponses.add(
        "backend.powerfox.energy",
        "/api/2.0/my/power_device_id/current",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("power_meter.json"),
        ),
    )
    power_meter: Poweropti = await powerfox_client.device("power_device_id")
    assert power_meter == snapshot
    assert isinstance(power_meter, PowerMeter)
    assert power_meter.energy_usage_low_tariff is None
    assert power_meter.energy_usage_high_tariff is None


async def test_water_meter_data(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    powerfox_client: Powerfox,
) -> None:
    """Test water meter data function."""
    aresponses.add(
        "backend.powerfox.energy",
        "/api/2.0/my/water_meter_id/current",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("water_meter.json"),
        ),
    )
    water_meter: Poweropti = await powerfox_client.device("water_meter_id")
    assert water_meter == snapshot
    assert isinstance(water_meter, WaterMeter)
