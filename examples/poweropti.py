"""Asynchronous Python client for Powerfox."""
import asyncio

from powerfox import Powerfox


async def main() -> None:
    """Show example on getting Powerfox data."""
    async with Powerfox(username="EMAIL_ADDRESS", password="PASSWORD") as client:
        poweropti = await client.device(device_id="DEVICE_ID")
        print(poweropti)


if __name__ == "__main__":
    asyncio.run(main())
