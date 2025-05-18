"""Service modules for ProjectX Gateway API endpoints."""

from abc import ABC


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


# Import service classes after BaseService is defined to avoid circular imports
from projectx_sdk.endpoints.account import AccountService  # noqa: E402
from projectx_sdk.endpoints.contract import ContractService  # noqa: E402
from projectx_sdk.endpoints.history import HistoryService, TimeUnit  # noqa: E402
from projectx_sdk.endpoints.order import OrderService  # noqa: E402
from projectx_sdk.endpoints.position import PositionService  # noqa: E402
from projectx_sdk.endpoints.trade import TradeService  # noqa: E402

__all__ = [
    "BaseService",
    "AccountService",
    "ContractService",
    "HistoryService",
    "OrderService",
    "PositionService",
    "TradeService",
    "TimeUnit",
]
