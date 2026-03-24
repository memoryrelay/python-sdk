"""
Type definitions for MemoryRelay SDK.
"""

from datetime import datetime
from typing import Any, Optional, Union

from pydantic import BaseModel, Field


class EntityInfo(BaseModel):
    """An extracted entity embedded in a memory response."""

    type: str
    value: str
    confidence: float = Field(default=1.0, description="Extraction confidence score (0.0-1.0)")


class Memory(BaseModel):
    """A memory object."""

    id: str
    object: str = "memory"
    content: str
    agent_id: str
    user_id: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    entities: list[EntityInfo] = Field(default_factory=list)
    memory_type: Optional[str] = Field(default=None, description="Memory type classification")
    extraction_model: Optional[str] = None
    extraction_method: Optional[str] = None
    extraction_status: Optional[str] = None
    visibility: Optional[str] = "private"
    salience_score: Optional[float] = Field(
        default=None, description="Computed salience score (0-1)"
    )
    importance: Optional[float] = Field(
        default=None, description="User/agent-assigned priority (0.0-1.0)"
    )
    tier: Optional[str] = Field(default=None, description="Memory tier: hot, warm, or cold")
    is_duplicate: bool = False
    session_id: Optional[str] = Field(default=None, description="Session this memory belongs to")
    project_id: Optional[str] = Field(default=None, description="Project this memory is scoped to")
    archived_at: Optional[Union[int, datetime]] = None
    created_at: Union[int, datetime]
    updated_at: Union[int, datetime]


class MemorySearchResult(BaseModel):
    """Search result with memory and relevance score."""

    memory: Memory
    score: float = Field(description="Similarity score (0-1)", ge=0.0, le=1.0)


class Entity(BaseModel):
    """An entity object."""

    id: str
    entity_type: str
    name: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    memory_count: int = 0
    relationship_count: int = 0
    created_at: Union[int, datetime]
    updated_at: Union[int, datetime]


class EntityLink(BaseModel):
    """Link between entity and memory."""

    entity_id: str
    memory_id: str
    relevance_score: float = 0.0
    created_at: Union[int, datetime]


class Agent(BaseModel):
    """An agent object."""

    id: str
    name: Optional[str] = None
    description: Optional[str] = None
    config: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    memory_count: Optional[int] = None
    session_count: Optional[int] = None
    project_count: Optional[int] = None
    last_active_at: Optional[datetime] = None
    created_at: Union[int, datetime]
    updated_at: Union[int, datetime]


class HealthStatus(BaseModel):
    """API health status."""

    status: str
    version: str
    api_version: str
    environment: str
    timestamp: int
    uptime_seconds: int
    services: dict[str, str]


class BatchMemoryItem(BaseModel):
    """Single memory for batch creation."""

    content: str = Field(..., min_length=1, max_length=50000)
    metadata: Optional[dict[str, Any]] = None
    agent_id: Optional[str] = None
    user_id: Optional[str] = None
    client_id: Optional[str] = None
    session_id: Optional[str] = None


class BatchMemoryResult(BaseModel):
    """Result for a single memory in batch operation."""

    index: int = Field(description="Index in the request array")
    status: str  # "success", "failed", "skipped"
    memory_id: Optional[str] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    content_preview: str = Field(default="", description="First 100 chars of memory content")


class BatchMemoryResponse(BaseModel):
    """Response from batch memory creation."""

    success: bool
    total: int
    succeeded: int
    failed: int
    skipped: int = 0
    results: list[BatchMemoryResult]
    timing: dict[str, float] = Field(default_factory=dict)


# ── v2 Async API Types ──────────────────────────────────────────


class MemoryAsyncResponse(BaseModel):
    """
    Response from async memory creation (v2).

    API returns 202 Accepted immediately while embedding generation
    happens in the background.

    Example:
        >>> response = client.memories.create_async(
        ...     content="User prefers dark mode",
        ...     agent_id="my-agent"
        ... )
        >>> print(response.status)  # "pending"
        >>> print(response.job_id)  # "arq:01HQERX3B9..."
    """

    id: str = Field(..., description="Memory ID")
    status: str = Field(..., description="Processing status (pending)")
    job_id: Optional[str] = Field(default=None, description="ARQ job ID for tracking")
    estimated_completion_seconds: Optional[int] = Field(
        default=None, description="Estimated time until ready (typically 3s)"
    )


class MemoryStatusResponse(BaseModel):
    """
    Memory processing status (v2).

    Poll this endpoint to check if embedding generation is complete.

    Status values:
    - "pending": Queued, waiting for worker
    - "processing": Worker generating embedding
    - "ready": Embedding complete, memory searchable
    - "failed": Embedding generation failed

    Example:
        >>> status = client.memories.get_status(memory_id)
        >>> if status.status == "ready":
        ...     memory = client.memories.get(memory_id)
    """

    id: str = Field(..., description="Memory ID")
    status: str = Field(..., description="Processing status (pending/processing/ready/failed)")
    created_at: Optional[Union[int, datetime]] = Field(
        default=None, description="When memory was created"
    )
    updated_at: Optional[Union[int, datetime]] = Field(
        default=None, description="When status was last updated"
    )
    error: Optional[str] = Field(default=None, description="Error message if failed")
