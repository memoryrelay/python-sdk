"""Memory resource management."""

from __future__ import annotations

import asyncio
import time
from typing import Any

import httpx

from ..exceptions import (
    APIError,
    MemoryRelayError,
    NetworkError,
    NotFoundError,
    RequestTimeoutError,
    ValidationError,
)
from ..models import (
    BatchMemoryRequest,
    BatchMemoryResponse,
    MaintenanceRequest,
    MaintenanceResponse,
    Memory,
    MemoryAsyncResponse,
    MemoryContextRequest,
    MemoryContextResponse,
    MemoryCreate,
    MemoryList,
    MemoryPromoteRequest,
    MemorySearchRequest,
    MemoryStatusResponse,
    MemoryUpdate,
    SearchResponse,
)


class MemoriesResource:
    """Synchronous memory operations."""

    def __init__(self, client: httpx.Client, base_url: str):
        self._client = client
        self._base_url = base_url

    def create(self, memory: MemoryCreate) -> Memory:
        """Create a new memory."""
        try:
            response = self._client.post(
                f"{self._base_url}/v1/memories", json=memory.model_dump(exclude_none=True)
            )
            self._handle_errors(response)
            return Memory(**response.json())
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    def list(self, agent_id: str | None = None, limit: int = 100, offset: int = 0) -> MemoryList:
        """List memories with optional filtering."""
        try:
            params: dict[str, Any] = {"limit": limit, "offset": offset}
            if agent_id:
                params["agent_id"] = agent_id

            response = self._client.get(f"{self._base_url}/v1/memories", params=params)
            self._handle_errors(response)
            return MemoryList(**response.json())
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    def get(self, memory_id: str) -> Memory:
        """Get a specific memory by ID."""
        try:
            response = self._client.get(f"{self._base_url}/v1/memories/{memory_id}")
            self._handle_errors(response)
            return Memory(**response.json())
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    def update(self, memory_id: str, memory: MemoryUpdate) -> Memory:
        """Update a memory."""
        try:
            response = self._client.put(
                f"{self._base_url}/v1/memories/{memory_id}",
                json=memory.model_dump(exclude_none=True),
            )
            self._handle_errors(response)
            return Memory(**response.json())
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    def delete(self, memory_id: str) -> None:
        """Delete a memory."""
        try:
            response = self._client.delete(f"{self._base_url}/v1/memories/{memory_id}")
            self._handle_errors(response)
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    def search(self, request: MemorySearchRequest) -> SearchResponse:
        """Perform semantic search on memories.

        Returns:
            SearchResponse with data (list of MemorySearchResult), query, and object fields.
        """
        try:
            response = self._client.post(
                f"{self._base_url}/v1/memories/search", json=request.model_dump(exclude_none=True)
            )
            self._handle_errors(response)
            return SearchResponse(**response.json())
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    def extract_entities(self, memory_id: str) -> dict:
        """Trigger entity extraction for a memory.

        Args:
            memory_id: Memory ID to extract entities from

        Returns:
            dict with status, memory_id, extraction_method, extraction_model
        """
        try:
            response = self._client.post(
                f"{self._base_url}/v1/memories/{memory_id}/extract-entities"
            )
            self._handle_errors(response)
            return response.json()
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    def get_extraction_status(self, memory_id: str) -> dict:
        """Get entity extraction status for a memory.

        Args:
            memory_id: Memory ID

        Returns:
            dict with status, extraction_method, extraction_model, updated_at, entity_count
        """
        try:
            response = self._client.get(
                f"{self._base_url}/v1/memories/{memory_id}/extraction-status"
            )
            self._handle_errors(response)
            return response.json()
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    def backfill_entities(
        self,
        limit: int = 100,
        agent_id: str | None = None,
    ) -> dict:
        """Backfill entity extraction for memories without entities.

        Args:
            limit: Max memories to process (1-500)
            agent_id: Limit to specific agent

        Returns:
            dict with status and queued count
        """
        try:
            params: dict[str, Any] = {"limit": limit}
            if agent_id:
                params["agent_id"] = agent_id
            response = self._client.post(
                f"{self._base_url}/v1/memories/backfill-entities", params=params
            )
            self._handle_errors(response)
            return response.json()
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    # ── V2 Async API ────────────────────────────────────────────────

    def create_async(self, memory: MemoryCreate) -> MemoryAsyncResponse:
        """Create a memory with async processing (V2 API).

        Returns at once with 202 Accepted; embedding and entity extraction run
        in the background. Poll with get_status() or wait_until_ready().
        """
        try:
            response = self._client.post(
                f"{self._base_url}/v2/memories", json=memory.model_dump(exclude_none=True)
            )
            self._handle_errors(response)
            return MemoryAsyncResponse(**response.json())
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    def get_status(self, memory_id: str) -> MemoryStatusResponse:
        """Get processing status of a V2 async memory."""
        try:
            response = self._client.get(f"{self._base_url}/v2/memories/{memory_id}/status")
            self._handle_errors(response)
            return MemoryStatusResponse(**response.json())
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    def wait_until_ready(
        self, memory_id: str, poll_interval: float = 0.5, timeout: float = 30.0
    ) -> Memory:
        """Poll get_status() until the memory is ready, then return it.

        Raises APIError when processing failed and RequestTimeoutError when
        the timeout passes first.
        """
        start_time = time.monotonic()

        while True:
            status = self.get_status(memory_id)

            if status.status == "ready":
                return self.get(memory_id)
            elif status.status == "failed":
                raise APIError(f"Memory processing failed: {status.error or 'Unknown error'}", 500)

            if time.monotonic() - start_time >= timeout:
                raise RequestTimeoutError(
                    f"Memory did not become ready within {timeout}s. " f"Status: {status.status}"
                )

            time.sleep(poll_interval)

    def promote(
        self,
        memory_id: str,
        importance: float,
        tier: str | None = None,
    ) -> Memory:
        """Update a memory's importance and recompute its tier.

        Args:
            memory_id: Memory ID
            importance: New importance value (0.0-1.0). Values >= 0.8 promote to hot tier.
            tier: Optional tier override ('hot', 'warm', 'cold'). Auto-computed if omitted.

        Returns:
            Updated Memory object
        """
        try:
            request = MemoryPromoteRequest(importance=importance, tier=tier)
            response = self._client.put(
                f"{self._base_url}/v1/memories/{memory_id}/importance",
                json=request.model_dump(exclude_none=True),
            )
            self._handle_errors(response)
            return Memory(**response.json())
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    def maintenance(self, action: str = "demote_cold") -> MaintenanceResponse:
        """Run memory maintenance operations.

        Args:
            action: Maintenance action. Currently only 'demote_cold' is supported.

        Returns:
            MaintenanceResponse with action and demoted_count
        """
        try:
            request = MaintenanceRequest(action=action)
            response = self._client.post(
                f"{self._base_url}/v1/memories/maintenance",
                json=request.model_dump(),
            )
            self._handle_errors(response)
            return MaintenanceResponse(**response.json())
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    def batch_create(self, request: BatchMemoryRequest) -> BatchMemoryResponse:
        """Create multiple memories in a single request.

        Args:
            request: Batch memory request with 1-100 memories

        Returns:
            BatchMemoryResponse with per-memory results
        """
        try:
            response = self._client.post(
                f"{self._base_url}/v1/memories/batch", json=request.model_dump(exclude_none=True)
            )
            self._handle_errors(response)
            return BatchMemoryResponse(**response.json())
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    def context(self, request: MemoryContextRequest) -> MemoryContextResponse:
        """Build a context window from relevant memories.

        Args:
            request: Context request with query and optional token budget

        Returns:
            MemoryContextResponse with formatted context string
        """
        try:
            response = self._client.post(
                f"{self._base_url}/v1/memories/context", json=request.model_dump(exclude_none=True)
            )
            self._handle_errors(response)
            return MemoryContextResponse(**response.json())
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    @staticmethod
    def _handle_errors(response: httpx.Response) -> None:
        """Handle HTTP errors and raise appropriate exceptions."""
        if response.is_success:
            return

        status_code = response.status_code
        try:
            error_data = response.json()
            message = error_data.get("detail", response.text)
        except Exception:
            message = response.text

        if status_code == 404:
            raise NotFoundError(message, status_code)
        elif status_code == 422:
            raise ValidationError(message, status_code)
        elif status_code >= 500:
            raise APIError(message, status_code)
        else:
            raise MemoryRelayError(message, status_code)


