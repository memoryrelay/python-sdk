"""
Memories resource - CRUD operations for memories.
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from memoryrelay.types import (
    BatchMemoryItem,
    BatchMemoryResponse,
    Memory,
    MemorySearchResult,
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
        metadata: Optional[Dict[str, Any]] = None,
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
            
        Example:
            >>> memory = client.memories.create(
            ...     content="User prefers dark mode",
            ...     agent_id="my-agent",
            ...     metadata={"category": "preference"}
            ... )
        """
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
        return Memory(**response)
    
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
        return Memory(**response)
    
    def update(
        self,
        memory_id: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Memory:
        """
        Update an existing memory.
        
        Args:
            memory_id: Memory ID
            content: New content (optional)
            metadata: New metadata (optional)
            
        Returns:
            Updated Memory object
        """
        response = self._client._request(
            "PUT",
            f"/v1/memories/{memory_id}",
            json={"content": content, "metadata": metadata},
        )
        return Memory(**response)
    
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
    ) -> List[Memory]:
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
        params: Dict[str, Any] = {"limit": limit, "offset": offset}
        if agent_id:
            params["agent_id"] = agent_id
        if user_id:
            params["user_id"] = user_id
        
        response = self._client._request("GET", "/v1/memories", params=params)
        return [Memory(**item) for item in response.get("data", [])]
    
    def search(
        self,
        query: str,
        agent_id: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 10,
        min_score: float = 0.0,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[MemorySearchResult]:
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
        return [MemorySearchResult(**item) for item in response.get("data", [])]
    
    def create_batch(
        self,
        memories: List[Dict[str, Any]],
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
        return BatchMemoryResponse(**response)
