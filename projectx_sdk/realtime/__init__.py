"""Real-time communication modules for ProjectX Gateway API."""

from projectx_sdk.realtime.connection import SignalRConnection
from projectx_sdk.realtime.market_hub import MarketHub
from projectx_sdk.realtime.user_hub import UserHub


class RealTimeClient:
    """
    Client for real-time communication with ProjectX Gateway API.

    Manages connections to the User and Market hubs for real-time data.
    """

    def __init__(self, auth_token: str, environment: str):
        """
        Initialize a real-time client.

        Args:
            auth_token: JWT auth token for API access
            environment: Environment name (e.g., 'topstepx')
        """
        # Create hub instances first
        self.user = UserHub.__new__(UserHub)
        self.market = MarketHub.__new__(MarketHub)

        # Initialize connections with the hub callbacks
        self._user_connection = SignalRConnection(
            hub_url=f"wss://gateway-rtc-{environment}.s2f.projectx.com/hubs/user",
            access_token=auth_token,
            connection_callback=self.user._on_connected,
        )
        self._market_connection = SignalRConnection(
            hub_url=f"wss://gateway-rtc-{environment}.s2f.projectx.com/hubs/market",
            access_token=auth_token,
            connection_callback=self.market._on_connected,
        )

        # Initialize hubs with the connections
        self.user._connection = self._user_connection
        self.user._is_connected = self._user_connection.is_connected()
        self.user._owns_connection = False

        self.market._connection = self._market_connection
        self.market._is_connected = self._market_connection.is_connected()
        self.market._owns_connection = False

        # Register handlers
        self.user._register_handlers()
        self.market._register_handlers()

    async def start(self):
        """Start both real-time connections."""
        await self._user_connection.start()
        await self._market_connection.start()

    async def stop(self):
        """Stop both real-time connections."""
        await self._user_connection.stop()
        await self._market_connection.stop()

    def is_connected(self) -> bool:
        """
        Check if both connections are active.

        Returns:
            True if both user and market connections are active
        """
        return self._user_connection.is_connected() and self._market_connection.is_connected()

    def reconnect_subscriptions(self):
        """
        Reestablish all active subscriptions after a reconnection.

        This is typically called after a connection is restored.
        """
        self.user.reconnect_subscriptions()
        self.market.reconnect_subscriptions()


# Class for backward compatibility with tests
class RealtimeService:
    """
    Legacy service class for real-time communication.

    This class is maintained for backward compatibility with tests.
    New code should use RealTimeClient instead.
    """

    def __init__(self, client):
        """
        Initialize the real-time service.

        Args:
            client: The ProjectXClient instance
        """
        self._client = client
        self._user = None
        self._market = None
        self._base_hub_url = f"wss://gateway-rtc-{client.environment}.s2f.projectx.com"

    @property
    def user(self):
        """
        Get the user hub.

        Returns:
            UserHub: The user hub instance
        """
        if self._user is None:
            self._user = UserHub(self._client, self._base_hub_url)
        return self._user

    @property
    def market(self):
        """
        Get the market hub.

        Returns:
            MarketHub: The market hub instance
        """
        if self._market is None:
            from projectx_sdk.realtime.market_hub import MarketHub

            self._market = MarketHub(self._client, self._base_hub_url)
        return self._market

    def start(self):
        """
        Start the real-time connections that have been created.
        """
        if self._user is not None:
            self._user.start()
        if self._market is not None:
            self._market.start()

    def stop(self):
        """
        Stop the real-time connections that have been created.
        """
        if self._user is not None:
            self._user.stop()
        if self._market is not None:
            self._market.stop()


__all__ = [
    "RealTimeClient",
    "RealtimeService",
    "UserHub",
    "MarketHub",
    "SignalRConnection",
]
