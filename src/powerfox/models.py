"""Asynchronous Python client for Powerfox."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from mashumaro import field_options
from mashumaro.mixins.orjson import DataClassORJSONMixin


@dataclass
class Device(DataClassORJSONMixin):
    """Object representing a Device from Powerfox."""

    device_id: str = field(metadata=field_options(alias="DeviceId"))
    date_added: datetime = field(
        metadata=field_options(
            alias="AccountAssociatedSince",
            deserialize=lambda x: datetime.fromtimestamp(x, tz=UTC),
        )
    )
    main_device: bool = field(metadata=field_options(alias="MainDevice"))
    bidirectional: bool = field(metadata=field_options(alias="Prosumer"))
    division: int = field(metadata=field_options(alias="Division"))
    name: str | None = field(metadata=field_options(alias="Name"), default=None)


@dataclass
class Poweropti(DataClassORJSONMixin):
    """Object representing a Poweropti device."""

    outdated: bool = field(metadata=field_options(alias="Outdated"))
    timestamp: datetime = field(
        metadata=field_options(
            alias="Timestamp",
            deserialize=lambda x: datetime.fromtimestamp(x, tz=UTC),
        )
    )


@dataclass
class PowerMeter(Poweropti):
    """Object representing a Power device."""

    power: int = field(metadata=field_options(alias="Watt"))
    energy_usage: float = field(metadata=field_options(alias="A_Plus"))
    energy_return: float = field(metadata=field_options(alias="A_Minus"))
    energy_usage_high_tariff: float | None = field(
        metadata=field_options(alias="A_Plus_HT"), default=None
    )
    energy_usage_low_tariff: float | None = field(
        metadata=field_options(alias="A_Plus_NT"), default=None
    )


# @dataclass
# class HeatMeter(Poweropti):
#     """Object representing a Heat device."""


@dataclass
class WaterMeter(Poweropti):
    """Object representing a Water device."""

    cold_water: float = field(metadata=field_options(alias="CubicMeterCold"))
    warm_water: float = field(metadata=field_options(alias="CubicMeterWarm"))
