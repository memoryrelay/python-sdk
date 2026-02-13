"""Async Entities resource - placeholder."""

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from memoryrelay.async_client import AsyncMemoryRelay


class AsyncEntitiesResource:
    """Async Entities API resource (placeholder)."""

    def __init__(self, client: "AsyncMemoryRelay") -> None:
        self._client = client
