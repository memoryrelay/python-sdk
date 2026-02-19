"""
MemoryRelay Python SDK

Official Python client for MemoryRelay API.
"""

__version__ = "0.2.0"

from memoryrelay.async_client import AsyncMemoryRelay
from memoryrelay.client import MemoryRelay
from memoryrelay.exceptions import (
    APIError,
    AuthenticationError,
    MemoryRelayError,
    NotFoundError,
    RateLimitError,
    ValidationError,
    TimeoutError,
)
from memoryrelay.types import (
    Agent,
    Entity,
    HealthStatus,
    Memory,
    MemorySearchResult,
    MemoryAsyncResponse,
    MemoryStatusResponse,
)

__all__ = [
    "MemoryRelay",
    "AsyncMemoryRelay",
    "MemoryRelayError",
    "APIError",
    "AuthenticationError",
    "RateLimitError",
    "NotFoundError",
    "ValidationError",
    "TimeoutError",
    "Memory",
    "MemorySearchResult",
    "MemoryAsyncResponse",
    "MemoryStatusResponse",
    "Entity",
    "Agent",
    "HealthStatus",
]
