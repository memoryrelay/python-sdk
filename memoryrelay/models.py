"""Pydantic models for MemoryRelay SDK."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

# ── Entity Info (embedded in Memory responses) ────────────────────


class EntityInfo(BaseModel):
    """An extracted entity embedded in a memory response."""

    type: str
    value: str
    confidence: float = Field(default=1.0, description="Extraction confidence score (0.0-1.0)")


# ── Memory Models ─────────────────────────────────────────────────


class Memory(BaseModel):
    """A memory in the MemoryRelay system."""

    id: str
    object: str = "memory"
    content: str
    agent_id: str
    user_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    entities: list[EntityInfo] = Field(default_factory=list)
    memory_type: str | None = Field(default=None, description="Memory type classification")
    extraction_model: str | None = None
    extraction_method: str | None = None
    extraction_status: str | None = None
    visibility: str | None = "private"
    salience_score: float | None = Field(default=None, description="Computed salience score (0-1)")
    importance: float | None = Field(
        default=None, description="User/agent-assigned priority (0.0-1.0)"
    )
    tier: str | None = Field(default=None, description="Memory tier: hot, warm, or cold")
    is_duplicate: bool = False
    embedding: list[float] | None = None
    archived_at: int | datetime | None = None
    created_at: int | datetime = Field(description="Unix timestamp or datetime")
    updated_at: int | datetime = Field(description="Unix timestamp or datetime")


class MemoryCreate(BaseModel):
    """Request model for creating a memory."""

    agent_id: str
    content: str
    metadata: dict[str, Any] | None = None
    visibility: str | None = Field(
        default=None, description="Memory visibility: 'private' (default) or 'confidential'"
    )
    memory_type: str | None = Field(
        default=None,
        description="Memory type: fact, event, insight, task, preference, entity_reference, system",
    )
    importance: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Memory importance (0.0-1.0). Defaults to 0.5. Values >= 0.8 promote to hot tier.",
    )
    tier: str | None = Field(
        default=None,
        description="Memory tier override: 'hot', 'warm', or 'cold'. Auto-computed if omitted.",
    )
    deduplicate: bool = Field(
        default=False, description="Check for duplicate content before storing"
    )
    dedup_threshold: float = Field(
        default=0.95, ge=0.5, le=1.0, description="Semantic similarity threshold for dedup"
    )


class MemoryUpdate(BaseModel):
    """Request model for updating a memory."""

    content: str | None = None
    metadata: dict[str, Any] | None = None


class MemorySearchRequest(BaseModel):
    """Request model for semantic search."""

    agent_id: str | None = Field(
        default=None, description="Agent namespace. If omitted, searches across all user's agents."
    )
    query: str
    limit: int = Field(default=10, ge=1, le=100)
    min_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Minimum similarity score (0-1)"
    )
    metadata_filter: dict[str, Any] | None = Field(
        default=None, description="Filter by metadata fields"
    )
    include_confidential: bool = Field(
        default=False, description="Include confidential memories in results."
    )
    include_archived: bool = Field(
        default=False, description="Include archived memories in results."
    )
    tier: str | None = Field(
        default=None,
        description="Filter by tier: 'hot', 'warm', or 'cold'. Omit to search all tiers.",
    )
    min_importance: float | None = Field(
        default=None, ge=0.0, le=1.0, description="Minimum importance threshold (0.0-1.0)"
    )


class MemorySearchResult(BaseModel):
    """A single search result with similarity score."""

    memory: Memory
    score: float = Field(description="Similarity score (0-1)", ge=0.0, le=1.0)


class SearchResponse(BaseModel):
    """Search results response from the API."""

    object: str = "search_results"
    data: list[MemorySearchResult]
    query: str


class MemoryList(BaseModel):
    """Paginated list of memories."""

    object: str = "list"
    data: list[Memory]
    has_more: bool = False
    next_cursor: str | None = None
    total_count: int | None = None


class MemoryPromoteRequest(BaseModel):
    """Request model for promoting/demoting a memory's importance and tier."""

    importance: float = Field(ge=0.0, le=1.0, description="New importance value (0.0-1.0)")
    tier: str | None = Field(
        default=None,
        description="Optional tier override: 'hot', 'warm', or 'cold'. Auto-computed if omitted.",
    )


class MaintenanceRequest(BaseModel):
    """Request model for memory maintenance operations."""

    action: str = Field(description="Maintenance action: 'demote_cold'")


class MaintenanceResponse(BaseModel):
    """Response from memory maintenance operations."""

    action: str
    demoted_count: int = Field(default=0, description="Number of memories demoted to cold tier")


# ── Agent Models ──────────────────────────────────────────────────


class Agent(BaseModel):
    """An agent in the MemoryRelay system."""

    id: str
    name: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    memory_count: int | None = None
    created_at: int | datetime = Field(description="Creation timestamp")
    updated_at: int | datetime = Field(description="Last update timestamp")


class AgentCreate(BaseModel):
    """Request model for creating an agent."""

    name: str
    metadata: dict[str, Any] | None = None


