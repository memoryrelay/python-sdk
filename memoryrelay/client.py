"""
MemoryRelay Python SDK - Main Client

Official Python client for MemoryRelay API.
"""

from typing import Any, Dict, List, Optional

import httpx

from memoryrelay.exceptions import (
    APIError,
    AuthenticationError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    TimeoutError,
    ValidationError,
)
from memoryrelay.resources.memories import MemoriesResource
from memoryrelay.resources.entities import EntitiesResource
from memoryrelay.resources.agents import AgentsResource
from memoryrelay.types import HealthStatus


class MemoryRelay:
    """
    MemoryRelay API Client.
    
    Usage:
        >>> client = MemoryRelay(api_key="mem_...")
        >>> 
        >>> # Create a memory
        >>> memory = client.memories.create(
        ...     content="User prefers dark mode",
        ...     agent_id="my-agent"
        ... )
        >>> 
        >>> # Search memories
        >>> results = client.memories.search(
        ...     query="user preferences",
        ...     limit=5
        ... )
        >>> 
        >>> # Batch create
        >>> response = client.memories.create_batch([
        ...     {"content": "Memory 1"},
        ...     {"content": "Memory 2"}
        ... ])
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.memoryrelay.net",
        timeout: float = 30.0,
        max_retries: int = 3,
        **kwargs: Any,
    ) -> None:
        """
        Initialize MemoryRelay client.
        
        Args:
            api_key: Your MemoryRelay API key (required)
            base_url: API base URL (default: https://api.memoryrelay.net)
            timeout: Request timeout in seconds (default: 30.0)
            max_retries: Maximum number of retries for failed requests (default: 3)
            **kwargs: Additional arguments passed to httpx.Client
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Create HTTP client
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            headers={
                "X-API-Key": api_key,
                "User-Agent": f"memoryrelay-python/0.1.0",
            },
            **kwargs,
        )
        
        # Initialize resource clients
        self.memories = MemoriesResource(self)
        self.entities = EntitiesResource(self)
        self.agents = AgentsResource(self)
    
    def health(self) -> HealthStatus:
        """
        Check API health status.
        
        Returns:
            HealthStatus object with service information
            
        Example:
            >>> health = client.health()
            >>> print(health.status)  # "healthy"
            >>> print(health.services)  # {"database": "up", ...}
        """
        response = self._request("GET", "/v1/health")
        return HealthStatus(**response)
    
    def _request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """
        Make an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            path: API endpoint path
            json: JSON body for request
            params: Query parameters
            headers: Additional headers
            
        Returns:
            Parsed JSON response
            
        Raises:
            AuthenticationError: Invalid API key
            RateLimitError: Rate limit exceeded
            NotFoundError: Resource not found
            ValidationError: Invalid request data
            APIError: Other API errors
            NetworkError: Connection/network errors
            TimeoutError: Request timeout
        """
        # Merge headers
        req_headers = self._client.headers.copy()
        if headers:
            req_headers.update(headers)
        
        # Retry logic
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                response = self._client.request(
                    method=method,
                    url=path,
                    json=json,
                    params=params,
                    headers=req_headers,
                )
                
                # Handle errors
                if response.status_code >= 400:
                    self._handle_error(response)
                
                # Parse response
                if response.status_code == 204:
                    return None
                
                return response.json()
                
            except httpx.TimeoutException as e:
                last_exception = TimeoutError(f"Request timeout after {self.timeout}s")
                if attempt == self.max_retries - 1:
                    raise last_exception from e
                    
            except httpx.NetworkError as e:
                last_exception = NetworkError(f"Network error: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise last_exception from e
                    
            except httpx.HTTPStatusError as e:
                # Don't retry client errors (4xx) except 429
                if 400 <= e.response.status_code < 500 and e.response.status_code != 429:
                    self._handle_error(e.response)
                last_exception = e
                if attempt == self.max_retries - 1:
                    self._handle_error(e.response)
        
        # Should never reach here, but just in case
        if last_exception:
            raise last_exception
    
    def _handle_error(self, response: httpx.Response) -> None:
        """Handle error responses from API."""
        try:
            error_data = response.json()
            error_msg = error_data.get("error", {}).get("message", "Unknown error")
            request_id = error_data.get("error", {}).get("request_id")
        except Exception:
            error_msg = response.text or f"HTTP {response.status_code}"
            request_id = None
        
        # Map status codes to exceptions
        if response.status_code == 401:
            raise AuthenticationError(
                error_msg,
                status_code=401,
                response=error_data if 'error_data' in locals() else None,
                request_id=request_id,
            )
        elif response.status_code == 404:
            raise NotFoundError(
                error_msg,
                status_code=404,
                response=error_data if 'error_data' in locals() else None,
                request_id=request_id,
            )
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                error_msg,
                retry_after=int(retry_after) if retry_after else None,
                request_id=request_id,
            )
        elif response.status_code in (400, 422):
            raise ValidationError(
                error_msg,
                status_code=response.status_code,
                response=error_data if 'error_data' in locals() else None,
                request_id=request_id,
            )
        else:
            raise APIError(
                error_msg,
                status_code=response.status_code,
                response=error_data if 'error_data' in locals() else None,
                request_id=request_id,
            )
    
    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()
    
    def __enter__(self) -> "MemoryRelay":
        """Context manager entry."""
        return self
    
    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()
