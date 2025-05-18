"""Tests for the real-time functionality."""

from unittest.mock import MagicMock, patch

from projectx_sdk.realtime import RealtimeService
from projectx_sdk.realtime.user_hub import UserHub


class TestRealtimeService:
    """Tests for the RealtimeService class."""

    def test_init(self, authenticated_client):
        """Test RealtimeService initialization."""
        service = RealtimeService(authenticated_client)

        assert service._client == authenticated_client
        assert service._user is None
        assert service._market is None
        assert service._base_hub_url is not None

    def test_user_hub_lazy_loading(self, authenticated_client):
        """Test that the user hub is lazily loaded."""
        service = RealtimeService(authenticated_client)

        # Initially, the user hub should be None
        assert service._user is None

        # Accessing the user property should create it
        user_hub = service.user
        assert user_hub is not None
        assert isinstance(user_hub, UserHub)

        # Should be cached now
        assert service._user is user_hub

        # Accessing again should return the same object
        assert service.user is user_hub

    @patch("projectx_sdk.realtime.market_hub.MarketHub")
    def test_market_hub_lazy_loading(self, mock_market_hub, authenticated_client):
        """Test that the market hub is lazily loaded."""
        mock_market_hub.return_value = MagicMock()

        service = RealtimeService(authenticated_client)

        # Initially, the market hub should be None
        assert service._market is None

        # Accessing the market property should create it
        market_hub = service.market
        assert market_hub is not None
        assert mock_market_hub.called

        # Should be cached now
        assert service._market is market_hub

        # Accessing again should return the same object
        assert service.market is market_hub

    @patch("projectx_sdk.realtime.user_hub.UserHub.start")
    @patch("projectx_sdk.realtime.market_hub.MarketHub.start")
    def test_start(self, mock_market_start, mock_user_start, authenticated_client):
        """Test starting the real-time hubs."""
        service = RealtimeService(authenticated_client)

        # Access the hubs to create them
        service.user
        service.market

        # Start the hubs
        service.start()

        # Check that start was called on both hubs
        mock_user_start.assert_called_once()
        mock_market_start.assert_called_once()

    @patch("projectx_sdk.realtime.user_hub.UserHub.start")
    def test_start_user_only(self, mock_user_start, authenticated_client):
        """Test starting only the user hub."""
        service = RealtimeService(authenticated_client)

        # Access only the user hub
        service.user

        # Start the hubs
        service.start()

        # Check that start was called on the user hub
        mock_user_start.assert_called_once()

    @patch("projectx_sdk.realtime.user_hub.UserHub.stop")
    @patch("projectx_sdk.realtime.market_hub.MarketHub.stop")
    def test_stop(self, mock_market_stop, mock_user_stop, authenticated_client):
        """Test stopping the real-time hubs."""
        service = RealtimeService(authenticated_client)

        # Access the hubs to create them
        service.user
        service.market

        # Stop the hubs
        service.stop()

        # Check that stop was called on both hubs
        mock_user_stop.assert_called_once()
        mock_market_stop.assert_called_once()
