"""
Tests for exception classes.
"""

import pytest
from memoryrelay.exceptions import (
    MemoryRelayError,
    APIError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ValidationError,
    NetworkError,
    TimeoutError,
)


def test_base_exception():
    """Test base MemoryRelayError exception."""
    error = MemoryRelayError("test error", status_code=500)
    
    assert error.message == "test error"
    assert error.status_code == 500
    assert str(error) == "test error"


def test_api_error():
    """Test APIError with full details."""
    error = APIError(
        "API error occurred",
        status_code=500,
        response={"error": "details"},
        request_id="req_123"
    )
    
    assert error.message == "API error occurred"
    assert error.status_code == 500
    assert error.response == {"error": "details"}
    assert error.request_id == "req_123"


def test_authentication_error():
    """Test AuthenticationError (401)."""
    error = AuthenticationError(
        "Invalid API key",
        status_code=401,
        request_id="req_456"
    )
    
    assert error.status_code == 401
    assert "Invalid API key" in error.message


def test_rate_limit_error():
    """Test RateLimitError with retry_after."""
    error = RateLimitError(
        "Rate limit exceeded",
        retry_after=60,
        request_id="req_789"
    )
    
    assert error.status_code == 429
    assert error.retry_after == 60
    assert error.request_id == "req_789"


def test_rate_limit_error_no_retry_after():
    """Test RateLimitError without retry_after."""
    error = RateLimitError("Rate limit exceeded")
    
    assert error.status_code == 429
    assert error.retry_after is None


def test_not_found_error():
    """Test NotFoundError (404)."""
    error = NotFoundError("Resource not found", status_code=404)
    
    assert error.status_code == 404
    assert "not found" in error.message


def test_validation_error():
    """Test ValidationError (400/422)."""
    error = ValidationError("Invalid input", status_code=422)
    
    assert error.status_code == 422
    assert "Invalid input" in error.message


def test_network_error():
    """Test NetworkError."""
    error = NetworkError("Connection failed")
    
    assert "Connection failed" in error.message
    assert error.status_code is None


def test_timeout_error():
    """Test TimeoutError."""
    error = TimeoutError("Request timeout")
    
    assert "timeout" in error.message
    assert error.status_code is None