class AgentList(BaseModel):
    """Paginated list of agents."""

    data: list[Agent]
    has_more: bool = False
    next_cursor: str | None = None
    total_count: int | None = None


# ── Entity Models ─────────────────────────────────────────────────


class Entity(BaseModel):
    """An entity in the MemoryRelay system."""

    id: str
    name: str
    entity_type: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    memory_count: int = 0
    relationship_count: int = 0
    created_at: int | datetime = Field(description="Creation timestamp")
    updated_at: int | datetime = Field(description="Last update timestamp")


class EntityCreate(BaseModel):
    """Request model for creating an entity."""

    name: str
    entity_type: str
    metadata: dict[str, Any] | None = None


class EntityUpdate(BaseModel):
    """Request model for updating an entity."""

    name: str | None = None
    metadata: dict[str, Any] | None = None


class EntityLinkCreate(BaseModel):
    """Request model for linking an entity to a memory."""

    entity_id: str
    memory_id: str
    relationship: str | None = Field(default="mentioned_in", description="Relationship label")


class EntityLinkResponse(BaseModel):
    """Response for an entity-memory link."""

    entity_id: str
    memory_id: str
    relevance_score: float
    created_at: int | datetime = Field(description="Creation timestamp")


class EntityList(BaseModel):
    """Paginated list of entities."""

    data: list[Entity]
    total_count: int
    has_more: bool = False


# ── V2 API Models ───────────────────────────────────────────────────


class MemoryAsyncResponse(BaseModel):
    """Response from V2 async memory creation."""

    id: str
    status: str = Field(description="Memory status: 'pending', 'ready', 'failed'")
    job_id: str | None = Field(default=None, description="ARQ job ID for tracking")
    estimated_completion_seconds: int | None = Field(
        default=None, description="Estimated time until embedding + extraction complete"
    )


class MemoryStatusResponse(BaseModel):
    """Response from V2 memory status check."""

    id: str
    status: str = Field(description="Overall status: 'pending', 'processing', 'ready', 'failed'")
    created_at: int | datetime | None = Field(default=None, description="Memory creation timestamp")
    updated_at: int | datetime | None = Field(default=None, description="Last update timestamp")
    error: str | None = Field(default=None, description="Error message if failed")


# ── Extraction Settings Models ──────────────────────────────────────


class ByokKeyCreate(BaseModel):
    """Request to create a BYOK extraction key."""

    provider: str = Field(description="Provider: openai, anthropic, google, azure, ollama, custom")
    api_key: str = Field(description="API key (encrypted at rest)")
    model: str = Field(description="Model name to use")
    label: str | None = Field(default=None, description="Human-readable label")
    base_url: str | None = Field(default=None, description="Custom API base URL")


class ByokKeyResponse(BaseModel):
    """Response with BYOK key details."""

    id: str
    provider: str
    label: str | None
    model: str
    base_url: str | None
    is_active: bool
    masked_key: str
    last_validated_at: str | None
    last_used_at: str | None
    created_at: str
    updated_at: str


class ExtractionSettings(BaseModel):
    """User's extraction settings and BYOK status."""

    tier: str = Field(description="Subscription tier: free, starter, builder, pro, scale")
    extractor: str = Field(description="Active extractor: gliner, llm, byok")
    byok_enabled_globally: bool
    byok_configured: bool
    byok_active: bool
    masked_api_key: str | None
    preferred_model: str
    base_url: str
    last_validated_at: str | None
    plan_limits: dict[str, Any]
    keys: list[ByokKeyResponse]


# ── Agent Update ─────────────────────────────────────────────────


class AgentUpdate(BaseModel):
    """Request model for updating an agent."""

    name: str | None = None
    description: str | None = None
    metadata: dict[str, Any] | None = None


# ── Memory Batch & Context ──────────────────────────────────────


class BatchMemoryItem(BaseModel):
    """A single memory item in a batch create request."""

    content: str
    agent_id: str
    metadata: dict[str, Any] | None = None
    importance: float | None = Field(default=None, ge=0.0, le=1.0)
    tier: str | None = None


class BatchMemoryRequest(BaseModel):
    """Request model for batch memory creation."""

    memories: list[BatchMemoryItem] = Field(min_length=1, max_length=100)
    parallel_embeddings: bool = Field(default=True)


class BatchMemoryResult(BaseModel):
    """Result for a single memory in a batch response."""

    status: str
    id: str | None = None
    error: str | None = None


class BatchMemoryResponse(BaseModel):
    """Response from batch memory creation."""

    success: bool
    total: int
    succeeded: int
    failed: int
    skipped: int = 0
    results: list[BatchMemoryResult]


class MemoryContextRequest(BaseModel):
    """Request model for building memory context."""

    query: str
    limit: int = Field(default=10, ge=1, le=50)
    threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    max_tokens: int | None = None
    agent_id: str | None = None


class MemoryContextResponse(BaseModel):
    """Response from building memory context."""

    context: str
    memories_used: int
    total_chars: int
