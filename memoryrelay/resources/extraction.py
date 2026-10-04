"""Extraction settings and BYOK management."""

from __future__ import annotations

import httpx

from ..exceptions import APIError, MemoryRelayError, NetworkError, NotFoundError, ValidationError
from ..models import (
    ByokKeyCreate,
    ByokKeyResponse,
    ExtractionSettings,
)


class ExtractionResource:
    """Synchronous extraction settings operations."""

    def __init__(self, client: httpx.Client, base_url: str):
        self._client = client
        self._base_url = base_url

    def get_settings(self) -> ExtractionSettings:
        """Get current extraction settings and BYOK status."""
        try:
            response = self._client.get(f"{self._base_url}/v1/extraction/settings")
            self._handle_errors(response)
            return ExtractionSettings(**response.json())
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    def create_key(self, key: ByokKeyCreate) -> ByokKeyResponse:
        """Add a new BYOK extraction key."""
        try:
            response = self._client.post(
                f"{self._base_url}/v1/extraction/keys", json=key.model_dump(exclude_none=True)
            )
            self._handle_errors(response)
            return ByokKeyResponse(**response.json())
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    def activate_key(self, key_id: str) -> ByokKeyResponse:
        """Activate a BYOK key (deactivates all others)."""
        try:
            response = self._client.post(f"{self._base_url}/v1/extraction/keys/{key_id}/activate")
            self._handle_errors(response)
            return ByokKeyResponse(**response.json())
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    def deactivate_all_keys(self) -> dict:
        """Deactivate all BYOK keys (use free extraction).

        Non-destructive: keys remain configured and can be re-activated.

        Returns:
            dict with status, message, and deactivated_count
        """
        try:
            response = self._client.post(f"{self._base_url}/v1/extraction/keys/deactivate-all")
            self._handle_errors(response)
            return response.json()
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    def delete_key(self, key_id: str) -> dict:
        """Delete a BYOK key."""
        try:
            response = self._client.delete(f"{self._base_url}/v1/extraction/keys/{key_id}")
            self._handle_errors(response)
            return response.json()
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    @staticmethod
    def _handle_errors(response: httpx.Response) -> None:
        """Handle HTTP errors and raise appropriate exceptions."""
        if response.is_success:
            return

        status_code = response.status_code
        try:
            error_data = response.json()
            message = error_data.get("detail", response.text)
        except Exception:
            message = response.text

        if status_code == 404:
            raise NotFoundError(message, status_code)
        elif status_code == 422:
            raise ValidationError(message, status_code)
        elif status_code >= 500:
            raise APIError(message, status_code)
        else:
            raise MemoryRelayError(message, status_code)


class AsyncExtractionResource:
    """Asynchronous extraction settings operations."""

    def __init__(self, client: httpx.AsyncClient, base_url: str):
        self._client = client
        self._base_url = base_url

    async def get_settings(self) -> ExtractionSettings:
        """Get current extraction settings and BYOK status."""
        try:
            response = await self._client.get(f"{self._base_url}/v1/extraction/settings")
            self._handle_errors(response)
            return ExtractionSettings(**response.json())
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    async def create_key(self, key: ByokKeyCreate) -> ByokKeyResponse:
        """Add a new BYOK extraction key."""
        try:
            response = await self._client.post(
                f"{self._base_url}/v1/extraction/keys", json=key.model_dump(exclude_none=True)
            )
            self._handle_errors(response)
            return ByokKeyResponse(**response.json())
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    async def activate_key(self, key_id: str) -> ByokKeyResponse:
        """Activate a BYOK key (deactivates all others)."""
        try:
            response = await self._client.post(
                f"{self._base_url}/v1/extraction/keys/{key_id}/activate"
            )
            self._handle_errors(response)
            return ByokKeyResponse(**response.json())
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    async def deactivate_all_keys(self) -> dict:
        """Deactivate all BYOK keys (use free extraction).

        Non-destructive: keys remain configured and can be re-activated.

        Returns:
            dict with status, message, and deactivated_count

        Example:
            >>> result = await client.extraction.deactivate_all_keys()
            >>> print(result["message"])
            "Deactivated 2 BYOK key(s). Now using free extraction (GLiNER)."
        """
        try:
            response = await self._client.post(
                f"{self._base_url}/v1/extraction/keys/deactivate-all"
            )
            self._handle_errors(response)
            return response.json()
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    async def delete_key(self, key_id: str) -> dict:
        """Delete a BYOK key."""
        try:
            response = await self._client.delete(f"{self._base_url}/v1/extraction/keys/{key_id}")
            self._handle_errors(response)
            return response.json()
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}", None) from e

    @staticmethod
    def _handle_errors(response: httpx.Response) -> None:
        """Handle HTTP errors and raise appropriate exceptions."""
        if response.is_success:
            return

        status_code = response.status_code
        try:
            error_data = response.json()
            message = error_data.get("detail", response.text)
        except Exception:
            message = response.text

        if status_code == 404:
            raise NotFoundError(message, status_code)
        elif status_code == 422:
            raise ValidationError(message, status_code)
        elif status_code >= 500:
            raise APIError(message, status_code)
        else:
            raise MemoryRelayError(message, status_code)
