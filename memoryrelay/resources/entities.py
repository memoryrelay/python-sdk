"""Entity resource management."""

from __future__ import annotations

from typing import Any

import httpx

from ..exceptions import APIError, MemoryRelayError, NetworkError, NotFoundError, ValidationError
from ..models import (
    Entity,
    EntityCreate,
    EntityLinkCreate,
    EntityLinkResponse,
    EntityList,
    EntityUpdate,
)


class EntitiesResource:
    """Synchronous entity operations."""

    def __init__(self, client: httpx.Client, base_url: str):
        self._client = client
        self._base_url = base_url

    def create(self, entity: EntityCreate) -> Entity:
        """Create a new entity."""
        try:
            response = self._client.post(
                f"{self._base_url}/v1/entities", json=entity.model_dump(exclude_none=True)
            )
            self._handle_errors(response)
            return Entity(**response.json())
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    def list(self, agent_id: str | None = None) -> EntityList:
        """List entities with optional agent filter."""
        try:
            params: dict[str, Any] = {}
            if agent_id:
                params["agent_id"] = agent_id

            response = self._client.get(f"{self._base_url}/v1/entities", params=params)
            self._handle_errors(response)
            return EntityList(**response.json())
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    def get(self, entity_id: str) -> Entity:
        """Get a specific entity by ID."""
        try:
            response = self._client.get(f"{self._base_url}/v1/entities/{entity_id}")
            self._handle_errors(response)
            return Entity(**response.json())
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    def update(self, entity_id: str, entity: EntityUpdate) -> Entity:
        """Update an entity.

        Args:
            entity_id: Entity ID
            entity: Update data (name and/or metadata)

        Returns:
            Updated Entity
        """
        try:
            response = self._client.put(
                f"{self._base_url}/v1/entities/{entity_id}",
                json=entity.model_dump(exclude_none=True),
            )
            self._handle_errors(response)
            return Entity(**response.json())
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    def delete(self, entity_id: str) -> None:
        """Delete an entity."""
        try:
            response = self._client.delete(f"{self._base_url}/v1/entities/{entity_id}")
            self._handle_errors(response)
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    def link_to_memory(self, link: EntityLinkCreate) -> EntityLinkResponse:
        """Link an entity to a memory.

        Args:
            link: Link data with entity_id, memory_id, and optional relationship label

        Returns:
            EntityLinkResponse with entity_id, memory_id, relevance_score, created_at
        """
        try:
            response = self._client.post(
                f"{self._base_url}/v1/entities/links", json=link.model_dump(exclude_none=True)
            )
            self._handle_errors(response)
            return EntityLinkResponse(**response.json())
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    def get_relationships(self, entity_id: str) -> dict:
        """Get relationships for an entity.

        Args:
            entity_id: Entity ID

        Returns:
            dict with data (list of relationships) and total count
        """
        try:
            response = self._client.get(f"{self._base_url}/v1/entities/{entity_id}/relationships")
            self._handle_errors(response)
            return response.json()
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    def get_neighborhood(self, entity_id: str) -> dict:
        """Get the neighborhood subgraph around an entity.

        Args:
            entity_id: Entity ID

        Returns:
            dict with center entity, neighboring entities, and relationships
        """
        try:
            response = self._client.get(f"{self._base_url}/v1/entities/{entity_id}/neighborhood")
            self._handle_errors(response)
            return response.json()
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


class AsyncEntitiesResource:
    """Asynchronous entity operations."""

    def __init__(self, client: httpx.AsyncClient, base_url: str):
        self._client = client
        self._base_url = base_url

    async def create(self, entity: EntityCreate) -> Entity:
        """Create a new entity."""
        try:
            response = await self._client.post(
                f"{self._base_url}/v1/entities", json=entity.model_dump(exclude_none=True)
            )
            self._handle_errors(response)
            return Entity(**response.json())
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    async def list(self, agent_id: str | None = None) -> EntityList:
        """List entities with optional agent filter."""
        try:
            params: dict[str, Any] = {}
            if agent_id:
                params["agent_id"] = agent_id

            response = await self._client.get(f"{self._base_url}/v1/entities", params=params)
            self._handle_errors(response)
            return EntityList(**response.json())
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    async def get(self, entity_id: str) -> Entity:
        """Get a specific entity by ID."""
        try:
            response = await self._client.get(f"{self._base_url}/v1/entities/{entity_id}")
            self._handle_errors(response)
            return Entity(**response.json())
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    async def update(self, entity_id: str, entity: EntityUpdate) -> Entity:
        """Update an entity.

        Args:
            entity_id: Entity ID
            entity: Update data (name and/or metadata)

        Returns:
            Updated Entity
        """
        try:
            response = await self._client.put(
                f"{self._base_url}/v1/entities/{entity_id}",
                json=entity.model_dump(exclude_none=True),
            )
            self._handle_errors(response)
            return Entity(**response.json())
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    async def delete(self, entity_id: str) -> None:
        """Delete an entity."""
        try:
            response = await self._client.delete(f"{self._base_url}/v1/entities/{entity_id}")
            self._handle_errors(response)
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    async def link_to_memory(self, link: EntityLinkCreate) -> EntityLinkResponse:
        """Link an entity to a memory.

        Args:
            link: Link data with entity_id, memory_id, and optional relationship label

        Returns:
            EntityLinkResponse with entity_id, memory_id, relevance_score, created_at
        """
        try:
            response = await self._client.post(
                f"{self._base_url}/v1/entities/links", json=link.model_dump(exclude_none=True)
            )
            self._handle_errors(response)
            return EntityLinkResponse(**response.json())
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    async def get_relationships(self, entity_id: str) -> dict:
        """Get relationships for an entity.

        Args:
            entity_id: Entity ID

        Returns:
            dict with data (list of relationships) and total count
        """
        try:
            response = await self._client.get(
                f"{self._base_url}/v1/entities/{entity_id}/relationships"
            )
            self._handle_errors(response)
            return response.json()
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    async def get_neighborhood(self, entity_id: str) -> dict:
        """Get the neighborhood subgraph around an entity.

        Args:
            entity_id: Entity ID

        Returns:
            dict with center entity, neighboring entities, and relationships
        """
        try:
            response = await self._client.get(
                f"{self._base_url}/v1/entities/{entity_id}/neighborhood"
            )
            self._handle_errors(response)
            return response.json()
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
