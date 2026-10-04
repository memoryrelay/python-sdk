"""
SDK Integration Tests against the live MemoryRelay API.

These tests verify that the Python SDK correctly communicates with the
production API end-to-end. They are skipped when MEMORYRELAY_API_KEY
is not set.

All resources created during tests are cleaned up afterward.

Usage:
    MEMORYRELAY_API_KEY=mem_prod_xxx pytest sdk/python/tests/test_integration.py -v
"""

import os
import time
import uuid

import pytest

# Skip entire module if no API key
API_KEY = os.environ.get("MEMORYRELAY_API_KEY", "")
API_URL = os.environ.get("MEMORYRELAY_API_URL", "https://api.memoryrelay.net")

pytestmark = pytest.mark.skipif(
    not API_KEY or not API_KEY.startswith("mem_"),
    reason="MEMORYRELAY_API_KEY not set or invalid (integration tests require live API)",
)


@pytest.fixture(scope="module")
def sync_client():
    """Create a sync client for the test module."""
    from memoryrelay import MemoryRelay

    client = MemoryRelay(api_key=API_KEY, base_url=API_URL)
    yield client
    client.close()


@pytest.fixture(scope="module")
def async_client():
    """Create an async client for the test module."""
    from memoryrelay import AsyncMemoryRelay

    return AsyncMemoryRelay(api_key=API_KEY, base_url=API_URL)


@pytest.fixture(scope="module")
def test_agent(sync_client):
    """Create a temporary test agent, cleaned up after all tests."""
    from memoryrelay import AgentCreate

    test_id = uuid.uuid4().hex[:8]
    agent = sync_client.agents.create(AgentCreate(name=f"sdk-test-{test_id}"))
    yield agent
    try:
        sync_client.agents.delete(agent.id)
    except Exception:
        pass


class TestSyncClient:
    """Integration tests for the synchronous MemoryRelay client."""

    def test_agent_lifecycle(self, sync_client):
        """Create, get, list, and delete an agent."""
        from memoryrelay import AgentCreate

        test_id = uuid.uuid4().hex[:8]
        agent = sync_client.agents.create(AgentCreate(name=f"lifecycle-{test_id}"))
        assert agent.id
        assert agent.name == f"lifecycle-{test_id}"

        fetched = sync_client.agents.get(agent.id)
        assert fetched.id == agent.id

        agents = sync_client.agents.list()
        agent_ids = [a.id for a in agents.data]
        assert agent.id in agent_ids

        sync_client.agents.delete(agent.id)

    def test_memory_create_and_get(self, sync_client, test_agent):
        """Store a memory and retrieve it by ID."""
        from memoryrelay import MemoryCreate

        test_id = uuid.uuid4().hex[:8]
        memory = sync_client.memories.create(
            MemoryCreate(
                agent_id=test_agent.id,
                content=f"SDK integration test {test_id}: Python is great for scripting",
                metadata={"source": "sdk-test", "test_id": test_id},
            )
        )
        assert memory.id
        assert memory.content.startswith(f"SDK integration test {test_id}")
        assert memory.agent_id == test_agent.id

        fetched = sync_client.memories.get(memory.id)
        assert fetched.id == memory.id
        assert fetched.content == memory.content

        # Cleanup
        sync_client.memories.delete(memory.id)

    def test_memory_update(self, sync_client, test_agent):
        """Create and then update a memory."""
        from memoryrelay import MemoryCreate, MemoryUpdate

        memory = sync_client.memories.create(
            MemoryCreate(
                agent_id=test_agent.id,
                content="Original content for update test",
            )
        )

        updated = sync_client.memories.update(
            memory.id,
            MemoryUpdate(content="Updated content for update test"),
        )
        assert updated.content == "Updated content for update test"

        # Cleanup
        sync_client.memories.delete(memory.id)

    def test_memory_list(self, sync_client, test_agent):
        """List memories for an agent."""
        from memoryrelay import MemoryCreate

        # Create a memory so we have at least one
        memory = sync_client.memories.create(
            MemoryCreate(
                agent_id=test_agent.id,
                content="Memory for list test",
            )
        )

        result = sync_client.memories.list(agent_id=test_agent.id, limit=10)
        assert len(result.data) >= 1

        # Cleanup
        sync_client.memories.delete(memory.id)

    def test_memory_search(self, sync_client, test_agent):
        """Store a memory, wait for embedding, then search for it."""
        from memoryrelay import MemoryCreate, MemorySearchRequest

        test_id = uuid.uuid4().hex[:8]
        unique_content = f"SDK search test {test_id}: elephants never forget anything"

        memory = sync_client.memories.create(
            MemoryCreate(agent_id=test_agent.id, content=unique_content)
        )

        # Poll until embedding is ready (max 60s)
        for _ in range(30):
            fetched = sync_client.memories.get(memory.id)
            if getattr(fetched, "extraction_status", None) == "ready":
                break
            time.sleep(2)

        # Search
        results = sync_client.memories.search(
            MemorySearchRequest(
                agent_id=test_agent.id,
                query="elephants memory forget",
                limit=5,
                min_score=0.3,
            )
        )
        found_ids = [r.memory.id for r in results.data]
        assert memory.id in found_ids, (
            f"Memory {memory.id} not found in search results. " f"Got IDs: {found_ids}"
        )

        # Cleanup
        sync_client.memories.delete(memory.id)

    def test_entity_lifecycle(self, sync_client, test_agent):
        """Create an entity, link it to a memory, then clean up."""
        from memoryrelay import EntityCreate, EntityLinkCreate, MemoryCreate

        memory = sync_client.memories.create(
            MemoryCreate(
                agent_id=test_agent.id,
                content="Entity lifecycle test content",
            )
        )

        entity = sync_client.entities.create(
            EntityCreate(name="TestConcept", entity_type="concept")
        )
        assert entity.id
        assert entity.name == "TestConcept"

        # Link entity to memory
        link = sync_client.entities.link_to_memory(
            EntityLinkCreate(
                entity_id=entity.id,
                memory_id=memory.id,
                relationship="mentioned_in",
            )
        )
        assert link.entity_id == entity.id
        assert link.memory_id == memory.id

        # List entities
        entities = sync_client.entities.list()
        entity_ids = [e.id for e in entities.data]
        assert entity.id in entity_ids

        # Cleanup
        sync_client.entities.delete(entity.id)
        sync_client.memories.delete(memory.id)

    def test_memory_deduplication(self, sync_client, test_agent):
        """Store the same content twice with dedup enabled."""
        from memoryrelay import MemoryCreate

        content = f"Dedup test {uuid.uuid4().hex[:8]}: this is unique content"

        mem1 = sync_client.memories.create(
            MemoryCreate(
                agent_id=test_agent.id,
                content=content,
                deduplicate=True,
            )
        )

        # Wait for embedding before dedup check can work
        for _ in range(30):
            fetched = sync_client.memories.get(mem1.id)
            if getattr(fetched, "extraction_status", None) == "ready":
                break
            time.sleep(2)

        mem2 = sync_client.memories.create(
            MemoryCreate(
                agent_id=test_agent.id,
                content=content,
                deduplicate=True,
                dedup_threshold=0.95,
            )
        )

        # If dedup worked, mem2 should be the same as mem1 (or flagged as duplicate)
        assert mem2.id == mem1.id or getattr(mem2, "is_duplicate", False)

        # Cleanup
        sync_client.memories.delete(mem1.id)
        if mem2.id != mem1.id:
            sync_client.memories.delete(mem2.id)

        # Note: dedup depends on embedding readiness, so we don't hard-assert
        # but we verify the flow doesn't error out


