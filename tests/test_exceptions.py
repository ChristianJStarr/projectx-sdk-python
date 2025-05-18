"""Tests for the exceptions module."""

from requests import Response

from projectx_sdk.exceptions import (
    APIError,
    AuthenticationError,
    ConnectionError,
    ProjectXError,
    RateLimitError,
    ValidationError,
)


class TestExceptions:
    """Tests for the custom exception classes."""

    def test_base_error(self):
        """Test the base ProjectXError class."""
        error = ProjectXError("Test error message")

        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.error_code is None
        assert error.response is None

    def test_base_error_with_code(self):
        """Test ProjectXError with an error code."""
        error = ProjectXError("Test error message", error_code=1001)

        assert str(error) == "[Error 1001] Test error message"
        assert error.message == "Test error message"
        assert error.error_code == 1001
        assert error.response is None

    def test_base_error_with_response(self):
        """Test ProjectXError with a response object."""
        response = Response()
        error = ProjectXError("Test error message", response=response)

        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.error_code is None
        assert error.response is response

    def test_authentication_error(self):
        """Test the AuthenticationError class."""
        error = AuthenticationError("Authentication failed")

        assert str(error) == "Authentication failed"
        assert error.message == "Authentication failed"
        assert error.error_code is None
        assert error.response is None

        # Check inheritance
        assert isinstance(error, ProjectXError)

    def test_api_error(self):
        """Test the APIError class."""
        error = APIError("API error", error_code=1002)

        assert str(error) == "[Error 1002] API error"
        assert error.message == "API error"
        assert error.error_code == 1002
        assert error.response is None

        # Check inheritance
        assert isinstance(error, ProjectXError)

    def test_connection_error(self):
        """Test the ConnectionError class."""
        error = ConnectionError("Connection failed")

        assert str(error) == "Connection failed"
        assert error.message == "Connection failed"
        assert error.error_code is None
        assert error.response is None

        # Check inheritance
        assert isinstance(error, ProjectXError)

    def test_rate_limit_error(self):
        """Test the RateLimitError class."""
        error = RateLimitError("Rate limit exceeded", error_code=429)

        assert str(error) == "[Error 429] Rate limit exceeded"
        assert error.message == "Rate limit exceeded"
        assert error.error_code == 429
        assert error.response is None

        # Check inheritance
        assert isinstance(error, ProjectXError)

    def test_validation_error(self):
        """Test the ValidationError class."""
        error = ValidationError("Invalid parameters")

        assert str(error) == "Invalid parameters"
        assert error.message == "Invalid parameters"
        assert error.error_code is None
        assert error.response is None

        # Check inheritance
        assert isinstance(error, ProjectXError)
