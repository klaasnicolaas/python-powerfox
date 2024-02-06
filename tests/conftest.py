"""Fixtures for the Powerfox tests."""
from collections.abc import AsyncGenerator

import pytest
from aiohttp import ClientSession

from powerfox import Powerfox


@pytest.fixture(name="powerfox_client")
async def client() -> AsyncGenerator[Powerfox, None]:
    """Return a Powerfox client."""
    async with ClientSession() as session, Powerfox(
        username="user", password="pass", session=session
    ) as powerfox_client:
        yield powerfox_client
