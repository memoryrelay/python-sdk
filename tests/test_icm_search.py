"""ICM full-text search in the sync and async clients, against a mocked server."""

import asyncio

import httpx

from memoryrelay import AsyncMemoryRelay, MemoryRelay

BASE = "https://api.test"
REL = "c" * 64
BODY = {"query": "deploy", "results": [], "searched": [], "skipped": []}


def handler_for(seen):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v2/icm/capabilities":
            return httpx.Response(200, json={"schema_versions": [2]})
        seen.append(request.url)
        return httpx.Response(200, json=BODY)

    return handler


def test_sync_search_sends_query_workspaces_release_and_limit():
    seen: list[httpx.URL] = []
    transport = httpx.MockTransport(handler_for(seen))
    with MemoryRelay(api_key="mem_test", base_url=BASE, transport=transport) as client:
        assert client.icm.search("deploy") == BODY
        client.icm.search("deploy", workspace_ids=["w1", "w2"], release_id=REL, limit=5)
    assert seen[0].path == "/v2/icm/search"
    assert dict(seen[0].params) == {"q": "deploy", "limit": "10"}
    assert seen[1].params.get_list("workspace_id") == ["w1", "w2"]
    assert seen[1].params["release_id"] == REL and seen[1].params["limit"] == "5"


def test_async_search_matches_sync():
    seen: list[httpx.URL] = []

    async def run():
        transport = httpx.MockTransport(handler_for(seen))
        async with AsyncMemoryRelay(api_key="mem_test", base_url=BASE, transport=transport) as c:
            return await c.icm.search("deploy", workspace_ids=["w1"])

    assert asyncio.run(run()) == BODY
    assert seen[0].path == "/v2/icm/search"
    assert seen[0].params.get_list("workspace_id") == ["w1"]
