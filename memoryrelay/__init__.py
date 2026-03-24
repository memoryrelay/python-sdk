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
    ForbiddenError,
    MemoryRelayError,
    NotFoundError,
    RateLimitError,
    TimeoutError,
    ValidationError,
)
from memoryrelay.types import (
    Agent,
    Entity,
    EntityInfo,
    HealthStatus,
    Memory,
    MemoryAsyncResponse,
    MemorySearchResult,
    MemoryStatusResponse,
)

__all__ = [
    "Agent",
    "APIError",
    "AsyncMemoryRelay",
    "AuthenticationError",
    "Entity",
    "EntityInfo",
    "ForbiddenError",
    "HealthStatus",
    "Memory",
    "MemoryAsyncResponse",
    "MemoryRelay",
    "MemoryRelayError",
    "MemorySearchResult",
    "MemoryStatusResponse",
    "NotFoundError",
    "RateLimitError",
    "TimeoutError",
    "ValidationError",
]
