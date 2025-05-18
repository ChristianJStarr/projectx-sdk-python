"""Account models for the ProjectX Gateway API."""

from typing import List

from projectx_sdk.models.base import BaseModel, BaseResponse


class Account(BaseModel):
    """Model representing a trading account."""

    def __init__(self, id, name, can_trade=False, is_visible=True, balance=None):
        """
        Initialize an account model.

        Args:
            id (int): The account ID
            name (str): The account name
            can_trade (bool, optional): Whether trading is enabled for the account
            is_visible (bool, optional): Whether the account is visible
            balance (float, optional): The account balance if available
        """
        self.id = id
        self.name = name
        self.can_trade = can_trade
        self.is_visible = is_visible
        self.balance = balance

    @classmethod
    def from_dict(cls, data):
        """
        Create an Account instance from dictionary data.

        Args:
            data (dict): Dictionary containing account data

        Returns:
            Account: An Account instance
        """
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            can_trade=data.get("canTrade", False),
            is_visible=data.get("isVisible", True),
            balance=data.get("balance"),
        )

    def to_dict(self):
        """
        Convert the Account model to a dictionary.

        Returns:
            dict: Dictionary representation of the account
        """
        return {
            "id": self.id,
            "name": self.name,
            "canTrade": self.can_trade,
            "isVisible": self.is_visible,
            "balance": self.balance,
        }

    def __repr__(self):
        """
        Return string representation of the account.

        Returns:
            str: String representation
        """
        return f"<Account id={self.id} name={self.name} can_trade={self.can_trade}>"


class AccountSearchResponse(BaseResponse):
    """Response model for account search results."""

    accounts: List[dict] = []