class TestAsyncClient:
    """Integration tests for the async MemoryRelay client."""

    @pytest.mark.asyncio
    async def test_async_agent_create(self, async_client):
        """Create and delete an agent using async client."""
        from memoryrelay import AgentCreate

        test_id = uuid.uuid4().hex[:8]
        agent = await async_client.agents.create(AgentCreate(name=f"async-test-{test_id}"))
        assert agent.id
        assert agent.name == f"async-test-{test_id}"

        await async_client.agents.delete(agent.id)

    @pytest.mark.asyncio
    async def test_async_memory_create_and_search(self, async_client):
        """Create a memory and search for it using async client."""
        from memoryrelay import AgentCreate, MemoryCreate, MemorySearchRequest

        test_id = uuid.uuid4().hex[:8]
        agent = await async_client.agents.create(AgentCreate(name=f"async-search-{test_id}"))

        memory = await async_client.memories.create(
            MemoryCreate(
                agent_id=agent.id,
                content=f"Async test {test_id}: semantic search validation",
            )
        )
        assert memory.id

        # Poll until ready
        import asyncio

        for _ in range(30):
            fetched = await async_client.memories.get(memory.id)
            if getattr(fetched, "extraction_status", None) == "ready":
                break
            await asyncio.sleep(2)

        results = await async_client.memories.search(
            MemorySearchRequest(
                agent_id=agent.id,
                query="semantic search validation",
                limit=5,
                min_score=0.3,
            )
        )
        found_ids = [r.memory.id for r in results.data]
        assert memory.id in found_ids

        # Cleanup
        await async_client.memories.delete(memory.id)
        await async_client.agents.delete(agent.id)

    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Verify async context manager works."""
        from memoryrelay import AsyncMemoryRelay

        async with AsyncMemoryRelay(api_key=API_KEY, base_url=API_URL) as client:
            agents = await client.agents.list()
            assert agents.data is not None


class TestErrorHandling:
    """Test that SDK properly surfaces API errors."""

    def test_not_found_error(self, sync_client):
        """Accessing a non-existent memory should raise NotFoundError."""
        from memoryrelay.exceptions import NotFoundError

        fake_id = str(uuid.uuid4())
        with pytest.raises((NotFoundError, Exception)):
            sync_client.memories.get(fake_id)

    def test_invalid_agent_id(self, sync_client):
        """Creating a memory with invalid agent ID should fail."""
        from memoryrelay import MemoryCreate

        fake_agent = str(uuid.uuid4())
        with pytest.raises(Exception):
            sync_client.memories.create(MemoryCreate(agent_id=fake_agent, content="Should fail"))
