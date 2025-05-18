"""Data models for historical market data API responses."""

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from projectx_sdk.models.base import BaseResponse


class Bar(BaseModel):
    """
    Market data bar (candle) model.

    Represents OHLCV (Open, High, Low, Close, Volume) data for a time period.
    """

    timestamp: datetime = Field(..., alias="t", description="Timestamp of the bar")
    open: float = Field(..., alias="o", description="Opening price")
    high: float = Field(..., alias="h", description="Highest price during the period")
    low: float = Field(..., alias="l", description="Lowest price during the period")
    close: float = Field(..., alias="c", description="Closing price")
    volume: int = Field(..., alias="v", description="Trading volume during the period")

    class Config:
        """Pydantic model configuration."""

        populate_by_name = True


class BarResponse(BaseResponse):
    """
    Response model for historical bar data requests.

    Contains a list of price bars (candles) for a time period.
    """

    bars: List[Bar] = Field(default_factory=list, description="List of price bars")
