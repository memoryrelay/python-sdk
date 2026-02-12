"""
Tests for Memories resource operations.
"""

import httpx
import pytest
import respx

from memoryrelay import MemoryRelay
from memoryrelay.exceptions import NotFoundError, ValidationError


@respx.mock
def test_create_memory():
    """Test creating a memory."""
    client = MemoryRelay(api_key="test_key")

    respx.post("https://api.memoryrelay.net/v1/memories").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": "mem_abc123",
                "content": "User prefers dark mode",
                "agent_id": "test-agent",
                "user_id": None,
                "metadata": {"category": "preference"},
                "embedding": None,
                "created_at": "2026-02-12T23:00:00Z",
                "updated_at": "2026-02-12T23:00:00Z",
            },
        )
    )

    memory = client.memories.create(
        content="User prefers dark mode", agent_id="test-agent", metadata={"category": "preference"}
    )

    assert memory.id == "mem_abc123"
    assert memory.content == "User prefers dark mode"
    assert memory.agent_id == "test-agent"
    assert memory.metadata == {"category": "preference"}


def test_create_memory_empty_content():
    """Test creating memory with empty content raises ValidationError."""
    client = MemoryRelay(api_key="test_key")

    with pytest.raises(ValidationError) as exc_info:
        client.memories.create(content="", agent_id="test-agent")

    assert "cannot be empty" in exc_info.value.message


def test_create_memory_whitespace_content():
    """Test creating memory with only whitespace raises ValidationError."""
    client = MemoryRelay(api_key="test_key")

    with pytest.raises(ValidationError) as exc_info:
        client.memories.create(content="   \n\t  ", agent_id="test-agent")

    assert "cannot be empty" in exc_info.value.message


def test_create_memory_too_long():
    """Test creating memory exceeding max length raises ValidationError."""
    client = MemoryRelay(api_key="test_key")

    long_content = "x" * 50001

    with pytest.raises(ValidationError) as exc_info:
        client.memories.create(content=long_content, agent_id="test-agent")

    assert "exceeds maximum length" in exc_info.value.message
    assert "50001" in exc_info.value.message


def test_create_memory_empty_agent_id():
    """Test creating memory with empty agent_id raises ValidationError."""
    client = MemoryRelay(api_key="test_key")

    with pytest.raises(ValidationError) as exc_info:
        client.memories.create(content="test", agent_id="")

    assert "agent_id cannot be empty" in exc_info.value.message


@respx.mock
def test_get_memory():
    """Test retrieving a memory by ID."""
    client = MemoryRelay(api_key="test_key")

    respx.get("https://api.memoryrelay.net/v1/memories/mem_123").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": "mem_123",
                "content": "Test memory",
                "agent_id": "test-agent",
                "user_id": None,
                "metadata": None,
                "embedding": None,
                "created_at": "2026-02-12T23:00:00Z",
                "updated_at": "2026-02-12T23:00:00Z",
            },
        )
    )

    memory = client.memories.get("mem_123")

    assert memory.id == "mem_123"
    assert memory.content == "Test memory"


@respx.mock
def test_get_memory_not_found():
    """Test getting non-existent memory raises NotFoundError."""
    client = MemoryRelay(api_key="test_key")

    respx.get("https://api.memoryrelay.net/v1/memories/nonexistent").mock(
        return_value=httpx.Response(404, json={"error": {"message": "Memory not found"}})
    )

    with pytest.raises(NotFoundError):
        client.memories.get("nonexistent")


@respx.mock
def test_update_memory():
    """Test updating a memory."""
    client = MemoryRelay(api_key="test_key")

    respx.put("https://api.memoryrelay.net/v1/memories/mem_123").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": "mem_123",
                "content": "Updated content",
                "agent_id": "test-agent",
                "user_id": None,
                "metadata": {"updated": True},
                "embedding": None,
                "created_at": "2026-02-12T23:00:00Z",
                "updated_at": "2026-02-12T23:05:00Z",
            },
        )
    )

    memory = client.memories.update(
        "mem_123", content="Updated content", metadata={"updated": True}
    )

    assert memory.id == "mem_123"
    assert memory.content == "Updated content"
    assert memory.metadata == {"updated": True}


def test_update_memory_empty_content():
    """Test updating with empty content raises ValidationError."""
    client = MemoryRelay(api_key="test_key")

    with pytest.raises(ValidationError) as exc_info:
        client.memories.update("mem_123", content="")

    assert "cannot be empty" in exc_info.value.message


