"""MemoryRelay Python SDK - Official client for the MemoryRelay API."""

__version__ = "0.4.0"

from .async_client import AsyncMemoryRelay
from .client import MemoryRelay
from .exceptions import (
    APIError,
    AuthenticationError,
    IcmError,
    IcmUnsupportedError,
    MemoryRelayError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from .models import (
    Agent,
    AgentCreate,
    AgentList,
    # Agent update
    AgentUpdate,
    # Memory batch & context
    BatchMemoryItem,
    BatchMemoryRequest,
    BatchMemoryResponse,
    BatchMemoryResult,
    # Extraction models
    ByokKeyCreate,
    ByokKeyResponse,
    Entity,
    EntityCreate,
    EntityInfo,
    EntityLinkCreate,
    EntityLinkResponse,
    EntityList,
    EntityUpdate,
    ExtractionSettings,
    Memory,
    # V2 API models
    MemoryAsyncResponse,
    MemoryContextRequest,
    MemoryContextResponse,
    MemoryCreate,
    MemoryList,
    MemorySearchRequest,
    MemorySearchResult,
    MemoryStatusResponse,
    MemoryUpdate,
    SearchResponse,
)

__all__ = [
    # Clients
    "MemoryRelay",
    "AsyncMemoryRelay",
    # Models
    "Memory",
    "MemoryCreate",
    "MemoryUpdate",
    "MemorySearchRequest",
    "MemorySearchResult",
    "MemoryList",
    "SearchResponse",
    "EntityInfo",
    "Agent",
    "AgentCreate",
    "AgentList",
    "Entity",
    "EntityCreate",
    "EntityUpdate",
    "EntityList",
    "EntityLinkCreate",
    "EntityLinkResponse",
    # V2 API models
    "MemoryAsyncResponse",
    "MemoryStatusResponse",
    # Extraction models
    "ByokKeyCreate",
    "ByokKeyResponse",
    "ExtractionSettings",
    # Agent update
    "AgentUpdate",
    # Memory batch & context
    "BatchMemoryItem",
    "BatchMemoryRequest",
    "BatchMemoryResult",
    "BatchMemoryResponse",
    "MemoryContextRequest",
    "MemoryContextResponse",
    # Exceptions
    "MemoryRelayError",
    "AuthenticationError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "APIError",
    "NetworkError",
    "IcmError",
    "IcmUnsupportedError",
]
