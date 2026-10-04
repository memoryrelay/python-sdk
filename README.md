# MemoryRelay Python SDK

Official Python client for the [MemoryRelay](https://memoryrelay.ai) API - A scalable memory management system for AI agents.

## Installation

```bash
pip install memoryrelay
```

## Quick Start

### Synchronous Client

```python
from memoryrelay import MemoryRelay, MemoryCreate, AgentCreate

# Initialize client
client = MemoryRelay(api_key="your-api-key")

# Create an agent
agent = client.agents.create(
    AgentCreate(
        name="MyAgent",
        description="A helpful assistant"
    )
)

# Store a memory
memory = client.memories.create(
    MemoryCreate(
        agent_id=agent.id,
        content="The user prefers technical explanations",
        metadata={"category": "preferences"}
    )
)

# Search memories
from memoryrelay import MemorySearchRequest

results = client.memories.search(
    MemorySearchRequest(
        agent_id=agent.id,
        query="How does the user like explanations?",
        limit=5
    )
)

for result in results:
    print(f"Score: {result.similarity}")
    print(f"Content: {result.memory.content}\n")
```

### Asynchronous Client

```python
import asyncio
from memoryrelay import AsyncMemoryRelay, MemoryCreate, AgentCreate

async def main():
    async with AsyncMemoryRelay(api_key="your-api-key") as client:
        # Create an agent
        agent = await client.agents.create(
            AgentCreate(name="AsyncAgent")
        )
        
        # Store a memory
        memory = await client.memories.create(
            MemoryCreate(
                agent_id=agent.id,
                content="Important information"
            )
        )
        
        # List memories
        memories = await client.memories.list(agent_id=agent.id)
        print(f"Total memories: {memories.total}")

asyncio.run(main())
```

## Features

✅ **ICM workspaces** - pinned, versioned context: builds, receipts, drafts, Git sources (`client.icm`)  
✅ **Fully typed** - Complete type hints for better IDE support  
✅ **Sync & Async** - Choose the client that fits your needs  
✅ **Pydantic models** - Validated request/response objects  
✅ **Error handling** - Custom exceptions for different error types  
✅ **Context managers** - Automatic resource cleanup  
✅ **Production ready** - Works with https://api.memoryrelay.net

## Authentication

Set your API key via environment variable:

```bash
export MEMORYRELAY_API_KEY="your-api-key"
```

Or pass it directly:

```python
client = MemoryRelay(api_key="your-api-key")
```

## Core Resources

### Memories

```python
# Create
memory = client.memories.create(
    MemoryCreate(
        agent_id="agent-123",
        content="User loves Python",
        metadata={"source": "conversation"}
    )
)

# List with filtering
memories = client.memories.list(
    agent_id="agent-123",
    limit=50,
    offset=0
)

# Get by ID
memory = client.memories.get("memory-id")

# Update
from memoryrelay import MemoryUpdate
updated = client.memories.update(
    "memory-id",
    MemoryUpdate(content="Updated content")
)

# Delete
client.memories.delete("memory-id")

# Semantic search
from memoryrelay import MemorySearchRequest
results = client.memories.search(
    MemorySearchRequest(
        agent_id="agent-123",
        query="What does the user like?",
        limit=10,
        threshold=0.7
    )
)
```

### Agents

```python
# Create
agent = client.agents.create(
    AgentCreate(
        name="CustomerSupport",
        description="Handles customer queries",
        metadata={"team": "support"}
    )
)

# List all
agents = client.agents.list()

# Get by ID
agent = client.agents.get("agent-id")

# Delete
client.agents.delete("agent-id")
```

### Entities

```python
# Create
entity = client.entities.create(
    EntityCreate(
        agent_id="agent-123",
        name="John Doe",
        entity_type="person",
        properties={"email": "john@example.com"}
    )
)

# List with filtering
entities = client.entities.list(agent_id="agent-123")

# Get by ID
entity = client.entities.get("entity-id")

# Delete
client.entities.delete("entity-id")
```

### ICM workspaces

ICM workspaces are pinned, versioned context an agent walks like a folder. The
`icm` resource covers `/v2/icm`: capabilities, workspaces, releases, context
builds for any target (a route, a stage, or a repository the workspace includes),
receipts, the key's root (its repositories and the route bound to each step),
Git sources and drafts. Against a server without ICM every call raises
`IcmUnsupportedError`.

```python
from memoryrelay import MemoryRelay

client = MemoryRelay(api_key="mem_prod_...")

caps = client.icm.capabilities()          # supported, build_targets, principal
root = client.icm.root(step="fix")        # the repositories this key can build for

workspaces = client.icm.list_workspaces()
ws = workspaces[0]["id"]

# Pinned context for a step, within a token budget; the receipt records what was supplied.
build = client.icm.build_context(ws, target={"kind": "route", "route": "fix"}, token_budget=6000)
receipt = client.icm.get_receipt(ws, build["receipt_id"])

# Context for one repository the workspace includes.
build = client.icm.build_context(ws, target={"kind": "repository", "alias": "api", "route": "fix"})

# Drafts: write files, check, propose. A person publishes or merges; the SDK never does.
client.icm.import_files(ws, {"icm.source.json": source_json, "routes/fix.md": body})
client.icm.check_draft(ws)
client.icm.propose_draft(ws, title="Refresh the fix route")
```

`AsyncMemoryRelay` exposes the same methods as coroutines.

## Exception Handling

```python
from memoryrelay import (
    MemoryRelayError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    APIError,
    NetworkError
)

try:
    memory = client.memories.get("invalid-id")
except NotFoundError as e:
    print(f"Memory not found: {e.message}")
except AuthenticationError:
    print("Invalid API key")
except ValidationError as e:
    print(f"Validation error: {e.message}")
except NetworkError as e:
    print(f"Network issue: {e.message}")
except MemoryRelayError as e:
    print(f"General error: {e.message} (status: {e.status_code})")
```

## Advanced Usage

### Custom Base URL

```python
client = MemoryRelay(
    api_key="your-api-key",
    base_url="https://custom-api.example.com"
)
```

### Custom Timeout

```python
client = MemoryRelay(
    api_key="your-api-key",
    timeout=60.0  # 60 seconds
)
```

### Custom Headers

```python
client = MemoryRelay(
    api_key="your-api-key",
    headers={"X-Custom-Header": "value"}
)
```

### Context Manager (Automatic Cleanup)

```python
with MemoryRelay(api_key="your-api-key") as client:
    agent = client.agents.create(AgentCreate(name="Test"))
    # Client automatically closed when exiting context
```

## Requirements

- Python 3.10+
- httpx >= 0.27.0
- pydantic >= 2.0.0

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy memoryrelay

# Linting
ruff check memoryrelay
```

## Links

- **Documentation**: https://docs.memoryrelay.ai/
- **API Reference**: https://docs.memoryrelay.ai/
- **GitHub**: https://github.com/yourusername/memoryrelay-python
- **Issues**: https://github.com/yourusername/memoryrelay-python/issues

## License

MIT License - see LICENSE file for details.