def test_update_memory_too_long():
    """Test updating with content too long raises ValidationError."""
    client = MemoryRelay(api_key="test_key")

    long_content = "x" * 50001

    with pytest.raises(ValidationError) as exc_info:
        client.memories.update("mem_123", content=long_content)

    assert "exceeds maximum length" in exc_info.value.message


@respx.mock
def test_delete_memory():
    """Test deleting a memory."""
    client = MemoryRelay(api_key="test_key")

    respx.delete("https://api.memoryrelay.net/v1/memories/mem_123").mock(
        return_value=httpx.Response(204)
    )

    # Should not raise
    client.memories.delete("mem_123")


@respx.mock
def test_list_memories():
    """Test listing memories."""
    client = MemoryRelay(api_key="test_key")

    respx.get("https://api.memoryrelay.net/v1/memories").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": [
                    {
                        "id": "mem_1",
                        "content": "Memory 1",
                        "agent_id": "test-agent",
                        "user_id": None,
                        "metadata": None,
                        "embedding": None,
                        "created_at": "2026-02-12T23:00:00Z",
                        "updated_at": "2026-02-12T23:00:00Z",
                    },
                    {
                        "id": "mem_2",
                        "content": "Memory 2",
                        "agent_id": "test-agent",
                        "user_id": None,
                        "metadata": None,
                        "embedding": None,
                        "created_at": "2026-02-12T23:01:00Z",
                        "updated_at": "2026-02-12T23:01:00Z",
                    },
                ]
            },
        )
    )

    memories = client.memories.list(agent_id="test-agent", limit=10)

    assert len(memories) == 2
    assert memories[0].id == "mem_1"
    assert memories[1].id == "mem_2"


@respx.mock
def test_search_memories():
    """Test searching memories."""
    client = MemoryRelay(api_key="test_key")

    respx.post("https://api.memoryrelay.net/v1/memories/search").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": [
                    {
                        "memory": {
                            "id": "mem_1",
                            "content": "User likes Python",
                            "agent_id": "test-agent",
                            "user_id": None,
                            "metadata": None,
                            "embedding": None,
                            "created_at": "2026-02-12T23:00:00Z",
                            "updated_at": "2026-02-12T23:00:00Z",
                        },
                        "score": 0.95,
                        "distance": 0.05,
                    },
                    {
                        "memory": {
                            "id": "mem_2",
                            "content": "User prefers TypeScript",
                            "agent_id": "test-agent",
                            "user_id": None,
                            "metadata": None,
                            "embedding": None,
                            "created_at": "2026-02-12T23:01:00Z",
                            "updated_at": "2026-02-12T23:01:00Z",
                        },
                        "score": 0.87,
                        "distance": 0.13,
                    },
                ]
            },
        )
    )

    results = client.memories.search(query="programming languages", agent_id="test-agent", limit=5)

    assert len(results) == 2
    assert results[0].score == 0.95
    assert results[0].memory.content == "User likes Python"
    assert results[1].score == 0.87


@respx.mock
def test_batch_create():
    """Test batch creating memories."""
    client = MemoryRelay(api_key="test_key")

    respx.post("https://api.memoryrelay.net/v1/memories/batch").mock(
        return_value=httpx.Response(
            200,
            json={
                "success": True,
                "total": 3,
                "succeeded": 3,
                "failed": 0,
                "skipped": 0,
                "results": [
                    {"status": "success", "memory_id": "mem_1", "error": None},
                    {"status": "success", "memory_id": "mem_2", "error": None},
                    {"status": "success", "memory_id": "mem_3", "error": None},
                ],
                "timing": {
                    "total_ms": 99.5,
                    "embedding_ms": 55.6,
                    "database_ms": 43.3,
                    "per_memory_avg_ms": 33.2,
                },
            },
        )
    )

    response = client.memories.create_batch(
        [
            {"content": "Memory 1", "agent_id": "test-agent"},
            {"content": "Memory 2", "agent_id": "test-agent"},
            {"content": "Memory 3", "agent_id": "test-agent"},
        ]
    )

    assert response.success is True
    assert response.total == 3
    assert response.succeeded == 3
    assert response.failed == 0
    assert len(response.results) == 3
    assert response.timing["total_ms"] == 99.5


def test_batch_create_invalid_item():
    """Test batch create with invalid item raises ValidationError."""
    client = MemoryRelay(api_key="test_key")

    with pytest.raises(Exception):  # Pydantic ValidationError
        client.memories.create_batch(
            [
                {"content": "Valid memory", "agent_id": "test"},
                {"agent_id": "test"},  # Missing content - Pydantic will catch
            ]
        )
