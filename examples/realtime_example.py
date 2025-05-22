"""
Example of using ProjectX SDK realtime features.

This example demonstrates how to properly set up and use the MarketHub
to subscribe to quote, trade, and market depth events.
"""

import logging
import os
import signal
import sys
import time
from typing import Any, Dict

from projectx_sdk import ProjectXClient
from projectx_sdk.realtime import RealtimeService

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("projectx_example")

# Global flag to control execution
running = True


def setup_signal_handlers():
    """Set up signal handlers to gracefully handle termination."""

    def signal_handler(sig, frame):
        global running
        logger.info("Received shutdown signal, closing connections...")
        running = False

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def handle_quote(contract_id: str, data: Dict[str, Any]):
    """
    Handle quote updates.

    Args:
        contract_id: The contract ID
        data: Quote data dictionary
    """
    bid = data.get("bid")
    ask = data.get("ask")
    last = data.get("last")
    timestamp = data.get("timestamp", "N/A")

    logger.info(f"Quote [{contract_id}]: Bid={bid}, Ask={ask}, Last={last} @ {timestamp}")


def handle_trade(contract_id: str, data: Dict[str, Any]):
    """
    Handle trade updates.

    Args:
        contract_id: The contract ID
        data: Trade data dictionary
    """
    price = data.get("price")
    size = data.get("size")
    timestamp = data.get("timestamp", "N/A")

    logger.info(f"Trade [{contract_id}]: Price={price}, Size={size} @ {timestamp}")


def handle_depth(contract_id: str, data: Dict[str, Any]):
    """
    Handle market depth updates.

    Args:
        contract_id: The contract ID
        data: Market depth data dictionary
    """
    bids = data.get("bids", [])
    asks = data.get("asks", [])

    top_bid = bids[0] if bids else {"price": "N/A", "size": "N/A"}
    top_ask = asks[0] if asks else {"price": "N/A", "size": "N/A"}

    logger.info(
        f"Depth [{contract_id}]: Top Bid={top_bid['price']} x {top_bid['size']}, "
        f"Top Ask={top_ask['price']} x {top_ask['size']}"
    )


def main():
    """Run the example."""
    # Set up signal handlers for graceful shutdown
    setup_signal_handlers()

    # Get credentials from environment variables
    username = os.environ.get("PROJECTX_USERNAME")
    api_key = os.environ.get("PROJECTX_API_KEY")
    environment = os.environ.get("PROJECTX_ENVIRONMENT")

    if not username or not api_key:
        logger.error("Please set PROJECTX_USERNAME and PROJECTX_API_KEY environment variables")
        return 1

    # Contract to subscribe to
    contract_id = "CON.F.US.ENQ.H25"  # E-mini NASDAQ-100 March 2025

    try:
        # Create and authenticate client
        logger.info("Initializing client...")
        client = ProjectXClient(username=username, api_key=api_key, environment=environment)

        # Create realtime service
        logger.info("Setting up realtime connections...")
        realtime = RealtimeService(client)

        # Access the market hub (lazy initialization)
        market_hub = realtime.market

        # Subscribe to market data events
        logger.info(f"Subscribing to market data for {contract_id}...")
        market_hub.subscribe_quotes(contract_id, handle_quote)
        market_hub.subscribe_trades(contract_id, handle_trade)
        market_hub.subscribe_market_depth(contract_id, handle_depth)

        # Start the connection
        logger.info("Starting realtime connection...")
        realtime.start()

        # Main loop - keep the program running
        logger.info("Listening for market events. Press Ctrl+C to exit.")
        while running:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down...")
    except Exception as e:
        logger.exception(f"Error in realtime example: {e}")
        return 1
    finally:
        # Clean up
        if "realtime" in locals():
            logger.info("Stopping realtime connections...")
            try:
                realtime.stop()
            except Exception as e:
                logger.error(f"Error stopping realtime service: {e}")

    logger.info("Example completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
