"""Market hub implementation for the ProjectX Gateway API real-time data."""

import logging
from typing import Any, Callable, Dict, Optional

from projectx_sdk.realtime.connection import SignalRConnection

logger = logging.getLogger(__name__)


class MarketHub:
    """
    Market Hub for real-time market data.

    Provides methods to subscribe to and receive market data events
    such as quotes, trades, and market depth (order book).
    """

    def __init__(self, client_or_connection, base_hub_url=None):
        """
        Initialize the market hub.

        This constructor supports two signatures for backward compatibility:
        1. MarketHub(client, base_hub_url) - legacy construction using client and base URL
        2. MarketHub(connection) - new construction using a SignalRConnection directly

        Args:
            client_or_connection: Either a ProjectXClient instance or a SignalRConnection
            base_hub_url (str, optional): The base hub URL (required for legacy constructor)
        """
        # Initialize instance variables first
        self.__init_instance_vars()

        # Determine if we're using the new or legacy constructor
        if isinstance(client_or_connection, SignalRConnection):
            # New constructor with SignalRConnection
            self._connection = client_or_connection
            self._is_connected = self._connection.is_connected()
            self._owns_connection = False
        else:
            # Legacy constructor with client and base_hub_url
            if base_hub_url is None:
                raise ValueError("base_hub_url is required when using client-based constructor")

            self._client = client_or_connection
            self.base_hub_url = base_hub_url
            self.hub_path = "/hubs/market"
            self.hub_url = f"{base_hub_url}{self.hub_path}"

            # Initialize connection but don't start yet
            self._connection: Optional[SignalRConnection] = None  # type: ignore
            self._is_connected = False
            self._owns_connection = True

        # Register event handlers if using direct connection
        if not self._owns_connection:
            self._register_handlers()

    def __init_instance_vars(self):
        """Initialize all instance variables."""
        self._quote_callbacks = {}
        self._trade_callbacks = {}
        self._depth_callbacks = {}
        self._subscribed_quotes = set()
        self._subscribed_trades = set()
        self._subscribed_depth = set()

    def _register_handlers(self):
        """Register event handlers for the market hub."""
        if self._connection:
            self._connection.on("GatewayQuote", self._handle_quote)
            self._connection.on("GatewayTrade", self._handle_trade)
            self._connection.on("GatewayDepth", self._handle_depth)

    def start(self):
        """
        Start the hub connection.

        This is only needed for legacy mode.

        Returns:
            bool: True if connection started successfully
        """
        if not self._owns_connection:
            logger.warning("Cannot start connection in direct connection mode")
            return True

        if self._is_connected:
            logger.info("Connection already started")
            return True

        try:
            if self._connection is None:
                self._connection = self._build_connection()

            # Register event handlers
            self._register_handlers()

            # Start the connection
            self._connection.start()
            self._is_connected = True
            return True

        except Exception as e:
            logger.error(f"Failed to start connection: {str(e)}")
            return False

    def _build_connection(self):
        """
        Build the connection for legacy mode.

        Returns:
            The connection object
        """
        if not self._owns_connection:
            return self._connection

        from signalrcore.hub_connection_builder import HubConnectionBuilder

        # Get the current auth token
        token = self._client.auth.get_token()

        # Build the connection with the token
        connection = (
            HubConnectionBuilder()
            .with_url(f"{self.hub_url}?access_token={token}")
            .with_automatic_reconnect(
                {
                    "type": "raw",
                    "keep_alive_interval": 10,
                    "reconnect_interval": 5,
                    "max_attempts": 10,
                }
            )
            .build()
        )

        # Set up event handlers for reconnection
        connection.on_open(lambda: self._on_connected())
        connection.on_reconnect(lambda: self._on_connected())

        return connection

    def stop(self):
        """
        Stop the hub connection.

        This is only needed for legacy mode.

        Returns:
            bool: True if connection stopped successfully
        """
        if not self._owns_connection:
            logger.warning("Cannot stop connection in direct connection mode")
            return True

        if not self._is_connected or not self._connection:
            logger.info("Connection already stopped or not started")
            return True

        try:
            self._connection.stop()
            self._is_connected = False
            return True

        except Exception as e:
            logger.error(f"Failed to stop connection: {str(e)}")
            return False

    def _handle_quote(self, contract_id: str, data: Dict[str, Any]) -> None:
        """
        Handle an incoming quote event.

        Args:
            contract_id: The contract ID the quote is for
            data: The quote data
        """
        if contract_id in self._quote_callbacks:
            for callback in self._quote_callbacks[contract_id]:
                try:
                    callback(contract_id, data)
                except Exception as e:
                    logger.error(f"Error in quote callback: {e}")

    def _handle_trade(self, contract_id: str, data: Dict[str, Any]) -> None:
        """
        Handle an incoming trade event.

        Args:
            contract_id: The contract ID the trade is for
            data: The trade data
        """
        if contract_id in self._trade_callbacks:
            for callback in self._trade_callbacks[contract_id]:
                try:
                    callback(contract_id, data)
                except Exception as e:
                    logger.error(f"Error in trade callback: {e}")

    def _handle_depth(self, contract_id: str, data: Dict[str, Any]) -> None:
        """
        Handle an incoming depth event.

        Args:
            contract_id: The contract ID the depth is for
            data: The market depth data
        """
        if contract_id in self._depth_callbacks:
            for callback in self._depth_callbacks[contract_id]:
                try:
                    callback(contract_id, data)
                except Exception as e:
                    logger.error(f"Error in depth callback: {e}")

    def subscribe_quotes(
        self, contract_id: str, callback: Callable[[str, Dict[str, Any]], None]
    ) -> None:
        """
        Subscribe to real-time quotes for a contract.

        Args:
            contract_id: The contract ID to subscribe to
            callback: Function to call when a quote is received
        """
        if contract_id not in self._quote_callbacks:
            self._quote_callbacks[contract_id] = []

            if self._connection:
                self._connection.invoke("SubscribeContractQuotes", contract_id)
                self._subscribed_quotes.add(contract_id)

        self._quote_callbacks[contract_id].append(callback)

    def unsubscribe_quotes(self, contract_id: str, callback: Optional[Callable] = None) -> None:
        """
        Unsubscribe from real-time quotes for a contract.

        Args:
            contract_id: The contract ID to unsubscribe from
            callback: Specific callback to remove, or None to remove all
        """
        if contract_id in self._quote_callbacks:
            if callback is None:
                self._quote_callbacks[contract_id] = []
            else:
                self._quote_callbacks[contract_id] = [
                    cb for cb in self._quote_callbacks[contract_id] if cb != callback
                ]

            if (
                not self._quote_callbacks[contract_id]
                and contract_id in self._subscribed_quotes
                and self._connection
            ):
                self._connection.invoke("UnsubscribeContractQuotes", contract_id)
                self._subscribed_quotes.remove(contract_id)

    def subscribe_trades(
        self, contract_id: str, callback: Callable[[str, Dict[str, Any]], None]
    ) -> None:
        """
        Subscribe to real-time trades for a contract.

        Args:
            contract_id: The contract ID to subscribe to
            callback: Function to call when a trade is received
        """
        if contract_id not in self._trade_callbacks:
            self._trade_callbacks[contract_id] = []

            if self._connection:
                self._connection.invoke("SubscribeContractTrades", contract_id)
                self._subscribed_trades.add(contract_id)

        self._trade_callbacks[contract_id].append(callback)

    def unsubscribe_trades(self, contract_id: str, callback: Optional[Callable] = None) -> None:
        """
        Unsubscribe from real-time trades for a contract.

        Args:
            contract_id: The contract ID to unsubscribe from
            callback: Specific callback to remove, or None to remove all
        """
        if contract_id in self._trade_callbacks:
            if callback is None:
                self._trade_callbacks[contract_id] = []
            else:
                self._trade_callbacks[contract_id] = [
                    cb for cb in self._trade_callbacks[contract_id] if cb != callback
                ]

            if (
                not self._trade_callbacks[contract_id]
                and contract_id in self._subscribed_trades
                and self._connection
            ):
                self._connection.invoke("UnsubscribeContractTrades", contract_id)
                self._subscribed_trades.remove(contract_id)

    def subscribe_market_depth(
        self, contract_id: str, callback: Callable[[str, Dict[str, Any]], None]
    ) -> None:
        """
        Subscribe to real-time market depth for a contract.

        Args:
            contract_id: The contract ID to subscribe to
            callback: Function to call when depth data is received
        """
        if contract_id not in self._depth_callbacks:
            self._depth_callbacks[contract_id] = []

            if self._connection:
                self._connection.invoke("SubscribeContractMarketDepth", contract_id)
                self._subscribed_depth.add(contract_id)

        self._depth_callbacks[contract_id].append(callback)

    def unsubscribe_market_depth(
        self, contract_id: str, callback: Optional[Callable] = None
    ) -> None:
        """
        Unsubscribe from real-time market depth for a contract.

        Args:
            contract_id: The contract ID to unsubscribe from
            callback: Specific callback to remove, or None to remove all
        """
        if contract_id in self._depth_callbacks:
            if callback is None:
                self._depth_callbacks[contract_id] = []
            else:
                self._depth_callbacks[contract_id] = [
                    cb for cb in self._depth_callbacks[contract_id] if cb != callback
                ]

            if (
                not self._depth_callbacks[contract_id]
                and contract_id in self._subscribed_depth
                and self._connection
            ):
                self._connection.invoke("UnsubscribeContractMarketDepth", contract_id)
                self._subscribed_depth.remove(contract_id)

    def reconnect_subscriptions(self) -> None:
        """Reestablish all active subscriptions after a reconnection."""
        if not self._connection:
            return

        # Resubscribe to quotes
        for contract_id in self._subscribed_quotes:
            self._connection.invoke("SubscribeContractQuotes", contract_id)

        # Resubscribe to trades
        for contract_id in self._subscribed_trades:
            self._connection.invoke("SubscribeContractTrades", contract_id)

        # Resubscribe to market depth
        for contract_id in self._subscribed_depth:
            self._connection.invoke("SubscribeContractMarketDepth", contract_id)

    def _on_connected(self) -> None:
        """
        Handle connection established or reconnection events.

        This restores all active subscriptions after a connection is established.
        """
        logger.info("Market hub connection established - restoring subscriptions")
        self.reconnect_subscriptions()
