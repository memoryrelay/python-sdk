"""
Example: Using MemoryRelay v2 Async API

Demonstrates the three main patterns for using v2's async memory creation:
1. Fire-and-forget (fastest, no waiting)
2. Poll until ready (drop-in v1 replacement)
3. Create and wait (convenience helper)
"""

import os
import time
from memoryrelay import MemoryRelay

# Get API key from environment
API_KEY = os.getenv("MEMORYRELAY_API_KEY", "mem_prod_...")

# Initialize client
client = MemoryRelay(api_key=API_KEY)

print("=" * 60)
print("MemoryRelay v2 Async API Examples")
print("=" * 60)

# ── Example 1: Fire-and-Forget (Fastest) ────────────────────────

print("\n1. Fire-and-Forget (fastest, no waiting)")
print("-" * 60)

start = time.time()
response = client.memories.create_async(
    content="User prefers dark mode in the UI",
    agent_id="example-agent",
    metadata={"category": "preference", "priority": "high"},
)
elapsed_ms = (time.time() - start) * 1000

print(f"✓ Memory {response.id} queued in {elapsed_ms:.0f}ms")
print(f"  Status: {response.status}")
print(f"  Job ID: {response.job_id}")
print(f"  Est. completion: {response.estimated_completion_seconds}s")
print("\nUse case: Bulk imports, background jobs, non-critical writes")

# ── Example 2: Poll Until Ready (Drop-in v1 Replacement) ────────

print("\n\n2. Poll Until Ready (drop-in v1 replacement)")
print("-" * 60)

start = time.time()
response = client.memories.create_async(
    content="User's favorite color is blue",
    agent_id="example-agent",
    metadata={"category": "preference"},
)
print(f"✓ Memory {response.id} queued in {(time.time() - start) * 1000:.0f}ms")

# Poll status every 0.5s until ready
print("  Polling status...", end="", flush=True)
memory = client.memories.wait_for_ready(response.id, timeout=10, poll_interval=0.5)
elapsed_ms = (time.time() - start) * 1000

print(f" ready in {elapsed_ms:.0f}ms")
print(f"  Memory ID: {memory.id}")
print(f"  Content: {memory.content}")
print(f"  Embedding dims: {len(memory.embedding) if memory.embedding else 0}")
print("\nUse case: Interactive flows, immediate feedback needed")

# ── Example 3: Create and Wait (Convenience Helper) ─────────────

print("\n\n3. Create and Wait (convenience helper)")
print("-" * 60)

start = time.time()
memory = client.memories.create_and_wait(
    content="User timezone is America/New_York",
    agent_id="example-agent",
    metadata={"category": "setting"},
    timeout=10,
)
elapsed_ms = (time.time() - start) * 1000

print(f"✓ Memory {memory.id} ready in {elapsed_ms:.0f}ms")
print(f"  Content: {memory.content}")
print(f"  Created: {memory.created_at}")
print("\nUse case: Same interface as v1, but faster (uses v2 internally)")

# ── Example 4: Search (v2 only returns ready memories) ──────────

print("\n\n4. Search (v2 automatically filters ready memories)")
print("-" * 60)

start = time.time()
results = client.memories.search(
    query="user preferences",
    agent_id="example-agent",
    limit=5,
    min_score=0.5,
)
elapsed_ms = (time.time() - start) * 1000

print(f"✓ Found {len(results)} results in {elapsed_ms:.0f}ms")
for i, result in enumerate(results, 1):
    print(f"  {i}. [{result.score:.2f}] {result.memory.content[:60]}...")

# ── Example 5: Error Handling ────────────────────────────────────

print("\n\n5. Error Handling")
print("-" * 60)

try:
    # Try with very short timeout to trigger TimeoutError
    response = client.memories.create_async(
        content="This will timeout",
        agent_id="example-agent",
    )
    memory = client.memories.wait_for_ready(response.id, timeout=0.1)
except Exception as e:
    print(f"✓ Caught TimeoutError (expected): {e.__class__.__name__}")
    print(f"  Message: {str(e)}")

print("\n" + "=" * 60)
print("Performance Summary")
print("=" * 60)
print("v1 (sync):  2-30s per memory (blocking)")
print("v2 (async): <50ms API response + 2-5s background processing")
print("Speedup:    60-600x faster API response time")
print("=" * 60)
