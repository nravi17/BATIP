"""
BATIP custom exceptions.
"""


class BATIPError(Exception):
    """Base exception for BATIP."""


class NetworkError(BATIPError):
    """Raised when a network request fails."""


class ProviderError(BATIPError):
    """Raised when a provider returns invalid data."""


class ParsingError(BATIPError):
    """Raised when response parsing fails."""