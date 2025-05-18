"""Service modules for ProjectX Gateway API endpoints."""

from abc import ABC

from projectx_sdk.endpoints.account import AccountService
from projectx_sdk.endpoints.contract import ContractService
from projectx_sdk.endpoints.history import HistoryService, TimeUnit
from projectx_sdk.endpoints.order import OrderService
from projectx_sdk.endpoints.position import PositionService
from projectx_sdk.endpoints.trade import TradeService


class BaseService(ABC):
    """
    Base class for API service endpoints.

    All specific API service classes inherit from this base class.
    """

    def __init__(self, client):
        """
        Initialize a service with a reference to the client.

        Args:
            client: The ProjectXClient instance
        """
        self._client = client


__all__ = [
    "AccountService",
    "ContractService",
    "HistoryService",
    "OrderService",
    "PositionService",
    "TradeService",
    "TimeUnit",
]
