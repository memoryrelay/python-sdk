"""
Type definitions for MemoryRelay SDK.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class Memory(BaseModel):
    """A memory object."""

    id: str
    content: str
    agent_id: str
    user_id: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None
    embedding: Optional[list[float]] = None
    created_at: datetime
    updated_at: datetime


class MemorySearchResult(BaseModel):
    """Search result with memory and relevance score."""

    memory: Memory
    score: float
    distance: Optional[float] = None


class Entity(BaseModel):
    """An entity object."""

    id: str
    agent_id: str
    entity_type: str
    entity_value: str
    metadata: Optional[dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class EntityLink(BaseModel):
    """Link between entity and memory."""

    entity_id: str
    memory_id: str
    created_at: datetime


class Agent(BaseModel):
    """An agent object."""

    id: str
    name: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


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


class BatchMemoryResult(BaseModel):
    """Result for a single memory in batch operation."""

    status: str  # "success", "failed", "skipped"
    memory_id: Optional[str] = None
    error: Optional[str] = None
    client_id: Optional[str] = None


class BatchMemoryResponse(BaseModel):
    """Response from batch memory creation."""

    success: bool
    total: int
    succeeded: int
    failed: int
    skipped: int
    results: list[BatchMemoryResult]
    timing: dict[str, float]
