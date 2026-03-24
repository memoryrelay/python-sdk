"""
Async Memories resource - CRUD operations for memories.
"""

import builtins
from typing import TYPE_CHECKING, Any, Optional, cast

from memoryrelay.exceptions import ValidationError
from memoryrelay.types import (
    BatchMemoryItem,
    BatchMemoryResponse,
    Memory,
    MemorySearchResult,
)

if TYPE_CHECKING:
    from memoryrelay.async_client import AsyncMemoryRelay


class AsyncMemoriesResource:
    """Async Memories API resource."""

    def __init__(self, client: "AsyncMemoryRelay") -> None:
        self._client = client

    async def create(
        self,
        content: str,
        agent_id: str,
        metadata: Optional[dict[str, Any]] = None,
        user_id: Optional[str] = None,
        visibility: Optional[str] = None,
        memory_type: Optional[str] = None,
        importance: Optional[float] = None,
        tier: Optional[str] = None,
        session_id: Optional[str] = None,
        project: Optional[str] = None,
        deduplicate: bool = False,
        dedup_threshold: float = 0.95,
        auto_extract_entities: Optional[bool] = None,
    ) -> Memory:
        """
        Create a new memory.

        Args:
            content: Memory content (1-50,000 characters)
            agent_id: Agent identifier
            metadata: Optional metadata dictionary
            user_id: Optional user identifier
            visibility: Memory visibility: 'private' (default) or 'confidential'
            memory_type: Memory type: fact, event, insight, task, preference, entity_reference, system
            importance: Memory importance (0.0-1.0). Defaults to 0.5. Values >= 0.8 promote to hot tier.
            tier: Memory tier override: 'hot', 'warm', or 'cold'. Auto-computed if omitted.
            session_id: Session ID to associate this memory with
            project: Project slug to scope this memory to
            deduplicate: Check for duplicate content before storing (default: False)
            dedup_threshold: Semantic similarity threshold for dedup (0.5-1.0, default: 0.95)
            auto_extract_entities: Extract entities from content. True=always, False=never, None=auto.

        Returns:
            Created Memory object

        Raises:
            ValidationError: Invalid input (empty content, too long, etc.)

        Example:
            >>> memory = await client.memories.create(
            ...     content="User prefers dark mode",
            ...     agent_id="my-agent",
            ...     metadata={"category": "preference"}
            ... )
        """
        # Validate input
        if not content or not content.strip():
            raise ValidationError("content cannot be empty", status_code=400)

        if len(content) > 50000:
            raise ValidationError(
                f"content exceeds maximum length of 50,000 characters (got {len(content)})",
                status_code=400,
            )

        if not agent_id or not agent_id.strip():
            raise ValidationError("agent_id cannot be empty", status_code=400)

        body: dict[str, Any] = {
            "content": content,
            "agent_id": agent_id,
        }
        if metadata is not None:
            body["metadata"] = metadata
        if user_id is not None:
            body["user_id"] = user_id
        if visibility is not None:
            body["visibility"] = visibility
        if memory_type is not None:
            body["memory_type"] = memory_type
        if importance is not None:
            body["importance"] = importance
        if tier is not None:
            body["tier"] = tier
        if session_id is not None:
            body["session_id"] = session_id
        if project is not None:
            body["project"] = project
        if deduplicate:
            body["deduplicate"] = deduplicate
            body["dedup_threshold"] = dedup_threshold
        if auto_extract_entities is not None:
            body["auto_extract_entities"] = auto_extract_entities

        response = await self._client._request(
            "POST",
            "/v1/memories",
            json=body,
        )
        return Memory(**cast(dict[str, Any], response))

    async def get(self, memory_id: str) -> Memory:
        """
        Retrieve a memory by ID.

        Args:
            memory_id: Memory ID

        Returns:
            Memory object

        Raises:
            NotFoundError: Memory not found
        """
        response = await self._client._request("GET", f"/v1/memories/{memory_id}")
        assert isinstance(response, dict)
        return Memory(**cast(dict[str, Any], response))

    async def update(
        self,
        memory_id: str,
        content: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Memory:
        """
        Update an existing memory.

        Args:
            memory_id: Memory ID
            content: New content (optional)
            metadata: New metadata (optional)

        Returns:
            Updated Memory object

        Raises:
            ValidationError: Invalid input
        """
        # Validate input if provided
        if content is not None:
            if not content.strip():
                raise ValidationError("content cannot be empty", status_code=400)

            if len(content) > 50000:
                raise ValidationError(
                    f"content exceeds maximum length of 50,000 characters (got {len(content)})",
                    status_code=400,
                )

        response = await self._client._request(
            "PUT",
            f"/v1/memories/{memory_id}",
            json={"content": content, "metadata": metadata},
        )
        return Memory(**cast(dict[str, Any], response))

    async def delete(self, memory_id: str) -> None:
        """
        Delete a memory.

        Args:
            memory_id: Memory ID
        """
        await self._client._request("DELETE", f"/v1/memories/{memory_id}")

    async def list(
        self,
        agent_id: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Memory]:
        """
        List memories with optional filtering.

        Args:
            agent_id: Filter by agent ID
            user_id: Filter by user ID
            limit: Maximum number of results (default: 100)
            offset: Number of results to skip (default: 0)

        Returns:
            List of Memory objects
        """
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if agent_id:
            params["agent_id"] = agent_id
        if user_id:
            params["user_id"] = user_id

        response = await self._client._request("GET", "/v1/memories", params=params)
        assert isinstance(response, dict)
        return [Memory(**item) for item in cast(dict[str, Any], response).get("data", [])]

    async def search(
        self,
        query: str,
        agent_id: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 10,
        min_score: float = 0.0,
        metadata_filter: Optional[dict[str, Any]] = None,
        search_mode: Optional[str] = None,
    ) -> builtins.list[MemorySearchResult]:
        """
        Semantic search for memories.

        Args:
            query: Search query
            agent_id: Filter by agent ID
            user_id: Filter by user ID
            limit: Maximum number of results (default: 10)
            min_score: Minimum similarity score (0.0-1.0, default: 0.0)
            metadata_filter: Filter by metadata fields
            search_mode: Search mode: 'hybrid' (default), 'semantic', 'keyword'

        Returns:
            List of MemorySearchResult objects with memories and scores

        Example:
            >>> results = await client.memories.search(
            ...     query="user preferences",
            ...     agent_id="my-agent",
            ...     limit=5,
            ...     min_score=0.7
            ... )
            >>> for result in results:
            ...     print(f"Score: {result.score}, Content: {result.memory.content}")
        """
        body: dict[str, Any] = {
            "query": query,
            "limit": limit,
            "min_score": min_score,
        }
        if agent_id is not None:
            body["agent_id"] = agent_id
        if user_id is not None:
            body["user_id"] = user_id
        if metadata_filter is not None:
            body["metadata_filter"] = metadata_filter
        if search_mode is not None:
            body["search_mode"] = search_mode

        response = await self._client._request(
            "POST",
            "/v1/memories/search",
            json=body,
        )
        return [
            MemorySearchResult(**item) for item in cast(dict[str, Any], response).get("data", [])
        ]

    async def create_batch(
        self,
        memories: builtins.list[dict[str, Any]],
        parallel_embeddings: bool = True,
    ) -> BatchMemoryResponse:
        """
        Create multiple memories in a single request.

        Args:
            memories: List of memory dicts with 'content' (required),
                     'metadata', 'agent_id', 'user_id', 'client_id' (optional)
            parallel_embeddings: Generate embeddings in parallel (default: True)

        Returns:
            BatchMemoryResponse with results and timing info

        Example:
            >>> response = await client.memories.create_batch([
            ...     {"content": "User likes Python", "agent_id": "my-agent"},
            ...     {"content": "User dislikes JavaScript", "agent_id": "my-agent"},
            ...     {"content": "User prefers tabs over spaces", "metadata": {"spicy": True}}
            ... ])
            >>> print(f"Created {response.succeeded}/{response.total} memories")
            >>> print(f"Took {response.timing['total_ms']:.0f}ms")
        """
        # Validate batch items
        batch_items = [BatchMemoryItem(**item) for item in memories]

        response = await self._client._request(
            "POST",
            "/v1/memories/batch",
            json={
                "memories": [item.model_dump(exclude_none=True) for item in batch_items],
                "parallel_embeddings": parallel_embeddings,
            },
        )
        return BatchMemoryResponse(**cast(dict[str, Any], response))
