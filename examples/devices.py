"""Asynchronous Python client for Powerfox."""
# ruff: noqa: S106
import asyncio

from powerfox import Powerfox


async def main() -> None:
    """Show example on getting Powerfox data."""
    async with Powerfox(username="EMAIL_ADDRESS", password="PASSWORD") as client:
        devices = await client.devices()
        print(devices)


if __name__ == "__main__":
    asyncio.run(main())
