"""Base connection class for SignalR WebSockets."""

import logging
import threading
from abc import ABC, abstractmethod

# This is a placeholder import - in real implementation, you'd use signalrcore or similar
from signalrcore.hub_connection_builder import HubConnectionBuilder

logger = logging.getLogger(__name__)


class HubConnection(ABC):
    """Base class for SignalR hub connections."""

    def __init__(self, client, base_hub_url, hub_path):
        """
        Initialize a hub connection.

        Args:
            client: The ProjectXClient instance
            base_hub_url (str): The base URL for the WebSocket hub
            hub_path (str): The specific hub path (e.g., '/hubs/user')
        """
        self._client = client
        self.base_hub_url = base_hub_url
        self.hub_path = hub_path
        self.hub_url = f"{base_hub_url}{hub_path}"

        # Initialize connection but don't start yet
        self._connection = None
        self._is_connected = False
        self._handlers = {}  # Event handlers

    def build_connection(self):
        """
        Build the SignalR hub connection.

        This creates the connection object but doesn't start it yet.

        Returns:
            The hub connection object
        """
        # Get the current auth token
        token = self._client.auth.token

        # Build the connection with the token
        connection = (
            HubConnectionBuilder()
            .with_url(f"{self.hub_url}?access_token={token}")
            .with_automatic_reconnect()
            .build()
        )

        # Set up basic event handlers
        connection.on_open(self._on_connection_open)
        connection.on_close(self._on_connection_close)
        connection.on_reconnect(self._on_reconnection)
        connection.on_error(self._on_error)

        return connection

    def start(self):
        """
        Start the hub connection.

        This establishes the WebSocket connection and subscribes to events.

        Returns:
            bool: True if connection started successfully
        """
        if self._is_connected:
            logger.info("Connection already started")
            return True

        try:
            if not self._connection:
                self._connection = self.build_connection()

            # Register event handlers
            self._register_handlers()

            # Start the connection
            self._connection.start()
            return True

        except Exception as e:
            logger.error(f"Failed to start connection: {str(e)}")
            return False

    def stop(self):
        """
        Stop the hub connection.

        This closes the WebSocket connection.

        Returns:
            bool: True if connection stopped successfully
        """
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

    @abstractmethod
    def _register_handlers(self):
        """
        Register event handlers for the connection.

        This should be implemented by subclasses to register
        specific event handlers for the hub.
        """
        pass

    def _on_connection_open(self):
        """Handle the connection open event."""
        self._is_connected = True
        logger.info(f"Connection opened to {self.hub_url}")

        # Perform any post-connection setup
        self._on_connected()

    def _on_connection_close(self):
        """Handle the connection close event."""
        self._is_connected = False
        logger.info(f"Connection closed to {self.hub_url}")

    def _on_reconnection(self):
        """Handle the reconnection event."""
        self._is_connected = True
        logger.info(f"Reconnected to {self.hub_url}")

        # Resubscribe to events after reconnection
        self._on_connected()

    def _on_error(self, error):
        """
        Handle connection errors.

        Args:
            error: The error object
        """
        logger.error(f"Connection error: {str(error)}")

    @abstractmethod
    def _on_connected(self):
        """
        Perform actions after connection is established.

        This is called both on initial connection and reconnection.
        Subclasses should implement this to perform any necessary
        subscriptions or other setup.
        """
        pass

    def invoke(self, method, *args):
        """
        Invoke a hub method.

        Args:
            method (str): The hub method name
            *args: Arguments to pass to the method

        Returns:
            The result of the method call

        Raises:
            Exception: If the connection is not established or the call fails
        """
        if not self._is_connected or not self._connection:
            raise Exception("Not connected to hub")

        return self._connection.send(method, args)

    def on(self, event, handler):
        """
        Register a handler for a hub event.

        Args:
            event (str): The event name
            handler (callable): The handler function

        Returns:
            self: For method chaining
        """
        if not self._handlers.get(event):
            self._handlers[event] = []

        self._handlers[event].append(handler)

        # If already connected, register with the connection
        if self._is_connected and self._connection:
            self._connection.on(event, handler)

        return self


