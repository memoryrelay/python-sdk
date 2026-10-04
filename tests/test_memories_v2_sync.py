"""The sync client's V2 async helpers, against a mocked server."""

import httpx
import pytest

from memoryrelay import MemoryCreate, MemoryRelay
from memoryrelay.exceptions import APIError, RequestTimeoutError

BASE = "https://api.test"
MEMORY = {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "content": "User prefers dark mode",
    "agent_id": "iris",
    "metadata": {},
    "entities": [],
    "created_at": 1700000000,
    "updated_at": 1700000000,
}


def make_client(statuses: list[str]):
    calls = {"status": 0, "posts": []}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST" and request.url.path == "/v2/memories":
            calls["posts"].append(request.read())
            return httpx.Response(
                202,
                json={
                    "id": MEMORY["id"],
                    "status": "pending",
                    "job_id": "arq:1",
                    "estimated_completion_seconds": 3,
                },
            )
        if request.url.path == f"/v2/memories/{MEMORY['id']}/status":
            i = min(calls["status"], len(statuses) - 1)
            calls["status"] += 1
            body = {
                "id": MEMORY["id"],
                "status": statuses[i],
                "created_at": 1700000000,
                "updated_at": 1700000000,
            }
            if statuses[i] == "failed":
                body["error"] = "embedding failed"
            return httpx.Response(200, json=body)
        if request.url.path == f"/v1/memories/{MEMORY['id']}":
            return httpx.Response(200, json=MEMORY)
        return httpx.Response(404, json={"detail": "not found"})

    client = MemoryRelay(api_key="mem_test", base_url=BASE, transport=httpx.MockTransport(handler))
    return client, calls


def test_create_async_then_wait_until_ready():
    client, calls = make_client(["pending", "processing", "ready"])
    accepted = client.memories.create_async(
        MemoryCreate(agent_id="iris", content="User prefers dark mode")
    )
    assert accepted.status == "pending" and accepted.job_id == "arq:1"
    assert b'"agent_id":"iris"' in calls["posts"][0]

    memory = client.memories.wait_until_ready(accepted.id, poll_interval=0)
    assert memory.id == MEMORY["id"]
    assert calls["status"] == 3


def test_get_status_and_failed_processing():
    client, _ = make_client(["failed"])
    status = client.memories.get_status(MEMORY["id"])
    assert status.status == "failed" and status.error == "embedding failed"
    with pytest.raises(APIError, match="embedding failed"):
        client.memories.wait_until_ready(MEMORY["id"], poll_interval=0)


def test_wait_until_ready_times_out():
    client, _ = make_client(["pending"])
    with pytest.raises(RequestTimeoutError):
        client.memories.wait_until_ready(MEMORY["id"], poll_interval=0, timeout=0)
