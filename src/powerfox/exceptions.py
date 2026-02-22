"""Asynchronous Python client for Powerfox."""


class PowerfoxError(Exception):
    """Generic Powerfox exception."""


class PowerfoxConnectionError(PowerfoxError):
    """Powerfox connection exception."""


class PowerfoxAuthenticationError(PowerfoxError):
    """Powerfox authentication exception."""


class PowerfoxNoDataError(PowerfoxError):
    """Powerfox no data exception."""


class PowerfoxPrivacyError(PowerfoxError):
    """Powerfox privacy exception.

    Raised when the customer has denied data transmission (HTTP 412).
    """


class PowerfoxUnsupportedDeviceError(PowerfoxError):
    """Powerfox unsupported device exception."""
