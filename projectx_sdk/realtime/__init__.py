"""Real-time communication modules for ProjectX Gateway API."""

import asyncio
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, Optional

from projectx_sdk.realtime.connection import SignalRConnection
from projectx_sdk.realtime.market_hub import MarketHub
from projectx_sdk.realtime.user_hub import UserHub

# Set up normal logging (removing the debug level override)
logger = logging.getLogger(__name__)


class SyncMarketHub:
    """Synchronous wrapper for MarketHub that hides async complexity."""

    def __init__(self, async_hub: MarketHub, event_loop: asyncio.AbstractEventLoop):
        """Initialize with the async hub and event loop."""
        self._async_hub = async_hub
        self._loop = event_loop

    def subscribe_quotes(
        self, contract_id: str, callback: Callable[[str, Dict[str, Any]], None]
    ) -> None:
        """Subscribe to quote updates for a contract."""
        future = asyncio.run_coroutine_threadsafe(
            self._async_hub.subscribe_quotes(contract_id, callback), self._loop
        )
        future.result(timeout=30)

    def unsubscribe_quotes(self, contract_id: str, callback: Optional[Callable] = None) -> None:
        """Unsubscribe from quote updates for a contract."""
        future = asyncio.run_coroutine_threadsafe(
            self._async_hub.unsubscribe_quotes(contract_id, callback), self._loop
        )
        future.result(timeout=30)

    def subscribe_trades(
        self, contract_id: str, callback: Callable[[str, Dict[str, Any]], None]
    ) -> None:
        """Subscribe to trade updates for a contract."""
        future = asyncio.run_coroutine_threadsafe(
            self._async_hub.subscribe_trades(contract_id, callback), self._loop
        )
        future.result(timeout=30)

    def unsubscribe_trades(self, contract_id: str, callback: Optional[Callable] = None) -> None:
        """Unsubscribe from trade updates for a contract."""
        future = asyncio.run_coroutine_threadsafe(
            self._async_hub.unsubscribe_trades(contract_id, callback), self._loop
        )
        future.result(timeout=30)

    def subscribe_market_depth(
        self, contract_id: str, callback: Callable[[str, Dict[str, Any]], None]
    ) -> None:
        """Subscribe to market depth updates for a contract."""
        future = asyncio.run_coroutine_threadsafe(
            self._async_hub.subscribe_market_depth(contract_id, callback), self._loop
        )
        future.result(timeout=30)

    def unsubscribe_market_depth(
        self, contract_id: str, callback: Optional[Callable] = None
    ) -> None:
        """Unsubscribe from market depth updates for a contract."""
        future = asyncio.run_coroutine_threadsafe(
            self._async_hub.unsubscribe_market_depth(contract_id, callback), self._loop
        )
        future.result(timeout=30)


class SyncUserHub:
    """Synchronous wrapper for UserHub that hides async complexity."""

    def __init__(self, async_hub: UserHub, event_loop: asyncio.AbstractEventLoop):
        """Initialize with the async hub and event loop."""
        self._async_hub = async_hub
        self._loop = event_loop

    # Add sync wrappers for UserHub methods as needed
    # For now, we'll add them when we encounter async methods


