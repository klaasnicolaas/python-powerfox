"""Asynchronous Python client for Powerfox."""

import asyncio

from powerfox import Powerfox


async def main() -> None:
    """Show example on getting RAW Powerfox response data."""
    async with Powerfox(username="EMAIL_ADDRESS", password="PASSWORD") as client:
        poweropti = await client.raw_device_data(device_id="DEVICE_ID")
        print(poweropti)


if __name__ == "__main__":
    asyncio.run(main())
