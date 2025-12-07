"""Example for the Powerfox report endpoint."""

import asyncio

from powerfox import Powerfox


async def main() -> None:
    """Show example on getting report data."""
    async with Powerfox(username="EMAIL_ADDRESS", password="PASSWORD") as client:
        report = await client.report(device_id="DEVICE_ID")
        print(report)

        # Example with date filters (year/month/day)
        report_filtered = await client.report(
            device_id="DEVICE_ID",
            year=2024,
            month=12,
            day=6,
        )
        print(report_filtered)


if __name__ == "__main__":
    asyncio.run(main())
