"""
Context manager usage for MemoryRelay Python SDK.
"""

from memoryrelay import MemoryRelay

# Use context manager for automatic cleanup
with MemoryRelay(api_key="mem_your_api_key_here") as client:
    # Create memories
    memory = client.memories.create(
        content="Important project deadline coming up",
        agent_id="task-agent"
    )
    
    # Search
    results = client.memories.search(
        query="deadlines",
        agent_id="task-agent"
    )
    
    print(f"Found {len(results)} memories about deadlines")
    
    # Client will automatically close when exiting context
