from datetime import datetime
from enum import IntEnum
from typing import Any, Dict, List, Optional

from projectx_sdk.endpoints import BaseService
from projectx_sdk.models.history import Bar, BarResponse


class TimeUnit(IntEnum):
    """Enumeration of time units for historical data bars."""

    SECOND = 1
    MINUTE = 2
    HOUR = 3
    DAY = 4
    WEEK = 5
    MONTH = 6


class HistoryService(BaseService):
    """Service for historical market data endpoints."""

    def retrieve_bars(
        self,
        contract_id: str,
        start_time: datetime,
        end_time: datetime,
        unit: TimeUnit = TimeUnit.MINUTE,
        unit_number: int = 1,
        limit: int = 1000,
        include_partial_bar: bool = False,
        live: bool = False,
    ) -> List[Bar]:
        """
        Retrieve historical price bars (candles) for a contract.

        Args:
            contract_id: The identifier of the contract to get data for
            start_time: The start timestamp of the data range
            end_time: The end timestamp of the data range
            unit: The time unit for aggregation of bars
            unit_number: The number of units per bar
            limit: The maximum number of bars to retrieve
            include_partial_bar: Whether to include the partial bar for the current period
            live: Whether to retrieve from live data feed or simulation

        Returns:
            A list of OHLCV bars for the requested time range
        """
        data = {
            "contractId": contract_id,
            "startTime": start_time.isoformat(),
            "endTime": end_time.isoformat(),
            "unit": int(unit),
            "unitNumber": unit_number,
            "limit": limit,
            "includePartialBar": include_partial_bar,
            "live": live,
        }

        response = self._client.post("History/retrieveBars", json=data)
        bar_response = BarResponse.model_validate(response)
        return bar_response.bars
