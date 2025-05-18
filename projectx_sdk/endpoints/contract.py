"""Service module for contract-related API endpoints."""

from typing import Any, Dict, List, Optional

from projectx_sdk.endpoints import BaseService
from projectx_sdk.models.contract import Contract, ContractSearchResponse


class ContractService(BaseService):
    """Service for contract-related endpoints."""

    def search(self, search_text: str, live: bool = False) -> List[Contract]:
        """
        Search for contracts by text.

        Args:
            search_text: The text to search for in contract names.
            live: Whether to search the live market contracts (True) or
                  the simulation contracts (False).

        Returns:
            A list of matching contracts.
        """
        data = {"searchText": search_text, "live": live}
        response: Dict[str, Any] = self._client.post("Contract/search", json=data)
        search_response = ContractSearchResponse.model_validate(response)
        return search_response.contracts  # type: ignore

    def search_by_id(self, contract_id: str) -> Optional[Contract]:
        """
        Search for a contract by its exact ID.

        Args:
            contract_id: The unique contract ID to search for.

        Returns:
            The matching contract if found, None otherwise.
        """
        data = {"contractId": contract_id}
        response: Dict[str, Any] = self._client.post("Contract/searchById", json=data)
        search_response = ContractSearchResponse.model_validate(response)
        return search_response.contracts[0] if search_response.contracts else None
