"""
Tests for v2 Async API methods.
"""

import time
import pytest
from unittest.mock import MagicMock, patch

from memoryrelay import MemoryRelay, MemoryAsyncResponse, MemoryStatusResponse, Memory
from memoryrelay.exceptions import ValidationError, TimeoutError


@pytest.fixture
def client():
    """Create a test client."""
    return MemoryRelay(api_key="test_key", base_url="https://api.test.memoryrelay.net")


class TestV2AsyncAPI:
    """Tests for v2 async memory creation."""

    def test_create_async_success(self, client):
        """Test successful async memory creation."""
        mock_response = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "status": "pending",
            "job_id": "arq:01HQERX3B9G7Y8Z9C6Q5V4W3X2",
            "estimated_completion_seconds": 3,
        }

        with patch.object(client, "_request", return_value=mock_response):
            response = client.memories.create_async(
                content="Test memory",
                agent_id="test-agent",
            )

            assert isinstance(response, MemoryAsyncResponse)
            assert response.id == "550e8400-e29b-41d4-a716-446655440000"
            assert response.status == "pending"
            assert response.job_id == "arq:01HQERX3B9G7Y8Z9C6Q5V4W3X2"
            assert response.estimated_completion_seconds == 3

    def test_create_async_validation(self, client):
        """Test input validation for async create."""
        # Empty content
        with pytest.raises(ValidationError, match="content cannot be empty"):
            client.memories.create_async(content="", agent_id="test-agent")

        # Content too long
        with pytest.raises(ValidationError, match="exceeds maximum length"):
            client.memories.create_async(content="x" * 50001, agent_id="test-agent")

        # Empty agent_id
        with pytest.raises(ValidationError, match="agent_id cannot be empty"):
            client.memories.create_async(content="Test", agent_id="")

    def test_get_status(self, client):
        """Test status polling."""
        mock_response = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "status": "ready",
            "created_at": "2026-02-19T20:00:00Z",
            "updated_at": "2026-02-19T20:00:03Z",
        }

        with patch.object(client, "_request", return_value=mock_response):
            status = client.memories.get_status("550e8400-e29b-41d4-a716-446655440000")

            assert isinstance(status, MemoryStatusResponse)
            assert status.id == "550e8400-e29b-41d4-a716-446655440000"
            assert status.status == "ready"

    def test_wait_for_ready_success(self, client):
        """Test wait_for_ready with successful completion."""
        memory_id = "550e8400-e29b-41d4-a716-446655440000"

        # Mock status response (pending → ready)
        status_responses = [
            {"id": memory_id, "status": "pending", "created_at": "2026-02-19T20:00:00Z", "updated_at": "2026-02-19T20:00:00Z"},
            {"id": memory_id, "status": "processing", "created_at": "2026-02-19T20:00:00Z", "updated_at": "2026-02-19T20:00:01Z"},
            {"id": memory_id, "status": "ready", "created_at": "2026-02-19T20:00:00Z", "updated_at": "2026-02-19T20:00:03Z"},
        ]

        # Mock memory response
        memory_response = {
            "id": memory_id,
            "content": "Test memory",
            "agent_id": "test-agent",
            "embedding": [0.1] * 384,
            "created_at": "2026-02-19T20:00:00Z",
            "updated_at": "2026-02-19T20:00:03Z",
        }

        call_count = 0

        def mock_request(method, path, **kwargs):
            nonlocal call_count
            if path.endswith("/status"):
                response = status_responses[min(call_count, len(status_responses) - 1)]
                call_count += 1
                return response
            else:
                return memory_response

        with patch.object(client, "_request", side_effect=mock_request):
            memory = client.memories.wait_for_ready(memory_id, timeout=5, poll_interval=0.1)

            assert isinstance(memory, Memory)
            assert memory.id == memory_id
            assert memory.content == "Test memory"
            assert len(memory.embedding) == 384

    def test_wait_for_ready_timeout(self, client):
        """Test wait_for_ready with timeout."""
        memory_id = "550e8400-e29b-41d4-a716-446655440000"

        # Always return "pending" to trigger timeout
        mock_response = {
            "id": memory_id,
            "status": "pending",
            "created_at": "2026-02-19T20:00:00Z",
            "updated_at": "2026-02-19T20:00:00Z",
        }

        with patch.object(client, "_request", return_value=mock_response):
            with pytest.raises(TimeoutError, match="not ready after"):
                client.memories.wait_for_ready(memory_id, timeout=0.5, poll_interval=0.1)

    def test_wait_for_ready_failed_status(self, client):
        """Test wait_for_ready with failed embedding generation."""
        memory_id = "550e8400-e29b-41d4-a716-446655440000"

        mock_response = {
            "id": memory_id,
            "status": "failed",
            "created_at": "2026-02-19T20:00:00Z",
            "updated_at": "2026-02-19T20:00:01Z",
        }

        with patch.object(client, "_request", return_value=mock_response):
            with pytest.raises(ValidationError, match="embedding generation failed"):
                client.memories.wait_for_ready(memory_id, timeout=5)

    def test_create_and_wait(self, client):
        """Test create_and_wait convenience method."""
        memory_id = "550e8400-e29b-41d4-a716-446655440000"

        # Mock async create response
        create_response = {
            "id": memory_id,
            "status": "pending",
            "job_id": "arq:01HQERX3B9G7Y8Z9C6Q5V4W3X2",
            "estimated_completion_seconds": 3,
        }

        # Mock status response (ready immediately for test speed)
        status_response = {
            "id": memory_id,
            "status": "ready",
            "created_at": "2026-02-19T20:00:00Z",
            "updated_at": "2026-02-19T20:00:03Z",
        }

        # Mock memory response
        memory_response = {
            "id": memory_id,
            "content": "Test memory",
            "agent_id": "test-agent",
            "embedding": [0.1] * 384,
            "created_at": "2026-02-19T20:00:00Z",
            "updated_at": "2026-02-19T20:00:03Z",
        }

        def mock_request(method, path, **kwargs):
            if method == "POST" and path == "/v2/memories":
                return create_response
            elif path.endswith("/status"):
                return status_response
            else:
                return memory_response

        with patch.object(client, "_request", side_effect=mock_request):
            memory = client.memories.create_and_wait(
                content="Test memory",
                agent_id="test-agent",
                timeout=5,
            )

            assert isinstance(memory, Memory)
            assert memory.id == memory_id
            assert memory.content == "Test memory"
            assert len(memory.embedding) == 384


