"""Custom error types for the backend.

Defining a structured hierarchy of exceptions helps categorise errors and
improve error handling consistency.  Downstream code can catch these
exceptions to return appropriate HTTP responses.
"""

from fastapi import HTTPException, status


class IntentParsingError(HTTPException):
    """Raised when the intent parser fails to understand the user's request."""

    def __init__(self, detail: str = "Failed to parse intent") -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class SimulationError(HTTPException):
    """Raised when a transaction simulation cannot be completed."""

    def __init__(self, detail: str = "Simulation failed") -> None:
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


class ExecutionError(HTTPException):
    """Raised when a transaction execution fails."""

    def __init__(self, detail: str = "Execution failed") -> None:
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


class RateLimitExceeded(HTTPException):
    """Raised when a client exceeds the allowed request rate."""

    def __init__(self, detail: str = "Rate limit exceeded") -> None:
        super().__init__(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=detail)