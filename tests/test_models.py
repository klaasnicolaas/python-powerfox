"""Test the models for Powerfox."""

import pytest
from aresponses import ResponsesMockServer
from syrupy.assertion import SnapshotAssertion

from powerfox import (
    Device,
    DeviceReport,
    DeviceType,
    HeatMeter,
    Powerfox,
    PowerMeter,
    Poweropti,
    WaterMeter,
)
from powerfox.models import _deserialize_timestamp

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


async def test_heat_meter_data(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    powerfox_client: Powerfox,
) -> None:
    """Test heat meter data function."""
    aresponses.add(
        "backend.powerfox.energy",
        "/api/2.0/my/heat_meter_id/current",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("heat_meter.json"),
        ),
    )
    heat_meter: Poweropti = await powerfox_client.device("heat_meter_id")
    assert heat_meter == snapshot
    assert isinstance(heat_meter, HeatMeter)


async def test_invalid_power_meter_data(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    powerfox_client: Powerfox,
) -> None:
    """Test invalid power meter data function."""
    aresponses.add(
        "backend.powerfox.energy",
        "/api/2.0/my/power_device_id/current",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("power_meter_invalid.json"),
        ),
    )
    power_meter = await powerfox_client.device("power_device_id")
    assert power_meter == snapshot
    assert isinstance(power_meter, PowerMeter)
    assert power_meter.energy_usage is None
    assert power_meter.energy_return is None


async def test_raw_response_data(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    powerfox_client: Powerfox,
) -> None:
    """Test raw response data function."""
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
    raw_data = await powerfox_client.raw_device_data("power_device_id")
    assert raw_data == snapshot


async def test_gas_report_data(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    powerfox_client: Powerfox,
) -> None:
    """Test gas report data function."""
    aresponses.add(
        "backend.powerfox.energy",
        "/api/2.0/my/flow_device_id/report",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("gas_report.json"),
        ),
    )
    report: DeviceReport = await powerfox_client.report("flow_device_id")
    assert report == snapshot
    assert report.gas
    assert report.gas.report_values


async def test_power_report_data(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    powerfox_client: Powerfox,
) -> None:
    """Test powermeter report data function."""
    aresponses.add(
        "backend.powerfox.energy",
        "/api/2.0/my/power_device_id/report",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("power_report.json"),
        ),
    )
    report: DeviceReport = await powerfox_client.report("power_device_id")
    assert report == snapshot
    assert report.consumption
    assert report.feed_in


async def test_report_with_filters(
    aresponses: ResponsesMockServer,
    powerfox_client: Powerfox,
) -> None:
    """Test report call with date filters."""
    aresponses.add(
        "backend.powerfox.energy",
        "/api/2.0/my/filter_device/report",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("gas_report.json"),
        ),
    )
    report = await powerfox_client.report(
        "filter_device",
        year=2024,
        month=12,
        day=6,
    )
    assert report.gas


async def test_report_month_requires_year(powerfox_client: Powerfox) -> None:
    """Test passing month without year raises ValueError."""
    with pytest.raises(ValueError, match=r"month.*year"):
        await powerfox_client.report("filter_device", month=12)


async def test_report_day_requires_month(powerfox_client: Powerfox) -> None:
    """Test passing day without month/year raises ValueError."""
    with pytest.raises(ValueError, match=r"day.*year.*month"):
        await powerfox_client.report("filter_device", year=2024, day=6)


def test_deserialize_timestamp_none() -> None:
    """Ensure timestamp helper handles None values."""
    assert _deserialize_timestamp(None) is None
