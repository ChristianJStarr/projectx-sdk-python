"""Tests for the endpoint service classes."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from projectx_sdk.endpoints.account import AccountService
from projectx_sdk.endpoints.contract import ContractService
from projectx_sdk.endpoints.history import HistoryService, TimeUnit
from projectx_sdk.endpoints.order import OrderService
from projectx_sdk.endpoints.position import PositionService
from projectx_sdk.endpoints.trade import TradeService
from projectx_sdk.models.account import Account
from projectx_sdk.models.contract import Contract
from projectx_sdk.models.history import Bar
from projectx_sdk.models.order import Order
from projectx_sdk.models.position import Position
from projectx_sdk.models.trade import Trade
from projectx_sdk.utils.constants import ENDPOINTS, OrderSide, OrderType


class TestAccountService:
    """Tests for the AccountService class."""

    def test_init(self, authenticated_client):
        """Test AccountService initialization."""
        service = AccountService(authenticated_client)
        assert service._client == authenticated_client

    def test_search(
        self, authenticated_client, mock_responses, api_base_url, mock_account_response
    ):
        """Test account search functionality."""
        # Mock the search endpoint
        mock_responses.add(
            mock_responses.POST,
            f"{api_base_url}{ENDPOINTS['account']['search']}",
            json=mock_account_response,
            status=200,
        )

        # Create the service and call search
        service = AccountService(authenticated_client)
        accounts = service.search(only_active_accounts=True)

        # Check the result
        assert len(accounts) == 2
        assert isinstance(accounts[0], Account)
        assert accounts[0].id == 1
        assert accounts[0].name == "TEST_ACCOUNT_1"
        assert accounts[0].can_trade is True
        assert accounts[0].balance == 50000

        assert accounts[1].id == 2
        assert accounts[1].name == "TEST_ACCOUNT_2"
        assert accounts[1].can_trade is False

    def test_search_empty_response(self, authenticated_client, mock_responses, api_base_url):
        """Test account search with empty response."""
        # Mock the search endpoint with an empty response
        mock_responses.add(
            mock_responses.POST,
            f"{api_base_url}{ENDPOINTS['account']['search']}",
            json={"accounts": [], "success": True, "errorCode": 0, "errorMessage": None},
            status=200,
        )

        # Create the service and call search
        service = AccountService(authenticated_client)
        accounts = service.search()

        # Check the result
        assert len(accounts) == 0
        assert isinstance(accounts, list)

    def test_search_api_error(self, authenticated_client, mock_responses, api_base_url):
        """Test account search with API error."""
        from projectx_sdk.exceptions import ProjectXError

        # Mock the search endpoint with an error
        mock_responses.add(
            mock_responses.POST,
            f"{api_base_url}{ENDPOINTS['account']['search']}",
            json={"success": False, "errorCode": 1001, "errorMessage": "Test error"},
            status=200,
        )

        # Create the service
        service = AccountService(authenticated_client)

        # Call search - should raise an APIError
        with pytest.raises(ProjectXError) as excinfo:
            service.search()

        # Check the exception
        assert "Test error" in str(excinfo.value)
        assert excinfo.value.error_code == 1001


class TestContractService:
    """Tests for the ContractService class."""

    def test_init(self, authenticated_client):
        """Test ContractService initialization."""
        service = ContractService(authenticated_client)
        assert service._client == authenticated_client

    def test_search(
        self, authenticated_client, mock_responses, api_base_url, mock_contract_response
    ):
        """Test contract search functionality."""
        # Mock the search endpoint
        mock_responses.add(
            mock_responses.POST,
            f"{api_base_url}/api/Contract/search",
            json=mock_contract_response,
            status=200,
        )

        # Create the service and call search
        service = ContractService(authenticated_client)
        contracts = service.search(search_text="NQ", live=False)

        # Check the result
        assert len(contracts) == 2
        assert isinstance(contracts[0], Contract)
        assert contracts[0].id == "CON.F.US.ENQ.H25"
        assert contracts[0].name == "ENQH25"
        assert contracts[0].tick_size == 0.25
        assert contracts[0].tick_value == 5
        assert contracts[0].active_contract is True

    def test_search_by_id(
        self, authenticated_client, mock_responses, api_base_url, mock_contract_response
    ):
        """Test contract search by ID functionality."""
        # Mock the search endpoint
        mock_responses.add(
            mock_responses.POST,
            f"{api_base_url}/api/Contract/searchById",
            json=mock_contract_response,
            status=200,
        )

        # Create the service and call search
        service = ContractService(authenticated_client)
        contract = service.search_by_id(contract_id="CON.F.US.ENQ.H25")

        # Check the result
        assert isinstance(contract, Contract)
        assert contract.id == "CON.F.US.ENQ.H25"
        assert contract.name == "ENQH25"

        # Test empty response
        mock_responses.replace(
            mock_responses.POST,
            f"{api_base_url}/api/Contract/searchById",
            json={"contracts": [], "success": True, "errorCode": 0, "errorMessage": None},
            status=200,
        )

        # Should return None when no contract found
        contract = service.search_by_id(contract_id="NONEXISTENT")
        assert contract is None


class TestHistoryService:
    """Tests for the HistoryService class."""

    def test_init(self, authenticated_client):
        """Test HistoryService initialization."""
        service = HistoryService(authenticated_client)
        assert service._client == authenticated_client

    def test_retrieve_bars(
        self, authenticated_client, mock_responses, api_base_url, mock_history_response
    ):
        """Test historical bars retrieval."""
        # Mock the retrieve bars endpoint
        mock_responses.add(
            mock_responses.POST,
            f"{api_base_url}/api/History/retrieveBars",
            json=mock_history_response,
            status=200,
        )

        # Create the service and call retrieve_bars
        service = HistoryService(authenticated_client)
        start_time = datetime(2023, 1, 1, tzinfo=timezone.utc)
        end_time = datetime(2023, 1, 2, tzinfo=timezone.utc)

        bars = service.retrieve_bars(
            contract_id="CON.F.US.ENQ.H25",
            start_time=start_time,
            end_time=end_time,
            unit=TimeUnit.HOUR,
            unit_number=1,
            limit=10,
            include_partial_bar=False,
            live=False,
        )

        # Check the result
        assert len(bars) == 3
        assert isinstance(bars[0], Bar)
        assert bars[0].timestamp.isoformat() == "2023-01-01T10:00:00+00:00"
        assert bars[0].open == 100.5
        assert bars[0].high == 101.25
        assert bars[0].low == 100.0
        assert bars[0].close == 101.0
        assert bars[0].volume == 1500


class TestOrderService:
    """Tests for the OrderService class."""

    def test_init(self, authenticated_client):
        """Test OrderService initialization."""
        service = OrderService(authenticated_client)
        assert service._client == authenticated_client

    def test_search(
        self, authenticated_client, mock_responses, api_base_url, mock_order_list_response
    ):
        """Test order search functionality."""
        # Mock the search endpoint
        mock_responses.add(
            mock_responses.POST,
            f"{api_base_url}/api/Order/search",
            json=mock_order_list_response,
            status=200,
        )

        # Create the service and call search
        service = OrderService(authenticated_client)
        start_time = datetime(2023, 1, 1, tzinfo=timezone.utc)
        end_time = datetime(2023, 1, 2, tzinfo=timezone.utc)

        orders = service.search(account_id=1, start_timestamp=start_time, end_timestamp=end_time)

        # Check the result
        assert len(orders) == 2
        assert isinstance(orders[0], Order)
        assert orders[0].id == 1001
        assert orders[0].account_id == 1
        assert orders[0].contract_id == "CON.F.US.ENQ.H25"
        assert orders[0].type == int(OrderType.MARKET)
        assert orders[0].side == int(OrderSide.BUY)

    def test_search_open(
        self, authenticated_client, mock_responses, api_base_url, mock_order_list_response
    ):
        """Test open orders search functionality."""
        # Mock the search endpoint
        mock_responses.add(
            mock_responses.POST,
            f"{api_base_url}/api/Order/searchOpen",
            json=mock_order_list_response,
            status=200,
        )

        # Create the service and call search
        service = OrderService(authenticated_client)
        orders = service.search_open(account_id=1)

        # Check the result
        assert len(orders) == 2
        assert isinstance(orders[0], Order)

    def test_place(self, authenticated_client, mock_responses, api_base_url, mock_order_response):
        """Test order placement functionality."""
        # Mock the place endpoint
        mock_responses.add(
            mock_responses.POST,
            f"{api_base_url}/api/Order/place",
            json=mock_order_response,
            status=200,
        )

        # Create the service and call place
        service = OrderService(authenticated_client)
        order_id = service.place(
            account_id=1,
            contract_id="CON.F.US.ENQ.H25",
            order_type=OrderType.MARKET,
            side=OrderSide.BUY,
            size=1,
        )

        # Check the result
        assert order_id == 1234

    def test_cancel(self, authenticated_client, mock_responses, api_base_url):
        """Test order cancellation functionality."""
        # Mock the cancel endpoint
        mock_responses.add(
            mock_responses.POST,
            f"{api_base_url}/api/Order/cancel",
            json={"success": True, "errorCode": 0, "errorMessage": None},
            status=200,
        )

        # Create the service and call cancel
        service = OrderService(authenticated_client)
        result = service.cancel(account_id=1, order_id=1001)

        # Check the result
        assert result is True

    def test_modify(self, authenticated_client, mock_responses, api_base_url):
        """Test order modification functionality."""
        # Mock the modify endpoint
        mock_responses.add(
            mock_responses.POST,
            f"{api_base_url}/api/Order/modify",
            json={"success": True, "errorCode": 0, "errorMessage": None},
            status=200,
        )

        # Create the service and call modify
        service = OrderService(authenticated_client)
        result = service.modify(account_id=1, order_id=1001, size=2, limit_price=100.5)

        # Check the result
        assert result is True


class TestPositionService:
    """Tests for the PositionService class."""

    def test_init(self, authenticated_client):
        """Test PositionService initialization."""
        service = PositionService(authenticated_client)
        assert service._client == authenticated_client

    def test_search_open(
        self, authenticated_client, mock_responses, api_base_url, mock_position_response
    ):
        """Test open positions search functionality."""
        # Mock the search endpoint
        mock_responses.add(
            mock_responses.POST,
            f"{api_base_url}/api/Position/searchOpen",
            json=mock_position_response,
            status=200,
        )

        # Create the service and call search
        service = PositionService(authenticated_client)
        positions = service.search_open(account_id=1)

        # Check the result
        assert len(positions) == 2
        assert isinstance(positions[0], Position)
        assert positions[0].id == 101
        assert positions[0].account_id == 1
        assert positions[0].contract_id == "CON.F.US.ENQ.H25"
        assert positions[0].size == 2

    def test_close_contract(self, authenticated_client, mock_responses, api_base_url):
        """Test position closing functionality."""
        # Mock the close endpoint
        mock_responses.add(
            mock_responses.POST,
            f"{api_base_url}/api/Position/closeContract",
            json={"success": True, "errorCode": 0, "errorMessage": None},
            status=200,
        )

        # Create the service and call close
        service = PositionService(authenticated_client)
        result = service.close_contract(account_id=1, contract_id="CON.F.US.ENQ.H25")

        # Check the result
        assert result is True

    def test_partial_close_contract(self, authenticated_client, mock_responses, api_base_url):
        """Test partial position closing functionality."""
        # Mock the partial close endpoint
        mock_responses.add(
            mock_responses.POST,
            f"{api_base_url}/api/Position/partialCloseContract",
            json={"success": True, "errorCode": 0, "errorMessage": None},
            status=200,
        )

        # Create the service and call partial close
        service = PositionService(authenticated_client)
        result = service.partial_close_contract(
            account_id=1, contract_id="CON.F.US.ENQ.H25", size=1
        )

        # Check the result
        assert result is True


class TestTradeService:
    """Tests for the TradeService class."""

    def test_init(self, authenticated_client):
        """Test TradeService initialization."""
        service = TradeService(authenticated_client)
        assert service._client == authenticated_client

    def test_search(self, authenticated_client, mock_responses, api_base_url, mock_trade_response):
        """Test trade search functionality."""
        # Mock the search endpoint
        mock_responses.add(
            mock_responses.POST,
            f"{api_base_url}/api/Trade/search",
            json=mock_trade_response,
            status=200,
        )

        # Create the service and call search
        service = TradeService(authenticated_client)
        start_time = datetime(2023, 1, 1, tzinfo=timezone.utc)
        end_time = datetime(2023, 1, 2, tzinfo=timezone.utc)

        trades = service.search(account_id=1, start_timestamp=start_time, end_timestamp=end_time)

        # Check the result
        assert len(trades) == 2
        assert isinstance(trades[0], Trade)
        assert trades[0].id == 2001
        assert trades[0].account_id == 1
        assert trades[0].contract_id == "CON.F.US.ENQ.H25"
        assert trades[0].price == 100.75
        assert trades[0].size == 1
