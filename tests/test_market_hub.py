"""Tests for the MarketHub class."""

from unittest.mock import Mock, patch

import pytest

from projectx_sdk.realtime.market_hub import MarketHub


class TestMarketHub:
    """Tests for the MarketHub class."""

    def test_init(self, mock_hub_connection):
        """Test MarketHub initialization."""
        hub = MarketHub(mock_hub_connection)
        assert hub._connection == mock_hub_connection
        assert isinstance(hub._quote_callbacks, dict)
        assert isinstance(hub._trade_callbacks, dict)
        assert isinstance(hub._depth_callbacks, dict)
        assert isinstance(hub._subscribed_quotes, set)
        assert isinstance(hub._subscribed_trades, set)
        assert isinstance(hub._subscribed_depth, set)

        # Check that event handlers are set up
        assert "GatewayQuote" in mock_hub_connection.on_handlers
        assert "GatewayTrade" in mock_hub_connection.on_handlers
        assert "GatewayDepth" in mock_hub_connection.on_handlers

    def test_subscribe_quotes(self, mock_hub_connection):
        """Test subscribing to quotes."""
        hub = MarketHub(mock_hub_connection)
        callback = Mock()

        hub.subscribe_quotes("CON.F.US.ENQ.H25", callback)

        # Check that the callback was added
        assert len(hub._quote_callbacks["CON.F.US.ENQ.H25"]) == 1
        assert hub._quote_callbacks["CON.F.US.ENQ.H25"][0] == callback

        # Check that the subscription was invoked
        mock_hub_connection.invoke.assert_called_with("SubscribeContractQuotes", "CON.F.US.ENQ.H25")

        # Check that the contract was added to subscribed quotes
        assert "CON.F.US.ENQ.H25" in hub._subscribed_quotes

    def test_unsubscribe_quotes(self, mock_hub_connection):
        """Test unsubscribing from quotes."""
        hub = MarketHub(mock_hub_connection)
        callback1 = Mock()
        callback2 = Mock()

        # Subscribe to quotes
        hub.subscribe_quotes("CON.F.US.ENQ.H25", callback1)
        hub.subscribe_quotes("CON.F.US.ENQ.H25", callback2)

        # Reset the mock to clear previous calls
        mock_hub_connection.invoke.reset_mock()

        # Unsubscribe from specific callback
        hub.unsubscribe_quotes("CON.F.US.ENQ.H25", callback1)

        # Check that only one callback remains
        assert len(hub._quote_callbacks["CON.F.US.ENQ.H25"]) == 1
        assert hub._quote_callbacks["CON.F.US.ENQ.H25"][0] == callback2

        # Check that unsubscribe wasn't called (still one callback)
        mock_hub_connection.invoke.assert_not_called()

        # Unsubscribe from all callbacks
        hub.unsubscribe_quotes("CON.F.US.ENQ.H25")

        # Check that no callbacks remain
        assert len(hub._quote_callbacks["CON.F.US.ENQ.H25"]) == 0

        # Check that unsubscribe was called
        mock_hub_connection.invoke.assert_called_with(
            "UnsubscribeContractQuotes", "CON.F.US.ENQ.H25"
        )

        # Check that the contract was removed from subscribed quotes
        assert "CON.F.US.ENQ.H25" not in hub._subscribed_quotes

    def test_handle_quote(self, mock_hub_connection):
        """Test handling quote events."""
        hub = MarketHub(mock_hub_connection)
        callback = Mock()

        # Subscribe to quotes
        hub.subscribe_quotes("CON.F.US.ENQ.H25", callback)

        # Simulate a quote event
        quote_data = {"bid": 15000.0, "ask": 15001.0, "last": 15000.5, "volume": 100}

        mock_hub_connection.trigger_event("GatewayQuote", "CON.F.US.ENQ.H25", quote_data)

        # Check that the callback was called with the correct data
        callback.assert_called_once_with("CON.F.US.ENQ.H25", quote_data)

        # Test error handling in callback
        callback.side_effect = Exception("Test error")

        # This should not raise an exception
        mock_hub_connection.trigger_event("GatewayQuote", "CON.F.US.ENQ.H25", quote_data)

    def test_subscribe_trades(self, mock_hub_connection):
        """Test subscribing to trades."""
        hub = MarketHub(mock_hub_connection)
        callback = Mock()

        hub.subscribe_trades("CON.F.US.ENQ.H25", callback)

        # Check that the callback was added
        assert len(hub._trade_callbacks["CON.F.US.ENQ.H25"]) == 1
        assert hub._trade_callbacks["CON.F.US.ENQ.H25"][0] == callback

        # Check that the subscription was invoked
        mock_hub_connection.invoke.assert_called_with("SubscribeContractTrades", "CON.F.US.ENQ.H25")

        # Check that the contract was added to subscribed trades
        assert "CON.F.US.ENQ.H25" in hub._subscribed_trades

    def test_handle_trade(self, mock_hub_connection):
        """Test handling trade events."""
        hub = MarketHub(mock_hub_connection)
        callback = Mock()

        # Subscribe to trades
        hub.subscribe_trades("CON.F.US.ENQ.H25", callback)

        # Simulate a trade event
        trade_data = {"price": 15000.5, "size": 2, "timestamp": "2023-01-01T12:00:00Z"}

        mock_hub_connection.trigger_event("GatewayTrade", "CON.F.US.ENQ.H25", trade_data)

        # Check that the callback was called with the correct data
        callback.assert_called_once_with("CON.F.US.ENQ.H25", trade_data)

    def test_subscribe_market_depth(self, mock_hub_connection):
        """Test subscribing to market depth."""
        hub = MarketHub(mock_hub_connection)
        callback = Mock()

        hub.subscribe_market_depth("CON.F.US.ENQ.H25", callback)

        # Check that the callback was added
        assert len(hub._depth_callbacks["CON.F.US.ENQ.H25"]) == 1
        assert hub._depth_callbacks["CON.F.US.ENQ.H25"][0] == callback

        # Check that the subscription was invoked
        mock_hub_connection.invoke.assert_called_with(
            "SubscribeContractMarketDepth", "CON.F.US.ENQ.H25"
        )

        # Check that the contract was added to subscribed depth
        assert "CON.F.US.ENQ.H25" in hub._subscribed_depth

    def test_handle_depth(self, mock_hub_connection):
        """Test handling depth events."""
        hub = MarketHub(mock_hub_connection)
        callback = Mock()

        # Subscribe to market depth
        hub.subscribe_market_depth("CON.F.US.ENQ.H25", callback)

        # Simulate a depth event
        depth_data = {
            "bids": [{"price": 15000.0, "size": 5}, {"price": 14999.5, "size": 10}],
            "asks": [{"price": 15001.0, "size": 3}, {"price": 15001.5, "size": 7}],
        }

        mock_hub_connection.trigger_event("GatewayDepth", "CON.F.US.ENQ.H25", depth_data)

        # Check that the callback was called with the correct data
        callback.assert_called_once_with("CON.F.US.ENQ.H25", depth_data)

    def test_reconnect_subscriptions(self, mock_hub_connection):
        """Test reconnecting subscriptions after disconnect."""
        hub = MarketHub(mock_hub_connection)

        # Add some subscriptions
        callback1 = Mock()
        callback2 = Mock()
        callback3 = Mock()

        hub.subscribe_quotes("CON.F.US.ENQ.H25", callback1)
        hub.subscribe_trades("CON.F.US.ENQ.H25", callback2)
        hub.subscribe_market_depth("CON.F.US.ENQ.H25", callback3)

        # Reset the mock to clear previous calls
        mock_hub_connection.invoke.reset_mock()

        # Reconnect subscriptions
        hub.reconnect_subscriptions()

        # Check that subscriptions were re-established
        assert mock_hub_connection.invoke.call_count == 3

        # Check specific calls (order might vary)
        mock_hub_connection.invoke.assert_any_call("SubscribeContractQuotes", "CON.F.US.ENQ.H25")
        mock_hub_connection.invoke.assert_any_call("SubscribeContractTrades", "CON.F.US.ENQ.H25")
        mock_hub_connection.invoke.assert_any_call(
            "SubscribeContractMarketDepth", "CON.F.US.ENQ.H25"
        )
