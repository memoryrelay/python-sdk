"""
MemoryRelay Python SDK

Official Python client for MemoryRelay API.
"""

__version__ = "0.1.0"

from memoryrelay.client import MemoryRelay
from memoryrelay.async_client import AsyncMemoryRelay
from memoryrelay.exceptions import (
    MemoryRelayError,
    APIError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ValidationError,
)
from memoryrelay.types import (
    Memory,
    MemorySearchResult,
    Entity,
    Agent,
    HealthStatus,
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
    "Memory",
    "MemorySearchResult",
    "Entity",
    "Agent",
    "HealthStatus",
]
