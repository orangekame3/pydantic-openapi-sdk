"""HTTP client with authentication support."""

from typing import Any

import httpx

from .exceptions import ApiError


class AuthPolicy:
    """Base authentication policy."""

    def apply(self, request: httpx.Request) -> httpx.Request:
        """Apply authentication to request."""
        return request


class BearerAuth(AuthPolicy):
    """Bearer token authentication."""

    def __init__(self, token: str):
        self.token = token

    def apply(self, request: httpx.Request) -> httpx.Request:
        request.headers["Authorization"] = f"Bearer {self.token}"
        return request


class ApiKeyAuth(AuthPolicy):
    """API key authentication."""

    def __init__(self, key: str, header_name: str = "X-API-Key"):
        self.key = key
        self.header_name = header_name

    def apply(self, request: httpx.Request) -> httpx.Request:
        request.headers[self.header_name] = self.key
        return request


class BasicAuth(AuthPolicy):
    """Basic authentication."""

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def apply(self, request: httpx.Request) -> httpx.Request:
        import base64

        credentials = base64.b64encode(
            f"{self.username}:{self.password}".encode()
        ).decode()
        request.headers["Authorization"] = f"Basic {credentials}"
        return request


class Client:
    """Synchronous HTTP client."""

    def __init__(
        self,
        base_url: str,
        auth: AuthPolicy | None = None,
        timeout: float | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.auth = auth
        self._client = httpx.Client(timeout=timeout)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self) -> None:
        """Close the client."""
        self._client.close()

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        json: Any | None = None,
    ) -> httpx.Response:
        """Make HTTP request."""
        url = f"{self.base_url}{path}"

        # Build request
        request = httpx.Request(
            method=method,
            url=url,
            params=params,
            headers=headers or {},
            json=json,
        )

        # Apply authentication
        if self.auth:
            request = self.auth.apply(request)

        # Send request
        response = self._client.send(request)

        # Check for errors
        if response.status_code >= 400:
            try:
                body = response.json()
            except Exception:
                body = response.text

            raise ApiError(status_code=response.status_code, body=body)

        return response


class TypedResponse:
    """Typed response wrapper."""

    def __init__(self, status_code: int, headers: dict[str, str], data: Any):
        self.status_code = status_code
        self.headers = headers
        self.data = data
