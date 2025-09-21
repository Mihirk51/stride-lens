__all__ = [
    "APIException",
]

from typing import Any, Optional


class APIException(Exception):
    """Custom exception for API errors."""

    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Any] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data
