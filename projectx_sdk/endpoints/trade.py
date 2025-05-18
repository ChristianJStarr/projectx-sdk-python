from datetime import datetime
from typing import List, Optional

from projectx_sdk.endpoints import BaseService
from projectx_sdk.models.trade import Trade, TradeSearchResponse


class TradeService(BaseService):
    """Service for trade-related endpoints."""

    def search(
        self, account_id: int, start_timestamp: datetime, end_timestamp: Optional[datetime] = None
    ) -> List[Trade]:
        """
        Search for executed trades (fills) for an account and time range.

        Args:
            account_id: The account ID to fetch trade history for
            start_timestamp: Start of the time range to retrieve trades from
            end_timestamp: End of the time range for trade retrieval (optional)

        Returns:
            A list of trades (executions) for the account within the time range
        """
        data = {"accountId": account_id, "startTimestamp": start_timestamp.isoformat()}

        if end_timestamp:
            data["endTimestamp"] = end_timestamp.isoformat()

        response = self._client.post("Trade/search", json=data)
        search_response = TradeSearchResponse.model_validate(response)
        return search_response.trades
