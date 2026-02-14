"""Asynchronous Python client for the Powerfox local interface."""

from __future__ import annotations

import asyncio
import socket
from dataclasses import dataclass
from importlib import metadata
from typing import Any, Self

from aiohttp import ClientError, ClientResponseError, ClientSession
from aiohttp.hdrs import METH_GET
from mashumaro.codecs.orjson import ORJSONDecoder
from yarl import URL

from .exceptions import (
    PowerfoxAuthenticationError,
    PowerfoxConnectionError,
    PowerfoxError,
)
from .models import LocalResponse

VERSION: str = metadata.version(__package__)  # ty:ignore[invalid-argument-type]


@dataclass
class PowerfoxLocal:
    """Client for the local poweropti REST API.

    Connects to a poweropti device on the local network via HTTP.
    Requires the powerfox PRO Service and firmware v2.02.07 or higher.
    """

    host: str
    api_key: str

    request_timeout: float = 10.0
    session: ClientSession | None = None

    _close_session: bool = False

    async def _request(
        self,
        uri: str,
        *,
        method: str = METH_GET,
    ) -> Any:
        """Handle a request to the local poweropti API.

        Args:
        ----
            uri: Request URI, for example, 'value'.
            method: HTTP method to use.

        Returns:
        -------
            The response text from the local poweropti API.

        Raises:
        ------
            PowerfoxConnectionError: An error occurred while communicating
                with the local poweropti API.
            PowerfoxAuthenticationError: Invalid or missing API key.
            PowerfoxError: Received an unexpected response from the API.

        """
        url = URL.build(
            scheme="http",
            host=self.host,
        ).join(URL(uri))

        headers = {
            "Accept": "application/json",
            "User-Agent": f"PythonPowerfox/{VERSION}",
            "X-API-KEY": self.api_key,
        }

        if self.session is None:
            self.session = ClientSession()
            self._close_session = True

        try:
            async with asyncio.timeout(self.request_timeout):
                response = await self.session.request(
                    method,
                    url,
                    headers=headers,
                )
                response.raise_for_status()
        except TimeoutError as exception:
            msg = "Timeout occurred while connecting to local poweropti."
            raise PowerfoxConnectionError(msg) from exception
        except ClientResponseError as exception:
            if exception.status == 401:
                msg = "Authentication to local poweropti failed."
                raise PowerfoxAuthenticationError(msg) from exception
            msg = "Error occurred while communicating with local poweropti."
            raise PowerfoxConnectionError(msg) from exception
        except (ClientError, socket.gaierror) as exception:
            msg = "Error occurred while communicating with local poweropti."
            raise PowerfoxConnectionError(msg) from exception

        content_type = response.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            text = await response.text()
            msg = "Unexpected content type response from local poweropti."
            raise PowerfoxError(
                msg,
                {"Content-Type": content_type, "Response": text},
            )

        return await response.text()

    async def value(self) -> LocalResponse:
        """Get current measurement data from the local poweropti.

        Returns
        -------
            The current measurement data.

        """
        response = await self._request("value")
        return ORJSONDecoder(LocalResponse).decode(response)

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> Self:
        """Async enter.

        Returns
        -------
            The PowerfoxLocal object.

        """
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        """Async exit.

        Args:
        ----
            _exc_info: Exec type.

        """
        await self.close()
