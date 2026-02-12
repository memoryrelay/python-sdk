"""
Basic usage examples for MemoryRelay Python SDK.
"""

from memoryrelay import MemoryRelay

# Initialize client
client = MemoryRelay(api_key="mem_your_api_key_here")

# Create a memory
memory = client.memories.create(
    content="User prefers dark mode in all applications",
    agent_id="my-agent",
    metadata={"category": "preference", "importance": "high"},
)
print(f"Created memory: {memory.id}")

# Search for memories
results = client.memories.search(
    query="user preferences", agent_id="my-agent", limit=5, min_score=0.7
)

print(f"\nFound {len(results)} relevant memories:")
for result in results:
    print(f"  Score: {result.score:.3f} - {result.memory.content[:50]}...")

# Batch create memories
batch_response = client.memories.create_batch(
    [
        {
            "content": "Meeting scheduled with John on March 1st",
            "agent_id": "my-agent",
            "metadata": {"type": "event"},
        },
        {
            "content": "Project deadline is Q1 2026",
            "agent_id": "my-agent",
            "metadata": {"type": "deadline"},
        },
        {
            "content": "User likes Python and TypeScript",
            "agent_id": "my-agent",
            "metadata": {"type": "preference"},
        },
    ]
)

print(f"\nBatch created {batch_response.succeeded}/{batch_response.total} memories")
print(f"Total time: {batch_response.timing['total_ms']:.0f}ms")
print(f"Embedding time: {batch_response.timing['embedding_ms']:.0f}ms")

# Update a memory
updated = client.memories.update(
    memory_id=memory.id,
    content="User strongly prefers dark mode in all applications",
    metadata={"category": "preference", "importance": "critical"},
)
print(f"\nUpdated memory: {updated.id}")

# List all memories for an agent
all_memories = client.memories.list(agent_id="my-agent", limit=10)
print(f"\nAgent has {len(all_memories)} memories")

# Check API health
health = client.health()
print(f"\nAPI Status: {health.status}")
print(f"Services: {health.services}")

# Clean up
client.memories.delete(memory.id)
print(f"\nDeleted memory: {memory.id}")

# Close client (or use context manager)
client.close()
