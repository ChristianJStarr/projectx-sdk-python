"""Tests for the model classes."""

from datetime import datetime

import pytest

from projectx_sdk.models.account import Account


class TestAccountModel:
    """Tests for the Account model class."""

    def test_init(self):
        """Test Account initialization with required fields."""
        account = Account(id=1, name="Test Account")

        assert account.id == 1
        assert account.name == "Test Account"
        assert account.can_trade is False  # Default
        assert account.is_visible is True  # Default
        assert account.balance is None  # Default

    def test_init_with_all_fields(self):
        """Test Account initialization with all fields."""
        account = Account(
            id=1, name="Test Account", can_trade=True, is_visible=False, balance=50000.0
        )

        assert account.id == 1
        assert account.name == "Test Account"
        assert account.can_trade is True
        assert account.is_visible is False
        assert account.balance == 50000.0

    def test_from_dict(self):
        """Test creating an Account from a dictionary."""
        data = {
            "id": 1,
            "name": "Test Account",
            "canTrade": True,
            "isVisible": False,
            "balance": 50000.0,
        }

        account = Account.from_dict(data)

        assert account.id == 1
        assert account.name == "Test Account"
        assert account.can_trade is True
        assert account.is_visible is False
        assert account.balance == 50000.0

    def test_from_dict_minimal(self):
        """Test creating an Account from a minimal dictionary."""
        data = {"id": 1, "name": "Test Account"}

        account = Account.from_dict(data)

        assert account.id == 1
        assert account.name == "Test Account"
        assert account.can_trade is False  # Default from API
        assert account.is_visible is True  # Default from API
        assert account.balance is None

    def test_to_dict(self):
        """Test converting an Account to a dictionary."""
        account = Account(
            id=1, name="Test Account", can_trade=True, is_visible=False, balance=50000.0
        )

        data = account.to_dict()

        assert data == {
            "id": 1,
            "name": "Test Account",
            "canTrade": True,
            "isVisible": False,
            "balance": 50000.0,
        }

    def test_repr(self):
        """Test the string representation of an Account."""
        account = Account(id=1, name="Test Account", can_trade=True)

        # The representation should include the ID, name, and can_trade value
        repr_str = repr(account)
        assert "id=1" in repr_str
        assert "name=Test Account" in repr_str
        assert "can_trade=True" in repr_str
