"""Asynchronous Python client for Powerfox."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from mashumaro import field_options
from mashumaro.mixins.orjson import DataClassORJSONMixin


def _deserialize_timestamp(value: int | None) -> datetime | None:
    """Convert a timestamp to a datetime object."""
    if value is None:
        return None
    try:
        return datetime.fromtimestamp(value, tz=UTC)
    except (OverflowError, OSError, ValueError):
        return None


class DeviceType(int, Enum):
    """Enum for the different device types."""

    NO_TYPE = -1
    POWER_METER = 0
    COLD_WATER_METER = 1
    HOT_WATER_METER = 2
    HEAT_METER = 3
    GAS_METER = 4
    COLD_HOT_WATER_METER = 5

    @property
    def human_readable(self) -> str:
        """Return a human readable string for the device type."""
        return {
            DeviceType.POWER_METER: "Power Meter",
            DeviceType.COLD_WATER_METER: "Cold Water Meter",
            DeviceType.HOT_WATER_METER: "Hot Water Meter",
            DeviceType.HEAT_METER: "Heat Meter",
            DeviceType.GAS_METER: "Gas Meter",
            DeviceType.COLD_HOT_WATER_METER: "Cold/Hot Water Meter",
        }.get(self, "Unknown")


@dataclass
class Device(DataClassORJSONMixin):
    """Object representing a Device from Powerfox."""

    id: str = field(metadata=field_options(alias="DeviceId"))
    date_added: datetime = field(
        metadata=field_options(
            alias="AccountAssociatedSince",
            deserialize=lambda x: datetime.fromtimestamp(x, tz=UTC),
        )
    )
    main_device: bool = field(metadata=field_options(alias="MainDevice"))
    bidirectional: bool = field(metadata=field_options(alias="Prosumer"))
    type: DeviceType = field(metadata=field_options(alias="Division"))
    name: str = field(metadata=field_options(alias="Name"), default="Poweropti")


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
    energy_usage: float | None = field(
        metadata=field_options(
            alias="A_Plus",
            deserialize=lambda x: x if x != 0 else None,
        ),
    )
    energy_return: float | None = field(
        metadata=field_options(
            alias="A_Minus",
            deserialize=lambda x: x if x != 0 else None,
        ),
    )
    energy_usage_high_tariff: float | None = field(
        metadata=field_options(alias="A_Plus_HT"), default=None
    )
    energy_usage_low_tariff: float | None = field(
        metadata=field_options(alias="A_Plus_NT"), default=None
    )


@dataclass
class HeatMeter(Poweropti):
    """Object representing a Heat device."""

    total_energy: int = field(metadata=field_options(alias="KiloWattHour"))
    delta_energy: int = field(metadata=field_options(alias="DeltaKiloWattHour"))
    total_volume: float = field(metadata=field_options(alias="CubicMeter"))
    delta_volume: float = field(metadata=field_options(alias="DeltaCubicMeter"))


@dataclass
class WaterMeter(Poweropti):
    """Object representing a Water device."""

    cold_water: float = field(metadata=field_options(alias="CubicMeterCold"))
    warm_water: float = field(metadata=field_options(alias="CubicMeterWarm"))


@dataclass
class ReportValue(DataClassORJSONMixin):
    """Object representing a report value entry."""

    device_id: str = field(metadata=field_options(alias="DeviceId"))
    timestamp: datetime = field(
        metadata=field_options(
            alias="Timestamp",
            deserialize=lambda x: datetime.fromtimestamp(x, tz=UTC),
        )
    )
    complete: bool = field(metadata=field_options(alias="Complete"))
    values_type: int | None = field(
        metadata=field_options(alias="ValuesType"),
        default=None,
    )
    delta: float | None = field(
        metadata=field_options(alias="Delta"),
        default=None,
    )
    delta_ht: float | None = field(
        metadata=field_options(alias="DeltaHT"),
        default=None,
    )
    delta_nt: float | None = field(
        metadata=field_options(alias="DeltaNT"),
        default=None,
    )
    delta_currency: float | None = field(
        metadata=field_options(alias="DeltaCurrency"),
        default=None,
    )
    total_delta: float | None = field(
        metadata=field_options(alias="TotalDelta"),
        default=None,
    )
    total_delta_currency: float | None = field(
        metadata=field_options(alias="TotalDeltaCurrency"),
        default=None,
    )
    consumption: float | None = field(
        metadata=field_options(alias="Consumption"),
        default=None,
    )
    consumption_kwh: float | None = field(
        metadata=field_options(alias="ConsumptionKWh"),
        default=None,
    )
    current_consumption: float | None = field(
        metadata=field_options(alias="CurrentConsumption"),
        default=None,
    )
    current_consumption_kwh: float | None = field(
        metadata=field_options(alias="CurrentConsumptionKwh"),
        default=None,
    )


@dataclass
class GasReport(DataClassORJSONMixin):
    """Object representing a gas report."""

    total_delta: float = field(metadata=field_options(alias="TotalDelta"))
    sum: float = field(metadata=field_options(alias="Sum"))
    total_delta_currency: float | None = field(
        metadata=field_options(alias="TotalDeltaCurrency"),
        default=None,
    )
    current_consumption_kwh: float | None = field(
        metadata=field_options(alias="CurrentConsumptionKwh"),
        default=None,
    )
    current_consumption: float | None = field(
        metadata=field_options(alias="CurrentConsumption"),
        default=None,
    )
    consumption_kwh: float | None = field(
        metadata=field_options(alias="ConsumptionKWh"),
        default=None,
    )
    consumption: float | None = field(
        metadata=field_options(alias="Consumption"),
        default=None,
    )
    max: float | None = field(
        metadata=field_options(alias="Max"),
        default=None,
    )
    max_currency: float | None = field(
        metadata=field_options(alias="MaxCurrency"),
        default=None,
    )
    max_consumption: float | None = field(
        metadata=field_options(alias="MaxConsumption"),
        default=None,
    )
    max_consumption_kwh: float | None = field(
        metadata=field_options(alias="MaxConsumptionKWh"),
        default=None,
    )
    min: float | None = field(
        metadata=field_options(alias="Min"),
        default=None,
    )
    min_consumption: float | None = field(
        metadata=field_options(alias="MinConsumption"),
        default=None,
    )
    min_consumption_kwh: float | None = field(
        metadata=field_options(alias="MinConsumptionKWh"),
        default=None,
    )
    avg_delta: float | None = field(
        metadata=field_options(alias="AvgDelta"),
        default=None,
    )
    avg_consumption: float | None = field(
        metadata=field_options(alias="AvgConsumption"),
        default=None,
    )
    avg_consumption_kwh: float | None = field(
        metadata=field_options(alias="AvgConsumptionKWh"),
        default=None,
    )
    meter_readings: list[dict[str, Any]] = field(
        default_factory=list,
        metadata=field_options(alias="MeterReadings"),
    )
    report_values: list[ReportValue] = field(
        default_factory=list,
        metadata=field_options(alias="ReportValues"),
    )
    sum_currency: float | None = field(
        metadata=field_options(alias="SumCurrency"),
        default=None,
    )


@dataclass
class EnergyReport(DataClassORJSONMixin):
    """Object representing an energy report section."""

    start_time: datetime | None = field(
        metadata=field_options(
            alias="StartTime",
            deserialize=_deserialize_timestamp,
        ),
        default=None,
    )
    start_time_currency: datetime | None = field(
        metadata=field_options(
            alias="StartTimeCurrency",
            deserialize=_deserialize_timestamp,
        ),
        default=None,
    )
    sum: float | None = field(
        metadata=field_options(alias="Sum"),
        default=None,
    )
    max: float | None = field(
        metadata=field_options(alias="Max"),
        default=None,
    )
    max_currency: float | None = field(
        metadata=field_options(alias="MaxCurrency"),
        default=None,
    )
    meter_readings: list[dict[str, Any]] = field(
        default_factory=list,
        metadata=field_options(alias="MeterReadings"),
    )
    report_values: list[ReportValue] = field(
        default_factory=list,
        metadata=field_options(alias="ReportValues"),
    )
    sum_currency: float | None = field(
        metadata=field_options(alias="SumCurrency"),
        default=None,
    )


@dataclass
class DeviceReport(DataClassORJSONMixin):
    """Object representing a report response."""

    gas: GasReport | None = field(
        default=None,
        metadata=field_options(alias="Gas"),
    )
    consumption: EnergyReport | None = field(
        default=None,
        metadata=field_options(alias="Consumption"),
    )
    feed_in: EnergyReport | None = field(
        default=None,
        metadata=field_options(alias="FeedIn"),
    )
