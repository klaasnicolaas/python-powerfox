"""Asynchronous Python client for Powerfox."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Device:
    """Object representing an Device from Powerfox."""

    device_id: str
    name: str | None
    date_added: datetime
    main_device: bool
    bidirectional: bool
    division: int

    @staticmethod
    def from_json(data: dict[str | int, Any]) -> Device:
        """Return Device object from the Powerfox API response.

        Args:
        ----
            data: The data from the Powerfox API.

        Returns:
        -------
            A Device object.

        """
        return Device(
            device_id=data["DeviceId"],
            name=data.get("Name"),
            date_added=data["AccountAssociatedSince"],
            main_device=data["MainDevice"],
            bidirectional=data["Prosumer"],
            division=data["Division"],
        )


# class Power

# class Heat

# class Water
