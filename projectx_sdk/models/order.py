"""Data models for order-related API responses."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from projectx_sdk.models.base import BaseResponse


class Order(BaseModel):
    """
    Order data model.

    Represents a trading order in the ProjectX platform.
    """

    id: int = Field(..., description="The unique order identifier")
    account_id: int = Field(..., alias="accountId", description="Account ID the order belongs to")
    contract_id: str = Field(..., alias="contractId", description="Contract ID the order is for")
    creation_timestamp: datetime = Field(
        ..., alias="creationTimestamp", description="When the order was created"
    )
    update_timestamp: Optional[datetime] = Field(
        None, alias="updateTimestamp", description="When the order was last updated"
    )
    status: int = Field(..., description="Order status code")
    type: int = Field(..., description="Order type code")
    side: int = Field(..., description="Order side (0=Buy, 1=Sell)")
    size: int = Field(..., description="Order quantity")
    limit_price: Optional[float] = Field(
        None, alias="limitPrice", description="Limit price for limit orders"
    )
    stop_price: Optional[float] = Field(
        None, alias="stopPrice", description="Stop price for stop orders"
    )
    trail_price: Optional[float] = Field(
        None, alias="trailPrice", description="Trail amount for trailing stop orders"
    )
    custom_tag: Optional[str] = Field(
        None, alias="customTag", description="User-defined tag for the order"
    )
    linked_order_id: Optional[int] = Field(
        None, alias="linkedOrderId", description="ID of a linked order"
    )

    class Config:
        """Pydantic model configuration."""

        populate_by_name = True


class OrderSearchResponse(BaseResponse):
    """
    Response model for order search operations.

    Contains a list of orders matching the search criteria.
    """

    orders: List[Order] = Field(default_factory=list, description="List of matching orders")


class OrderPlacementResponse(BaseResponse):
    """
    Response model for order placement operations.

    Contains the ID of the newly placed order.
    """

    order_id: int = Field(0, alias="orderId", description="ID of the newly placed order")

    class Config:
        """Pydantic model configuration."""

        populate_by_name = True


class OrderCancellationResponse(BaseResponse):
    """
    Response model for order cancellation operations.

    Contains only success/error information.
    """

    pass


class OrderModificationResponse(BaseResponse):
    """
    Response model for order modification operations.

    Contains only success/error information.
    """

    pass
