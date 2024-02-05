"""Asynchronous Python client for Powerfox."""

import asyncio
import socket
from dataclasses import dataclass
from importlib import metadata
from typing import Any, Self

from aiohttp import BasicAuth, ClientError, ClientResponseError, ClientSession
from aiohttp.hdrs import METH_GET
from mashumaro.codecs.orjson import ORJSONDecoder
from yarl import URL

from .exceptions import (
    PowerfoxAuthenticationError,
    PowerfoxConnectionError,
    PowerfoxError,
)
from .models import Device


@dataclass
class Powerfox:
    """Main class for handling connections with the Powerfox API."""

    username: str
    password: str

    request_timeout: float = 10.0
    session: ClientSession | None = None

    _close_session: bool = False

    async def _request(
        self,
        uri: str,
        *,
        method: str = METH_GET,
        params: dict[str, Any] | None = None,
    ) -> str:
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
        version = metadata.version(__package__)
        url = URL.build(
            scheme="https",
            host="backend.powerfox.energy",
            path="/api/2.0/",
        ).join(URL(uri))

        headers = {
            "Accept": "application/json",
            "User-Agent": f"Python Powerfox/{version}",
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

    async def devices(self) -> list[Device]:
        """Get list of all Poweropti devices.

        Returns
        -------
            A list of all Poweropti devices.

        """
        response = await self._request("my/all/devices")
        return ORJSONDecoder(list[Device]).decode(response)

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
