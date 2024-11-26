"""Asynchronous Python client for Powerfox."""

import asyncio

from powerfox import Powerfox


async def main() -> None:
    """Show example on getting Powerfox data."""
    async with Powerfox(username="EMAIL_ADDRESS", password="PASSWORD") as client:
        devices = await client.all_devices()
        print(devices)

        # How to show humand readable device type
        for device in devices:
            print(device.type.human_readable)


if __name__ == "__main__":
    asyncio.run(main())
