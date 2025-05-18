"""
ProjectX Gateway API SDK for Python.

A Python client library for interacting with the ProjectX Gateway API.
"""

__version__ = "0.1.0"

from projectx_sdk.client import ProjectXClient
from projectx_sdk.endpoints.history import TimeUnit
from projectx_sdk.exceptions import (
    AuthenticationError,
    ProjectXError,
    RequestError,
    ResourceNotFoundError,
)
from projectx_sdk.realtime import RealTimeClient
from projectx_sdk.utils.constants import OrderSide, OrderType

__all__ = [
    "ProjectXClient",
    "RealTimeClient",
    "OrderType",
    "OrderSide",
    "TimeUnit",
    "ProjectXError",
    "AuthenticationError",
    "RequestError",
    "ResourceNotFoundError",
]
