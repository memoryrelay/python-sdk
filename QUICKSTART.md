# MemoryRelay Python SDK - Quick Reference

## Installation
```bash
pip install memoryrelay
```

## Basic Setup

### Sync Client
```python
from memoryrelay import MemoryRelay

client = MemoryRelay(api_key="your-api-key")
# or use MEMORYRELAY_API_KEY env var
```

### Async Client
```python
from memoryrelay import AsyncMemoryRelay

async with AsyncMemoryRelay(api_key="your-api-key") as client:
    # Use client here
    pass
```

## Quick Examples

### Create Agent & Memory
```python
from memoryrelay import AgentCreate, MemoryCreate

# Create agent
agent = client.agents.create(AgentCreate(name="MyAgent"))

# Store memory
memory = client.memories.create(
    MemoryCreate(
        agent_id=agent.id,
        content="User prefers Python",
        metadata={"category": "preference"}
    )
)
```

### Semantic Search
```python
from memoryrelay import MemorySearchRequest

results = client.memories.search(
    MemorySearchRequest(
        agent_id=agent.id,
        query="What language does user prefer?",
        limit=5,
        threshold=0.7
    )
)

for result in results:
    print(f"[{result.similarity:.2f}] {result.memory.content}")
```

### CRUD Operations
```python
# List
memories = client.memories.list(agent_id="agent-id", limit=50)

# Get
memory = client.memories.get("memory-id")

# Update
from memoryrelay import MemoryUpdate
updated = client.memories.update(
    "memory-id",
    MemoryUpdate(content="New content")
)

# Delete
client.memories.delete("memory-id")
```

## Key Features

✅ **Type Safe** - Full type hints with Pydantic models  
✅ **Sync & Async** - Both client types included  
✅ **Context Managers** - Automatic cleanup  
✅ **Error Handling** - Specific exception types  
✅ **Production Ready** - Works with https://api.memoryrelay.net

## Exception Handling
```python
from memoryrelay import NotFoundError, ValidationError

try:
    memory = client.memories.get("invalid-id")
except NotFoundError:
    print("Memory not found")
except ValidationError as e:
    print(f"Invalid request: {e.message}")
```

## API Reference

### Client Options
- `api_key`: Authentication (or use `MEMORYRELAY_API_KEY` env)
- `base_url`: API endpoint (default: `https://api.memoryrelay.net`)
- `timeout`: Request timeout in seconds (default: 30.0)
- `headers`: Additional HTTP headers

### Resources
- `client.memories` - Memory CRUD + search
- `client.agents` - Agent management
- `client.entities` - Entity tracking

See README.md for complete documentation.
