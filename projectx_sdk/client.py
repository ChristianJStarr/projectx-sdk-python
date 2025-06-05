"""Main client for ProjectX Gateway API."""

import logging
from typing import Any, Dict, Optional, cast

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
from projectx_sdk.realtime import SyncRealTimeClient

logger = logging.getLogger(__name__)


class ProjectXClient:
    """
    Main client for interacting with the ProjectX Gateway API.

    This client provides access to all the API services and handles authentication,
    session management, and request routing.
    """

    # Map of environment names to base URLs (only new endpoints)
    ENVIRONMENT_URLS = {
        "alphaticks": "https://api.alphaticks.projectx.com",
        "blueguardian": "https://api.blueguardianfutures.projectx.com",
        "blusky": "https://api.blusky.projectx.com",
        "e8x": "https://api.e8.projectx.com",
        "fundingfutures": "https://api.fundingfutures.projectx.com",
        "thefuturesdesk": "https://api.thefuturesdesk.projectx.com",
        "futureselite": "https://api.futureselite.projectx.com",
        "fxifyfutures": "https://api.fxifyfutures.projectx.com",
        "goatfunded": "https://api.goatfundedfutures.projectx.com",
        "tickticktrader": "https://api.tickticktrader.projectx.com",
        "toponefutures": "https://api.toponefutures.projectx.com",
        "topstepx": "https://api.topstepx.com",
        "tx3funding": "https://api.tx3funding.projectx.com",
        # For testing/demo
        "demo": "https://gateway-api-demo.s2f.projectx.com",
    }

    # Map of environment names to user hub URLs (only new endpoints)
    USER_HUB_URLS = {
        "alphaticks": "https://rtc.alphaticks.projectx.com/hubs/user",
        "blueguardian": "https://rtc.blueguardianfutures.projectx.com/hubs/user",
        "blusky": "https://rtc.blusky.projectx.com/hubs/user",
        "e8x": "https://rtc.e8.projectx.com/hubs/user",
        "fundingfutures": "https://rtc.fundingfutures.projectx.com/hubs/user",
        "thefuturesdesk": "https://rtc.thefuturesdesk.projectx.com/hubs/user",
        "futureselite": "https://rtc.futureselite.projectx.com/hubs/user",
        "fxifyfutures": "https://rtc.fxifyfutures.projectx.com/hubs/user",
        "goatfunded": "https://rtc.goatfundedfutures.projectx.com/hubs/user",
        "tickticktrader": "https://rtc.tickticktrader.projectx.com/hubs/user",
        "toponefutures": "https://rtc.toponefutures.projectx.com/hubs/user",
        "topstepx": "https://rtc.topstepx.com/hubs/user",
        "tx3funding": "https://rtc.tx3funding.projectx.com/hubs/user",
        # For testing/demo
        "demo": "https://gateway-api-demo.s2f.projectx.com/hubs/user",
    }

    # Map of environment names to market hub URLs (only new endpoints)
    MARKET_HUB_URLS = {
        "alphaticks": "https://rtc.alphaticks.projectx.com/hubs/market",
        "blueguardian": "https://rtc.blueguardianfutures.projectx.com/hubs/market",
        "blusky": "https://rtc.blusky.projectx.com/hubs/market",
        "e8x": "https://rtc.e8.projectx.com/hubs/market",
        "fundingfutures": "https://rtc.fundingfutures.projectx.com/hubs/market",
        "thefuturesdesk": "https://rtc.thefuturesdesk.projectx.com/hubs/market",
        "futureselite": "https://rtc.futureselite.projectx.com/hubs/market",
        "fxifyfutures": "https://rtc.fxifyfutures.projectx.com/hubs/market",
        "goatfunded": "https://rtc.goatfundedfutures.projectx.com/hubs/market",
        "tickticktrader": "https://rtc.tickticktrader.projectx.com/hubs/market",
        "toponefutures": "https://rtc.toponefutures.projectx.com/hubs/market",
        "topstepx": "https://rtc.topstepx.com/hubs/market",
        "tx3funding": "https://rtc.tx3funding.projectx.com/hubs/market",
        # For testing/demo
        "demo": "https://gateway-api-demo.s2f.projectx.com/hubs/market",
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
        self._realtime: Optional[SyncRealTimeClient] = None

    @property
    def realtime(self) -> SyncRealTimeClient:
        """
        Get the real-time client for WebSocket connections.

        This is lazy-initialized on first access.

        Returns:
            The real-time client
        """
        if not self._realtime:
            token = self.auth.get_token()
            self._realtime = SyncRealTimeClient(
                auth_token=token,
                environment=self.environment,
                user_hub_url=self.USER_HUB_URLS.get(self.environment),
                market_hub_url=self.MARKET_HUB_URLS.get(self.environment),
            )
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
                json_data = response.json()
            except ValueError:
                raise RequestError(f"Invalid JSON response: {response.text}")

            # Defensive check: ensure we got a dictionary (handles None case for mypy)
            if json_data is None:
                raise ProjectXError("Received null response from API")

            # Safe to cast now that we've checked
            response_data: Dict[str, Any] = cast(Dict[str, Any], json_data)

            # Check for API-level errors
            success = response_data.get("success", True)  # type: ignore[union-attr]
            if not success:
                error_code = response_data.get("errorCode", 0)  # type: ignore[union-attr]
                err_msg = response_data.get(  # type: ignore[union-attr]
                    "errorMessage", "Unknown error"
                )

                raise ProjectXError(
                    f"API error {error_code}: {err_msg}",
                    error_code=error_code,
                    response=response_data,
                )

            return response_data

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
        # Use the generic request method with the DELETE HTTP method
        return self.request("DELETE", path, **kwargs)
