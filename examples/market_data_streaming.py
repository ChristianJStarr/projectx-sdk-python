"""Example demonstrating real-time market data streaming with the ProjectX SDK."""

import os
import threading
import time
from collections import deque
from datetime import datetime

from projectx_sdk import ProjectXClient

# Get API credentials from environment variables
USERNAME = os.environ.get("PROJECTX_USERNAME")
API_KEY = os.environ.get("PROJECTX_API_KEY")
ENVIRONMENT = os.environ.get("PROJECTX_ENVIRONMENT", "demo")


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

    def on_price_update(self, data):
        """Handle real-time price updates."""
        contract_id = data.get("contractId")
        if not contract_id or contract_id not in self.subscribed_contracts:
            return

        with self.lock:
            if contract_id not in self.price_history:
                self.price_history[contract_id] = deque(maxlen=100)  # Keep last 100 prices

            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            price_data = {
                "timestamp": timestamp,
                "last": data.get("last"),
                "bid": data.get("bid"),
                "ask": data.get("ask"),
                "volume": data.get("volume"),
            }
            self.price_history[contract_id].append(price_data)

    def on_trade_update(self, data):
        """Handle real-time trade updates."""
        contract_id = data.get("contractId")
        if not contract_id or contract_id not in self.subscribed_contracts:
            return

        contract_name = self.subscribed_contracts[contract_id]
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        print(f"\n[{timestamp}] TRADE: {contract_name}")
        print(f"  Price: {data.get('price')}")
        print(f"  Size: {data.get('size')}")
        print(f"  Side: {data.get('side')}")

    def subscribe_contract(self, contract):
        """Subscribe to real-time data for a contract."""
        contract_id = contract.id

        # Store contract info
        self.subscribed_contracts[contract_id] = contract.name

        # Initialize price history
        with self.lock:
            self.price_history[contract_id] = deque(maxlen=100)

        # Subscribe to price updates
        self.client.realtime.market.subscribe_prices(
            contract_id=contract_id, callback=self.on_price_update
        )

        # Subscribe to trade updates
        self.client.realtime.market.subscribe_trades(
            contract_id=contract_id, callback=self.on_trade_update
        )

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

        while True:
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        # Clean up
        monitor.stop()
        client.realtime.stop()


if __name__ == "__main__":
    if not USERNAME or not API_KEY:
        print("Please set PROJECTX_USERNAME and PROJECTX_API_KEY environment variables.")
    else:
        stream_market_data()
