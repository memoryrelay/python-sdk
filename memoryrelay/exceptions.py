"""Exceptions for MemoryRelay SDK."""

from __future__ import annotations


class MemoryRelayError(Exception):
    """Base exception for all MemoryRelay errors."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class AuthenticationError(MemoryRelayError):
    """Raised when API key is invalid or missing."""

    pass


class NotFoundError(MemoryRelayError):
    """Raised when a resource is not found (404)."""

    pass


class ValidationError(MemoryRelayError):
    """Raised when request validation fails (422)."""

    pass


class RateLimitError(MemoryRelayError):
    """Raised when rate limit is exceeded (429)."""

    pass


class APIError(MemoryRelayError):
    """Raised for general API errors (5xx)."""

    pass


class NetworkError(MemoryRelayError):
    """Raised when network request fails."""

    pass


class RequestTimeoutError(MemoryRelayError):
    """Raised when a request times out."""

    pass


class IcmError(MemoryRelayError):
    """A refused ICM request; ``code`` is the server's stable ICM code."""

    def __init__(self, message: str, status_code: int | None = None, *, code: str):
        super().__init__(message, status_code)
        self.code = code


class IcmUnsupportedError(IcmError):
    """The server does not offer ICM. Nothing was built; do not fall back to search."""

    def __init__(self) -> None:
        super().__init__(
            "This MemoryRelay server does not offer ICM (/v2/icm)", None, code="icm_unsupported"
        )
