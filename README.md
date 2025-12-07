<!-- Banner -->
![alt Banner of the Powerfox package](https://raw.githubusercontent.com/klaasnicolaas/python-powerfox/main/assets/header_powerfox-min.png)

<!-- PROJECT SHIELDS -->
[![GitHub Release][releases-shield]][releases]
[![Python Versions][python-versions-shield]][pypi]
![Project Stage][project-stage-shield]
![Project Maintenance][maintenance-shield]
[![License][license-shield]](LICENSE)

[![GitHub Activity][commits-shield]][commits-url]
[![PyPi Downloads][downloads-shield]][downloads-url]
[![GitHub Last Commit][last-commit-shield]][commits-url]
[![Open in Dev Containers][devcontainer-shield]][devcontainer]

[![Build Status][build-shield]][build-url]
[![Typing Status][typing-shield]][typing-url]
[![Code Coverage][codecov-shield]][codecov-url]


Asynchronous Python client for [Powerfox][poweropti] devices (poweropti's).

## About

A python package with which you can read the data from a [poweropti][poweropti]
device, via your Powerfox account (cloud polling). [Powerfox][powerfox] has various
poweropti devices on the market that you can use with a power, heat and water meter.

## Installation

```bash
pip install powerfox
```

## Poweropti devices

Not all Poweropti devices are supported currently. Check the list below to see if your
device is working with this package. Or help us by testing a device and let us know if
it works.

| Device                | Type        | Supported  |
| --------------------- | ----------- | ---------- |
| PA 201901 / PA 201902 | Power meter | Yes        |
| PB 202001             | Power meter | Yes        |
| WA 201902             | Water meter | Yes        |
| Powerfox FLOW         | Gas meter   | Yes (report) |
| HA 201902             | Heat meter  | Yes        |

## Datasets

- `Powerfox.all_devices()` lists all devices linked to your account.
- `Powerfox.device(...)` gives the realtime snapshot for a Poweropti device.
- `Powerfox.report(...)` exposes hourly/daily blocks such as FLOW gas consumption.

### Device inventory (`all_devices`)

Use `Powerfox.all_devices()` to fetch the list of Poweropti devices linked to your
account. This endpoint is independent from the realtime `/current` data.

| Field           | Type         | Description                                    |
| :-------------- | :----------- | :--------------------------------------------- |
| `device_id`     | `str`        | Unique identifier of the device.               |
| `name`          | `str`        | Friendly name configured in the app.           |
| `date_added`    | `datetime`   | When the device was linked to your account.    |
| `main_device`   | `bool`       | Whether this is the main device in the portal. |
| `bidirectional` | `bool`       | True for prosumer/power meters with feed-in.   |
| `type`          | `DeviceType` | Division value (`device.type.human_readable`). |

### Realtime device data (`device`)

This route powers all non-FLOW devices. The Powerfox FLOW gas meter does not expose a
`/current` payload, so use the report dataset described below.

<details>
  <summary>Realtime dataset details (click to expand)</summary>

#### Power meter snapshot

| Field                      | Type       | Unit | Description                                   |
| :------------------------- | :--------- | :--- | :-------------------------------------------- |
| `outdated`                 | `bool`     | -    | Data freshness indicator from Powerfox.       |
| `timestamp`                | `datetime` | -    | Timestamp of the snapshot.                    |
| `power`                    | `int`      | W    | Instant power draw.                           |
| `energy_usage`             | `float`    | kWh  | Grid import since last reset (`None` if zero). |
| `energy_return`            | `float`    | kWh  | Grid export since last reset (`None` if zero). |
| `energy_usage_high_tariff` | `float`    | kWh  | High tariff import (optional).                |
| `energy_usage_low_tariff`  | `float`    | kWh  | Low tariff import (optional).                 |

#### Water meter snapshot

| Field       | Type       | Unit | Description                |
| :---------- | :--------- | :--- | :------------------------- |
| `outdated`  | `bool`     | -    | Data freshness indicator.  |
| `timestamp` | `datetime` | -    | Timestamp of the snapshot. |
| `cold_water`| `float`    | m³   | Total cold water usage.    |
| `warm_water`| `float`    | m³   | Total warm water usage.    |

#### Heat meter snapshot

| Field         | Type       | Unit | Description                                |
| :------------ | :--------- | :--- | :----------------------------------------- |
| `outdated`    | `bool`     | -    | Data freshness indicator.                  |
| `timestamp`   | `datetime` | -    | Timestamp of the snapshot.                 |
| `total_energy`| `int`      | kWh  | Total consumed energy.                     |
| `delta_energy`| `int`      | kWh  | Consumption delta since previous reading.  |
| `total_volume`| `float`    | m³   | Total volume (heating circuit).            |
| `delta_volume`| `float`    | m³   | Volume delta since previous reading.       |

</details>

### Report data (`report`)

`Powerfox.report(device_id, *, year=None, month=None, day=None)` exposes the
`my/{device_id}/report` endpoint and returns a `DeviceReport` composed of optional
sections. When no filters are provided the last 24 hours are returned. `month` requires
`year`, and `day` requires both `year` and `month`.

<details>
  <summary>Report dataset details (click to expand)</summary>

#### FLOW gas meter (`GasReport`)

| Field                  | Unit           | Description                                                                |
| :--------------------- | :------------- | :------------------------------------------------------------------------- |
| `sum` / `total_delta`  | m³ / impulses  | Total gas consumption for the window.                                      |
| `consumption`          | m³             | Consumption for the period (identical to `sum`).                           |
| `consumption_kwh`      | kWh            | Consumption converted to kWh (requires tariff).                            |
| `current_consumption`  | m³             | Current FLOW reading from the report payload.                              |
| `avg_delta`, `min`, `max` | m³         | Aggregated hourly min/max/average consumption.                             |
| `avg_consumption_kwh` etc. | kWh       | Same aggregates in kWh.                                                    |
| `sum_currency`, `max_currency` | €     | Currency values when a tariff is configured.                               |
| `report_values`        | -              | List of `ReportValue` entries (hourly blocks).                             |

#### Power/Heat/Water history (`EnergyReport`)

| Field        | Unit        | Description                                         |
| :----------- | :---------- | :-------------------------------------------------- |
| `start_time` | `datetime`  | Start of the returned time series.                  |
| `sum`        | kWh / m³    | Total consumption for the requested window.         |
| `max`        | kWh / m³    | Maximum hourly/daily value in the window.           |
| `sum_currency` | €         | Optional total cost (requires tariff).              |
| `report_values` | -        | List of `ReportValue` entries (hourly/daily deltas). |

#### ReportValue entries

Each element in `report_values` represents an hourly (or daily) block.

| Field                 | Unit        | Description                                                  |
| :-------------------- | :---------- | :----------------------------------------------------------- |
| `timestamp`           | `datetime`  | Start time of the block (UTC).                               |
| `delta` / `consumption` | kWh / m³  | Consumption for that block.                                  |
| `delta_ht` / `delta_nt` | kWh       | Tariff specific deltas for power meters.                     |
| `delta_currency`      | €           | Cost for the block (requires tariff).                        |
| `total_delta`         | impulses/m³ | Aggregate impulse count when provided (FLOW).                |
| `current_consumption` | kWh / m³    | Current instantaneous reading if the API includes it.        |
| `values_type`         | int         | Distinguishes consumption (`1`) vs feed-in (`2`).            |

</details>

Use `Powerfox.report(device_id, *, year=None, month=None, day=None)` to retrieve the
hourly or daily datasets from the `my/{device_id}/report` endpoint. This method powers
the Powerfox FLOW gas meter support and can also be used for historic consumption or
feed-in data for other devices. The response is parsed into a `DeviceReport`
dataclass, which may contain:

- `gas`: a `GasReport` section with FLOW totals and hourly consumption.
- `consumption`: consumption data for power meters.
- `feed_in`: feed-in data for bidirectional meters.

The `month` parameter requires `year`, and `day` requires both `year` and `month`. When
no parameters are given the API returns the last 24 hours.

### Example

```python
import asyncio

from powerfox import Powerfox


async def main() -> None:
    """Show example on using this package."""
    async with Powerfox(
        username="EMAIL_ADDRESS",
        password="PASSWORD",
    ) as client:
        devices = await client.all_devices()
        print(devices)


if __name__ == "__main__":
    asyncio.run(main())
```

More examples can be found in the [examples folder](./examples/).

### Class Parameters

| Parameter | value Type | Description |
| :-------- | :--------- | :---------- |
| `username` | `str` | The email address of your Powerfox account. |
| `password` | `str` | The password of your Powerfox account. |

## Contributing

This is an active open-source project. We are always open to people who want to
use the code or contribute to it.

We've set up a separate document for our
[contribution guidelines](CONTRIBUTING.md).

Thank you for being involved! :heart_eyes:

## Setting up development environment

The simplest way to begin is by utilizing the [Dev Container][devcontainer]
feature of Visual Studio Code or by opening a CodeSpace directly on GitHub.
By clicking the button below you immediately start a Dev Container in Visual Studio Code.

[![Open in Dev Containers][devcontainer-shield]][devcontainer]

This Python project relies on [Poetry][poetry] as its dependency manager,
providing comprehensive management and control over project dependencies.

You need at least:

- Python 3.12+
- [Poetry][poetry-install]

### Installation

Install all packages, including all development requirements:

```bash
poetry install
```

_Poetry creates by default an virtual environment where it installs all
necessary pip packages_.

### Prek

This repository uses the [prek][prek] framework, all changes
are linted and tested with each commit. To setup the prek check, run:

```bash
poetry run prek install
```

And to run all checks and tests manually, use the following command:

```bash
poetry run prek run --all-files
```

### Testing

It uses [pytest](https://docs.pytest.org/en/stable/) as the test framework. To run the tests:

```bash
poetry run pytest
```

To update the [syrupy](https://github.com/tophat/syrupy) snapshot tests:

```bash
poetry run pytest --snapshot-update
```

## License

MIT License

Copyright (c) 2025 Klaas Schoute

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


<!-- LINKS FROM PLATFORM -->
[powerfox]: https://www.powerfox.energy
[poweropti]: https://shop.powerfox.energy/collections/frontpage


<!-- MARKDOWN LINKS & IMAGES -->
[build-shield]: https://github.com/klaasnicolaas/python-powerfox/actions/workflows/tests.yaml/badge.svg
[build-url]: https://github.com/klaasnicolaas/python-powerfox/actions/workflows/tests.yaml
[codecov-shield]: https://codecov.io/gh/klaasnicolaas/python-powerfox/branch/main/graph/badge.svg?token=GWI54W3CG9
[codecov-url]: https://codecov.io/gh/klaasnicolaas/python-powerfox
[commits-shield]: https://img.shields.io/github/commit-activity/y/klaasnicolaas/python-powerfox.svg
[commits-url]: https://github.com/klaasnicolaas/python-powerfox/commits/main
[devcontainer-shield]: https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode
[devcontainer]: https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/klaasnicolaas/python-powerfox
[downloads-shield]: https://img.shields.io/pypi/dm/powerfox
[downloads-url]: https://pypistats.org/packages/powerfox
[last-commit-shield]: https://img.shields.io/github/last-commit/klaasnicolaas/python-powerfox.svg
[license-shield]: https://img.shields.io/github/license/klaasnicolaas/python-powerfox.svg
[maintenance-shield]: https://img.shields.io/maintenance/yes/2025.svg
[project-stage-shield]: https://img.shields.io/badge/project%20stage-experimental-yellow.svg
[pypi]: https://pypi.org/project/powerfox/
[python-versions-shield]: https://img.shields.io/pypi/pyversions/powerfox
[releases-shield]: https://img.shields.io/github/release/klaasnicolaas/python-powerfox.svg
[releases]: https://github.com/klaasnicolaas/python-powerfox/releases
[typing-shield]: https://github.com/klaasnicolaas/python-powerfox/actions/workflows/typing.yaml/badge.svg
[typing-url]: https://github.com/klaasnicolaas/python-powerfox/actions/workflows/typing.yaml

[poetry-install]: https://python-poetry.org/docs/#installation
[poetry]: https://python-poetry.org
[prek]: https://github.com/j178/prek
