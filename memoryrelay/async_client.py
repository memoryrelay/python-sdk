"""Asynchronous MemoryRelay client."""

from __future__ import annotations

from typing import Any

import httpx

from .exceptions import AuthenticationError
from .resources.agents import AsyncAgentsResource
from .resources.entities import AsyncEntitiesResource
from .resources.extraction import AsyncExtractionResource
from .resources.icm import AsyncIcmResource
from .resources.memories import AsyncMemoriesResource


class AsyncMemoryRelay:
    """Asynchronous client for the MemoryRelay API.

    Example:
        >>> async with AsyncMemoryRelay(api_key="your-api-key") as client:
        ...     agent = await client.agents.create(name="MyAgent")
        ...     memory = await client.memories.create(
        ...         agent_id=agent.id,
        ...         content="Important information"
        ...     )
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://api.memoryrelay.net",
        timeout: float = 30.0,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ):
        """Initialize the AsyncMemoryRelay client.

        Args:
            api_key: API key for authentication. Can also be set via MEMORYRELAY_API_KEY env var.
            base_url: Base URL for the API (default: https://api.memoryrelay.net)
            timeout: Request timeout in seconds (default: 30.0)
            headers: Additional headers to include in requests
            **kwargs: Additional arguments passed to httpx.AsyncClient

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

        self._client = httpx.AsyncClient(
            base_url=base_url, headers=default_headers, timeout=timeout, **kwargs
        )

        self._base_url = base_url

        # Initialize resource managers
        self.memories = AsyncMemoriesResource(self._client, base_url)
        self.agents = AsyncAgentsResource(self._client, base_url)
        self.entities = AsyncEntitiesResource(self._client, base_url)
        self.extraction = AsyncExtractionResource(self._client, base_url)
        self.icm = AsyncIcmResource(self._client, base_url)

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> AsyncMemoryRelay:
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()
