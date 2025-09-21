"""Base API client for making HTTP requests with support for all REST methods."""

__all__ = [
    "BaseAPIClient",
    "APIResponse",
    "APIException",
]

import json
from typing import Any, Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from src.core.exceptions import APIException
from src.core.loggers import get_logger


class APIResponse:
    """Wrapper for API responses."""

    def __init__(self, status_code: int, data: Any, headers: Dict[str, str]):
        self.status_code = status_code
        self.data = data
        self.headers = headers

    @property
    def is_success(self) -> bool:
        """Check if the response indicates success (2xx status codes)."""
        return 200 <= self.status_code < 300

    def json(self) -> Any:
        """Get response data as JSON (alias for data property)."""
        return self.data


class BaseAPIClient:
    """A simple, expandable API client with support for all REST methods."""

    def __init__(self, base_url: str, timeout: int = 30, logger_name: Optional[str] = None):
        """
        Initialize the API client.

        Args:
            base_url: The base URL for the API
            timeout: Request timeout in seconds
            logger_name: Optional logger name for this client
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.logger = get_logger(logger_name) if logger_name else get_logger()
        self._default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _build_url(self, endpoint: str) -> str:
        """Build the full URL from base URL and endpoint."""
        return urljoin(f"{self.base_url}/", endpoint.lstrip("/"))

    def _prepare_headers(self, headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Prepare headers by merging default headers with provided ones."""
        final_headers = self._default_headers.copy()
        if headers:
            final_headers.update(headers)
        return final_headers

    def _prepare_data(self, data: Any) -> Optional[bytes]:
        """Prepare request data for sending."""
        if data is None:
            return None

        if isinstance(data, (dict, list)):
            return json.dumps(data).encode("utf-8")
        elif isinstance(data, str):
            return data.encode("utf-8")
        elif isinstance(data, bytes):
            return data
        else:
            return json.dumps(data).encode("utf-8")

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Any = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
    ) -> APIResponse:
        """
        Make an HTTP request.

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE, etc.)
            endpoint: API endpoint
            data: Request body data
            headers: Additional headers
            params: URL query parameters

        Returns:
            APIResponse object with status code, data, and headers

        Raises:
            APIException: If the request fails
        """
        url = self._build_url(endpoint)

        # Add query parameters
        if params:
            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            url = f"{url}?{query_string}"

        prepared_headers = self._prepare_headers(headers)
        prepared_data = self._prepare_data(data)

        self.logger.debug(f"Making {method} request to {url}")

        try:
            request = Request(url=url, data=prepared_data, headers=prepared_headers, method=method)

            with urlopen(request, timeout=self.timeout) as response:
                response_data = response.read().decode("utf-8")

                # Try to parse JSON response
                try:
                    response_data = json.loads(response_data)
                except json.JSONDecodeError:
                    # Keep as string if not valid JSON
                    pass

                # Convert headers to dict
                response_headers = dict(response.headers)

                api_response = APIResponse(status_code=response.status, data=response_data, headers=response_headers)

                self.logger.debug(f"Request successful: {response.status}")
                return api_response

        except HTTPError as e:
            error_data = None
            try:
                error_data = json.loads(e.read().decode("utf-8"))
            except (json.JSONDecodeError, AttributeError):
                pass

            self.logger.error(f"HTTP error {e.code}: {e.reason}")
            raise APIException(message=f"HTTP {e.code}: {e.reason}", status_code=e.code, response_data=error_data)

        except URLError as e:
            self.logger.error(f"URL error: {e.reason}")
            raise APIException(f"Connection error: {e.reason}")

        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            raise APIException(f"Unexpected error: {str(e)}")

    def get(
        self, endpoint: str, params: Optional[Dict[str, str]] = None, headers: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """Make a GET request."""
        return self._make_request("GET", endpoint, params=params, headers=headers)

    def post(
        self,
        endpoint: str,
        data: Any = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
    ) -> APIResponse:
        """Make a POST request."""
        return self._make_request("POST", endpoint, data=data, headers=headers, params=params)

    def put(
        self,
        endpoint: str,
        data: Any = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
    ) -> APIResponse:
        """Make a PUT request."""
        return self._make_request("PUT", endpoint, data=data, headers=headers, params=params)

    def patch(
        self,
        endpoint: str,
        data: Any = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
    ) -> APIResponse:
        """Make a PATCH request."""
        return self._make_request("PATCH", endpoint, data=data, headers=headers, params=params)

    def delete(
        self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """Make a DELETE request."""
        return self._make_request("DELETE", endpoint, headers=headers, params=params)

    def head(
        self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """Make a HEAD request."""
        return self._make_request("HEAD", endpoint, headers=headers, params=params)

    def options(
        self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """Make an OPTIONS request."""
        return self._make_request("OPTIONS", endpoint, headers=headers, params=params)

    def set_default_header(self, key: str, value: str) -> None:
        """Set a default header that will be included in all requests."""
        self._default_headers[key] = value

    def remove_default_header(self, key: str) -> None:
        """Remove a default header."""
        self._default_headers.pop(key, None)

    def set_timeout(self, timeout: int) -> None:
        """Set the request timeout."""
        self.timeout = timeout
