"""
Memories resource - CRUD operations for memories.
"""

import builtins
import time
from typing import TYPE_CHECKING, Any, Optional, cast

from memoryrelay.exceptions import TimeoutError, ValidationError
from memoryrelay.types import (
    BatchMemoryItem,
    BatchMemoryResponse,
    Memory,
    MemoryAsyncResponse,
    MemorySearchResult,
    MemoryStatusResponse,
)

if TYPE_CHECKING:
    from memoryrelay.client import MemoryRelay


class MemoriesResource:
    """Memories API resource."""

    def __init__(self, client: "MemoryRelay") -> None:
        self._client = client

    def create(
        self,
        content: str,
        agent_id: str,
        metadata: Optional[dict[str, Any]] = None,
        user_id: Optional[str] = None,
    ) -> Memory:
        """
        Create a new memory.

        Args:
            content: Memory content (1-50,000 characters)
            agent_id: Agent identifier
            metadata: Optional metadata dictionary
            user_id: Optional user identifier

        Returns:
            Created Memory object

        Raises:
            ValidationError: Invalid input (empty content, too long, etc.)

        Example:
            >>> memory = client.memories.create(
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

        response = self._client._request(
            "POST",
            "/v1/memories",
            json={
                "content": content,
                "agent_id": agent_id,
                "metadata": metadata,
                "user_id": user_id,
            },
        )
        return Memory(**cast(dict[str, Any], response))

    def get(self, memory_id: str) -> Memory:
        """
        Retrieve a memory by ID.

        Args:
            memory_id: Memory ID

        Returns:
            Memory object

        Raises:
            NotFoundError: Memory not found
        """
        response = self._client._request("GET", f"/v1/memories/{memory_id}")
        assert isinstance(response, dict)
        return Memory(**cast(dict[str, Any], response))

    def update(
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

        response = self._client._request(
            "PUT",
            f"/v1/memories/{memory_id}",
            json={"content": content, "metadata": metadata},
        )
        return Memory(**cast(dict[str, Any], response))

    def delete(self, memory_id: str) -> None:
        """
        Delete a memory.

        Args:
            memory_id: Memory ID
        """
        self._client._request("DELETE", f"/v1/memories/{memory_id}")

    def list(
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

        response = self._client._request("GET", "/v1/memories", params=params)
        assert isinstance(response, dict)
        return [Memory(**item) for item in cast(dict[str, Any], response).get("data", [])]

    def search(
        self,
        query: str,
        agent_id: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 10,
        min_score: float = 0.0,
        metadata_filter: Optional[dict[str, Any]] = None,
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

        Returns:
            List of MemorySearchResult objects with memories and scores

        Example:
            >>> results = client.memories.search(
            ...     query="user preferences",
            ...     agent_id="my-agent",
            ...     limit=5,
            ...     min_score=0.7
            ... )
            >>> for result in results:
            ...     print(f"Score: {result.score}, Content: {result.memory.content}")
        """
        response = self._client._request(
            "POST",
            "/v1/memories/search",
            json={
                "query": query,
                "agent_id": agent_id,
                "user_id": user_id,
                "limit": limit,
                "min_score": min_score,
                "metadata_filter": metadata_filter,
            },
        )
        return [
            MemorySearchResult(**item) for item in cast(dict[str, Any], response).get("data", [])
        ]

    def create_batch(
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
            >>> response = client.memories.create_batch([
            ...     {"content": "User likes Python", "agent_id": "my-agent"},
            ...     {"content": "User dislikes JavaScript", "agent_id": "my-agent"},
            ...     {"content": "User prefers tabs over spaces", "metadata": {"spicy": True}}
            ... ])
            >>> print(f"Created {response.succeeded}/{response.total} memories")
            >>> print(f"Took {response.timing['total_ms']:.0f}ms")
        """
        # Validate batch items
        batch_items = [BatchMemoryItem(**item) for item in memories]

        response = self._client._request(
            "POST",
            "/v1/memories/batch",
            json={
                "memories": [item.model_dump(exclude_none=True) for item in batch_items],
                "parallel_embeddings": parallel_embeddings,
            },
        )
        return BatchMemoryResponse(**cast(dict[str, Any], response))

    # ── v2 Async API Methods ──────────────────────────────────────────

    def create_async(
        self,
        content: str,
        agent_id: str,
        metadata: Optional[dict[str, Any]] = None,
        user_id: Optional[str] = None,
    ) -> MemoryAsyncResponse:
        """
        Create a new memory asynchronously (v2 API).

        Returns immediately with 202 Accepted while embedding generation
        happens in the background. Use `get_status()` to check completion
        or `wait_for_ready()` to block until ready.

        Performance: <50ms response time (60-600x faster than sync v1 API).

        Args:
            content: Memory content (1-50,000 characters)
            agent_id: Agent identifier
            metadata: Optional metadata dictionary
            user_id: Optional user identifier

        Returns:
            MemoryAsyncResponse with memory_id, status, and job_id

        Raises:
            ValidationError: Invalid input (empty content, too long, etc.)

        Example:
            >>> # Fire-and-forget (fastest)
            >>> response = client.memories.create_async(
            ...     content="User prefers dark mode",
            ...     agent_id="my-agent"
            ... )
            >>> print(f"Memory {response.id} queued (job: {response.job_id})")
            >>>
            >>> # Poll until ready
            >>> memory = client.memories.wait_for_ready(response.id, timeout=10)
            >>> print(f"Memory ready: {memory.id}")
        """
        # Validate input (same as v1)
        if not content or not content.strip():
            raise ValidationError("content cannot be empty", status_code=400)

        if len(content) > 50000:
            raise ValidationError(
                f"content exceeds maximum length of 50,000 characters (got {len(content)})",
                status_code=400,
            )

        if not agent_id or not agent_id.strip():
            raise ValidationError("agent_id cannot be empty", status_code=400)

        response = self._client._request(
            "POST",
            "/v2/memories",
            json={
                "content": content,
                "agent_id": agent_id,
                "metadata": metadata,
                "user_id": user_id,
            },
        )
        return MemoryAsyncResponse(**cast(dict[str, Any], response))

    def get_status(self, memory_id: str) -> MemoryStatusResponse:
        """
        Check the processing status of an async memory (v2 API).

        Status values:
        - "pending": Queued, waiting for worker
        - "processing": Worker generating embedding
        - "ready": Embedding complete, memory searchable
        - "failed": Embedding generation failed

        Args:
            memory_id: Memory ID

        Returns:
            MemoryStatusResponse with current status

        Raises:
            NotFoundError: Memory not found

        Example:
            >>> response = client.memories.create_async(content="...", agent_id="...")
            >>> status = client.memories.get_status(response.id)
            >>> print(status.status)  # "pending", "processing", "ready", or "failed"
        """
        response = self._client._request("GET", f"/v2/memories/{memory_id}/status")
        return MemoryStatusResponse(**cast(dict[str, Any], response))

    def wait_for_ready(
        self,
        memory_id: str,
        timeout: float = 30.0,
        poll_interval: float = 0.5,
    ) -> Memory:
        """
        Poll memory status until ready or timeout.

        This is a convenience method that combines `get_status()` and `get()`
        to provide a drop-in replacement for v1's synchronous `create()`.

        Args:
            memory_id: Memory ID
            timeout: Maximum time to wait in seconds (default: 30.0)
            poll_interval: Time between status checks in seconds (default: 0.5)

        Returns:
            Memory object once status is "ready"

        Raises:
            TimeoutError: Memory not ready after timeout seconds
            ValidationError: Memory status is "failed"
            NotFoundError: Memory not found

        Example:
            >>> # Create async, wait for ready (drop-in v1 replacement)
            >>> response = client.memories.create_async(
            ...     content="User prefers dark mode",
            ...     agent_id="my-agent"
            ... )
            >>> memory = client.memories.wait_for_ready(response.id, timeout=10)
            >>> print(f"Memory ready: {memory.id}")
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            status = self.get_status(memory_id)

            if status.status == "ready":
                # Memory is ready, fetch full memory
                return self.get(memory_id)

            elif status.status == "failed":
                raise ValidationError(
                    f"Memory {memory_id} embedding generation failed",
                    status_code=500,
                )

            # Still pending or processing, wait and retry
            time.sleep(poll_interval)

        # Timeout exceeded
        elapsed = time.time() - start_time
        raise TimeoutError(
            f"Memory {memory_id} not ready after {elapsed:.1f}s (timeout: {timeout}s)",
            status_code=408,
        )

    def create_and_wait(
        self,
        content: str,
        agent_id: str,
        metadata: Optional[dict[str, Any]] = None,
        user_id: Optional[str] = None,
        timeout: float = 30.0,
    ) -> Memory:
        """
        Create memory async and wait for completion (convenience method).

        This is a drop-in replacement for v1's synchronous `create()` that
        uses v2's async API internally. Combines `create_async()` and
        `wait_for_ready()` in a single call.

        Args:
            content: Memory content (1-50,000 characters)
            agent_id: Agent identifier
            metadata: Optional metadata dictionary
            user_id: Optional user identifier
            timeout: Maximum time to wait in seconds (default: 30.0)

        Returns:
            Memory object once ready

        Raises:
            ValidationError: Invalid input or embedding generation failed
            TimeoutError: Memory not ready after timeout seconds

        Example:
            >>> # Same interface as v1, but faster (uses v2 internally)
            >>> memory = client.memories.create_and_wait(
            ...     content="User prefers dark mode",
            ...     agent_id="my-agent"
            ... )
            >>> print(f"Memory ready: {memory.id}")
        """
        response = self.create_async(
            content=content,
            agent_id=agent_id,
            metadata=metadata,
            user_id=user_id,
        )
        return self.wait_for_ready(response.id, timeout=timeout)