class SignalRConnection:
    """SignalR connection for ProjectX Gateway API real-time data."""

    def __init__(self, hub_url, access_token, connection_callback=None):
        """
        Initialize a SignalR connection.

        Args:
            hub_url (str): The WebSocket hub URL
            access_token (str): JWT authentication token
            connection_callback (callable, optional): Callback to invoke when connection is established or reconnected
        """
        self.hub_url = hub_url
        self.access_token = access_token
        self._connection = self._build_connection()
        self._is_connected = False
        self._handlers = {}
        self._lock = threading.Lock()
        self._reconnecting = False
        self._connection_callback = connection_callback

    def _build_connection(self):
        """
        Build the SignalR connection.

        Returns:
            The SignalR connection object
        """
        return (
            HubConnectionBuilder()
            .with_url(f"{self.hub_url}?access_token={self.access_token}")
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

    async def start(self):
        """
        Start the SignalR connection.

        This method is asynchronous and returns when the connection
        is established.

        Raises:
            Exception: If connection fails
        """
        if self._is_connected:
            logger.debug("SignalR connection already started")
            return

        try:
            # Set up handlers for connection events
            self._connection.on_open(self._on_connection_open)
            self._connection.on_close(self._on_connection_close)
            self._connection.on_reconnecting(self._on_reconnecting)
            self._connection.on_reconnected(self._on_reconnected)
            self._connection.on_error(self._on_error)

            # Register all existing event handlers
            self._register_handlers()

            # Start the connection
            await self._connection.start()
            self._is_connected = True
            logger.info(f"SignalR connection established to {self.hub_url}")

        except Exception as e:
            logger.error(f"Failed to start SignalR connection: {str(e)}")
            raise e

    async def stop(self):
        """
        Stop the SignalR connection.

        This method is asynchronous and returns when the connection
        is closed.
        """
        if not self._is_connected:
            logger.debug("SignalR connection already stopped")
            return

        try:
            await self._connection.stop()
            self._is_connected = False
            logger.info(f"SignalR connection closed to {self.hub_url}")
        except Exception as e:
            logger.error(f"Error stopping SignalR connection: {str(e)}")

    def is_connected(self):
        """
        Check if the connection is active.

        Returns:
            bool: True if connected, False otherwise
        """
        return self._is_connected

    def on(self, event, callback):
        """
        Register a callback for a hub event.

        Args:
            event (str): Event name
            callback (callable): Callback function

        Returns:
            self: For method chaining
        """
        with self._lock:
            if event not in self._handlers:
                self._handlers[event] = []

            self._handlers[event].append(callback)

            # If already connected, register with the connection
            if self._is_connected and not self._reconnecting:
                self._connection.on(event, callback)

        return self

    async def invoke(self, method, *args):
        """
        Invoke a hub method.

        Args:
            method (str): Hub method name
            *args: Arguments to pass to the method

        Returns:
            The result of the method invocation

        Raises:
            Exception: If not connected or method invocation fails
        """
        if not self._is_connected:
            raise Exception("Not connected to SignalR hub")

        try:
            return await self._connection.send(method, args)
        except Exception as e:
            logger.error(f"Error invoking hub method {method}: {str(e)}")
            raise e

    def _register_handlers(self):
        """Register all existing event handlers with the connection."""
        with self._lock:
            for event, callbacks in self._handlers.items():
                for callback in callbacks:
                    self._connection.on(event, callback)

    def _on_connection_open(self):
        """Handle connection open event."""
        self._is_connected = True
        logger.info(f"SignalR connection opened to {self.hub_url}")

        # Call the connection callback if provided
        if self._connection_callback:
            try:
                self._connection_callback()
            except Exception as e:
                logger.error(f"Error in connection callback: {str(e)}")

    def _on_connection_close(self):
        """Handle connection close event."""
        self._is_connected = False
        logger.info(f"SignalR connection closed to {self.hub_url}")

    def _on_reconnecting(self, error=None):
        """
        Handle reconnecting event.

        Args:
            error: The error that caused the reconnection attempt
        """
        with self._lock:
            self._reconnecting = True
            self._is_connected = False

        if error:
            logger.warning(f"SignalR connection reconnecting due to error: {str(error)}")
        else:
            logger.info("SignalR connection reconnecting")

    def _on_reconnected(self, connection_id=None):
        """
        Handle reconnected event.

        Args:
            connection_id: The new connection ID
        """
        with self._lock:
            self._reconnecting = False
            self._is_connected = True

        logger.info(f"SignalR connection reconnected with ID: {connection_id}")

        # Re-register all handlers
        self._register_handlers()

        # Call the connection callback if provided
        if self._connection_callback:
            try:
                self._connection_callback()
            except Exception as e:
                logger.error(f"Error in connection callback: {str(e)}")

    def _on_error(self, error):
        """
        Handle connection error event.

        Args:
            error: The error object
        """
        logger.error(f"SignalR connection error: {str(error)}")
