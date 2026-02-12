# MemoryRelay Python SDK

Official Python client for [MemoryRelay](https://memoryrelay.io) - persistent memory for AI agents.

[![PyPI version](https://img.shields.io/pypi/v/memoryrelay)](https://pypi.org/project/memoryrelay/)
[![Python versions](https://img.shields.io/pypi/pyversions/memoryrelay)](https://pypi.org/project/memoryrelay/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- 🚀 **Simple API** - Intuitive Pythonic interface
- ⚡ **Async/Await Support** - Full async client for high-performance applications
- 🔍 **Semantic Search** - Vector-based memory retrieval
- 📦 **Batch Operations** - Create multiple memories efficiently
- 🏷️ **Entity Tracking** - Automatic relationship management
- 🔐 **Type Safe** - Full Pydantic models and type hints
- 🐍 **Python 3.9+** - Modern Python support
- ✅ **Production Tested** - Verified against live API

## Installation

```bash
pip install memoryrelay
```

## Quick Start

### Sync Client

```python
from memoryrelay import MemoryRelay

# Initialize client
client = MemoryRelay(api_key="mem_your_api_key_here")

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

for result in results:
    print(f"Score: {result.score:.3f}")
    print(f"Content: {result.memory.content}")
```

### Async Client

```python
import asyncio
from memoryrelay import AsyncMemoryRelay

async def main():
    async with AsyncMemoryRelay(api_key="mem_your_api_key_here") as client:
        # Create a memory
        memory = await client.memories.create(
            content="User prefers dark mode",
            agent_id="my-agent"
        )
        
        # Search memories
        results = await client.memories.search(
            query="user preferences",
            limit=5
        )
        
        for result in results:
            print(f"Score: {result.score:.3f}")
            print(f"Content: {result.memory.content}")

asyncio.run(main())
```

## Usage

### Initialize Client

#### Sync Client

```python
from memoryrelay import MemoryRelay

# Basic initialization
client = MemoryRelay(api_key="mem_your_api_key_here")

# With custom configuration
client = MemoryRelay(
    api_key="mem_your_api_key_here",
    base_url="https://api.memoryrelay.net",  # Optional
    timeout=30.0,  # Request timeout in seconds
    max_retries=3  # Max retries for failed requests
)

# Or use context manager (recommended)
with MemoryRelay(api_key="mem_...") as client:
    # Your code here
    pass
```

#### Async Client

```python
from memoryrelay import AsyncMemoryRelay

# Basic initialization
client = AsyncMemoryRelay(api_key="mem_your_api_key_here")

# Use async context manager (recommended)
async with AsyncMemoryRelay(api_key="mem_...") as client:
    # Your async code here
    memory = await client.memories.create(...)
```

### Create Memories

#### Sync

```python
# Create a single memory
memory = client.memories.create(
    content="User completed Python tutorial",
    agent_id="learning-agent",
    metadata={"course": "python-101", "completed": True}
)

# Batch create (faster for multiple memories)
response = client.memories.create_batch([
    {"content": "Memory 1", "agent_id": "agent-1"},
    {"content": "Memory 2", "agent_id": "agent-1"},
    {"content": "Memory 3", "agent_id": "agent-1"}
])

print(f"Created {response.succeeded}/{response.total} memories")
print(f"Took {response.timing['total_ms']:.0f}ms")
```

#### Async

```python
# Create a single memory
memory = await client.memories.create(
    content="User completed Python tutorial",
    agent_id="learning-agent",
    metadata={"course": "python-101", "completed": True}
)

# Batch create (faster for multiple memories)
response = await client.memories.create_batch([
    {"content": "Memory 1", "agent_id": "agent-1"},
    {"content": "Memory 2", "agent_id": "agent-1"},
    {"content": "Memory 3", "agent_id": "agent-1"}
])

print(f"Created {response.succeeded}/{response.total} memories")
print(f"Took {response.timing['total_ms']:.0f}ms")
```

### Search Memories

```python
# Semantic search
results = client.memories.search(
    query="what programming languages does the user know?",
    agent_id="my-agent",
    limit=10,
    min_score=0.7  # Only return results with score >= 0.7
)

# With metadata filtering
results = client.memories.search(
    query="completed courses",
    metadata_filter={"completed": True}
)
```

### Update & Delete

```python
# Update memory
updated = client.memories.update(
    memory_id="mem_abc123",
    content="Updated content",
    metadata={"updated": True}
)

# Delete memory
client.memories.delete(memory_id="mem_abc123")
```

### List Memories

```python
# List all memories for an agent
memories = client.memories.list(
    agent_id="my-agent",
    limit=100,
    offset=0
)

# List with user filter
memories = client.memories.list(
    user_id="user_123",
    limit=50
)
```

### Entity Management

```python
# Create entity
entity = client.entities.create(
    entity_type="person",
    entity_value="John Doe",
    agent_id="my-agent"
)

# Link entity to memory
client.entities.link(
    entity_id=entity.id,
    memory_id=memory.id
)

# List entities
entities = client.entities.list(
    agent_id="my-agent",
    entity_type="person"
)
```

### Health Check

```python
health = client.health()
print(f"API Status: {health.status}")
print(f"Version: {health.version}")
print(f"Services: {health.services}")
```

## Error Handling

```python
from memoryrelay import (
    MemoryRelay,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ValidationError,
    APIError,
)

try:
    memory = client.memories.create(
        content="Test memory",
        agent_id="my-agent"
    )
except AuthenticationError:
    print("Invalid API key")
except RateLimitError as e:
    print(f"Rate limit exceeded. Retry after {e.retry_after}s")
except NotFoundError:
    print("Resource not found")
except ValidationError as e:
    print(f"Invalid request: {e.message}")
except APIError as e:
    print(f"API error: {e.message} (status: {e.status_code})")
```

## Examples

See the [examples/](./examples/) directory for more usage examples:

- [basic_usage.py](./examples/basic_usage.py) - Sync client CRUD operations
- [context_manager.py](./examples/context_manager.py) - Using context managers
- [async_usage.py](./examples/async_usage.py) - Async/await operations

## Development

### Setup

```bash
git clone https://github.com/memoryrelay/python-sdk.git
cd python-sdk
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -e ".[dev]"
```

### Testing

```bash
pytest
pytest --cov=memoryrelay  # With coverage
```

### Code Quality

```bash
black .
ruff check .
mypy memoryrelay
```

## API Reference

Full API documentation available at [memoryrelay.io/docs](https://memoryrelay.io/docs)

## Support

- **Documentation**: [memoryrelay.io/docs](https://memoryrelay.io/docs)
- **GitHub Issues**: [github.com/memoryrelay/python-sdk/issues](https://github.com/memoryrelay/python-sdk/issues)
- **Email**: hello@memoryrelay.io

## License

MIT License - see [LICENSE](./LICENSE) for details.
