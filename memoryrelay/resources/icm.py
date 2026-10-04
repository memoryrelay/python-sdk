"""ICM resource: pinned context workspaces (``/v2/icm``).

Read operations, context builds, Git sources (``get_source``;
``configure_source`` and ``sync_source`` are people-only), drafts
(``get_draft``, ``check_draft``, and ``import_files``, the one draft write an
agent key may make) and a Git draft's pull request (``propose_draft``: a person
with publisher, or a confined key when the source allows agent proposals;
``refresh_proposal``). A person always decides: they publish, or merge the
pull request in GitHub. Results are
returned as the server's JSON, unmodified: hashes and receipts are evidence
and are not re-shaped here.

A server without ICM answers ``capabilities()`` with ``{"supported": False}``;
every other call on such a server raises ``IcmUnsupportedError``. There is no
fallback to memory search: pinned context and search results are not
interchangeable.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from typing import Any, cast

import httpx

from ..exceptions import IcmError, IcmUnsupportedError, NetworkError

_PREFIX = "/v2/icm"


def _raise_for(response: httpx.Response) -> None:
    if response.is_success:
        return
    try:
        problem = response.json()
    except ValueError:
        problem = {}
    raise IcmError(
        problem.get("detail") or response.text or response.reason_phrase,
        response.status_code,
        code=problem.get("code") or "http_error",
    )


TARGET_KINDS = ("entry", "route", "stage", "record", "notes", "nodes", "impact", "repository")


def _build_body(
    *,
    target: dict[str, Any] | None,
    stage: str | None,
    project_id: str | None,
    runtime: str | None,
    token_budget: int | None,
    release_id: str | None,
    channel: str | None,
) -> dict[str, Any]:
    """The context-build request. ``target`` names what to build for; ``stage`` is
    the older spelling of ``{"kind": "stage", "id": stage}``. Without a release or
    channel the server builds the live version."""
    if (target is None) == (stage is None):
        raise ValueError("Give exactly one of target or stage")
    if target is not None and target.get("kind") not in TARGET_KINDS:
        raise ValueError(f"target['kind'] must be one of {TARGET_KINDS}")
    if release_id is not None and channel is not None:
        raise ValueError("Give at most one of release_id or channel")
    body: dict[str, Any] = {"target": target} if target is not None else {"stage": stage}
    for key, value in (
        ("project_id", project_id),
        ("runtime", runtime),
        ("token_budget", token_budget),
        ("release_id", release_id),
        ("channel", channel),
    ):
        if value is not None:
            body[key] = value
    return body


IMPORT_MODES = ("merge", "mirror")


def _import_body(
    files: Mapping[str, str],
    *,
    client: Mapping[str, Any],
    origin: Mapping[str, Any],
    mode: str,
    prefix: str | None,
) -> dict[str, Any]:
    """A draft import: every file with the sha256 of its UTF-8 bytes."""
    if mode not in IMPORT_MODES:
        raise ValueError(f"mode must be one of {IMPORT_MODES}")
    if mode == "mirror" and prefix is None:
        raise ValueError("A mirror import names the folder it mirrors (prefix)")
    if not files:
        raise ValueError("An import holds at least one file")
    if not client.get("name") or not origin.get("kind") or not origin.get("id"):
        raise ValueError("client needs a name; origin needs a kind and an id")
    body: dict[str, Any] = {
        "client": dict(client),
        "origin": dict(origin),
        "mode": mode,
        "files": [
            {
                "path": path,
                "content": content,
                "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
            }
            for path, content in sorted(files.items())
        ],
    }
    if prefix is not None:
        body["prefix"] = prefix
    return body


def _source_body(
    repository: str,
    ref: str,
    path: str,
    credential_id: str | None,
    auto_sync: bool,
    agent_proposals: bool = False,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "provider": "github",
        "repository": repository,
        "ref": ref,
        "path": path,
        "auto_sync": auto_sync,
        "agent_proposals": agent_proposals,
    }
    if credential_id is not None:
        body["credential_id"] = credential_id
    return body


def _proposal_body(expected_digest: str, title: str | None, body: str | None) -> dict[str, Any]:
    if len(expected_digest) != 64 or any(c not in "0123456789abcdef" for c in expected_digest):
        raise ValueError("expected_digest is the 64-hex draft digest the caller reviewed")
    out: dict[str, Any] = {"expected_digest": expected_digest}
    if title is not None:
        out["title"] = title
    if body is not None:
        out["body"] = body
    return out


def _if_match(revision: int | None) -> dict[str, str]:
    return {} if revision is None else {"If-Match": f'"{revision}"'}


class IcmResource:
    """Synchronous ICM operations."""

    def __init__(self, client: httpx.Client, base_url: str):
        self._client = client
        self._base_url = base_url
        self._supported: bool | None = None

    def _call(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        try:
            response = self._client.request(method, f"{self._base_url}{_PREFIX}{path}", **kwargs)
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e
        _raise_for(response)
        return cast(dict[str, Any], response.json())

    def capabilities(self) -> dict[str, Any]:
        """Server support for ICM; ``{"supported": False}`` when absent."""
        try:
            caps = self._call("GET", "/capabilities")
        except IcmError as e:
            if e.status_code == 404:
                self._supported = False
                return {"supported": False}
            raise
        self._supported = True
        return {"supported": True, **caps}

    def _require(self) -> None:
        if self._supported is not True and not self.capabilities()["supported"]:
            raise IcmUnsupportedError()

    def list_workspaces(self) -> list[dict[str, Any]]:
        self._require()
        return cast(list[dict[str, Any]], self._call("GET", "/workspaces")["workspaces"])

    def get_release(self, workspace_id: str, release_id: str) -> dict[str, Any]:
        self._require()
        return self._call("GET", f"/workspaces/{workspace_id}/releases/{release_id}")

    def build_context(
        self,
        workspace_id: str,
        *,
        target: dict[str, Any] | None = None,
        stage: str | None = None,
        project_id: str | None = None,
        runtime: str | None = None,
        token_budget: int | None = None,
        release_id: str | None = None,
        channel: str | None = None,
    ) -> dict[str, Any]:
        """Build context for a target (entry, route, stage, record, notes, nodes,
        impact, repository). Check ``disposition``: a blocked build supplies nothing."""
        body = _build_body(
            target=target,
            stage=stage,
            project_id=project_id,
            runtime=runtime,
            token_budget=token_budget,
            release_id=release_id,
            channel=channel,
        )
        self._require()
        return self._call("POST", f"/workspaces/{workspace_id}/context/builds", json=body)

    def root(self, *, step: str | None = None) -> dict[str, Any]:
        """The root: one row per repository your workspaces include, with what is
        bound. It lists; ``context_for`` still answers ``no_binding``."""
        self._require()
        return self._call("GET", "/root", params={"step": step} if step else None)

    def list_repositories(self, workspace_id: str) -> dict[str, Any]:
        """A knowledge workspace's inclusions, with each mirror's state."""
        self._require()
        return self._call("GET", f"/workspaces/{workspace_id}/repositories")

    def list_relationships(self, workspace_id: str) -> dict[str, Any]:
        """Typed links to and from other workspaces, filtered to what you may see."""
        self._require()
        return self._call("GET", f"/workspaces/{workspace_id}/relationships")

    def get_receipt(self, workspace_id: str, receipt_id: str) -> dict[str, Any]:
        self._require()
        return self._call("GET", f"/workspaces/{workspace_id}/receipts/{receipt_id}")

    def get_run(self, workspace_id: str, run_id: str) -> dict[str, Any]:
        """A run's per-stage status; ``approval_stale`` means edited after approval."""
        self._require()
        return self._call("GET", f"/workspaces/{workspace_id}/runs/{run_id}")

    def get_source(self, workspace_id: str) -> dict[str, Any]:
        """A Git-authority workspace's source and its last sync (never a token)."""
        self._require()
        return self._call("GET", f"/workspaces/{workspace_id}/source")

    def configure_source(
        self,
        workspace_id: str,
        repository: str,
        *,
        ref: str = "main",
        path: str = "",
        credential_id: str | None = None,
        auto_sync: bool = False,
        expected_revision: int | None = None,
        agent_proposals: bool = False,
    ) -> dict[str, Any]:
        """Create or replace the source. People only (a key gets ``human_only``);
        ``expected_revision`` is the source's current revision when one exists.
        ``agent_proposals`` lets a confined agent key open pull requests (admin)."""
        self._require()
        return self._call(
            "PUT",
            f"/workspaces/{workspace_id}/source",
            json=_source_body(repository, ref, path, credential_id, auto_sync, agent_proposals),
            headers=_if_match(expected_revision),
        )

    def sync_source(self, workspace_id: str) -> dict[str, Any]:
        """Sync now. People only. ``outcome`` is published, unchanged or failed;
        a failure leaves live alone and lists ``errors``."""
        self._require()
        return self._call("POST", f"/workspaces/{workspace_id}/source/sync")

    def import_files(
        self,
        workspace_id: str,
        files: Mapping[str, str],
        *,
        client: Mapping[str, Any],
        origin: Mapping[str, Any],
        mode: str = "merge",
        prefix: str | None = None,
        expected_revision: int | None = None,
    ) -> dict[str, Any]:
        """Land ``{path: text}`` in the workspace's draft (``icm:run``, a key confined
        to the workspace, or a person). Returns added/modified/removed/unchanged
        paths and the draft with its ``digest``; a person publishes it."""
        body = _import_body(files, client=client, origin=origin, mode=mode, prefix=prefix)
        self._require()
        return self._call(
            "POST",
            f"/workspaces/{workspace_id}/draft/imports",
            json=body,
            headers=_if_match(expected_revision),
        )

    def get_draft(self, workspace_id: str) -> dict[str, Any]:
        """The draft: changes, ``digest`` and, on a Git workspace, its ``proposal``."""
        self._require()
        return self._call("GET", f"/workspaces/{workspace_id}/draft")

    def check_draft(self, workspace_id: str) -> dict[str, Any]:
        """Compile and walk the draft as a publish (or, on Git, the sync) would."""
        self._require()
        return self._call("POST", f"/workspaces/{workspace_id}/draft/check")

    def propose_draft(
        self,
        workspace_id: str,
        expected_digest: str,
        *,
        title: str | None = None,
        body: str | None = None,
    ) -> dict[str, Any]:
        """Open or update a Git draft's pull request, bound to ``expected_digest``.
        A person merges it in GitHub; MemoryRelay never merges."""
        payload = _proposal_body(expected_digest, title, body)
        self._require()
        return self._call("POST", f"/workspaces/{workspace_id}/draft/pull-request", json=payload)

    def refresh_proposal(self, workspace_id: str) -> dict[str, Any]:
        """Read the pull request's state; a merged one syncs and clears the draft."""
        self._require()
        return self._call("POST", f"/workspaces/{workspace_id}/draft/pull-request/refresh")


