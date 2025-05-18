"""Tests for the authentication module."""

from datetime import datetime, timedelta

import pytest

from projectx_sdk.auth import Authenticator
from projectx_sdk.exceptions import AuthenticationError
from projectx_sdk.utils.constants import ENDPOINTS


class TestAuthenticator:
    """Tests for the Authenticator class."""

    def test_init(self):
        """Test authenticator initialization."""
        base_url = "https://test-api.example.com"
        auth = Authenticator(base_url)

        assert auth.base_url == base_url
        assert auth.token is None
        assert auth.token_expiry is None
        assert auth.token_lifetime == timedelta(hours=24)

    def test_authenticate_with_key_success(self, mock_responses, api_base_url, auth_token):
        """Test successful authentication with API key."""
        auth = Authenticator(api_base_url)

        # Mock the auth response
        mock_responses.add(
            mock_responses.POST,
            f"{api_base_url}{ENDPOINTS['auth']['login_key']}",
            json={"token": auth_token, "success": True, "errorCode": 0, "errorMessage": None},
            status=200,
        )

        # Authenticate
        result = auth.authenticate_with_key("test_user", "test_api_key")

        # Check the result
        assert result is True
        assert auth.token == auth_token
        assert auth.token_expiry is not None

        # Token should be valid for about 24 hours (within a small margin)
        expected_expiry = datetime.now() + timedelta(hours=24)
        expiry_diff = abs((auth.token_expiry - expected_expiry).total_seconds())
        assert expiry_diff < 10  # Within 10 seconds

    def test_authenticate_with_key_api_error(self, mock_responses, api_base_url):
        """Test handling API errors during authentication."""
        auth = Authenticator(api_base_url)

        # Mock an error response
        mock_responses.add(
            mock_responses.POST,
            f"{api_base_url}{ENDPOINTS['auth']['login_key']}",
            json={
                "token": None,
                "success": False,
                "errorCode": 1001,
                "errorMessage": "Invalid credentials",
            },
            status=200,
        )

        # Try to authenticate - should raise an exception
        with pytest.raises(AuthenticationError) as excinfo:
            auth.authenticate_with_key("test_user", "wrong_api_key")

        # Check the exception details
        assert "Invalid credentials" in str(excinfo.value)
        assert excinfo.value.error_code == 1001

        # Token should still be None
        assert auth.token is None
        assert auth.token_expiry is None

    def test_authenticate_with_key_request_error(self, mock_responses, api_base_url):
        """Test handling request errors during authentication."""
        auth = Authenticator(api_base_url)

        # Mock a network error using the more compatible approach
        mock_responses.add(
            mock_responses.POST,
            f"{api_base_url}{ENDPOINTS['auth']['login_key']}",
            status=502,
            json={"error": "Bad Gateway"},
        )

        # Try to authenticate - should raise an exception
        with pytest.raises(AuthenticationError) as excinfo:
            auth.authenticate_with_key("test_user", "test_api_key")

        # Check that it mentions a request failure
        assert "request failed" in str(excinfo.value).lower()

        # Token should still be None
        assert auth.token is None
        assert auth.token_expiry is None

    def test_authenticate_with_app_success(self, mock_responses, api_base_url, auth_token):
        """Test successful authentication with app credentials."""
        auth = Authenticator(api_base_url)

        # Mock the auth response
        mock_responses.add(
            mock_responses.POST,
            f"{api_base_url}{ENDPOINTS['auth']['login_app']}",
            json={"token": auth_token, "success": True, "errorCode": 0, "errorMessage": None},
            status=200,
        )

        # Authenticate
        result = auth.authenticate_with_app(
            username="test_user",
            password="test_password",
            device_id="test_device",
            app_id="test_app",
            verify_key="test_key",
        )

        # Check the result
        assert result is True
        assert auth.token == auth_token
        assert auth.token_expiry is not None

    def test_validate_token_success(self, mock_responses, api_base_url, auth_token):
        """Test successful token validation."""
        auth = Authenticator(api_base_url)

        # Set an initial token
        auth.token = auth_token
        auth.token_expiry = datetime.now() + timedelta(hours=1)

        # Mock the validate response with a new token
        new_token = f"{auth_token}.new"
        mock_responses.add(
            mock_responses.POST,
            f"{api_base_url}{ENDPOINTS['auth']['validate']}",
            json={"success": True, "errorCode": 0, "errorMessage": None, "newToken": new_token},
            status=200,
        )

        # Validate the token
        result = auth.validate_token()

        # Check the result
        assert result is True
        assert auth.token == new_token  # Token should be updated

    def test_validate_token_no_token(self):
        """Test validation with no token set."""
        auth = Authenticator("https://test-api.example.com")

        with pytest.raises(AuthenticationError) as excinfo:
            auth.validate_token()

        assert "No token available" in str(excinfo.value)

    def test_validate_token_api_error(self, mock_responses, api_base_url, auth_token):
        """Test handling API errors during token validation."""
        auth = Authenticator(api_base_url)

        # Set an initial token
        auth.token = auth_token
        auth.token_expiry = datetime.now() + timedelta(hours=1)

        # Mock an error response
        mock_responses.add(
            mock_responses.POST,
            f"{api_base_url}{ENDPOINTS['auth']['validate']}",
            json={
                "success": False,
                "errorCode": 1002,
                "errorMessage": "Token expired",
                "newToken": None,
            },
            status=200,
        )

        # Try to validate - should raise an exception
        with pytest.raises(AuthenticationError) as excinfo:
            auth.validate_token()

        # Check the exception details
        assert "Token expired" in str(excinfo.value)
        assert excinfo.value.error_code == 1002

    def test_get_auth_header_no_token(self):
        """Test getting auth header with no token set."""
        auth = Authenticator("https://test-api.example.com")

        with pytest.raises(AuthenticationError) as excinfo:
            auth.get_auth_header()

        assert "No authentication token available" in str(excinfo.value)

    def test_get_auth_header_with_token(self, auth_token):
        """Test getting auth header with a valid token."""
        auth = Authenticator("https://test-api.example.com")

        # Set a token
        auth.token = auth_token
        auth.token_expiry = datetime.now() + timedelta(hours=1)

        # Get the header
        header = auth.get_auth_header()

        # Check the header
        assert header == {"Authorization": f"Bearer {auth_token}"}

    def test_get_auth_header_expiring_soon(self, auth_token):
        """Test getting auth header with a token expiring soon."""
        auth = Authenticator("https://test-api.example.com")

        # Set a token that expires soon (15 minutes from now)
        auth.token = auth_token
        auth.token_expiry = datetime.now() + timedelta(minutes=15)  # Less than 30 minutes

        # Mock the validate_token method with a spy
        validate_called = [False]  # Use a list to be mutable in the inner function

        def spy_validate_token():
            validate_called[0] = True
            return True

        auth.validate_token = spy_validate_token

        # Get the header - should trigger a token validation
        header = auth.get_auth_header()

        # Check if validate_token was called
        assert validate_called[0] is True, "validate_token was not called"

        # Check the header
        assert header == {"Authorization": f"Bearer {auth_token}"}

    def test_is_authenticated(self, auth_token):
        """Test checking authentication status."""
        auth = Authenticator("https://test-api.example.com")

        # Initially should not be authenticated
        assert auth.is_authenticated() is False

        # Set a valid token
        auth.token = auth_token
        auth.token_expiry = datetime.now() + timedelta(hours=1)

        # Now should be authenticated
        assert auth.is_authenticated() is True

        # Set an expired token
        auth.token_expiry = datetime.now() - timedelta(hours=1)

        # Should no longer be authenticated
        assert auth.is_authenticated() is False
