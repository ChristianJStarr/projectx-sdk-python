"""Data models for ProjectX Gateway API."""

from abc import ABC, abstractmethod

from projectx_sdk.models.account import Account, AccountSearchResponse
from projectx_sdk.models.base import BaseResponse
from projectx_sdk.models.contract import Contract, ContractSearchResponse
from projectx_sdk.models.history import Bar, BarResponse
from projectx_sdk.models.order import (
    Order,
    OrderCancellationResponse,
    OrderModificationResponse,
    OrderPlacementResponse,
    OrderSearchResponse,
)
from projectx_sdk.models.position import Position, PositionSearchResponse
from projectx_sdk.models.trade import Trade, TradeSearchResponse


class BaseModel(ABC):
    """
    Base class for API data models.

    All specific API model classes inherit from this base class.
    """

    @classmethod
    @abstractmethod
    def from_dict(cls, data):
        """
        Create a model instance from a dictionary (typically API response data).

        Args:
            data (dict): Dictionary containing model data

        Returns:
            BaseModel: An instance of the model
        """
        pass

    @abstractmethod
    def to_dict(self):
        """
        Convert model to a dictionary for API requests.

        Returns:
            dict: Dictionary representation of the model
        """
        pass


__all__ = [
    "BaseModel",
    "BaseResponse",
    "Account",
    "AccountSearchResponse",
    "Contract",
    "ContractSearchResponse",
    "Bar",
    "BarResponse",
    "Order",
    "OrderSearchResponse",
    "OrderPlacementResponse",
    "OrderCancellationResponse",
    "OrderModificationResponse",
    "Position",
    "PositionSearchResponse",
    "Trade",
    "TradeSearchResponse",
]