class AsyncIcmResource:
    """Asynchronous ICM operations."""

    def __init__(self, client: httpx.AsyncClient, base_url: str):
        self._client = client
        self._base_url = base_url
        self._supported: bool | None = None

    async def _call(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        try:
            response = await self._client.request(
                method, f"{self._base_url}{_PREFIX}{path}", **kwargs
            )
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e
        _raise_for(response)
        return cast(dict[str, Any], response.json())

    async def capabilities(self) -> dict[str, Any]:
        """Server support for ICM; ``{"supported": False}`` when absent."""
        try:
            caps = await self._call("GET", "/capabilities")
        except IcmError as e:
            if e.status_code == 404:
                self._supported = False
                return {"supported": False}
            raise
        self._supported = True
        return {"supported": True, **caps}

    async def _require(self) -> None:
        if self._supported is not True and not (await self.capabilities())["supported"]:
            raise IcmUnsupportedError()

    async def list_workspaces(self) -> list[dict[str, Any]]:
        await self._require()
        return cast(list[dict[str, Any]], (await self._call("GET", "/workspaces"))["workspaces"])

    async def get_release(self, workspace_id: str, release_id: str) -> dict[str, Any]:
        await self._require()
        return await self._call("GET", f"/workspaces/{workspace_id}/releases/{release_id}")

    async def build_context(
        self,
        workspace_id: str,
        *,
        target: dict[str, Any] | None = None,
        stage: str | None = None,
        project_id: str | None = None,
        runtime: str | None = None,
        token_budget: int | None = None,
        release_id: str | None = None,
        channel: str | None = None,
    ) -> dict[str, Any]:
        """Build context for a target (entry, route, stage, record, notes, nodes,
        impact, repository). Check ``disposition``: a blocked build supplies nothing."""
        body = _build_body(
            target=target,
            stage=stage,
            project_id=project_id,
            runtime=runtime,
            token_budget=token_budget,
            release_id=release_id,
            channel=channel,
        )
        await self._require()
        return await self._call("POST", f"/workspaces/{workspace_id}/context/builds", json=body)

    async def root(self, *, step: str | None = None) -> dict[str, Any]:
        """The root: one row per repository your workspaces include, with what is
        bound. It lists; ``context_for`` still answers ``no_binding``."""
        await self._require()
        return await self._call("GET", "/root", params={"step": step} if step else None)

    async def list_repositories(self, workspace_id: str) -> dict[str, Any]:
        """A knowledge workspace's inclusions, with each mirror's state."""
        await self._require()
        return await self._call("GET", f"/workspaces/{workspace_id}/repositories")

    async def list_relationships(self, workspace_id: str) -> dict[str, Any]:
        """Typed links to and from other workspaces, filtered to what you may see."""
        await self._require()
        return await self._call("GET", f"/workspaces/{workspace_id}/relationships")

    async def get_receipt(self, workspace_id: str, receipt_id: str) -> dict[str, Any]:
        await self._require()
        return await self._call("GET", f"/workspaces/{workspace_id}/receipts/{receipt_id}")

    async def get_run(self, workspace_id: str, run_id: str) -> dict[str, Any]:
        """A run's per-stage status; ``approval_stale`` means edited after approval."""
        await self._require()
        return await self._call("GET", f"/workspaces/{workspace_id}/runs/{run_id}")

    async def get_source(self, workspace_id: str) -> dict[str, Any]:
        """A Git-authority workspace's source and its last sync (never a token)."""
        await self._require()
        return await self._call("GET", f"/workspaces/{workspace_id}/source")

    async def configure_source(
        self,
        workspace_id: str,
        repository: str,
        *,
        ref: str = "main",
        path: str = "",
        credential_id: str | None = None,
        auto_sync: bool = False,
        expected_revision: int | None = None,
        agent_proposals: bool = False,
    ) -> dict[str, Any]:
        """Create or replace the source. People only (a key gets ``human_only``);
        ``expected_revision`` is the source's current revision when one exists.
        ``agent_proposals`` lets a confined agent key open pull requests (admin)."""
        await self._require()
        return await self._call(
            "PUT",
            f"/workspaces/{workspace_id}/source",
            json=_source_body(repository, ref, path, credential_id, auto_sync, agent_proposals),
            headers=_if_match(expected_revision),
        )

    async def sync_source(self, workspace_id: str) -> dict[str, Any]:
        """Sync now. People only. ``outcome`` is published, unchanged or failed;
        a failure leaves live alone and lists ``errors``."""
        await self._require()
        return await self._call("POST", f"/workspaces/{workspace_id}/source/sync")

    async def import_files(
        self,
        workspace_id: str,
        files: Mapping[str, str],
        *,
        client: Mapping[str, Any],
        origin: Mapping[str, Any],
        mode: str = "merge",
        prefix: str | None = None,
        expected_revision: int | None = None,
    ) -> dict[str, Any]:
        """Land ``{path: text}`` in the workspace's draft (``icm:run``, a key confined
        to the workspace, or a person). Returns added/modified/removed/unchanged
        paths and the draft with its ``digest``; a person publishes it."""
        body = _import_body(files, client=client, origin=origin, mode=mode, prefix=prefix)
        await self._require()
        return await self._call(
            "POST",
            f"/workspaces/{workspace_id}/draft/imports",
            json=body,
            headers=_if_match(expected_revision),
        )

    async def get_draft(self, workspace_id: str) -> dict[str, Any]:
        """The draft: changes, ``digest`` and, on a Git workspace, its ``proposal``."""
        await self._require()
        return await self._call("GET", f"/workspaces/{workspace_id}/draft")

    async def check_draft(self, workspace_id: str) -> dict[str, Any]:
        """Compile and walk the draft as a publish (or, on Git, the sync) would."""
        await self._require()
        return await self._call("POST", f"/workspaces/{workspace_id}/draft/check")

    async def propose_draft(
        self,
        workspace_id: str,
        expected_digest: str,
        *,
        title: str | None = None,
        body: str | None = None,
    ) -> dict[str, Any]:
        """Open or update a Git draft's pull request, bound to ``expected_digest``.
        A person merges it in GitHub; MemoryRelay never merges."""
        payload = _proposal_body(expected_digest, title, body)
        await self._require()
        return await self._call(
            "POST", f"/workspaces/{workspace_id}/draft/pull-request", json=payload
        )

    async def refresh_proposal(self, workspace_id: str) -> dict[str, Any]:
        """Read the pull request's state; a merged one syncs and clears the draft."""
        await self._require()
        return await self._call("POST", f"/workspaces/{workspace_id}/draft/pull-request/refresh")
