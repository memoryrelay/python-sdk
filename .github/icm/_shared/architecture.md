---
verified_at: 2026-10-15
verified_commit: b398f4ade5053147138b820135d12fdaf215ad2f
---

# Architecture — what the package is, and where each part lives

- `memoryrelay/__init__.py` — the public surface: `__version__` (line 3) and every exported client, model and exception in `__all__`. A new public name is exported here or it is not public.
- `memoryrelay/client.py`, `memoryrelay/async_client.py` — `MemoryRelay` and `AsyncMemoryRelay`: the key from the argument or `MEMORYRELAY_API_KEY` (`client.py:49-57`), the default base URL (`client.py:32`), one `httpx` client shared by every resource, extra keyword arguments passed to `httpx` (so a test passes `transport=`), and the resources attached at `client.py:74-78`.
- `memoryrelay/resources/memories.py` — memories: create, list, get, update, delete, search, entity extraction, promote, maintenance, batch and context, and the v2 asynchronous create with `get_status` and `wait_until_ready`. Sync class at line 38, async at line 332.
- `memoryrelay/resources/agents.py`, `memoryrelay/resources/entities.py`, `memoryrelay/resources/extraction.py` — agents; entities, links and the graph; extraction settings and BYOK keys. Each module holds the sync class and its async twin, and each class its own `_handle_errors`.
- `memoryrelay/resources/icm.py` — `/v2/icm`. Its docstring (lines 1-17) holds the rules: results are the server's JSON unmodified (receipts and hashes are evidence), `IcmUnsupportedError` against a server without ICM, no fallback to memory search, and which calls are people-only. Errors go through `_raise_for` (line 32) to `IcmError` with the server's `code`. Sync class at line 204, async at line 436.
- `memoryrelay/models.py` — the Pydantic models for memories, agents, entities and extraction. ICM has none: it returns dicts.
- `memoryrelay/exceptions.py` — `MemoryRelayError` and its subclasses, each carrying `status_code`; `IcmError` adds `code`.
- `memoryrelay/integrations/langchain.py`, `memoryrelay/integrations/llamaindex.py` — optional adapters; their dependencies are the `langchain` and `llamaindex` extras (`pyproject.toml:33-39`), imported inside a `try` so the core package needs neither.
- The routes and payloads belong to memoryrelay/api: [upstream.md](upstream.md).