class AsyncMemoriesResource:
    """Asynchronous memory operations."""

    def __init__(self, client: httpx.AsyncClient, base_url: str):
        self._client = client
        self._base_url = base_url

    async def create(self, memory: MemoryCreate) -> Memory:
        """Create a new memory."""
        try:
            response = await self._client.post(
                f"{self._base_url}/v1/memories", json=memory.model_dump(exclude_none=True)
            )
            self._handle_errors(response)
            return Memory(**response.json())
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    async def list(
        self, agent_id: str | None = None, limit: int = 100, offset: int = 0
    ) -> MemoryList:
        """List memories with optional filtering."""
        try:
            params: dict[str, Any] = {"limit": limit, "offset": offset}
            if agent_id:
                params["agent_id"] = agent_id

            response = await self._client.get(f"{self._base_url}/v1/memories", params=params)
            self._handle_errors(response)
            return MemoryList(**response.json())
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    async def get(self, memory_id: str) -> Memory:
        """Get a specific memory by ID."""
        try:
            response = await self._client.get(f"{self._base_url}/v1/memories/{memory_id}")
            self._handle_errors(response)
            return Memory(**response.json())
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    async def update(self, memory_id: str, memory: MemoryUpdate) -> Memory:
        """Update a memory."""
        try:
            response = await self._client.put(
                f"{self._base_url}/v1/memories/{memory_id}",
                json=memory.model_dump(exclude_none=True),
            )
            self._handle_errors(response)
            return Memory(**response.json())
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    async def delete(self, memory_id: str) -> None:
        """Delete a memory."""
        try:
            response = await self._client.delete(f"{self._base_url}/v1/memories/{memory_id}")
            self._handle_errors(response)
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    async def search(self, request: MemorySearchRequest) -> SearchResponse:
        """Perform semantic search on memories.

        Returns:
            SearchResponse with data (list of MemorySearchResult), query, and object fields.
        """
        try:
            response = await self._client.post(
                f"{self._base_url}/v1/memories/search", json=request.model_dump(exclude_none=True)
            )
            self._handle_errors(response)
            return SearchResponse(**response.json())
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    async def extract_entities(self, memory_id: str) -> dict:
        """Trigger entity extraction for a memory.

        Args:
            memory_id: Memory ID to extract entities from

        Returns:
            dict with status, memory_id, extraction_method, extraction_model
        """
        try:
            response = await self._client.post(
                f"{self._base_url}/v1/memories/{memory_id}/extract-entities"
            )
            self._handle_errors(response)
            return response.json()
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    async def get_extraction_status(self, memory_id: str) -> dict:
        """Get entity extraction status for a memory.

        Args:
            memory_id: Memory ID

        Returns:
            dict with status, extraction_method, extraction_model, updated_at, entity_count
        """
        try:
            response = await self._client.get(
                f"{self._base_url}/v1/memories/{memory_id}/extraction-status"
            )
            self._handle_errors(response)
            return response.json()
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    async def backfill_entities(
        self,
        limit: int = 100,
        agent_id: str | None = None,
    ) -> dict:
        """Backfill entity extraction for memories without entities.

        Args:
            limit: Max memories to process (1-500)
            agent_id: Limit to specific agent

        Returns:
            dict with status and queued count
        """
        try:
            params: dict[str, Any] = {"limit": limit}
            if agent_id:
                params["agent_id"] = agent_id
            response = await self._client.post(
                f"{self._base_url}/v1/memories/backfill-entities", params=params
            )
            self._handle_errors(response)
            return response.json()
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    # ── V2 Async API ────────────────────────────────────────────────

    async def create_async(self, memory: MemoryCreate) -> MemoryAsyncResponse:
        """Create a memory with async processing (V2 API).

        Returns immediately with 202 Accepted. Embedding and entity extraction
        happen in the background. Use get_status() or wait_until_ready() to poll.

        Args:
            memory: Memory creation request

        Returns:
            MemoryAsyncResponse with status and job_id

        Example:
            >>> response = await client.memories.create_async(
            ...     MemoryCreate(agent_id="my-agent", content="User prefers dark mode")
            ... )
            >>> print(f"Memory ID: {response.id}, Status: {response.status}")
            >>> # Poll until ready
            >>> memory = await client.memories.wait_until_ready(response.id)
        """
        try:
            response = await self._client.post(
                f"{self._base_url}/v2/memories", json=memory.model_dump(exclude_none=True)
            )
            self._handle_errors(response)
            return MemoryAsyncResponse(**response.json())
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    async def get_status(self, memory_id: str) -> MemoryStatusResponse:
        """Get processing status of a V2 async memory.

        Args:
            memory_id: Memory ID

        Returns:
            MemoryStatusResponse with status and error details

        Example:
            >>> status = await client.memories.get_status(memory_id)
            >>> print(f"Status: {status.status}")
        """
        try:
            response = await self._client.get(f"{self._base_url}/v2/memories/{memory_id}/status")
            self._handle_errors(response)
            return MemoryStatusResponse(**response.json())
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    async def wait_until_ready(
        self, memory_id: str, poll_interval: float = 0.5, timeout: float = 30.0
    ) -> Memory:
        """Wait for async memory to be ready, then return it.

        Polls get_status() until status is "ready" or "failed".

        Args:
            memory_id: Memory ID
            poll_interval: Seconds between status checks (default 0.5s)
            timeout: Maximum seconds to wait (default 30s)

        Returns:
            Completed Memory object

        Raises:
            APIError: If memory processing failed
            RequestTimeoutError: If timeout exceeded

        Example:
            >>> response = await client.memories.create_async(...)
            >>> memory = await client.memories.wait_until_ready(response.id)
            >>> print(f"Memory ready with {len(memory.entities)} entities")
        """
        start_time = asyncio.get_event_loop().time()

        while True:
            status = await self.get_status(memory_id)

            if status.status == "ready":
                # Fetch full memory
                return await self.get(memory_id)
            elif status.status == "failed":
                raise APIError(f"Memory processing failed: {status.error or 'Unknown error'}", 500)

            # Check timeout
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed >= timeout:
                raise RequestTimeoutError(
                    f"Memory did not become ready within {timeout}s. " f"Status: {status.status}"
                )

            # Wait before next poll
            await asyncio.sleep(poll_interval)

    async def promote(
        self,
        memory_id: str,
        importance: float,
        tier: str | None = None,
    ) -> Memory:
        """Update a memory's importance and recompute its tier.

        Args:
            memory_id: Memory ID
            importance: New importance value (0.0-1.0). Values >= 0.8 promote to hot tier.
            tier: Optional tier override ('hot', 'warm', 'cold'). Auto-computed if omitted.

        Returns:
            Updated Memory object
        """
        try:
            request = MemoryPromoteRequest(importance=importance, tier=tier)
            response = await self._client.put(
                f"{self._base_url}/v1/memories/{memory_id}/importance",
                json=request.model_dump(exclude_none=True),
            )
            self._handle_errors(response)
            return Memory(**response.json())
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    async def maintenance(self, action: str = "demote_cold") -> MaintenanceResponse:
        """Run memory maintenance operations.

        Args:
            action: Maintenance action. Currently only 'demote_cold' is supported.

        Returns:
            MaintenanceResponse with action and demoted_count
        """
        try:
            request = MaintenanceRequest(action=action)
            response = await self._client.post(
                f"{self._base_url}/v1/memories/maintenance",
                json=request.model_dump(),
            )
            self._handle_errors(response)
            return MaintenanceResponse(**response.json())
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    async def batch_create(self, request: BatchMemoryRequest) -> BatchMemoryResponse:
        """Create multiple memories in a single request.

        Args:
            request: Batch memory request with 1-100 memories

        Returns:
            BatchMemoryResponse with per-memory results
        """
        try:
            response = await self._client.post(
                f"{self._base_url}/v1/memories/batch", json=request.model_dump(exclude_none=True)
            )
            self._handle_errors(response)
            return BatchMemoryResponse(**response.json())
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    async def context(self, request: MemoryContextRequest) -> MemoryContextResponse:
        """Build a context window from relevant memories.

        Args:
            request: Context request with query and optional token budget

        Returns:
            MemoryContextResponse with formatted context string
        """
        try:
            response = await self._client.post(
                f"{self._base_url}/v1/memories/context", json=request.model_dump(exclude_none=True)
            )
            self._handle_errors(response)
            return MemoryContextResponse(**response.json())
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    @staticmethod
    def _handle_errors(response: httpx.Response) -> None:
        """Handle HTTP errors and raise appropriate exceptions."""
        if response.is_success:
            return

        status_code = response.status_code
        try:
            error_data = response.json()
            message = error_data.get("detail", response.text)
        except Exception:
            message = response.text

        if status_code == 404:
            raise NotFoundError(message, status_code)
        elif status_code == 422:
            raise ValidationError(message, status_code)
        elif status_code >= 500:
            raise APIError(message, status_code)
        else:
            raise MemoryRelayError(message, status_code)
