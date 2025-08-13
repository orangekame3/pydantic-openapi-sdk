"""API exceptions."""

from typing import Any


class ApiError(Exception):
    """Base API error."""

    def __init__(self, status_code: int, body: Any, message: str = None):
        self.status_code = status_code
        self.body = body
        self.message = message or f"API error {status_code}"
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"ApiError({self.status_code}): {self.message}"