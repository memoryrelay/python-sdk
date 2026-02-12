"""
Exception classes for MemoryRelay SDK.
"""

from typing import Any, Optional


class MemoryRelayError(Exception):
    """Base exception for all MemoryRelay errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class APIError(MemoryRelayError):
    """Generic API error."""
    
    def __init__(
        self,
        message: str,
        status_code: int,
        response: Optional[Any] = None,
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(message, status_code)
        self.response = response
        self.request_id = request_id


class AuthenticationError(APIError):
    """Authentication failed (401)."""
    pass


class RateLimitError(APIError):
    """Rate limit exceeded (429)."""
    
    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(message, 429, request_id=request_id)
        self.retry_after = retry_after


class NotFoundError(APIError):
    """Resource not found (404)."""
    pass


class ValidationError(APIError):
    """Request validation failed (400/422)."""
    pass


class NetworkError(MemoryRelayError):
    """Network/connection error."""
    pass


class TimeoutError(MemoryRelayError):
    """Request timeout."""
    pass
