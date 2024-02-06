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
[![Maintainability][maintainability-shield]][maintainability-url]
[![Code Coverage][codecov-shield]][codecov-url]


Asynchronous Python client for [Powerfox][poweropti] devices (poweropti's).

## About

A python package with which you can read the data from a [poweropti][poweropti]
device. [Powerfox][powerfox] has various poweropti devices on the market that you
can use with a power, heater and water meter.

## Installation

```bash
pip install powerfox
```

## Datasets

- List of all your Poweropti devices linked to your account.
- Get information from a specific Poweropti device.

<details>
  <summary>CLICK HERE! to see all datasets</summary>

### All Devices

| Name | Type | Description |
| :--- | :--- | :---------- |
| `device_id` | Str | The unique identifier of the device. |
| `name` | Str | The name of the device. |
| `date_added` | Datetime | The date the device was added to your account. |
| `main_device` | Bool | If the device is the main device. |
| `bidirectional` | Bool | If the device is bidirectional. |
| `division` | Int | The division number of the device. |

### Poweropti for Power meters

| Name | Type | Description |
| :--- | :--- | :---------- |
| `outdated` | Bool | If the data from the device is outdated. |
| `timestamp` | Datetime | The timestamp of the data. |
| `power` | Int | The amount of power used in W. |
| `energy_usage` | Float | The amount of energy used (from the grid) in kWh. |
| `energy_return` | Float | The amount of energy returned (to the grid) in kWh. |
| `energy_usage_high_tariff` | Float | The amount of energy used in kWh during high tariff. |
| `energy_usage_low_tariff` | Float | The amount of energy used in kWh during low tariff. |

### Poweropti for Water meters

| Name | Type | Description |
| :--- | :--- | :---------- |
| `outdated` | Bool | If the data from the device is outdated. |
| `timestamp` | Datetime | The timestamp of the data. |
| `cold_water` | Float | The amount of cold water used in m³. |
| `warm_water` | Float | The amount of warm water used in m³. |
</details>

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

- Python 3.11+
- [Poetry][poetry-install]

Install all packages, including all development requirements:

```bash
poetry install
```

Poetry creates by default an virtual environment where it installs all
necessary pip packages, to enter or exit the venv run the following commands:

```bash
poetry shell
exit
```

Setup the pre-commit check, you must run this inside the virtual environment:

```bash
pre-commit install
```

*Now you're all set to get started!*

As this repository uses the [pre-commit][pre-commit] framework, all changes
are linted and tested with each commit. You can run all checks and tests
manually, using the following command:

```bash
poetry run pre-commit run --all-files
```

To run just the Python tests:

```bash
poetry run pytest
```

To update the syrupy snapshot tests:

```bash
poetry run pytest --snapshot-update
```

## License

MIT License

Copyright (c) 2024 Klaas Schoute

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
[maintainability-shield]: https://api.codeclimate.com/v1/badges/a036b3dc5a9656137de2/maintainability
[maintainability-url]: https://codeclimate.com/github/klaasnicolaas/python-powerfox/maintainability
[maintenance-shield]: https://img.shields.io/maintenance/yes/2024.svg
[project-stage-shield]: https://img.shields.io/badge/project%20stage-experimental-yellow.svg
[pypi]: https://pypi.org/project/powerfox/
[python-versions-shield]: https://img.shields.io/pypi/pyversions/powerfox
[releases-shield]: https://img.shields.io/github/release/klaasnicolaas/python-powerfox.svg
[releases]: https://github.com/klaasnicolaas/python-powerfox/releases
[typing-shield]: https://github.com/klaasnicolaas/python-powerfox/actions/workflows/typing.yaml/badge.svg
[typing-url]: https://github.com/klaasnicolaas/python-powerfox/actions/workflows/typing.yaml

[poetry-install]: https://python-poetry.org/docs/#installation
[poetry]: https://python-poetry.org
[pre-commit]: https://pre-commit.com
