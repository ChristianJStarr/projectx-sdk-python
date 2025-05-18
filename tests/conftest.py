"""Pytest configuration for ProjectX SDK tests."""

from unittest.mock import MagicMock

import pytest
import responses

from projectx_sdk import ProjectXClient
from projectx_sdk.utils.constants import ENDPOINTS


@pytest.fixture
def mock_responses():
    """
    Fixture to mock HTTP responses using the responses library.

    Returns:
        ResponsesMock: A context manager for mocking HTTP responses.
    """
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        yield rsps


@pytest.fixture
def api_base_url():
    """
    Fixture for the API base URL to use in tests.

    Returns:
        str: The base URL for the test API.
    """
    return "https://gateway-api-demo.s2f.projectx.com"


@pytest.fixture
def auth_token():
    """
    Fixture for a mock auth token.

    Returns:
        str: A mock JWT token.
    """
    # JWT token split across lines to avoid line length limit
    return (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IlRlc3QgVXNlciIsImlhdCI6MTUxNjIzOTAyMn0."
        "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    )


@pytest.fixture
def mock_api_key_auth(mock_responses, api_base_url, auth_token):
    """
    Fixture to mock a successful API key authentication.

    Args:
        mock_responses: The responses mock fixture.
        api_base_url: The base URL fixture.
        auth_token: The auth token fixture.

    Returns:
        dict: A dictionary with the mock auth response.
    """
    auth_response = {"token": auth_token, "success": True, "errorCode": 0, "errorMessage": None}

    # Mock the login endpoint
    mock_responses.add(
        responses.POST,
        f"{api_base_url}{ENDPOINTS['auth']['login_key']}",
        json=auth_response,
        status=200,
    )

    # Mock the token validation endpoint
    validate_response = {
        "success": True,
        "errorCode": 0,
        "errorMessage": None,
        "newToken": auth_token,
    }

    mock_responses.add(
        responses.POST,
        f"{api_base_url}{ENDPOINTS['auth']['validate']}",
        json=validate_response,
        status=200,
    )

    return auth_response


@pytest.fixture
def authenticated_client(mock_responses, mock_api_key_auth, api_base_url):
    """
    Fixture for an authenticated client instance.

    Args:
        mock_responses: The responses mock fixture.
        mock_api_key_auth: The mock auth fixture.
        api_base_url: The base URL fixture.

    Returns:
        ProjectXClient: An authenticated client instance.
    """
    client = ProjectXClient(username="test_user", api_key="test_api_key", environment="demo")

    return client


@pytest.fixture
def mock_account_response():
    """
    Fixture for a mock account search response.

    Returns:
        dict: A mock account response.
    """
    return {
        "accounts": [
            {
                "id": 1,
                "name": "TEST_ACCOUNT_1",
                "balance": 50000,
                "canTrade": True,
                "isVisible": True,
            },
            {
                "id": 2,
                "name": "TEST_ACCOUNT_2",
                "balance": 25000,
                "canTrade": False,
                "isVisible": True,
            },
        ],
        "success": True,
        "errorCode": 0,
        "errorMessage": None,
    }


@pytest.fixture
def mock_contract_response():
    """
    Fixture for a mock contract search response.

    Returns:
        dict: A mock contract response.
    """
    return {
        "contracts": [
            {
                "id": "CON.F.US.ENQ.H25",
                "name": "ENQH25",
                "description": "E-mini NASDAQ-100: March 2025",
                "tickSize": 0.25,
                "tickValue": 5,
                "activeContract": True,
            },
            {
                "id": "CON.F.US.MNQ.H25",
                "name": "MNQH25",
                "description": "Micro E-mini Nasdaq-100: March 2025",
                "tickSize": 0.25,
                "tickValue": 0.5,
                "activeContract": True,
            },
        ],
        "success": True,
        "errorCode": 0,
        "errorMessage": None,
    }


@pytest.fixture
def mock_order_response():
    """
    Fixture for a mock order placement response.

    Returns:
        dict: A mock order response.
    """
    return {"orderId": 1234, "success": True, "errorCode": 0, "errorMessage": None}


@pytest.fixture
def mock_order_list_response():
    """
    Fixture for a mock order search response.

    Returns:
        dict: A mock order list response.
    """
    return {
        "orders": [
            {
                "id": 1001,
                "accountId": 1,
                "contractId": "CON.F.US.ENQ.H25",
                "creationTimestamp": "2023-01-01T12:00:00+00:00",
                "updateTimestamp": "2023-01-01T12:01:00+00:00",
                "status": 1,
                "type": 2,  # Market order
                "side": 0,  # Buy
                "size": 1,
                "limitPrice": None,
                "stopPrice": None,
                "trailPrice": None,
                "customTag": "Test order 1",
                "linkedOrderId": None,
            },
            {
                "id": 1002,
                "accountId": 1,
                "contractId": "CON.F.US.MNQ.H25",
                "creationTimestamp": "2023-01-01T13:00:00+00:00",
                "updateTimestamp": "2023-01-01T13:01:00+00:00",
                "status": 1,
                "type": 1,  # Limit order
                "side": 1,  # Sell
                "size": 2,
                "limitPrice": 15000.0,
                "stopPrice": None,
                "trailPrice": None,
                "customTag": "Test order 2",
                "linkedOrderId": None,
            },
        ],
        "success": True,
        "errorCode": 0,
        "errorMessage": None,
    }


@pytest.fixture
def mock_position_response():
    """
    Fixture for a mock position search response.

    Returns:
        dict: A mock position response.
    """
    return {
        "positions": [
            {
                "id": 101,
                "accountId": 1,
                "contractId": "CON.F.US.ENQ.H25",
                "creationTimestamp": "2023-01-01T12:00:00+00:00",
                "type": 1,
                "size": 2,
                "averagePrice": 15000.0,
            },
            {
                "id": 102,
                "accountId": 1,
                "contractId": "CON.F.US.MNQ.H25",
                "creationTimestamp": "2023-01-01T13:00:00+00:00",
                "type": 1,
                "size": -1,
                "averagePrice": 1500.0,
            },
        ],
        "success": True,
        "errorCode": 0,
        "errorMessage": None,
    }


@pytest.fixture
def mock_trade_response():
    """
    Fixture for a mock trade search response.

    Returns:
        dict: A mock trade response.
    """
    return {
        "trades": [
            {
                "id": 2001,
                "accountId": 1,
                "contractId": "CON.F.US.ENQ.H25",
                "creationTimestamp": "2023-01-01T12:00:00+00:00",
                "price": 100.75,
                "profitAndLoss": 25.0,
                "fees": 1.5,
                "side": 0,
                "size": 1,
                "voided": False,
                "orderId": 1001,
            },
            {
                "id": 2002,
                "accountId": 1,
                "contractId": "CON.F.US.MNQ.H25",
                "creationTimestamp": "2023-01-01T13:00:00+00:00",
                "price": 150.50,
                "profitAndLoss": None,
                "fees": 1.5,
                "side": 1,
                "size": 2,
                "voided": False,
                "orderId": 1002,
            },
        ],
        "success": True,
        "errorCode": 0,
        "errorMessage": None,
    }


@pytest.fixture
def mock_history_response():
    """
    Fixture for a mock historical bars response.

    Returns:
        dict: A mock history response.
    """
    return {
        "bars": [
            {
                "t": "2023-01-01T10:00:00+00:00",
                "o": 100.5,
                "h": 101.25,
                "l": 100.0,
                "c": 101.0,
                "v": 1500,
            },
            {
                "t": "2023-01-01T11:00:00+00:00",
                "o": 101.0,
                "h": 102.0,
                "l": 100.75,
                "c": 101.5,
                "v": 1200,
            },
            {
                "t": "2023-01-01T12:00:00+00:00",
                "o": 101.5,
                "h": 102.5,
                "l": 101.25,
                "c": 102.25,
                "v": 1800,
            },
        ],
        "success": True,
        "errorCode": 0,
        "errorMessage": None,
    }


@pytest.fixture
def mock_hub_connection():
    """
    Fixture for a mock SignalR connection.

    Returns:
        MagicMock: A mock SignalR connection.
    """
    connection = MagicMock()
    connection.is_connected.return_value = True
    connection.invoke.return_value = None

    # Make it appear to be a SignalRConnection instance
    from projectx_sdk.realtime.connection import SignalRConnection

    connection.__class__ = SignalRConnection

    # Set up the on method to store handlers
    connection.on_handlers = {}

    def mock_on(event_name, handler):
        connection.on_handlers[event_name] = handler

    connection.on.side_effect = mock_on

    # Add helper to simulate events
    def trigger_event(event_name, *args):
        if event_name in connection.on_handlers:
            connection.on_handlers[event_name](*args)

    connection.trigger_event = trigger_event

    return connection
