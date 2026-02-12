"""
Entities resource - entity tracking and relationships.
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from memoryrelay.types import Entity

if TYPE_CHECKING:
    from memoryrelay.client import MemoryRelay


class EntitiesResource:
    """Entities API resource."""
    
    def __init__(self, client: "MemoryRelay") -> None:
        self._client = client
    
    def create(
        self,
        entity_type: str,
        entity_value: str,
        agent_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Entity:
        """
        Create a new entity.
        
        Args:
            entity_type: Type of entity (e.g., "person", "organization", "project")
            entity_value: Value/name of entity
            agent_id: Agent identifier
            metadata: Optional metadata
            
        Returns:
            Created Entity object
        """
        response = self._client._request(
            "POST",
            "/v1/entities",
            json={
                "entity_type": entity_type,
                "entity_value": entity_value,
                "agent_id": agent_id,
                "metadata": metadata,
            },
        )
        return Entity(**response)
    
    def get(self, entity_id: str) -> Entity:
        """
        Retrieve an entity by ID.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            Entity object
        """
        response = self._client._request("GET", f"/v1/entities/{entity_id}")
        return Entity(**response)
    
    def list(
        self,
        agent_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Entity]:
        """
        List entities with optional filtering.
        
        Args:
            agent_id: Filter by agent ID
            entity_type: Filter by entity type
            limit: Maximum results (default: 100)
            offset: Skip results (default: 0)
            
        Returns:
            List of Entity objects
        """
        params: Dict[str, Any] = {"limit": limit, "offset": offset}
        if agent_id:
            params["agent_id"] = agent_id
        if entity_type:
            params["entity_type"] = entity_type
        
        response = self._client._request("GET", "/v1/entities", params=params)
        return [Entity(**item) for item in response.get("data", [])]
    
    def link(self, entity_id: str, memory_id: str) -> None:
        """
        Link an entity to a memory.
        
        Args:
            entity_id: Entity ID
            memory_id: Memory ID
        """
        self._client._request(
            "POST",
            f"/v1/entities/{entity_id}/link",
            json={"memory_id": memory_id},
        )
    
    def unlink(self, entity_id: str, memory_id: str) -> None:
        """
        Unlink an entity from a memory.
        
        Args:
            entity_id: Entity ID
            memory_id: Memory ID
        """
        self._client._request(
            "DELETE",
            f"/v1/entities/{entity_id}/link/{memory_id}",
        )
    
    def delete(self, entity_id: str) -> None:
        """
        Delete an entity.
        
        Args:
            entity_id: Entity ID
        """
        self._client._request("DELETE", f"/v1/entities/{entity_id}")
