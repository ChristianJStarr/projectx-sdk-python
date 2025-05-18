"""ProjectX SDK custom exceptions."""


class ProjectXError(Exception):
    """Base exception for all ProjectX SDK errors."""

    def __init__(self, message, error_code=None, response=None):
        """
        Initialize a ProjectXError.

        Args:
            message: Error message
            error_code: Optional error code
            response: Optional response data
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.response = response

    def __str__(self):
        """
        Get string representation of the error.

        Returns:
            String representation including error code if available
        """
        if self.error_code:
            return f"[Error {self.error_code}] {self.message}"
        return self.message


class AuthenticationError(ProjectXError):
    """Authentication-related errors."""

    pass


class APIError(ProjectXError):
    """Errors returned by the API."""

    pass


class ConnectionError(ProjectXError):
    """Connection-related errors."""

    pass


class RateLimitError(ProjectXError):
    """Rate limiting errors."""

    pass


class ValidationError(ProjectXError):
    """Input validation errors."""

    pass


class RequestError(ProjectXError):
    """General request errors."""

    pass


class ResourceNotFoundError(ProjectXError):
    """Resource not found errors (404)."""

    pass
