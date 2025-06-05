"""Example demonstrating real-time market data streaming with the ProjectX SDK."""

import os
import signal
import sys
import threading
import time
from collections import deque
from datetime import datetime

from projectx_sdk import ProjectXClient

# Get API credentials from environment variables
USERNAME = os.environ.get("PROJECTX_USERNAME")
API_KEY = os.environ.get("PROJECTX_API_KEY")
ENVIRONMENT = os.environ.get("PROJECTX_ENVIRONMENT", "demo")

# Global variables for graceful shutdown
shutdown_requested = False
client = None
monitor = None


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global shutdown_requested, client, monitor
    print("\nShutdown signal received. Cleaning up...")
    shutdown_requested = True

    if monitor:
        monitor.stop()
    if client:
        try:
            client.realtime.stop()
        except Exception as e:
            print(f"Error during cleanup: {e}")

    sys.exit(0)


class MarketDataMonitor:
    """Class to monitor and display real-time market data."""

    def __init__(self, client):
        """Initialize the market data monitor.

        Args:
            client: The ProjectX client instance
        """
        self.client = client
        self.subscribed_contracts = {}
        self.price_history = {}
        self.lock = threading.Lock()
        self.running = True

        # Start the display thread
        self.display_thread = threading.Thread(target=self.display_updates)
        self.display_thread.daemon = True
        self.display_thread.start()

    def on_quote_update(self, contract_id, data):
        """Handle real-time price updates."""
        print(f"Quote update for {contract_id}: {data}")
        if not contract_id or contract_id not in self.subscribed_contracts:
            return

        with self.lock:
            if contract_id not in self.price_history:
                self.price_history[contract_id] = deque(maxlen=100)  # Keep last 100 prices

            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            price_data = {
                "timestamp": timestamp,
                "last": data.get("lastPrice"),  # Field mapping: lastPrice -> last
                "bid": data.get("bestBid"),  # Field mapping: bestBid -> bid
                "ask": data.get("bestAsk"),  # Field mapping: bestAsk -> ask
                "volume": data.get("volume"),
            }
            self.price_history[contract_id].append(price_data)
            print(f"Processed price data: {price_data}")

    def on_trade_update(self, contract_id, data):
        """Handle real-time trade updates."""
        if not contract_id or contract_id not in self.subscribed_contracts:
            return

        contract_name = self.subscribed_contracts[contract_id]
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        print(f"\n[{timestamp}] TRADE: {contract_name}")
        print(f"  Trade data type: {type(data)}")
        print(f"  Trade data: {data}")

        # Handle case where data might be a list or dict
        try:
            if isinstance(data, list):
                print(f"  Data is a list with {len(data)} items")
                # If data is a list, take the first item or handle accordingly
                trade_data = data[0] if data else {}
                print(f"  Using first item: {trade_data}")
            else:
                trade_data = data

            print(f"  Price: {trade_data.get('price', 'N/A')}")
            print(f"  Size: {trade_data.get('size', 'N/A')}")
            print(f"  Side: {trade_data.get('side', 'N/A')}")
        except Exception as e:
            print(f"  Error processing trade data: {e}")
            print(f"  Raw data: {data}")

    def subscribe_contract(self, contract):
        """Subscribe to real-time data for a contract."""
        contract_id = contract.id

        # Store contract info
        self.subscribed_contracts[contract_id] = contract.name

        # Initialize price history
        with self.lock:
            self.price_history[contract_id] = deque(maxlen=100)

        # Subscribe to price updates
        self.client.realtime.market.subscribe_quotes(
            contract_id=contract_id, callback=self.on_quote_update
        )
        print("subscribed to quotes")

        # Subscribe to trade updates
        self.client.realtime.market.subscribe_trades(
            contract_id=contract_id, callback=self.on_trade_update
        )
        print("subscribed to trades")

        print(f"Subscribed to real-time data for {contract.name}")

    def display_updates(self):
        """Periodically display the latest price updates."""
        while self.running:
            time.sleep(1)  # Update display every second

            with self.lock:
                if not self.price_history:
                    continue

                print("\n" + "=" * 50)
                print(f"MARKET DATA UPDATES - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("=" * 50)

                for contract_id, prices in self.price_history.items():
                    if not prices:
                        continue

                    contract_name = self.subscribed_contracts[contract_id]
                    latest = prices[-1]

                    print(f"\n{contract_name}:")
                    print(f"  Last: {latest['last']}")
                    print(f"  Bid: {latest['bid']}")
                    print(f"  Ask: {latest['ask']}")
                    print(f"  Volume: {latest['volume']}")

                    # Calculate price change if we have history
                    if len(prices) > 1:
                        first_price = prices[0]["last"]
                        latest_price = latest["last"]
                        if first_price and latest_price:
                            change = latest_price - first_price
                            change_pct = (change / first_price) * 100 if first_price else 0
                            print(f"  Change: {change:+.2f} ({change_pct:+.2f}%)")

    def stop(self):
        """Stop the monitor."""
        self.running = False


def stream_market_data():
    """Stream real-time market data for selected contracts."""
    global client, monitor

    # Set up signal handling for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Initialize the client
    print(f"Connecting to ProjectX {ENVIRONMENT} environment...")
    client = ProjectXClient(username=USERNAME, api_key=API_KEY, environment=ENVIRONMENT)

    # Create the market data monitor
    monitor = MarketDataMonitor(client)

    try:
        # Get symbols to monitor
        symbols_input = input("Enter symbols to monitor (comma-separated, e.g., ES,NQ,MNQ): ")
        symbols = [s.strip() for s in symbols_input.split(",")]

        if not symbols:
            print("No symbols provided.")
            return

        # Initialize real-time connection
        client.realtime.start()

        # Search for and subscribe to each contract
        for symbol in symbols:
            contracts = client.contracts.search(search_text=symbol, live=False)

            if not contracts:
                print(f"No contracts found matching '{symbol}'.")
                continue

            # Display available contracts
            print(f"\nAvailable contracts for '{symbol}':")
            for i, contract in enumerate(contracts[:3]):  # Show first 3 matches
                print(f"{i+1}. {contract.name} - {contract.description}")

            # Select a contract
            try:
                selection = int(
                    input(f"Select a contract for '{symbol}' (enter number, 0 to skip): ")
                )
                if selection == 0:
                    continue

                selection -= 1  # Adjust for 0-based indexing
                if selection < 0 or selection >= len(contracts):
                    print("Invalid selection, skipping.")
                    continue

                # Subscribe to the selected contract
                monitor.subscribe_contract(contracts[selection])

            except ValueError:
                print("Invalid input, skipping.")
                continue

        if not monitor.subscribed_contracts:
            print("No contracts were subscribed.")
            return

        # Main loop to keep the script running
        print("\nStreaming real-time market data. Press Ctrl+C to exit.")

        while not shutdown_requested:
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nKeyboard interrupt received...")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    finally:
        # Clean up (signal handler may have already done this)
        print("Final cleanup...")
        if monitor:
            monitor.stop()
        if client:
            try:
                client.realtime.stop()
                print("Real-time client stopped successfully")
            except Exception as e:
                print(f"Error stopping real-time client: {e}")


if __name__ == "__main__":
    if not USERNAME or not API_KEY:
        print("Please set PROJECTX_USERNAME and PROJECTX_API_KEY environment variables.")
    else:
        stream_market_data()