class TestV2PerformanceComparison:
    """Performance comparison tests (v1 vs v2)."""

    def test_response_time_comparison(self, client):
        """Test that v2 is significantly faster than v1 (mocked)."""
        # Mock v1 response (slow, 2-5s)
        v1_response = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "content": "Test memory",
            "agent_id": "test-agent",
            "embedding": [0.1] * 384,
            "created_at": "2026-02-19T20:00:00Z",
            "updated_at": "2026-02-19T20:00:05Z",
        }

        # Mock v2 response (fast, <50ms)
        v2_response = {
            "id": "660f9511-f30c-52e5-b827-557766551111",
            "status": "pending",
            "job_id": "arq:01HQERX3B9G7Y8Z9C6Q5V4W3X2",
            "estimated_completion_seconds": 3,
        }

        def mock_request_v1(method, path, **kwargs):
            time.sleep(2)  # Simulate 2s blocking
            return v1_response

        def mock_request_v2(method, path, **kwargs):
            return v2_response  # Instant return

        # Test v1 (slow)
        with patch.object(client, "_request", side_effect=mock_request_v1):
            start = time.time()
            client.memories.create(content="Test v1", agent_id="test-agent")
            v1_duration = time.time() - start

        # Test v2 (fast)
        with patch.object(client, "_request", side_effect=mock_request_v2):
            start = time.time()
            client.memories.create_async(content="Test v2", agent_id="test-agent")
            v2_duration = time.time() - start

        # v2 should be at least 10x faster (realistically 60-600x)
        assert v2_duration < v1_duration / 10
        print(f"\nPerformance: v1={v1_duration:.3f}s, v2={v2_duration:.3f}s, speedup={v1_duration/v2_duration:.0f}x")
