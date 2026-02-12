"""
Tests for MemoryRelay client initialization and basic functionality.
"""

import pytest
import httpx
import respx

from memoryrelay import MemoryRelay
from memoryrelay.exceptions import (
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ValidationError,
    NetworkError,
    TimeoutError,
)


def test_client_initialization():
    """Test client initializes with correct defaults."""
    client = MemoryRelay(api_key="test_key_123")
    
    assert client.api_key == "test_key_123"
    assert client.base_url == "https://api.memoryrelay.net"
    assert client.timeout == 30.0
    assert client.max_retries == 3
    
    # Check resources initialized
    assert client.memories is not None
    assert client.entities is not None
    assert client.agents is not None


def test_client_custom_config():
    """Test client accepts custom configuration."""
    client = MemoryRelay(
        api_key="custom_key",
        base_url="https://custom.api.com",
        timeout=60.0,
        max_retries=5,
    )
    
    assert client.api_key == "custom_key"
    assert client.base_url == "https://custom.api.com"
    assert client.timeout == 60.0
    assert client.max_retries == 5


def test_context_manager():
    """Test client works as context manager."""
    with MemoryRelay(api_key="test_key") as client:
        assert client.api_key == "test_key"
    
    # Client should be closed after context
    assert client._client.is_closed


@respx.mock
def test_health_check():
    """Test health check endpoint."""
    client = MemoryRelay(api_key="test_key")
    
    # Mock health response
    respx.get("https://api.memoryrelay.net/v1/health").mock(
        return_value=httpx.Response(
            200,
            json={
                "status": "healthy",
                "version": "1.0.0",
                "api_version": "v1",
                "environment": "production",
                "timestamp": 1707782400,
                "uptime_seconds": 86400,
                "services": {
                    "database": "up",
                    "redis": "up",
                    "embeddings": "up"
                }
            }
        )
    )
    
    health = client.health()
    
    assert health.status == "healthy"
    assert health.version == "1.0.0"
    assert health.services["database"] == "up"


@respx.mock
def test_authentication_error():
    """Test 401 raises AuthenticationError."""
    client = MemoryRelay(api_key="invalid_key")
    
    respx.post("https://api.memoryrelay.net/v1/memories").mock(
        return_value=httpx.Response(
            401,
            json={
                "error": {
                    "message": "Invalid API key",
                    "request_id": "req_123"
                }
            }
        )
    )
    
    with pytest.raises(AuthenticationError) as exc_info:
        client.memories.create(content="test", agent_id="test")
    
    assert exc_info.value.status_code == 401
    assert "Invalid API key" in exc_info.value.message
    assert exc_info.value.request_id == "req_123"


@respx.mock
def test_rate_limit_error():
    """Test 429 raises RateLimitError with retry_after."""
    client = MemoryRelay(api_key="test_key", max_retries=1)
    
    respx.post("https://api.memoryrelay.net/v1/memories").mock(
        return_value=httpx.Response(
            429,
            headers={"Retry-After": "60"},
            json={
                "error": {
                    "message": "Rate limit exceeded",
                    "request_id": "req_456"
                }
            }
        )
    )
    
    with pytest.raises(RateLimitError) as exc_info:
        client.memories.create(content="test", agent_id="test")
    
    assert exc_info.value.status_code == 429
    assert exc_info.value.retry_after == 60
    assert "Rate limit exceeded" in exc_info.value.message


@respx.mock
def test_not_found_error():
    """Test 404 raises NotFoundError."""
    client = MemoryRelay(api_key="test_key")
    
    respx.get("https://api.memoryrelay.net/v1/memories/nonexistent").mock(
        return_value=httpx.Response(
            404,
            json={
                "error": {
                    "message": "Memory not found",
                    "request_id": "req_789"
                }
            }
        )
    )
    
    with pytest.raises(NotFoundError) as exc_info:
        client.memories.get("nonexistent")
    
    assert exc_info.value.status_code == 404
    assert "Memory not found" in exc_info.value.message


@respx.mock
def test_validation_error():
    """Test 400/422 raises ValidationError."""
    client = MemoryRelay(api_key="test_key")
    
    respx.post("https://api.memoryrelay.net/v1/memories").mock(
        return_value=httpx.Response(
            422,
            json={
                "error": {
                    "message": "content is required",
                    "request_id": "req_abc"
                }
            }
        )
    )
    
    with pytest.raises(ValidationError) as exc_info:
        client.memories.create(content="", agent_id="test")
    
    assert exc_info.value.status_code == 400  # Client-side validation
    assert "cannot be empty" in exc_info.value.message


@respx.mock
def test_network_error_retry():
    """Test network errors trigger retry with backoff."""
    client = MemoryRelay(api_key="test_key", max_retries=3)
    
    # First 2 calls fail with network error, 3rd succeeds
    route = respx.post("https://api.memoryrelay.net/v1/memories")
    route.side_effect = [
        httpx.NetworkError("Connection refused"),
        httpx.NetworkError("Connection refused"),
        httpx.Response(
            200,
            json={
                "id": "mem_123",
                "content": "test",
                "agent_id": "test",
                "user_id": None,
                "metadata": None,
                "embedding": None,
                "created_at": "2026-02-12T23:00:00Z",
                "updated_at": "2026-02-12T23:00:00Z"
            }
        ),
    ]
    
    memory = client.memories.create(content="test", agent_id="test")
    
    assert memory.id == "mem_123"
    assert route.call_count == 3


@respx.mock
def test_network_error_exhausted():
    """Test network errors exhaust retries and raise."""
    client = MemoryRelay(api_key="test_key", max_retries=2)
    
    route = respx.post("https://api.memoryrelay.net/v1/memories")
    route.side_effect = httpx.NetworkError("Connection refused")
    
    with pytest.raises(NetworkError) as exc_info:
        client.memories.create(content="test", agent_id="test")
    
    assert "Connection refused" in str(exc_info.value)
    assert route.call_count == 2


@respx.mock
def test_timeout_error():
    """Test timeout errors are handled correctly."""
    client = MemoryRelay(api_key="test_key", timeout=1.0, max_retries=1)
    
    respx.post("https://api.memoryrelay.net/v1/memories").mock(
        side_effect=httpx.TimeoutException("Request timeout")
    )
    
    with pytest.raises(TimeoutError) as exc_info:
        client.memories.create(content="test", agent_id="test")
    
    assert "timeout after 1.0s" in str(exc_info.value)


@respx.mock
def test_error_without_json_body():
    """Test errors without JSON body are handled gracefully."""
    client = MemoryRelay(api_key="test_key")
    
    respx.post("https://api.memoryrelay.net/v1/memories").mock(
        return_value=httpx.Response(500, text="Internal Server Error")
    )
    
    with pytest.raises(Exception) as exc_info:
        client.memories.create(content="test", agent_id="test")
    
    # Should contain status code or text
    assert "500" in str(exc_info.value) or "Internal Server Error" in str(exc_info.value)


def test_base_url_trailing_slash():
    """Test base_url handles trailing slashes correctly."""
    client = MemoryRelay(
        api_key="test_key",
        base_url="https://api.example.com/"
    )
    
    assert client.base_url == "https://api.example.com"
