"""Asynchronous Python client for Powerfox."""


class PowerfoxError(Exception):
    """Generic Powerfox exception."""


class PowerfoxConnectionError(PowerfoxError):
    """Powerfox connection exception."""


class PowerfoxAuthenticationError(PowerfoxError):
    """Powerfox authentication exception."""
