"""Asynchronous Python client for the Powerfox local interface."""

import asyncio

from powerfox import PowerfoxLocal


async def main() -> None:
    """Show example on getting data from a local poweropti."""
    async with PowerfoxLocal(
        host="IP_ADDRESS",
        api_key="DEVICE_ID",
    ) as client:
        value = await client.value()
        print(value)


if __name__ == "__main__":
    asyncio.run(main())
