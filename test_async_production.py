"""
Test async Python SDK against production MemoryRelay API.
"""

import asyncio
from datetime import datetime, UTC

from memoryrelay import AsyncMemoryRelay


async def test_async_production():
    """Test async SDK against production API."""
    print("=" * 70)
    print("MemoryRelay Async Python SDK - Production API Test")
    print("=" * 70)
    print()
    
    api_key = "mem_prod_e0affdcce0f3859b2ee691f6cfd73ff2"
    api_url = "https://api.memoryrelay.net"
    
    async with AsyncMemoryRelay(api_key=api_key, base_url=api_url) as client:
        # Test health
        print("1. Testing async health check...")
        health = await client.health()
        print(f"   ✅ Status: {health.status}")
        print()
        
        # Test create
        print("2. Testing async create...")
        test_content = f"Async SDK test at {datetime.now(UTC).isoformat()}"
        memory = await client.memories.create(
            content=test_content,
            agent_id="iris",
            metadata={"async": True, "test": True}
        )
        print(f"   ✅ Created: {memory.id}")
        print()
        
        # Test search
        print("3. Testing async search...")
        results = await client.memories.search(query="async SDK", agent_id="iris", limit=3)
        print(f"   ✅ Found {len(results)} results")
        print()
        
        # Test batch
        print("4. Testing async batch create...")
        batch_response = await client.memories.create_batch([
            {"content": f"Async batch 1 at {datetime.now(UTC).isoformat()}", "agent_id": "iris"},
            {"content": f"Async batch 2 at {datetime.now(UTC).isoformat()}", "agent_id": "iris"},
            {"content": f"Async batch 3 at {datetime.now(UTC).isoformat()}", "agent_id": "iris"}
        ])
        print(f"   ✅ Batch: {batch_response.succeeded}/3 succeeded")
        print(f"   ✅ Timing: {batch_response.timing['total_ms']:.1f}ms")
        print()
        
        # Cleanup
        print("5. Cleaning up...")
        await client.memories.delete(memory.id)
        for result in batch_response.results:
            if result.memory_id:
                await client.memories.delete(result.memory_id)
        print(f"   ✅ Deleted {1 + batch_response.succeeded} test memories")
        print()
    
    print("=" * 70)
    print("✅ Async SDK working correctly!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_async_production())
