# MemoryRelay Python SDK

Official Python client for MemoryRelay API.

## Installation

```bash
pip install memoryrelay
```

## Quick Start

```python
from memoryrelay import MemoryRelay

client = MemoryRelay(api_key="mem_...")

# Create a memory
memory = client.memories.create(
    content="User prefers dark mode",
    agent_id="my-agent"
)

# Search memories
results = client.memories.search(
    query="user preferences",
    limit=5
)

# Batch create
client.memories.create_batch([
    {"content": "Memory 1"},
    {"content": "Memory 2"},
    {"content": "Memory 3"}
])
```

## Documentation

Full documentation at [memoryrelay.io/docs](https://memoryrelay.io/docs)

## License

MIT
