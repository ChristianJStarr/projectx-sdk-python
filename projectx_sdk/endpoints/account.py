"""Account service for the ProjectX Gateway API."""

from projectx_sdk.endpoints import BaseService
from projectx_sdk.models.account import Account
from projectx_sdk.utils.constants import ENDPOINTS


class AccountService(BaseService):
    """Service for account-related operations."""

    def search(self, only_active_accounts=False):
        """
        Search for accounts.

        Args:
            only_active_accounts (bool, optional): If True, only return active accounts.
                Defaults to False.

        Returns:
            list[Account]: List of account objects

        Raises:
            AuthenticationError: If not authenticated
            APIError: If the API returns an error
        """
        response = self._client.request(
            "POST",
            ENDPOINTS["account"]["search"],
            json={"onlyActiveAccounts": only_active_accounts},
        )

        # Parse account data into model objects
        accounts = []
        for account_data in response.get("accounts", []):
            accounts.append(Account.from_dict(account_data))

        return accounts
