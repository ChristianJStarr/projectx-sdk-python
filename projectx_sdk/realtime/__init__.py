"""Real-time communication modules for ProjectX Gateway API."""

from typing import Optional

from projectx_sdk.realtime.connection import SignalRConnection
from projectx_sdk.realtime.market_hub import MarketHub
from projectx_sdk.realtime.user_hub import UserHub


class RealTimeClient:
    """
    Client for real-time communication with ProjectX Gateway API.

    Manages connections to the User and Market hubs for real-time data.
    """

    def __init__(
        self,
        auth_token: str,
        environment: str,
        user_hub_url: Optional[str] = None,
        market_hub_url: Optional[str] = None,
    ):
        """
        Initialize a real-time client.

        Args:
            auth_token: JWT auth token for API access
            environment: Environment name (e.g., 'topstepx')
            user_hub_url: URL for the user hub (optional)
            market_hub_url: URL for the market hub (optional)
        """
        # Create hub instances with their connections
        self._user_connection = SignalRConnection(
            hub_url=user_hub_url or f"wss://gateway-rtc-{environment}.s2f.projectx.com/hubs/user",
            access_token=auth_token,
            connection_callback=None,  # Will be set by UserHub
        )
        self._market_connection = SignalRConnection(
            hub_url=market_hub_url
            or f"wss://gateway-rtc-{environment}.s2f.projectx.com/hubs/market",
            access_token=auth_token,
            connection_callback=None,  # Will be set by MarketHub
        )

        self.user = UserHub(self._user_connection)
        self.market = MarketHub(self._market_connection)

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
        # Cast the result to bool to satisfy mypy
        user_connected = bool(self._user_connection.is_connected())
        market_connected = bool(self._market_connection.is_connected())
        return user_connected and market_connected

    def reconnect_subscriptions(self):
        """
        Reestablish all active subscriptions after a reconnection.

        This is typically called after a connection is restored.
        """
        self.user.reconnect_subscriptions()
        self.market.reconnect_subscriptions()


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
        self._user_hub_url = client.USER_HUB_URLS.get(client.environment)
        self._market_hub_url = client.MARKET_HUB_URLS.get(client.environment)

    @property
    def user(self):
        """
        Get the user hub.

        Returns:
            UserHub: The user hub instance
        """
        if self._user is None:
            self._user = UserHub(self._client, None, self._user_hub_url)
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

            self._market = MarketHub(self._client, None, self._market_hub_url)
        return self._market

    def start(self):
        """Start the real-time connections that have been created."""
        if self._user is not None:
            self._user.start()
        if self._market is not None:
            self._market.start()

    def stop(self):
        """Stop the real-time connections that have been created."""
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
