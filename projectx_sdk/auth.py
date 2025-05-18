"""Authentication functionality for the ProjectX Gateway API."""

from datetime import datetime, timedelta
from typing import Optional

import requests

from projectx_sdk.exceptions import AuthenticationError
from projectx_sdk.utils.constants import ENDPOINTS


class Authenticator:
    """
    Handles authentication and token management for the ProjectX Gateway API.

    Responsible for:
    - Initial authentication with API keys or app credentials
    - Token storage and renewal
    - Providing valid tokens for API requests
    """

    def __init__(
        self,
        base_url: str,
        username: Optional[str] = None,
        api_key: Optional[str] = None,
        password: Optional[str] = None,
        device_id: Optional[str] = None,
        app_id: Optional[str] = None,
        verify_key: Optional[str] = None,
        token: Optional[str] = None,
        timeout: int = 30,
    ):
        """
        Initialize the authenticator.

        Args:
            base_url (str): The base URL for the API environment
            username (str, optional): Username for authentication
            api_key (str, optional): API key for authentication
            password (str, optional): Password for app authentication
            device_id (str, optional): Device ID for app authentication
            app_id (str, optional): App ID for app authentication
            verify_key (str, optional): Verification key for app authentication
            token (str, optional): Existing token to use
            timeout (int, optional): Request timeout in seconds
        """
        self.base_url = base_url
        self.token = token
        self.token_expiry = None if token is None else datetime.now() + timedelta(hours=24)
        self.timeout = timeout

        # Default token expiry is 24 hours from issue
        self.token_lifetime = timedelta(hours=24)

        # Authenticate if credentials are provided and no token exists
        if not self.token:
            if username and api_key:
                self.authenticate_with_key(username, api_key)
            elif username and password and device_id and app_id and verify_key:
                self.authenticate_with_app(username, password, device_id, app_id, verify_key)

    def authenticate_with_key(self, username, api_key):
        """
        Authenticate using username and API key.

        Args:
            username (str): The username
            api_key (str): The API key for authentication

        Returns:
            bool: True if authentication was successful

        Raises:
            AuthenticationError: If authentication fails
        """
        endpoint = f"{self.base_url}{ENDPOINTS['auth']['login_key']}"

        payload = {"userName": username, "apiKey": api_key}

        try:
            response = requests.post(endpoint, json=payload, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            if not data.get("success", False):
                raise AuthenticationError(
                    f"Authentication failed: {data.get('errorMessage', 'Unknown error')}",
                    error_code=data.get("errorCode"),
                )

            self.token = data.get("token")
            self.token_expiry = datetime.now() + self.token_lifetime

            return True

        except requests.RequestException as e:
            raise AuthenticationError(f"Authentication request failed: {str(e)}")

    def authenticate_with_app(self, username, password, device_id, app_id, verify_key):
        """
        Authenticate using application credentials.

        Args:
            username (str): Admin username
            password (str): Admin password
            device_id (str): Device identifier
            app_id (str): Application identifier (GUID)
            verify_key (str): Verification key

        Returns:
            bool: True if authentication was successful

        Raises:
            AuthenticationError: If authentication fails
        """
        endpoint = f"{self.base_url}{ENDPOINTS['auth']['login_app']}"

        payload = {
            "userName": username,
            "password": password,
            "deviceId": device_id,
            "appId": app_id,
            "verifyKey": verify_key,
        }

        try:
            response = requests.post(endpoint, json=payload, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            if not data.get("success", False):
                raise AuthenticationError(
                    f"Authentication failed: {data.get('errorMessage', 'Unknown error')}",
                    error_code=data.get("errorCode"),
                )

            self.token = data.get("token")
            self.token_expiry = datetime.now() + self.token_lifetime

            return True

        except requests.RequestException as e:
            raise AuthenticationError(f"Authentication request failed: {str(e)}")

    def validate_token(self):
        """
        Validate and renew the current token if needed.

        Returns:
            bool: True if validation was successful

        Raises:
            AuthenticationError: If validation fails
        """
        if not self.token:
            raise AuthenticationError("No token available for validation")

        endpoint = f"{self.base_url}{ENDPOINTS['auth']['validate']}"

        try:
            response = requests.post(
                endpoint, headers={"Authorization": f"Bearer {self.token}"}, timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()

            if not data.get("success", False):
                raise AuthenticationError(
                    f"Token validation failed: {data.get('errorMessage', 'Unknown error')}",
                    error_code=data.get("errorCode"),
                )

            # Update token if a new one was provided
            if "newToken" in data and data["newToken"]:
                self.token = data["newToken"]
                self.token_expiry = datetime.now() + self.token_lifetime

            return True

        except requests.RequestException as e:
            raise AuthenticationError(f"Token validation request failed: {str(e)}")

    def get_token(self):
        """
        Get the current authentication token, validating if necessary.

        Returns:
            str: The current authentication token

        Raises:
            AuthenticationError: If no valid token is available
        """
        if not self.is_authenticated():
            if self.token:
                # Try to validate and refresh the token
                self.validate_token()
            else:
                raise AuthenticationError("No authentication token available")
        else:
            # Check if token is close to expiry (less than 30 minutes remaining)
            if self.token_expiry and (self.token_expiry - datetime.now() < timedelta(minutes=30)):
                # Validate to try and get a fresh token
                self.validate_token()

        return self.token

    def get_auth_header(self):
        """
        Get the authentication header with a valid token.

        Returns:
            dict: The Authorization header with the bearer token

        Raises:
            AuthenticationError: If no valid token is available
        """
        token = self.get_token()
        return {"Authorization": f"Bearer {token}"}

    def is_authenticated(self):
        """
        Check if the client is currently authenticated with a valid token.

        Returns:
            bool: True if authenticated with a non-expired token
        """
        return (
            self.token is not None
            and self.token_expiry is not None
            and self.token_expiry > datetime.now()
        )
