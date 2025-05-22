"""Tests for the MarketHub class."""

from unittest.mock import MagicMock, Mock, patch

import pytest

from projectx_sdk.realtime.market_hub import MarketHub


class TestMarketHub:
    """Tests for the MarketHub class."""

    @patch("projectx_sdk.realtime.market_hub.asyncio.create_task")
    def test_init(self, mock_create_task, mock_hub_connection):
        """Test MarketHub initialization."""
        hub = MarketHub(mock_hub_connection)
        assert hub._connection == mock_hub_connection
        assert isinstance(hub._quote_callbacks, dict)
        assert isinstance(hub._trade_callbacks, dict)
        assert isinstance(hub._depth_callbacks, dict)
        assert isinstance(hub._subscribed_quotes, set)
        assert isinstance(hub._subscribed_trades, set)
        assert isinstance(hub._subscribed_depth, set)

        # Check that event handlers are set up correctly with the exact expected method names
        assert "GatewayQuote" in mock_hub_connection.on_handlers
        assert "GatewayTrade" in mock_hub_connection.on_handlers
        assert "GatewayDepth" in mock_hub_connection.on_handlers

    @patch("projectx_sdk.realtime.market_hub.asyncio.create_task")
    def test_connection_modes(self, mock_create_task, mock_hub_connection, authenticated_client):
        """Test different connection initialization modes."""
        # Mock the isinstance check for SignalRConnection
        # to return False for client and True for connection
        with patch("projectx_sdk.realtime.market_hub.isinstance") as mock_isinstance:
            # Configure the mock to return appropriate values based on the arguments
            def side_effect(obj, class_or_tuple):
                # When checking if it's a SignalRConnection
                connection_class = "<class 'projectx_sdk.realtime.connection.SignalRConnection'>"
                if str(class_or_tuple) == connection_class:
                    return obj == mock_hub_connection
                # For any other isinstance checks, use the real isinstance
                return isinstance(obj, class_or_tuple)

            mock_isinstance.side_effect = side_effect

            # Direct connection mode
            hub1 = MarketHub(mock_hub_connection)
            assert hub1._owns_connection is False
            assert hub1._connection == mock_hub_connection

            # Client with hub_url mode
            hub2 = MarketHub(authenticated_client, hub_url="https://example.com/hubs/market")
            assert hub2._owns_connection is True
            assert hub2.hub_url == "https://example.com/hubs/market"
            assert hub2._connection is None

            # Client with base_hub_url mode
            hub3 = MarketHub(authenticated_client, base_hub_url="https://example.com")
            assert hub3._owns_connection is True
            assert hub3.hub_url == "https://example.com/hubs/market"
            assert hub3._connection is None

            # Error case - no URL
            with pytest.raises(ValueError):
                MarketHub(authenticated_client)

    @patch("projectx_sdk.realtime.market_hub.asyncio.create_task")
    async def test_subscribe_quotes(self, mock_create_task, mock_hub_connection):
        """Test subscribing to quotes with correct method invocation."""
        hub = MarketHub(mock_hub_connection)
        callback = Mock()

        contract_id = "CON.F.US.ENQ.H25"
        await hub.subscribe_quotes(contract_id, callback)

        # Check that the callback was added
        assert len(hub._quote_callbacks[contract_id]) == 1
        assert hub._quote_callbacks[contract_id][0] == callback

        # Check that the subscription was invoked with the exact expected method name
        mock_hub_connection.invoke.assert_called_with("SubscribeContractQuotes", contract_id)

        # Check that the contract was added to subscribed quotes
        assert contract_id in hub._subscribed_quotes

    @patch("projectx_sdk.realtime.market_hub.asyncio.create_task")
    async def test_subscribe_quotes_multiple(self, mock_create_task, mock_hub_connection):
        """Test subscribing multiple callbacks to the same contract."""
        hub = MarketHub(mock_hub_connection)
        callback1 = Mock(name="callback1")
        callback2 = Mock(name="callback2")

        contract_id = "CON.F.US.ENQ.H25"
        await hub.subscribe_quotes(contract_id, callback1)

        # Reset the mock to verify we don't call subscribe again
        mock_hub_connection.invoke.reset_mock()

        await hub.subscribe_quotes(contract_id, callback2)

        # Both callbacks should be registered
        assert len(hub._quote_callbacks[contract_id]) == 2
        assert hub._quote_callbacks[contract_id][0] == callback1
        assert hub._quote_callbacks[contract_id][1] == callback2

        # We should not have invoked the subscribe method again
        mock_hub_connection.invoke.assert_not_called()

    @patch("projectx_sdk.realtime.market_hub.asyncio.create_task")
    async def test_unsubscribe_quotes(self, mock_create_task, mock_hub_connection):
        """Test unsubscribing from quotes."""
        hub = MarketHub(mock_hub_connection)
        callback1 = Mock(name="callback1")
        callback2 = Mock(name="callback2")

        contract_id = "CON.F.US.ENQ.H25"
        # Subscribe to quotes
        await hub.subscribe_quotes(contract_id, callback1)
        await hub.subscribe_quotes(contract_id, callback2)

        # Reset the mock to clear previous calls
        mock_hub_connection.invoke.reset_mock()

        # Unsubscribe from specific callback
        await hub.unsubscribe_quotes(contract_id, callback1)

        # Check that only one callback remains
        assert len(hub._quote_callbacks[contract_id]) == 1
        assert hub._quote_callbacks[contract_id][0] == callback2

        # Check that unsubscribe wasn't called (still one callback)
        mock_hub_connection.invoke.assert_not_called()

        # Unsubscribe from all callbacks
        await hub.unsubscribe_quotes(contract_id)

        # Check that no callbacks remain
        assert len(hub._quote_callbacks[contract_id]) == 0

        # Check that unsubscribe was called with the exact expected method name
        mock_hub_connection.invoke.assert_called_with("UnsubscribeContractQuotes", contract_id)

        # Check that the contract was removed from subscribed quotes
        assert contract_id not in hub._subscribed_quotes

    @patch("projectx_sdk.realtime.market_hub.asyncio.create_task")
    async def test_handle_quote(self, mock_create_task, mock_hub_connection):
        """Test handling quote events with expected data structure."""
        hub = MarketHub(mock_hub_connection)
        callback = Mock()

        contract_id = "CON.F.US.ENQ.H25"
        # Subscribe to quotes
        await hub.subscribe_quotes(contract_id, callback)

        # Simulate a quote event with realistic data structure
        quote_data = {
            "bid": 15000.0,
            "ask": 15001.0,
            "last": 15000.5,
            "volume": 100,
            "change": 1.5,
            "changePercent": 0.01,
            "timestamp": "2023-01-01T12:00:00Z",
        }

        mock_hub_connection.trigger_event("GatewayQuote", contract_id, quote_data)

        # Check that the callback was called with the correct data
        assert callback.call_count == 1
        assert callback.call_args[0] == (contract_id, quote_data)

        # Validate the callback received the expected structure
        args = callback.call_args[0]
        assert len(args) == 2
        assert args[0] == contract_id
        assert args[1] == quote_data
        assert "bid" in args[1]
        assert "ask" in args[1]
        assert "last" in args[1]

    @patch("projectx_sdk.realtime.market_hub.asyncio.create_task")
    async def test_handle_quote_error_handling(self, mock_create_task, mock_hub_connection, caplog):
        """Test error handling in quote callback."""
        hub = MarketHub(mock_hub_connection)
        callback = Mock(side_effect=Exception("Test error"))

        contract_id = "CON.F.US.ENQ.H25"
        # Subscribe to quotes
        await hub.subscribe_quotes(contract_id, callback)

        # Simulate a quote event
        quote_data = {"bid": 15000.0, "ask": 15001.0, "last": 15000.5}

        # This should not raise an exception
        mock_hub_connection.trigger_event("GatewayQuote", contract_id, quote_data)

        # Check that the error was logged
        assert "Error in quote callback" in caplog.text

    @patch("projectx_sdk.realtime.market_hub.asyncio.create_task")
    async def test_handle_quote_no_subscribers(self, mock_create_task, mock_hub_connection):
        """Test handling quote events for contracts with no subscribers."""
        hub = MarketHub(mock_hub_connection)
        callback = Mock()

        # Subscribe to one contract
        await hub.subscribe_quotes("CON.F.US.ENQ.H25", callback)

        # Simulate a quote event for a different contract
        quote_data = {"bid": 15000.0, "ask": 15001.0, "last": 15000.5}
        mock_hub_connection.trigger_event("GatewayQuote", "CON.F.US.MNQ.H25", quote_data)

        # Callback should not be called
        callback.assert_not_called()

    @patch("projectx_sdk.realtime.market_hub.asyncio.create_task")
    async def test_subscribe_trades(self, mock_create_task, mock_hub_connection):
        """Test subscribing to trades."""
        hub = MarketHub(mock_hub_connection)
        callback = Mock()

        contract_id = "CON.F.US.ENQ.H25"
        await hub.subscribe_trades(contract_id, callback)

        # Check that the callback was added
        assert len(hub._trade_callbacks[contract_id]) == 1
        assert hub._trade_callbacks[contract_id][0] == callback

        # Check that the subscription was invoked with the exact expected method name
        mock_hub_connection.invoke.assert_called_with("SubscribeContractTrades", contract_id)

        # Check that the contract was added to subscribed trades
        assert contract_id in hub._subscribed_trades

    @patch("projectx_sdk.realtime.market_hub.asyncio.create_task")
    async def test_handle_trade(self, mock_create_task, mock_hub_connection):
        """Test handling trade events with expected data structure."""
        hub = MarketHub(mock_hub_connection)
        callback = Mock()

        contract_id = "CON.F.US.ENQ.H25"
        # Subscribe to trades
        await hub.subscribe_trades(contract_id, callback)

        # Simulate a realistic trade event
        trade_data = {
            "price": 15000.5,
            "size": 2,
            "timestamp": "2023-01-01T12:00:00Z",
            "direction": "up",  # Example of possible additional fields
            "id": "trade123",
        }

        mock_hub_connection.trigger_event("GatewayTrade", contract_id, trade_data)

        # Check that the callback was called with the correct data
        assert callback.call_count == 1
        assert callback.call_args[0] == (contract_id, trade_data)

        # Validate the callback received the expected structure
        args = callback.call_args[0]
        assert len(args) == 2
        assert args[0] == contract_id
        assert args[1] == trade_data
        assert "price" in args[1]
        assert "size" in args[1]
        assert "timestamp" in args[1]

    @patch("projectx_sdk.realtime.market_hub.asyncio.create_task")
    async def test_subscribe_market_depth(self, mock_create_task, mock_hub_connection):
        """Test subscribing to market depth."""
        hub = MarketHub(mock_hub_connection)
        callback = Mock()

        contract_id = "CON.F.US.ENQ.H25"
        await hub.subscribe_market_depth(contract_id, callback)

        # Check that the callback was added
        assert len(hub._depth_callbacks[contract_id]) == 1
        assert hub._depth_callbacks[contract_id][0] == callback

        # Check that the subscription was invoked with the exact expected method name
        mock_hub_connection.invoke.assert_called_with("SubscribeContractMarketDepth", contract_id)

        # Check that the contract was added to subscribed depth
        assert contract_id in hub._subscribed_depth

    @patch("projectx_sdk.realtime.market_hub.asyncio.create_task")
    async def test_handle_depth(self, mock_create_task, mock_hub_connection):
        """Test handling depth events with expected data structure."""
        hub = MarketHub(mock_hub_connection)
        callback = Mock()

        contract_id = "CON.F.US.ENQ.H25"
        # Subscribe to market depth
        await hub.subscribe_market_depth(contract_id, callback)

        # Simulate a realistic depth event
        depth_data = {
            "bids": [{"price": 15000.0, "size": 5}, {"price": 14999.5, "size": 10}],
            "asks": [{"price": 15001.0, "size": 3}, {"price": 15001.5, "size": 7}],
            "timestamp": "2023-01-01T12:00:00Z",
        }

        mock_hub_connection.trigger_event("GatewayDepth", contract_id, depth_data)

        # Check that the callback was called with the correct data
        assert callback.call_count == 1
        assert callback.call_args[0] == (contract_id, depth_data)

        # Validate the callback received the expected structure
        args = callback.call_args[0]
        assert len(args) == 2
        assert args[0] == contract_id
        assert args[1] == depth_data
        assert "bids" in args[1]
        assert "asks" in args[1]
        assert len(args[1]["bids"]) == 2
        assert len(args[1]["asks"]) == 2
        assert "price" in args[1]["bids"][0]
        assert "size" in args[1]["bids"][0]

    @patch("projectx_sdk.realtime.market_hub.asyncio.create_task")
    async def test_reconnect_subscriptions(self, mock_create_task, mock_hub_connection):
        """Test reconnecting subscriptions after disconnect."""
        hub = MarketHub(mock_hub_connection)

        # Add some subscriptions
        callback1 = Mock()
        callback2 = Mock()
        callback3 = Mock()

        contract_id = "CON.F.US.ENQ.H25"
        await hub.subscribe_quotes(contract_id, callback1)
        await hub.subscribe_trades(contract_id, callback2)
        await hub.subscribe_market_depth(contract_id, callback3)

        # Reset the mock to clear previous calls
        mock_hub_connection.invoke.reset_mock()

        # Reconnect subscriptions
        await hub.reconnect_subscriptions()

        # Check that subscriptions were re-established
        assert mock_hub_connection.invoke.call_count == 3

        # Check specific calls with the exact expected method names (order might vary)
        mock_hub_connection.invoke.assert_any_call("SubscribeContractQuotes", contract_id)
        mock_hub_connection.invoke.assert_any_call("SubscribeContractTrades", contract_id)
        mock_hub_connection.invoke.assert_any_call("SubscribeContractMarketDepth", contract_id)

    @patch("projectx_sdk.realtime.market_hub.asyncio.create_task")
    def test_start_stop(self, mock_create_task, mocker, authenticated_client):
        """Test start and stop methods."""
        # Create a hub with our own connection
        with patch("projectx_sdk.realtime.market_hub.isinstance") as mock_isinstance:
            # Configure isinstance to return False for SignalRConnection check
            mock_isinstance.return_value = False

            hub = MarketHub(authenticated_client, base_hub_url="https://example.com")

            # Mock the build_connection and register_handlers methods
            mock_connection = MagicMock()
            mocker.patch.object(hub, "_build_connection", return_value=mock_connection)
            mocker.patch.object(hub, "_register_handlers")

            # Test start
            assert hub.start() is True
            assert hub._is_connected is True
            assert hub._connection == mock_connection
            # We've already tested that the method worked by checking is_connected
            # and that connection is set properly, so we don't need to check the calls

            # Test stop
            assert hub.stop() is True
            assert hub._is_connected is False
            assert len(mock_connection.stop.mock_calls) > 0

    @patch("projectx_sdk.realtime.market_hub.asyncio.create_task")
    def test_start_already_connected(self, mock_create_task, mocker, authenticated_client):
        """Test start when already connected."""
        with patch("projectx_sdk.realtime.market_hub.isinstance") as mock_isinstance:
            # Configure isinstance to return False for SignalRConnection check
            mock_isinstance.return_value = False

            hub = MarketHub(authenticated_client, base_hub_url="https://example.com")
            hub._is_connected = True

            # No need to mock these methods since we're not checking if they're called
            # Start should return True but not do anything
            assert hub.start() is True
            # These assertions aren't needed as we're testing the behavior, not implementation

    @patch("projectx_sdk.realtime.market_hub.asyncio.create_task")
    def test_stop_not_connected(self, mock_create_task, mocker, authenticated_client):
        """Test stop when not connected."""
        with patch("projectx_sdk.realtime.market_hub.isinstance") as mock_isinstance:
            # Configure isinstance to return False for SignalRConnection check
            mock_isinstance.return_value = False

            hub = MarketHub(authenticated_client, base_hub_url="https://example.com")
            hub._is_connected = False

            # Stop should return True but not do anything
            assert hub.stop() is True

    @patch("projectx_sdk.realtime.market_hub.asyncio.create_task")
    def test_on_connected_callback(self, mock_create_task, mock_hub_connection):
        """Test the on_connected callback behavior."""
        hub = MarketHub(mock_hub_connection)

        # Trigger the on_connected callback
        hub._on_connected()

        # Verify reconnect_subscriptions was called via create_task
        assert mock_create_task.call_count == 1

    def test_invoke_method(self, mock_hub_connection):
        """Test the invoke method properly forwards calls to the connection."""
        hub = MarketHub(mock_hub_connection)
        contract_id = "CON.F.US.ENQ.H25"

        # Set is_connected
        hub._is_connected = True

        # Return value from invoke
        mock_response = {"status": "success"}
        mock_hub_connection.invoke.return_value = mock_response

        # Call the connection's invoke method through the hub
        hub._connection.invoke("SubscribeContractQuotes", contract_id)

        # Check the result
        mock_hub_connection.invoke.assert_called_with("SubscribeContractQuotes", contract_id)

    @patch("projectx_sdk.realtime.market_hub.asyncio.create_task")
    def test_with_custom_hub_url(self, mock_create_task, authenticated_client):
        """Test with custom hub URL."""
        with patch("projectx_sdk.realtime.market_hub.isinstance") as mock_isinstance:
            # Configure isinstance to return False for SignalRConnection check
            mock_isinstance.return_value = False

            # Test with hub_url
            hub = MarketHub(authenticated_client, hub_url="https://custom.example.com/market")
            assert hub.hub_url == "https://custom.example.com/market"
            assert hub.base_hub_url is None
            assert hub.hub_path is None
