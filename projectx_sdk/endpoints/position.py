from typing import Any, Dict, List, Optional

from projectx_sdk.endpoints import BaseService
from projectx_sdk.models.position import Position, PositionSearchResponse


class PositionService(BaseService):
    """Service for position-related endpoints."""

    def search_open(self, account_id: int) -> List[Position]:
        """
        Search for open positions for a given account.

        Args:
            account_id: The account ID for which to retrieve open positions

        Returns:
            A list of open positions for the account
        """
        data = {"accountId": account_id}

        response = self._client.post("Position/searchOpen", json=data)
        search_response = PositionSearchResponse.model_validate(response)
        return search_response.positions

    def close_contract(self, account_id: int, contract_id: str) -> bool:
        """
        Close any open position in a specific contract.

        This will send market orders to offset the entire open position
        in the specified contract, closing it out completely.

        Args:
            account_id: The account ID in which the position exists
            contract_id: The contract ID of the position to close

        Returns:
            True if the close operation was successful, False otherwise
        """
        data = {"accountId": account_id, "contractId": contract_id}

        response = self._client.post("Position/closeContract", json=data)
        return response.get("success", False)

    def partial_close_contract(self, account_id: int, contract_id: str, size: int) -> bool:
        """
        Partially close an open position by a given size.

        This will reduce an open position in the specified contract
        by placing an offsetting order of the specified size.

        Args:
            account_id: The account ID of the position
            contract_id: The contract ID for which to reduce the position
            size: The quantity of the position to close

        Returns:
            True if the partial close operation was successful, False otherwise
        """
        data = {"accountId": account_id, "contractId": contract_id, "size": size}

        response = self._client.post("Position/partialCloseContract", json=data)
        return response.get("success", False)
