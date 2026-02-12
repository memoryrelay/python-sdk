"""Async Agents resource - placeholder."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from memoryrelay.async_client import AsyncMemoryRelay


class AsyncAgentsResource:
    """Async Agents API resource (placeholder)."""
    
    def __init__(self, client: "AsyncMemoryRelay") -> None:
        self._client = client
