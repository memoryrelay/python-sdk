"""
Agents resource - agent management.
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from memoryrelay.types import Agent

if TYPE_CHECKING:
    from memoryrelay.client import MemoryRelay


class AgentsResource:
    """Agents API resource."""
    
    def __init__(self, client: "MemoryRelay") -> None:
        self._client = client
    
    def create(
        self,
        agent_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Agent:
        """
        Create a new agent.
        
        Args:
            agent_id: Unique agent identifier
            name: Agent name (optional)
            description: Agent description (optional)
            metadata: Optional metadata
            
        Returns:
            Created Agent object
        """
        response = self._client._request(
            "POST",
            "/v1/agents",
            json={
                "id": agent_id,
                "name": name,
                "description": description,
                "metadata": metadata,
            },
        )
        return Agent(**response)
    
    def get(self, agent_id: str) -> Agent:
        """
        Retrieve an agent by ID.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent object
        """
        response = self._client._request("GET", f"/v1/agents/{agent_id}")
        return Agent(**response)
    
    def list(self, limit: int = 100, offset: int = 0) -> List[Agent]:
        """
        List all agents.
        
        Args:
            limit: Maximum results (default: 100)
            offset: Skip results (default: 0)
            
        Returns:
            List of Agent objects
        """
        params = {"limit": limit, "offset": offset}
        response = self._client._request("GET", "/v1/agents", params=params)
        return [Agent(**item) for item in response.get("data", [])]
    
    def update(
        self,
        agent_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Agent:
        """
        Update an agent.
        
        Args:
            agent_id: Agent ID
            name: New name (optional)
            description: New description (optional)
            metadata: New metadata (optional)
            
        Returns:
            Updated Agent object
        """
        response = self._client._request(
            "PUT",
            f"/v1/agents/{agent_id}",
            json={
                "name": name,
                "description": description,
                "metadata": metadata,
            },
        )
        return Agent(**response)
    
    def delete(self, agent_id: str) -> None:
        """
        Delete an agent.
        
        Args:
            agent_id: Agent ID
        """
        self._client._request("DELETE", f"/v1/agents/{agent_id}")
