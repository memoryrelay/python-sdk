"""
Async usage example for MemoryRelay Python SDK.
"""

import asyncio

from memoryrelay import AsyncMemoryRelay


async def main():
    """Async example."""
    # Use async context manager
    async with AsyncMemoryRelay(api_key="mem_your_api_key_here") as client:
        # Create a memory
        memory = await client.memories.create(
            content="User prefers dark mode in all applications",
            agent_id="my-agent",
            metadata={"category": "preference", "importance": "high"},
        )
        print(f"Created memory: {memory.id}")

        # Search for memories
        results = await client.memories.search(
            query="user preferences", agent_id="my-agent", limit=5, min_score=0.7
        )

        print(f"\nFound {len(results)} relevant memories:")
        for result in results:
            print(f"  Score: {result.score:.3f} - {result.memory.content[:50]}...")

        # Batch create memories
        batch_response = await client.memories.create_batch(
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

        # Clean up
        await client.memories.delete(memory.id)
        print(f"\nDeleted memory: {memory.id}")


if __name__ == "__main__":
    asyncio.run(main())
