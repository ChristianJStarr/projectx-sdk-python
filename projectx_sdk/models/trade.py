"""Data models for trade-related API responses."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from projectx_sdk.models.base import BaseResponse


class Trade(BaseModel):
    """
    Trade data model.

    Represents an executed trade (fill) in the ProjectX platform.
    """

    id: int = Field(..., description="The unique trade identifier")
    account_id: int = Field(..., alias="accountId", description="Account ID the trade belongs to")
    contract_id: str = Field(..., alias="contractId", description="Contract ID that was traded")
    creation_timestamp: datetime = Field(
        ..., alias="creationTimestamp", description="When the trade was executed"
    )
    price: float = Field(..., description="Execution price of the trade")
    profit_and_loss: Optional[float] = Field(
        None, alias="profitAndLoss", description="P&L for the trade if it closed a position"
    )
    fees: float = Field(..., description="Fees associated with the trade")
    side: int = Field(..., description="Trade side (0=Buy, 1=Sell)")
    size: int = Field(..., description="Number of contracts traded")
    voided: bool = Field(..., description="Whether the trade was voided/removed")
    order_id: int = Field(
        ..., alias="orderId", description="The order ID that generated this trade"
    )

    class Config:
        """Pydantic model configuration."""

        populate_by_name = True


class TradeSearchResponse(BaseResponse):
    """
    Response model for trade search operations.

    Contains a list of trades matching the search criteria.
    """

    trades: List[Trade] = Field(default_factory=list, description="List of matching trades")