class SyncRealTimeClient:
    """
    Synchronous real-time client that hides async complexity from users.

    This client manages an async event loop in a background thread,
    providing a simple synchronous API for users.
    """

    def __init__(
        self,
        auth_token: str,
        environment: str,
        user_hub_url: Optional[str] = None,
        market_hub_url: Optional[str] = None,
    ):
        """
        Initialize a synchronous real-time client.

        Args:
            auth_token: JWT auth token for API access
            environment: Environment name (e.g., 'topstepx')
            user_hub_url: URL for the user hub (optional)
            market_hub_url: URL for the market hub (optional)
        """
        self._auth_token = auth_token
        self._environment = environment
        self._user_hub_url = user_hub_url
        self._market_hub_url = market_hub_url

        # Background thread and event loop
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="realtime")
        self._async_client: Optional[RealTimeClient] = None
        self._started = False

        # Sync wrappers for hubs
        self._user: Optional[SyncUserHub] = None
        self._market: Optional[SyncMarketHub] = None

    def start(self):
        """Start the real-time connections."""
        if self._started:
            return

        def _run_async_client():
            """Run the async client in a background thread."""
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)

            try:
                # Create the async client
                self._async_client = RealTimeClient(
                    auth_token=self._auth_token,
                    environment=self._environment,
                    user_hub_url=self._user_hub_url,
                    market_hub_url=self._market_hub_url,
                )

                # Run the event loop
                self._loop.run_forever()
            except Exception as e:
                logger.error(f"Error in async client thread: {e}")
            finally:
                if self._loop:
                    self._loop.close()

        # Start the background thread
        self._thread = threading.Thread(target=_run_async_client, daemon=True)
        self._thread.start()

        # Wait for the loop to be ready
        while self._loop is None:
            threading.Event().wait(0.01)

        # Start the async client (we know _async_client and _loop are not None here)
        if self._async_client and self._loop:
            future = asyncio.run_coroutine_threadsafe(self._async_client.start(), self._loop)
            future.result(timeout=30)  # Wait up to 30 seconds

            # Create sync wrappers for hubs
            self._user = SyncUserHub(self._async_client.user, self._loop)
            self._market = SyncMarketHub(self._async_client.market, self._loop)

        self._started = True
        logger.info("Sync real-time client started")

    def stop(self):
        """Stop the real-time connections."""
        if not self._started:
            return

        logger.info("Stopping sync real-time client...")

        try:
            if self._async_client and self._loop:
                # Stop the async client with a shorter timeout and better error handling
                try:
                    future = asyncio.run_coroutine_threadsafe(self._async_client.stop(), self._loop)
                    future.result(timeout=10)  # Reduced timeout from 30 to 10 seconds
                    logger.info("Async client stopped successfully")
                except Exception as e:
                    logger.warning(f"Error stopping async client (ignoring): {e}")

                # Stop the event loop gracefully
                try:
                    self._loop.call_soon_threadsafe(self._loop.stop)
                    logger.debug("Event loop stop requested")
                except Exception as e:
                    logger.warning(f"Error stopping event loop (ignoring): {e}")

            # Wait for thread to finish with timeout
            if self._thread and self._thread.is_alive():
                self._thread.join(timeout=3)  # Reduced timeout from 5 to 3 seconds
                if self._thread.is_alive():
                    logger.warning("Background thread did not shut down within timeout")
                else:
                    logger.debug("Background thread stopped successfully")

        except Exception as e:
            logger.error(f"Error stopping sync real-time client: {e}")
        finally:
            # Always clean up regardless of errors
            self._started = False
            try:
                self._executor.shutdown(wait=False)  # Don't wait for executor shutdown
            except Exception as e:
                logger.warning(f"Error shutting down executor (ignoring): {e}")

            logger.info("Sync real-time client stopped")

    def is_connected(self) -> bool:
        """Check if the connections are active."""
        if not self._started or not self._async_client:
            return False
        return self._async_client.is_connected()

    @property
    def user(self) -> SyncUserHub:
        """Get the user hub."""
        if not self._user:
            raise RuntimeError("Client not started. Call start() first.")
        return self._user

    @property
    def market(self) -> SyncMarketHub:
        """Get the market hub."""
        if not self._market:
            raise RuntimeError("Client not started. Call start() first.")
        return self._market


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
        try:
            await self._user_connection.start()
        except Exception as e:
            # Log the error but continue to try to connect to the market hub
            logger.error(f"Failed to start user connection: {str(e)}")

        try:
            await self._market_connection.start()
        except Exception as e:
            logger.error(f"Failed to start market connection: {str(e)}")

    async def stop(self):
        """Stop both real-time connections."""
        try:
            await self._user_connection.stop()
        except Exception as e:
            logger.error(f"Error stopping user connection: {str(e)}")

        try:
            await self._market_connection.stop()
        except Exception as e:
            logger.error(f"Error stopping market connection: {str(e)}")

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
        asyncio.create_task(self.market.reconnect_subscriptions())


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
    "SyncRealTimeClient",
    "SyncMarketHub",
    "SyncUserHub",
    "RealTimeClient",
    "RealtimeService",
    "UserHub",
    "MarketHub",
    "SignalRConnection",
]
