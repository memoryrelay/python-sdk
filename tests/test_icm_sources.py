"""ICM sources and draft imports in the sync client, against a mocked server."""

import hashlib
import json

import httpx
import pytest

from memoryrelay import IcmError, MemoryRelay

BASE = "https://api.test"


def make_client(handler):
    return MemoryRelay(api_key="mem_test", base_url=BASE, transport=httpx.MockTransport(handler))


def caps_or(handler):
    def wrapped(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v2/icm/capabilities":
            return httpx.Response(200, json={"schema_versions": [2]})
        return handler(request)

    return wrapped


def test_import_files_hashes_each_file_and_sends_if_match():
    seen = {}

    def handler(request):
        seen["path"] = request.url.path
        seen["if_match"] = request.headers.get("If-Match")
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json={"added": ["a.md"], "digest": "d" * 64, "revision": 2})

    with make_client(caps_or(handler)) as client:
        out = client.icm.import_files(
            "w1",
            {"skills/b.md": "B\n", "skills/a.md": "A\n"},
            client={"name": "cc"},
            origin={"kind": "skills", "id": "x"},
            mode="mirror",
            prefix="skills/",
            expected_revision=1,
        )
    assert out["revision"] == 2
    assert seen["path"] == "/v2/icm/workspaces/w1/draft/imports"
    assert seen["if_match"] == '"1"'
    body = seen["body"]
    assert body["mode"] == "mirror" and body["prefix"] == "skills/"
    assert [f["path"] for f in body["files"]] == ["skills/a.md", "skills/b.md"]
    assert body["files"][0]["sha256"] == hashlib.sha256(b"A\n").hexdigest()


@pytest.mark.parametrize(
    "kwargs",
    [
        {"mode": "mirror"},
        {"mode": "replace"},
        {"client": {}},
        {"origin": {"kind": "skills"}},
    ],
)
def test_import_files_refuses_bad_requests_locally(kwargs):
    def handler(request):  # pragma: no cover - never reached
        raise AssertionError("no request expected")

    args = {"client": {"name": "cc"}, "origin": {"kind": "skills", "id": "x"}, **kwargs}
    with make_client(handler) as client, pytest.raises(ValueError):
        client.icm.import_files("w1", {"a.md": "A"}, **args)


def test_sources_calls_and_errors():
    calls = []

    def handler(request):
        calls.append((request.method, request.url.path, request.headers.get("If-Match")))
        if request.method == "POST":
            return httpx.Response(
                403, json={"detail": "Only a person", "code": "human_only", "status": 403}
            )
        if request.method == "PUT":
            return httpx.Response(200, json={"source": json.loads(request.content), "revision": 3})
        return httpx.Response(200, json={"source": None, "revision": 0})

    with make_client(caps_or(handler)) as client:
        assert client.icm.get_source("w1")["source"] is None
        put = client.icm.configure_source(
            "w1", "acme/factory", path="icm", credential_id="c1", expected_revision=2
        )
        assert put["source"] == {
            "provider": "github",
            "repository": "acme/factory",
            "ref": "main",
            "path": "icm",
            "auto_sync": False,
            "agent_proposals": False,
            "credential_id": "c1",
        }
        with pytest.raises(IcmError) as exc:
            client.icm.sync_source("w1")
    assert exc.value.code == "human_only" and exc.value.status_code == 403
    assert calls == [
        ("GET", "/v2/icm/workspaces/w1/source", None),
        ("PUT", "/v2/icm/workspaces/w1/source", '"2"'),
        ("POST", "/v2/icm/workspaces/w1/source/sync", None),
    ]


def test_draft_and_proposal_calls():
    calls = []

    def handler(request):
        calls.append((request.method, request.url.path, request.content))
        if request.url.path.endswith("/pull-request"):
            return httpx.Response(200, json={"number": 3, "state": "open"})
        return httpx.Response(200, json={"digest": "d" * 64, "proposal": None})

    with make_client(caps_or(handler)) as client:
        assert client.icm.get_draft("w1")["proposal"] is None
        client.icm.check_draft("w1")
        pr = client.icm.propose_draft("w1", "d" * 64, title="T")
        client.icm.refresh_proposal("w1")
        with pytest.raises(ValueError):
            client.icm.propose_draft("w1", "not-a-digest")
    assert pr["number"] == 3
    assert [(m, p) for m, p, _ in calls] == [
        ("GET", "/v2/icm/workspaces/w1/draft"),
        ("POST", "/v2/icm/workspaces/w1/draft/check"),
        ("POST", "/v2/icm/workspaces/w1/draft/pull-request"),
        ("POST", "/v2/icm/workspaces/w1/draft/pull-request/refresh"),
    ]
    assert json.loads(calls[2][2]) == {"expected_digest": "d" * 64, "title": "T"}


def test_configure_source_sends_agent_proposals():
    seen = {}

    def handler(request):
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json={"revision": 1})

    with make_client(caps_or(handler)) as client:
        client.icm.configure_source("w1", "acme/factory", agent_proposals=True)
    assert seen["body"]["agent_proposals"] is True
