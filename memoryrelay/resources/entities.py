"""
Entities resource - entity tracking and relationships.
"""

from typing import TYPE_CHECKING, Any, Optional, cast

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
        name: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Entity:
        """
        Create a new entity.

        Args:
            entity_type: Type of entity (e.g., "person", "organization", "project")
            name: Name of the entity
            metadata: Optional metadata

        Returns:
            Created Entity object
        """
        response = self._client._request(
            "POST",
            "/v1/entities",
            json={
                "entity_type": entity_type,
                "name": name,
                "metadata": metadata,
            },
        )
        return Entity(**cast(dict[str, Any], response))

    def get(self, entity_id: str) -> Entity:
        """
        Retrieve an entity by ID.

        Args:
            entity_id: Entity ID

        Returns:
            Entity object
        """
        response = self._client._request("GET", f"/v1/entities/{entity_id}")
        assert isinstance(response, dict)
        return Entity(**cast(dict[str, Any], response))

    def list(
        self,
        agent_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Entity]:
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
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if agent_id:
            params["agent_id"] = agent_id
        if entity_type:
            params["entity_type"] = entity_type

        response = self._client._request("GET", "/v1/entities", params=params)
        assert isinstance(response, dict)
        return [Entity(**item) for item in cast(dict[str, Any], response).get("data", [])]

    def link(self, entity_id: str, memory_id: str, relationship: Optional[str] = None) -> None:
        """
        Link an entity to a memory.

        Args:
            entity_id: Entity ID
            memory_id: Memory ID
            relationship: Relationship label (default: "mentioned_in")
        """
        body: dict[str, Any] = {"memory_id": memory_id}
        if relationship:
            body["relationship"] = relationship

        self._client._request(
            "POST",
            f"/v1/entities/{entity_id}/link",
            json=body,
        )

    def delete(self, entity_id: str) -> None:
        """
        Delete an entity.

        Args:
            entity_id: Entity ID
        """
        self._client._request("DELETE", f"/v1/entities/{entity_id}")
