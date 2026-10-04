"""Examples for V2 Async API and BYOK Toggle features."""

import asyncio

from memoryrelay import (
    AsyncMemoryRelay,
    ByokKeyCreate,
    MemoryCreate,
)


async def v2_async_example():
    """Example: Using V2 async API for fast memory creation."""

    async with AsyncMemoryRelay(api_key="your-api-key") as client:
        # Create memory with async processing (V2 API)
        # Returns immediately (< 50ms) while embedding + extraction happen in background
        response = await client.memories.create_async(
            MemoryCreate(
                agent_id="my-agent",
                content="User prefers dark mode and san-serif fonts",
                metadata={"source": "preferences"},
            )
        )

        print(f"Memory ID: {response.id}")
        print(f"Status: {response.status}")
        print(f"Job ID: {response.job_id}")
        print(f"Estimated completion: {response.estimated_completion_seconds}s")

        # Option 1: Wait for memory to be ready (polling)
        print("\nWaiting for memory to be ready...")
        memory = await client.memories.wait_until_ready(
            response.id, poll_interval=0.5, timeout=30.0  # Poll every 500ms  # Max wait 30s
        )

        print("✅ Memory ready!")
        print(f"  Embedding dimensions: {len(memory.embedding) if memory.embedding else 0}")
        print(f"  Extraction method: {memory.extraction_method}")

        # Option 2: Manual status polling
        status = await client.memories.get_status(response.id)
        print("\nStatus check:")
        print(f"  Overall: {status.status}")
        print(f"  Embedding: {status.embedding_status}")
        print(f"  Extraction: {status.extraction_status}")
        print(f"  Progress: {status.progress}")


async def byok_toggle_example():
    """Example: Managing BYOK keys and toggling extraction method."""

    async with AsyncMemoryRelay(api_key="your-api-key") as client:
        # Check current extraction settings
        settings = await client.extraction.get_settings()

        print(f"Current extraction method: {settings.extractor}")
        print(f"Subscription tier: {settings.tier}")
        print(f"BYOK enabled: {settings.byok_enabled_globally}")
        print(f"BYOK active: {settings.byok_active}")
        print(f"Configured keys: {len(settings.keys)}")

        # Add a new BYOK key
        if settings.byok_enabled_globally:
            print("\n--- Adding BYOK Key ---")

            key = await client.extraction.create_key(
                ByokKeyCreate(
                    provider="openai", api_key="sk-proj-...", model="gpt-4o", label="My OpenAI Key"
                )
            )

            print(f"✅ Key added: {key.id}")
            print(f"  Provider: {key.provider}")
            print(f"  Model: {key.model}")
            print(f"  Masked key: {key.masked_key}")
            print(f"  Active: {key.is_active}")

            # Key is automatically active after creation (if first key)
            # Now using BYOK extraction

            # Create a memory using BYOK extraction
            response = await client.memories.create_async(
                MemoryCreate(agent_id="my-agent", content="Important business data")
            )
            memory = await client.memories.wait_until_ready(response.id)
            print(f"\nMemory extracted with: {memory.extraction_method}")

            # Toggle to free extraction (GLiNER)
            print("\n--- Switching to Free Extraction ---")

            result = await client.extraction.deactivate_all_keys()
            print(f"✅ {result['message']}")
            print(f"  Deactivated: {result['deactivated_count']} key(s)")

            # Verify extraction method changed
            settings = await client.extraction.get_settings()
            print(f"  Current extractor: {settings.extractor}")  # Should be "gliner"

            # Create a memory using free extraction
            response = await client.memories.create_async(
                MemoryCreate(agent_id="my-agent", content="Testing free extraction")
            )
            memory = await client.memories.wait_until_ready(response.id)
            print(f"\nMemory extracted with: {memory.extraction_method}")

            # Re-activate BYOK key
            print("\n--- Re-activating BYOK ---")

            activated_key = await client.extraction.activate_key(key.id)
            print(f"✅ Key reactivated: {activated_key.id}")
            print(f"  Provider: {activated_key.provider}")
            print(f"  Model: {activated_key.model}")

            # Now back to using BYOK extraction


async def batch_async_example():
    """Example: Create many memories in parallel with V2 async API."""

    async with AsyncMemoryRelay(api_key="your-api-key") as client:
        # Create 100 memories in parallel
        memories_to_create = [
            MemoryCreate(
                agent_id="my-agent", content=f"Important fact number {i}", metadata={"index": i}
            )
            for i in range(100)
        ]

        print(f"Creating {len(memories_to_create)} memories...")

        # Create all memories (returns immediately)
        responses = await asyncio.gather(
            *[client.memories.create_async(mem) for mem in memories_to_create]
        )

        print(f"✅ {len(responses)} memories queued for processing")

        # Wait for all to be ready
        print("Waiting for all memories to be ready...")

        memories = await asyncio.gather(
            *[client.memories.wait_until_ready(response.id, timeout=60.0) for response in responses]
        )

        print(f"✅ All {len(memories)} memories ready!")
        print(
            f"  Average embedding dimensions: {sum(len(m.embedding or []) for m in memories) / len(memories):.0f}"
        )


async def main():
    """Run all examples."""

    print("=" * 60)
    print("V2 Async API Example")
    print("=" * 60)
    await v2_async_example()

    print("\n" + "=" * 60)
    print("BYOK Toggle Example")
    print("=" * 60)
    await byok_toggle_example()

    print("\n" + "=" * 60)
    print("Batch Async Example")
    print("=" * 60)
    await batch_async_example()


if __name__ == "__main__":
    asyncio.run(main())
