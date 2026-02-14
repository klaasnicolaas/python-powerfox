"""Fixtures for the Powerfox tests."""

from collections.abc import AsyncGenerator

import pytest
from aiohttp import ClientSession

from powerfox import Powerfox, PowerfoxLocal


@pytest.fixture(name="powerfox_client")
async def client() -> AsyncGenerator[Powerfox, None]:
    """Return a Powerfox client."""
    async with (
        ClientSession() as session,
        Powerfox(username="user", password="pass", session=session) as powerfox_client,
    ):
        yield powerfox_client


@pytest.fixture(name="powerfox_local_client")
async def local_client() -> AsyncGenerator[PowerfoxLocal, None]:
    """Return a PowerfoxLocal client."""
    async with (
        ClientSession() as session,
        PowerfoxLocal(
            host="192.168.1.50",
            api_key="1097bd725557",
            session=session,
        ) as powerfox_local_client,
    ):
        yield powerfox_local_client
