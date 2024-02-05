"""Test the models for Powerfox."""
# ruff: noqa: S106
from aiohttp import ClientSession
from aresponses import ResponsesMockServer
from syrupy.assertion import SnapshotAssertion

from powerfox import Device, Powerfox

from . import load_fixtures


async def test_all_devices_data(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
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
    async with ClientSession() as session:
        client = Powerfox(username="user", password="pass", session=session)
        devices: list[Device] = await client.all_devices()
        assert devices == snapshot
