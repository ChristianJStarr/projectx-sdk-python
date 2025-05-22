"""User hub implementation for the ProjectX Gateway API."""

import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional, Set

from projectx_sdk.realtime.connection import SignalRConnection

logger = logging.getLogger(__name__)


class UserHub:
    """
    User hub connection for real-time updates on user data.

    This hub provides real-time updates for:
    - Account changes
    - Order status updates
    - Position updates
    - Trade (execution) notifications
    """

    def __init__(self, client_or_connection, base_hub_url=None, hub_url=None):
        """
        Initialize the user hub connection.

        This constructor supports multiple signatures for flexibility:
        1. UserHub(client, base_hub_url) - legacy construction using client and base URL
        2. UserHub(client, None, hub_url) - construction using client and direct hub URL
        3. UserHub(connection) - construction using a SignalRConnection directly

        Args:
            client_or_connection: Either a ProjectXClient instance or a SignalRConnection
            base_hub_url (str, optional): The base hub URL (for legacy constructor)
            hub_url (str, optional): The complete hub URL (overrides base_hub_url)
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
            # Constructor with client and URL
            self._client = client_or_connection
            self._owns_connection = True

            if hub_url:
                # Direct hub URL provided
                self.hub_url = hub_url
                self.base_hub_url = None
                self.hub_path = None
            elif base_hub_url:
                # Base URL provided, construct hub URL
                self.base_hub_url = base_hub_url
                self.hub_path = "/hubs/user"
                self.hub_url = f"{base_hub_url}{self.hub_path}"
            else:
                raise ValueError(
                    "Either base_hub_url or hub_url is required when using client-based constructor"
                )

            # Initialize connection but don't start yet
            self._connection: Optional[SignalRConnection] = None  # type: ignore
            self._is_connected = False

        # Register handlers if using direct connection
        if not self._owns_connection:
            self._register_handlers()

    def __init_instance_vars(self):
        """Initialize all instance variables."""
        # Track active subscriptions
        self._account_subscribed = False
        self._subscribed_orders: Set[int] = set()
        self._subscribed_positions: Set[int] = set()
        self._subscribed_trades: Set[int] = set()

        # Event callbacks
        self._account_callbacks: List[Callable] = []
        self._order_callbacks: Dict[str, List[Any]] = {}  # account_id -> [callbacks]
        self._position_callbacks: Dict[str, List[Any]] = {}
        self._trade_callbacks: Dict[str, List[Any]] = {}

    def _register_handlers(self):
        """Register event handlers for the user hub."""
        if self._connection:
            self._connection.on("GatewayUserAccount", self._handle_account_update)
            self._connection.on("GatewayUserOrder", self._handle_order_update)
            self._connection.on("GatewayUserPosition", self._handle_position_update)
            self._connection.on("GatewayUserTrade", self._handle_trade_update)

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

    def reconnect_subscriptions(self):
        """Resubscribe to events after connection is established."""
        # Resubscribe to accounts if previously subscribed
        if self._account_subscribed:
            self.subscribe_accounts()

        # Resubscribe to orders
        for account_id in self._subscribed_orders:
            self.subscribe_orders(account_id)

        # Resubscribe to positions
        for account_id in self._subscribed_positions:
            self.subscribe_positions(account_id)

        # Resubscribe to trades
        for account_id in self._subscribed_trades:
            self.subscribe_trades(account_id)

    def _on_connected(self):
        """
        Handle connection established or reconnection events.

        This restores all active subscriptions after a connection is established.
        """
        logger.info("User hub connection established - restoring subscriptions")
        self.reconnect_subscriptions()

    def subscribe_accounts(self, callback=None):
        """
        Subscribe to account updates.

        Args:
            callback (callable, optional): Callback function for account updates.
                The function should accept a single argument (the account data).

        Returns:
            self: For method chaining
        """
        if callback:
            self._account_callbacks.append(callback)

        if self._is_connected:
            asyncio.create_task(self.invoke("SubscribeAccounts"))
            self._account_subscribed = True

        return self

    def unsubscribe_accounts(self):
        """
        Unsubscribe from account updates.

        Returns:
            self: For method chaining
        """
        if self._is_connected and self._account_subscribed:
            asyncio.create_task(self.invoke("UnsubscribeAccounts"))
            self._account_subscribed = False

        return self

    def subscribe_orders(self, account_id, callback=None):
        """
        Subscribe to order updates for a specific account.

        Args:
            account_id (int): Account ID to subscribe to
            callback (callable, optional): Callback function for order updates.
                The function should accept a single argument (the order data).

        Returns:
            self: For method chaining
        """
        if callback:
            if account_id not in self._order_callbacks:
                self._order_callbacks[str(account_id)] = []
            self._order_callbacks[str(account_id)].append(callback)

        if self._is_connected:
            asyncio.create_task(self.invoke("SubscribeOrders", account_id))
            self._subscribed_orders.add(account_id)

        return self

    def unsubscribe_orders(self, account_id):
        """
        Unsubscribe from order updates for a specific account.

        Args:
            account_id (int): Account ID to unsubscribe from

        Returns:
            self: For method chaining
        """
        if self._is_connected and account_id in self._subscribed_orders:
            asyncio.create_task(self.invoke("UnsubscribeOrders", account_id))
            self._subscribed_orders.discard(account_id)

        return self

    def subscribe_positions(self, account_id, callback=None):
        """
        Subscribe to position updates for a specific account.

        Args:
            account_id (int): Account ID to subscribe to
            callback (callable, optional): Callback function for position updates.
                The function should accept a single argument (the position data).

        Returns:
            self: For method chaining
        """
        if callback:
            if account_id not in self._position_callbacks:
                self._position_callbacks[str(account_id)] = []
            self._position_callbacks[str(account_id)].append(callback)

        if self._is_connected:
            asyncio.create_task(self.invoke("SubscribePositions", account_id))
            self._subscribed_positions.add(account_id)

        return self

    def unsubscribe_positions(self, account_id):
        """
        Unsubscribe from position updates for a specific account.

        Args:
            account_id (int): Account ID to unsubscribe from

        Returns:
            self: For method chaining
        """
        if self._is_connected and account_id in self._subscribed_positions:
            asyncio.create_task(self.invoke("UnsubscribePositions", account_id))
            self._subscribed_positions.discard(account_id)

        return self

    def subscribe_trades(self, account_id, callback=None):
        """
        Subscribe to trade updates for a specific account.

        Args:
            account_id (int): Account ID to subscribe to
            callback (callable, optional): Callback function for trade updates.
                The function should accept a single argument (the trade data).

        Returns:
            self: For method chaining
        """
        if callback:
            if account_id not in self._trade_callbacks:
                self._trade_callbacks[str(account_id)] = []
            self._trade_callbacks[str(account_id)].append(callback)

        if self._is_connected:
            asyncio.create_task(self.invoke("SubscribeTrades", account_id))
            self._subscribed_trades.add(account_id)

        return self

    def unsubscribe_trades(self, account_id):
        """
        Unsubscribe from trade updates for a specific account.

        Args:
            account_id (int): Account ID to unsubscribe from

        Returns:
            self: For method chaining
        """
        if self._is_connected and account_id in self._subscribed_trades:
            asyncio.create_task(self.invoke("UnsubscribeTrades", account_id))
            self._subscribed_trades.discard(account_id)

        return self

    async def invoke(self, method, *args):
        """
        Invoke a hub method.

        Args:
            method (str): Hub method name
            *args: Arguments to pass to the method

        Returns:
            The result of the method invocation
        """
        if not self._is_connected or not self._connection:
            raise Exception("Not connected to hub")

        return await self._connection.invoke(method, *args)

    def _handle_account_update(self, data):
        """
        Handle account update events.

        Args:
            data: Account data from the hub event
        """
        # Handle various types of input data
        processed_data = data
        try:
            # Handle data if it's a string
            if isinstance(data, str):
                processed_data = {"accountId": data}
            # Handle data if it's a list (from signalR direct invocation)
            elif isinstance(data, list) and len(data) > 0:
                if isinstance(data[0], str):
                    processed_data = {"accountId": data[0]}
                else:
                    processed_data = data[0]
        except Exception as e:
            logger.error(f"Error processing account data: {e}")
            return

        # Call all registered account callbacks
        for callback in self._account_callbacks:
            try:
                callback(processed_data)
            except Exception as e:
                logger.error(f"Error in account callback: {e}")

    def _handle_order_update(self, data_or_account_id, data=None):
        """
        Handle order update events.

        This handler supports two invocation patterns:
        1. _handle_order_update(data) - where data contains the account_id and order data
        2. _handle_order_update(account_id, data) - where account_id is passed separately

        Args:
            data_or_account_id: Either the data dict or the account ID
            data: Order data from the hub event (when using the second pattern)
        """
        # Determine which pattern we're using
        if data is None:
            # First pattern: data_or_account_id is the data object
            # Process various data formats
            account_id = None
            order_data: Dict[str, Any] = {}

            try:
                # Handle string data
                if isinstance(data_or_account_id, str):
                    account_id = data_or_account_id
                    order_data = {}
                # Handle data if it's a list (from signalR direct invocation)
                elif isinstance(data_or_account_id, list) and len(data_or_account_id) > 0:
                    # SignalR direct format: [account_id, data_dict]
                    if len(data_or_account_id) >= 2 and isinstance(data_or_account_id[0], str):
                        account_id = data_or_account_id[0]
                        order_data = data_or_account_id[1]
                    else:
                        item = data_or_account_id[0]
                        if isinstance(item, str):
                            account_id = item
                        else:
                            account_id = item.get("accountId")
                            order_data = item
                # Handle dictionary data
                elif isinstance(data_or_account_id, dict):
                    account_id = data_or_account_id.get("accountId")
                    order_data = data_or_account_id
                else:
                    logger.warning("Order update has unrecognized format")
                    return

                if not account_id:
                    logger.warning("Order update missing account ID")
                    return
            except Exception as e:
                logger.error(f"Error processing order data: {e}")
                return
        else:
            # Second pattern: data_or_account_id is the account_id
            account_id = data_or_account_id
            order_data = data

        # Call registered callbacks for this account
        if account_id is not None:
            callbacks = self._order_callbacks.get(str(account_id), [])
        else:
            callbacks = []
        for callback in callbacks:
            try:
                callback(account_id, order_data)
            except Exception as e:
                logger.error(f"Error in order callback: {e}")

    def _handle_position_update(self, data_or_account_id, data=None):
        """
        Handle position update events.

        This handler supports two invocation patterns:
        1. _handle_position_update(data) - where data contains the account_id and position data
        2. _handle_position_update(account_id, data) - where account_id is passed separately

        Args:
            data_or_account_id: Either the data dict or the account ID
            data: Position data from the hub event (when using the second pattern)
        """
        # Determine which pattern we're using
        if data is None:
            # First pattern: data_or_account_id is the data object
            # Process various data formats
            account_id = None
            position_data: Dict[str, Any] = {}

            try:
                # Handle string data
                if isinstance(data_or_account_id, str):
                    account_id = data_or_account_id
                    position_data = {}
                # Handle data if it's a list (from signalR direct invocation)
                elif isinstance(data_or_account_id, list) and len(data_or_account_id) > 0:
                    # SignalR direct format: [account_id, data_dict]
                    if len(data_or_account_id) >= 2 and isinstance(data_or_account_id[0], str):
                        account_id = data_or_account_id[0]
                        position_data = data_or_account_id[1]
                    else:
                        item = data_or_account_id[0]
                        if isinstance(item, str):
                            account_id = item
                        else:
                            account_id = item.get("accountId")
                            position_data = item
                # Handle dictionary data
                elif isinstance(data_or_account_id, dict):
                    account_id = data_or_account_id.get("accountId")
                    position_data = data_or_account_id
                else:
                    logger.warning("Position update has unrecognized format")
                    return

                if not account_id:
                    logger.warning("Position update missing account ID")
                    return
            except Exception as e:
                logger.error(f"Error processing position data: {e}")
                return
        else:
            # Second pattern: data_or_account_id is the account_id
            account_id = data_or_account_id
            position_data = data

        # Call registered callbacks for this account
        if account_id is not None:
            callbacks = self._position_callbacks.get(str(account_id), [])
        else:
            callbacks = []
        for callback in callbacks:
            try:
                callback(account_id, position_data)
            except Exception as e:
                logger.error(f"Error in position callback: {e}")

    def _handle_trade_update(self, data_or_account_id, data=None):
        """
        Handle trade update events.

        This handler supports two invocation patterns:
        1. _handle_trade_update(data) - where data contains the account_id and trade data
        2. _handle_trade_update(account_id, data) - where account_id is passed separately

        Args:
            data_or_account_id: Either the data dict or the account ID
            data: Trade data from the hub event (when using the second pattern)
        """
        # Determine which pattern we're using
        if data is None:
            # First pattern: data_or_account_id is the data object
            # Process various data formats
            account_id = None
            trade_data: Dict[str, Any] = {}

            try:
                # Handle string data
                if isinstance(data_or_account_id, str):
                    account_id = data_or_account_id
                    trade_data = {}
                # Handle data if it's a list (from signalR direct invocation)
                elif isinstance(data_or_account_id, list) and len(data_or_account_id) > 0:
                    # SignalR direct format: [account_id, data_dict]
                    if len(data_or_account_id) >= 2 and isinstance(data_or_account_id[0], str):
                        account_id = data_or_account_id[0]
                        trade_data = data_or_account_id[1]
                    else:
                        item = data_or_account_id[0]
                        if isinstance(item, str):
                            account_id = item
                        else:
                            account_id = item.get("accountId")
                            trade_data = item
                # Handle dictionary data
                elif isinstance(data_or_account_id, dict):
                    account_id = data_or_account_id.get("accountId")
                    trade_data = data_or_account_id
                else:
                    logger.warning("Trade update has unrecognized format")
                    return

                if not account_id:
                    logger.warning("Trade update missing account ID")
                    return
            except Exception as e:
                logger.error(f"Error processing trade data: {e}")
                return
        else:
            # Second pattern: data_or_account_id is the account_id
            account_id = data_or_account_id
            trade_data = data

        # Call registered callbacks for this account
        if account_id is not None:
            callbacks = self._trade_callbacks.get(str(account_id), [])
        else:
            callbacks = []
        for callback in callbacks:
            try:
                callback(account_id, trade_data)
            except Exception as e:
                logger.error(f"Error in trade callback: {e}")
