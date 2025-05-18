"""Main client for ProjectX Gateway API."""

import logging
from typing import Any, Dict, Optional

import requests

from projectx_sdk.auth import Authenticator
from projectx_sdk.endpoints import (
    AccountService,
    ContractService,
    HistoryService,
    OrderService,
    PositionService,
    TradeService,
)
from projectx_sdk.exceptions import (
    AuthenticationError,
    ProjectXError,
    RequestError,
    ResourceNotFoundError,
)
from projectx_sdk.realtime import RealTimeClient

logger = logging.getLogger(__name__)


class ProjectXClient:
    """
    Main client for interacting with the ProjectX Gateway API.

    This client provides access to all the API services and handles authentication,
    session management, and request routing.
    """

    # Map of environment names to base URLs
    ENVIRONMENT_URLS = {
        "alphaticks": "https://gateway-api-alphaticks.s2f.projectx.com",
        "blueguardian": "https://gateway-api-blueguardian.s2f.projectx.com",
        "blusky": "https://gateway-api-blusky.s2f.projectx.com",
        "e8x": "https://gateway-api-e8x.s2f.projectx.com",
        "fundingfutures": "https://gateway-api-fundingfutures.s2f.projectx.com",
        "thefuturesdesk": "https://gateway-api-thefuturesdesk.s2f.projectx.com",
        "futureselite": "https://gateway-api-futureselite.s2f.projectx.com",
        "fxifyfutures": "https://gateway-api-fxifyfutures.s2f.projectx.com",
        "goatfunded": "https://gateway-api-goatfunded.s2f.projectx.com",
        "tickticktrader": "https://gateway-api-tickticktrader.s2f.projectx.com",
        "toponefutures": "https://gateway-api-toponefutures.s2f.projectx.com",
        "topstepx": "https://gateway-api-topstepx.s2f.projectx.com",
        "tx3funding": "https://gateway-api-tx3funding.s2f.projectx.com",
        # For testing/demo
        "demo": "https://gateway-api-demo.s2f.projectx.com",
    }

    def __init__(
        self,
        username: Optional[str] = None,
        api_key: Optional[str] = None,
        password: Optional[str] = None,
        device_id: Optional[str] = None,
        app_id: Optional[str] = None,
        verify_key: Optional[str] = None,
        environment: str = "demo",
        token: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
    ):
        """
        Initialize a new ProjectX client.

        There are multiple authentication methods:
        1. Using username + api_key (standard API key auth)
        2. Using username + password + device_id + app_id + verify_key (application auth)
        3. Using an existing token directly

        Args:
            username: User's username
            api_key: User's API key (for API key auth)
            password: User's password (for application auth)
            device_id: Device ID (for application auth)
            app_id: Application ID (for application auth)
            verify_key: Verification key (for application auth)
            environment: Environment name (e.g., 'topstepx', 'demo', etc.)
            token: Existing auth token (if you already have one)
            base_url: Override the base URL (if not using an environment)
            timeout: Request timeout in seconds
        """
        # Set up the base URL
        if base_url:
            self.base_url = base_url
        elif environment in self.ENVIRONMENT_URLS:
            self.base_url = self.ENVIRONMENT_URLS[environment]
        else:
            raise ValueError(f"Unknown environment: {environment}. Use base_url parameter instead.")

        self.environment = environment
        self.timeout = timeout

        # Set up the authenticator
        self.auth = Authenticator(
            base_url=self.base_url,
            username=username,
            api_key=api_key,
            password=password,
            device_id=device_id,
            app_id=app_id,
            verify_key=verify_key,
            token=token,
            timeout=timeout,
        )

        # Initialize service endpoints
        self.accounts = AccountService(self)
        self.contracts = ContractService(self)
        self.history = HistoryService(self)
        self.orders = OrderService(self)
        self.positions = PositionService(self)
        self.trades = TradeService(self)

        # Real-time client (lazy-initialized)
        self._realtime = None

    @property
    def realtime(self) -> RealTimeClient:
        """
        Get the real-time client for WebSocket connections.

        This is lazy-initialized on first access.

        Returns:
            The real-time client
        """
        if not self._realtime:
            token = self.auth.get_token()
            self._realtime = RealTimeClient(auth_token=token, environment=self.environment)
        return self._realtime

    def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API.

        Args:
            method: HTTP method ('GET', 'POST', etc.)
            path: API path (will be appended to base URL)
            params: Query parameters
            data: Request body (form data)
            json: Request body (JSON data)
            headers: Additional headers
            timeout: Request timeout (overrides client timeout)

        Returns:
            The parsed JSON response

        Raises:
            AuthenticationError: If authentication fails
            RequestError: If the request fails
            ResourceNotFoundError: If the resource is not found
            ProjectXError: For other API errors
        """
        # Make sure we have a token
        token = self.auth.get_token()

        # Prepare the request URL and headers
        # Ensure path doesn't start with '/api/' since we'll add it
        if path.startswith("/api/"):
            path = path[5:]  # Remove the leading '/api/'
        elif path.startswith("api/"):
            path = path[4:]  # Remove the leading 'api/'

        url = f"{self.base_url}/api/{path}"
        request_headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}

        if headers:
            request_headers.update(headers)

        request_timeout = timeout if timeout is not None else self.timeout

        try:
            response = requests.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json,
                headers=request_headers,
                timeout=request_timeout,
            )

            # Handle response errors
            if response.status_code == 401:
                raise AuthenticationError("Authentication failed: Invalid or expired token")

            if response.status_code == 404:
                raise ResourceNotFoundError(f"Resource not found: {path}")

            if response.status_code >= 400:
                error_data = {}
                try:
                    error_data = response.json()
                except Exception:
                    pass

                message = f"API request failed with status {response.status_code}"
                if error_data and "errorMessage" in error_data:
                    message = f"{message}: {error_data['errorMessage']}"

                raise RequestError(message, error_code=response.status_code, response=error_data)

            # Parse the response
            try:
                data = response.json()
            except ValueError:
                raise RequestError(f"Invalid JSON response: {response.text}")

            # Check for API-level errors
            if not data.get("success", True):
                error_code = data.get("errorCode", 0)
                error_message = data.get("errorMessage", "Unknown error")
                raise ProjectXError(
                    f"API error {error_code}: {error_message}", error_code=error_code, response=data
                )

            return data

        except requests.RequestException as e:
            raise RequestError(f"Request failed: {str(e)}")

    def get(self, path: str, **kwargs) -> Dict[str, Any]:
        """Make a GET request to the API."""
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> Dict[str, Any]:
        """Make a POST request to the API."""
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs) -> Dict[str, Any]:
        """Make a PUT request to the API."""
        return self.request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs) -> Dict[str, Any]:
        """Make a DELETE request to the API."""
        return self.request("DELETE", path, **kwargs)
