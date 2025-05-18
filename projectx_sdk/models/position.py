from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from projectx_sdk.models.base import BaseResponse


class Position(BaseModel):
    """
    Position data model.

    Represents a trading position (open holding) in the ProjectX platform.
    """

    id: int = Field(..., description="The unique position identifier")
    account_id: int = Field(
        ..., alias="accountId", description="Account ID the position belongs to"
    )
    contract_id: str = Field(..., alias="contractId", description="Contract ID of the position")
    creation_timestamp: datetime = Field(
        ..., alias="creationTimestamp", description="When the position was opened"
    )
    type: int = Field(..., description="Position type code")
    size: int = Field(
        ..., description="Position size/quantity (positive for long, negative for short)"
    )
    average_price: float = Field(
        ..., alias="averagePrice", description="Average entry price of the position"
    )

    class Config:
        """Pydantic model configuration."""

        populate_by_name = True


class PositionSearchResponse(BaseResponse):
    """
    Response model for position search operations.

    Contains a list of positions matching the search criteria.
    """

    positions: List[Position] = Field(
        default_factory=list, description="List of matching positions"
    )
