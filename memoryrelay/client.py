"""Synchronous MemoryRelay client."""

from __future__ import annotations

from typing import Any

import httpx

from .exceptions import AuthenticationError
from .resources.agents import AgentsResource
from .resources.entities import EntitiesResource
from .resources.extraction import ExtractionResource
from .resources.icm import IcmResource
from .resources.memories import MemoriesResource


class MemoryRelay:
    """Synchronous client for the MemoryRelay API.

    Example:
        >>> client = MemoryRelay(api_key="your-api-key")
        >>> agent = client.agents.create(name="MyAgent")
        >>> memory = client.memories.create(
        ...     agent_id=agent.id,
        ...     content="Important information"
        ... )
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://api.memoryrelay.net",
        timeout: float = 30.0,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ):
        """Initialize the MemoryRelay client.

        Args:
            api_key: API key for authentication. Can also be set via MEMORYRELAY_API_KEY env var.
            base_url: Base URL for the API (default: https://api.memoryrelay.net)
            timeout: Request timeout in seconds (default: 30.0)
            headers: Additional headers to include in requests
            **kwargs: Additional arguments passed to httpx.Client

        Raises:
            AuthenticationError: If no API key is provided
        """
        if not api_key:
            import os

            api_key = os.getenv("MEMORYRELAY_API_KEY")

        if not api_key:
            raise AuthenticationError(
                "API key is required. Provide via api_key parameter or MEMORYRELAY_API_KEY environment variable."
            )

        default_headers = {
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "memoryrelay-python/0.1.0",
        }

        if headers:
            default_headers.update(headers)

        self._client = httpx.Client(
            base_url=base_url, headers=default_headers, timeout=timeout, **kwargs
        )

        self._base_url = base_url

        # Initialize resource managers
        self.memories = MemoriesResource(self._client, base_url)
        self.agents = AgentsResource(self._client, base_url)
        self.entities = EntitiesResource(self._client, base_url)
        self.extraction = ExtractionResource(self._client, base_url)
        self.icm = IcmResource(self._client, base_url)

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self) -> MemoryRelay:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()
