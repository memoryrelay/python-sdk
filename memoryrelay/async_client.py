"""
Async MemoryRelay Python SDK - Async Client

Async/await version of the MemoryRelay client for use with asyncio.
"""

import logging
import asyncio
from typing import Any, Dict, List, Optional, Union

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
from memoryrelay.resources.async_memories import AsyncMemoriesResource
from memoryrelay.resources.async_entities import AsyncEntitiesResource
from memoryrelay.resources.async_agents import AsyncAgentsResource
from memoryrelay.types import HealthStatus

logger = logging.getLogger("memoryrelay.async")


class AsyncMemoryRelay:
    """
    Async MemoryRelay API Client.
    
    Usage:
        >>> client = AsyncMemoryRelay(api_key="mem_...")
        >>> 
        >>> # Create a memory
        >>> memory = await client.memories.create(
        ...     content="User prefers dark mode",
        ...     agent_id="my-agent"
        ... )
        >>> 
        >>> # Search memories
        >>> results = await client.memories.search(
        ...     query="user preferences",
        ...     limit=5
        ... )
        >>> 
        >>> # Batch create
        >>> response = await client.memories.create_batch([
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
        Initialize AsyncMemoryRelay client.
        
        Args:
            api_key: Your MemoryRelay API key (required)
            base_url: API base URL (default: https://api.memoryrelay.net)
            timeout: Request timeout in seconds (default: 30.0)
            max_retries: Maximum number of retries for failed requests (default: 3)
            **kwargs: Additional arguments passed to httpx.AsyncClient
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        
        logger.debug(
            f"Initializing AsyncMemoryRelay client: base_url={self.base_url}, "
            f"timeout={timeout}s, max_retries={max_retries}"
        )
        
        # Import version dynamically to avoid circular imports
        try:
            from memoryrelay import __version__
            user_agent = f"memoryrelay-python-async/{__version__}"
        except ImportError:
            user_agent = "memoryrelay-python-async/0.1.0"
        
        # Create async HTTP client
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers={
                "X-API-Key": api_key,
                "User-Agent": user_agent,
            },
            **kwargs,
        )
        
        # Initialize resource clients
        self.memories = AsyncMemoriesResource(self)
        self.entities = AsyncEntitiesResource(self)
        self.agents = AsyncAgentsResource(self)
    
    async def health(self) -> HealthStatus:
        """
        Check API health status.
        
        Returns:
            HealthStatus object with service information
            
        Example:
            >>> health = await client.health()
            >>> print(health.status)  # "healthy"
            >>> print(health.services)  # {"database": "up", ...}
        """
        response = await self._request("GET", "/v1/health")
        return HealthStatus(**response)
    
    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Union[Dict[str, Any], List[Any], None]:
        """
        Make an async HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            path: API endpoint path
            json: JSON body for request
            params: Query parameters
            headers: Additional headers
            
        Returns:
            Parsed JSON response (dict, list, or None for 204)
            
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
        
        # Retry logic with exponential backoff
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                logger.debug(
                    f"{method} {path} (attempt {attempt + 1}/{self.max_retries})"
                )
                
                response = await self._client.request(
                    method=method,
                    url=path,
                    json=json,
                    params=params,
                    headers=req_headers,
                )
                
                logger.debug(
                    f"Response: {response.status_code} "
                    f"({response.elapsed.total_seconds():.3f}s)"
                )
                
                # Handle errors
                if response.status_code >= 400:
                    self._handle_error(response)
                
                # Parse response
                if response.status_code == 204:
                    return None
                
                return response.json()
                
            except httpx.TimeoutException as e:
                logger.warning(f"Request timeout: {e}")
                last_exception = TimeoutError(f"Request timeout after {self.timeout}s")
                if attempt == self.max_retries - 1:
                    raise last_exception from e
                # Exponential backoff
                await asyncio.sleep(2 ** attempt)
                    
            except httpx.NetworkError as e:
                logger.warning(f"Network error: {e}")
                last_exception = NetworkError(f"Network error: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise last_exception from e
                # Exponential backoff
                await asyncio.sleep(2 ** attempt)
                    
            except RateLimitError as e:
                logger.warning(
                    f"Rate limited: {e.message} "
                    f"(retry_after={e.retry_after}s)"
                )
                # Don't retry on last attempt
                if attempt == self.max_retries - 1:
                    raise
                # Respect Retry-After header
                wait_time = e.retry_after if e.retry_after else (2 ** attempt)
                logger.debug(f"Waiting {wait_time}s before retry...")
                await asyncio.sleep(wait_time)
                    
            except httpx.HTTPStatusError as e:
                # Don't retry client errors (4xx) except 429
                if 400 <= e.response.status_code < 500 and e.response.status_code != 429:
                    self._handle_error(e.response)
                
                logger.warning(f"HTTP error: {e.response.status_code}")
                last_exception = e
                
                # Don't retry on last attempt
                if attempt == self.max_retries - 1:
                    self._handle_error(e.response)
                
                # Exponential backoff for 5xx errors
                await asyncio.sleep(2 ** attempt)
        
        # Should never reach here, but just in case
        if last_exception:
            raise last_exception
    
    def _handle_error(self, response: httpx.Response) -> None:
        """Handle error responses from API."""
        error_data: Optional[Dict[str, Any]] = None
        
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
                response=error_data,
                request_id=request_id,
            )
        elif response.status_code == 404:
            raise NotFoundError(
                error_msg,
                status_code=404,
                response=error_data,
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
                response=error_data,
                request_id=request_id,
            )
        else:
            raise APIError(
                error_msg,
                status_code=response.status_code,
                response=error_data,
                request_id=request_id,
            )
    
    async def aclose(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()
    
    async def __aenter__(self) -> "AsyncMemoryRelay":
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        await self.aclose()
