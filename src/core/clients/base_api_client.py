"""Simple API client for making HTTP requests."""

__all__ = [
    "BaseAPIClient",
    "APIResponse",
    "APIException",
]

import json
from typing import Any, Dict, Optional

import requests

from src.core.exceptions import APIException


class APIResponse:
    """Simple wrapper for API responses."""

    def __init__(self, status_code: int, data: Any):
        self.status_code = status_code
        self.data = data

    @property
    def is_success(self) -> bool:
        """Check if the response indicates success (2xx status codes)."""
        return 200 <= self.status_code < 300

    def get_json(self) -> Any:
        """Parse response data as JSON."""
        if isinstance(self.data, str):
            return json.loads(self.data)
        return self.data

    def get_dict(self) -> Dict[str, Any]:
        """Parse response data as a dictionary."""
        if isinstance(self.data, str):
            parsed = json.loads(self.data)
            if not isinstance(parsed, dict):
                raise ValueError("Response data is not a dictionary")
            return parsed
        elif isinstance(self.data, dict):
            return self.data
        else:
            raise ValueError("Response data is not a dictionary")


class BaseAPIClient:
    """Simple API client for HTTP requests."""

    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _make_request(self, method: str, endpoint: str, **kwargs) -> APIResponse:
        """Make an HTTP request."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            response = requests.request(method, url, timeout=self.timeout, **kwargs)
            response.raise_for_status()

            try:
                data = response.json()
            except ValueError:
                data = response.text

            return APIResponse(response.status_code, data)

        except requests.exceptions.Timeout:
            raise APIException(f"Request timed out after {self.timeout} seconds")
        except requests.exceptions.HTTPError as e:
            raise APIException(f"HTTP {e.response.status_code}: {e.response.reason}")
        except requests.exceptions.ConnectionError:
            raise APIException(f"Connection error to {url}")
        except requests.exceptions.RequestException as e:
            raise APIException(f"Request failed: {str(e)}")

    def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """Make a GET request."""
        return self._make_request("GET", endpoint, params=params, headers=headers)

    def post(
        self,
        endpoint: str,
        data: Any = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> APIResponse:
        """Make a POST request."""
        return self._make_request("POST", endpoint, json=data, headers=headers, params=params)

    def put(
        self,
        endpoint: str,
        data: Any = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> APIResponse:
        """Make a PUT request."""
        return self._make_request("PUT", endpoint, json=data, headers=headers, params=params)

    def patch(
        self,
        endpoint: str,
        data: Any = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> APIResponse:
        """Make a PATCH request."""
        return self._make_request("PATCH", endpoint, json=data, headers=headers, params=params)

    def delete(
        self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None
    ) -> APIResponse:
        """Make a DELETE request."""
        return self._make_request("DELETE", endpoint, headers=headers, params=params)

    def head(
        self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None
    ) -> APIResponse:
        """Make a HEAD request."""
        return self._make_request("HEAD", endpoint, headers=headers, params=params)

    def options(
        self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None
    ) -> APIResponse:
        """Make an OPTIONS request."""
        return self._make_request("OPTIONS", endpoint, headers=headers, params=params)
