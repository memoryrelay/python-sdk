"""Basic usage examples for MemoryRelay SDK."""

import asyncio

from memoryrelay import (
    AgentCreate,
    AsyncMemoryRelay,
    EntityCreate,
    MemoryCreate,
    MemoryRelay,
    MemorySearchRequest,
)


def sync_example():
    """Synchronous usage example."""
    print("=== Synchronous Example ===\n")

    # Initialize client (uses MEMORYRELAY_API_KEY env var)
    client = MemoryRelay(api_key="your-api-key-here")

    try:
        # 1. Create an agent
        print("Creating agent...")
        agent = client.agents.create(
            AgentCreate(
                name="DemoAgent",
                description="A demo agent for testing",
                metadata={"version": "1.0"},
            )
        )
        print(f"✓ Created agent: {agent.id}\n")

        # 2. Store some memories
        print("Storing memories...")
        memories = [
            "The user prefers Python over JavaScript",
            "The user works in machine learning",
            "The user likes detailed technical explanations",
        ]

        for content in memories:
            client.memories.create(
                MemoryCreate(agent_id=agent.id, content=content, metadata={"source": "demo"})
            )
            print(f"✓ Stored: {content}")

        print()

        # 3. Search memories
        print("Searching memories...")
        results = client.memories.search(
            MemorySearchRequest(
                agent_id=agent.id,
                query="What programming languages does the user know?",
                limit=3,
                threshold=0.5,
            )
        )

        print(f"Found {len(results)} relevant memories:\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. [{result.similarity:.2f}] {result.memory.content}")

        print()

        # 4. Create an entity
        print("Creating entity...")
        entity = client.entities.create(
            EntityCreate(
                agent_id=agent.id,
                name="Python",
                entity_type="technology",
                properties={"category": "programming_language", "paradigm": "multi-paradigm"},
            )
        )
        print(f"✓ Created entity: {entity.name} ({entity.id})\n")

        # 5. List all resources
        print("Listing all agents...")
        agents = client.agents.list()
        print(f"Total agents: {agents.total}\n")

        print("Listing memories for agent...")
        memory_list = client.memories.list(agent_id=agent.id, limit=10)
        print(f"Total memories: {memory_list.total}\n")

        # 6. Cleanup (optional)
        print("Cleaning up...")
        client.agents.delete(agent.id)
        print("✓ Deleted agent\n")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()


async def async_example():
    """Asynchronous usage example."""
    print("=== Asynchronous Example ===\n")

    async with AsyncMemoryRelay(api_key="your-api-key-here") as client:
        try:
            # Create agent
            print("Creating agent...")
            agent = await client.agents.create(AgentCreate(name="AsyncDemoAgent"))
            print(f"✓ Created agent: {agent.id}\n")

            # Store memories concurrently
            print("Storing memories concurrently...")
            memory_tasks = [
                client.memories.create(
                    MemoryCreate(agent_id=agent.id, content=f"Async memory #{i}")
                )
                for i in range(1, 4)
            ]

            memories = await asyncio.gather(*memory_tasks)
            print(f"✓ Stored {len(memories)} memories\n")

            # Search
            print("Searching...")
            results = await client.memories.search(
                MemorySearchRequest(agent_id=agent.id, query="async", limit=5)
            )
            print(f"Found {len(results)} results\n")

            # Cleanup
            await client.agents.delete(agent.id)
            print("✓ Cleaned up\n")

        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Run examples."""
    print("\n" + "=" * 50)
    print("MemoryRelay SDK Examples")
    print("=" * 50 + "\n")

    # Run sync example
    sync_example()

    print("\n" + "-" * 50 + "\n")

    # Run async example
    asyncio.run(async_example())

    print("=" * 50)
    print("Examples completed!")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
