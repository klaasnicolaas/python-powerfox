"""Asynchronous Python client for Powerfox."""

from __future__ import annotations

import asyncio
import socket
from dataclasses import dataclass
from importlib import metadata
from typing import Annotated, Any, Self

from aiohttp import BasicAuth, ClientError, ClientResponseError, ClientSession
from aiohttp.hdrs import METH_GET
from mashumaro.codecs.orjson import ORJSONDecoder
from mashumaro.exceptions import SuitableVariantNotFoundError
from mashumaro.types import Discriminator
from yarl import URL

from .exceptions import (
    PowerfoxAuthenticationError,
    PowerfoxConnectionError,
    PowerfoxError,
    PowerfoxNoDataError,
    PowerfoxUnsupportedDeviceError,
)
from .models import Device, Poweropti

VERSION = metadata.version(__package__)


@dataclass
class Powerfox:
    """Main class for handling connections with the Powerfox API."""

    username: str
    password: str

    request_timeout: float = 30.0
    session: ClientSession | None = None

    _close_session: bool = False

    async def _request(
        self,
        uri: str,
        *,
        method: str = METH_GET,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Handle a request to the Powerfox API.

        Args:
        ----
            uri: Request URI, without '/api/', for example, 'status'.
            method: HTTP method to use.
            params: Extra options to improve or limit the response.

        Returns:
        -------
            A Python dictionary (JSON decoded) with the response from
            the Powerfox API.

        Raises:
        ------
            PowerfoxConnectionError: An error occurred while communicating
                with the Powerfox API.
            PowerfoxError: Received an unexpected response from the Powerfox API.

        """
        url = URL.build(
            scheme="https",
            host="backend.powerfox.energy",
            path="/api/2.0/",
        ).join(URL(uri))

        headers = {
            "Accept": "application/json",
            "User-Agent": f"PythonPowerfox/{VERSION}",
        }

        if self.session is None:
            self.session = ClientSession()
            self._close_session = True

        # Set basic auth credentials.
        auth = BasicAuth(self.username, self.password)

        try:
            async with asyncio.timeout(self.request_timeout):
                response = await self.session.request(
                    method,
                    url,
                    auth=auth,
                    headers=headers,
                    params=params,
                    ssl=True,
                )
                response.raise_for_status()
        except TimeoutError as exception:
            msg = "Timeout occurred while connecting to Powerfox API."
            raise PowerfoxConnectionError(msg) from exception
        except ClientResponseError as exception:
            if exception.status == 401:
                msg = "Authentication to the Powerfox API failed."
                raise PowerfoxAuthenticationError(msg) from exception
            msg = "Error occurred while communicating with Powerfox API."
            raise PowerfoxConnectionError(msg) from exception
        except (ClientError, socket.gaierror) as exception:
            msg = "Error occurred while communicating with Powerfox API."
            raise PowerfoxConnectionError(msg) from exception

        content_type = response.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            text = await response.text()
            msg = "Unexpected content type response from Powerfox API."
            raise PowerfoxError(
                msg,
                {"Content-Type": content_type, "Response": text},
            )

        return await response.text()

    async def all_devices(self) -> list[Device]:
        """Get list of all Poweropti devices.

        Returns
        -------
            A list of all Poweropti devices.

        Raises
        ------
            PowerfoxNoDataError: If no devices are found or the response is empty.

        """
        response = await self._request("my/all/devices")
        if response == "[]":
            msg = "No Poweropti devices found."
            raise PowerfoxNoDataError(msg)
        return ORJSONDecoder(list[Device]).decode(response)

    async def device(self, device_id: str) -> Poweropti:
        """Get information about a specific Poweropti device.

        Args:
        ----
            device_id: The device ID to get information about.

        Returns:
        -------
            Information about the Poweropti device.

        Raises:
        ------
            PowerfoxNoDataError: If the response is empty or invalid JSON.

        """
        response = await self._request(
            f"my/{device_id}/current",
            params={"unit": "kwh"},
        )
        if response == "{}":
            msg = f"No data available for Poweropti device {device_id}."
            raise PowerfoxNoDataError(msg)

        try:
            return ORJSONDecoder(
                Annotated[Poweropti, Discriminator(include_subtypes=True)]
            ).decode(response)
        except SuitableVariantNotFoundError as err:
            data = ORJSONDecoder(dict).decode(response)
            division = data.get("Division", "unknown")
            msg = (
                "Unsupported device type received "
                f"(Division={division}) for device {device_id}."
            )
            raise PowerfoxUnsupportedDeviceError(msg) from err

    async def raw_device_data(self, device_id: str) -> dict[str, Any]:
        """Get raw JSON data for a specific Poweropti device.

        Args:
        ----
            device_id: The device ID to get information about.

        Returns:
        -------
            The raw response data as a dictionary.

        Raises:
        ------
            PowerfoxNoDataError: If the response is empty or invalid JSON.

        """
        response = await self._request(
            f"my/{device_id}/current",
            params={"unit": "kwh"},
        )

        data = ORJSONDecoder(dict).decode(response)
        if not data:
            msg = f"No data available for Poweropti device {device_id}."
            raise PowerfoxNoDataError(msg)
        return data

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> Self:
        """Async enter.

        Returns
        -------
            The Powerfox object.

        """
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        """Async exit.

        Args:
        ----
            _exc_info: Exec type.

        """
        await self.close()
