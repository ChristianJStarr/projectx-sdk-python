"""Basic usage example for the ProjectX SDK."""

import os
import time
from datetime import datetime, timedelta

from projectx_sdk import OrderSide, OrderType, ProjectXClient
from projectx_sdk.endpoints.history import TimeUnit

# Get API credentials from environment variables
USERNAME = os.environ.get("PROJECTX_USERNAME")
API_KEY = os.environ.get("PROJECTX_API_KEY")
ENVIRONMENT = os.environ.get("PROJECTX_ENVIRONMENT", "demo")


# Basic example of using the SDK
def main():
    # Initialize the client
    print(f"Connecting to ProjectX {ENVIRONMENT} environment...")
    client = ProjectXClient(username=USERNAME, api_key=API_KEY, environment=ENVIRONMENT)

    # Search for accounts
    print("Searching for accounts...")
    accounts = client.accounts.search(only_active_accounts=True)

    if not accounts:
        print("No active accounts found.")
        return

    account = accounts[0]
    print(f"Using account: {account.name} (ID: {account.id})")

    # Search for a contract
    print("Searching for contracts...")
    contracts = client.contracts.search(search_text="MNQ", live=False)

    if not contracts:
        print("No contracts found matching the search.")
        return

    contract = contracts[0]
    print(f"Found contract: {contract.name} - {contract.description} (ID: {contract.id})")

    # Get historical data
    print("Fetching historical data...")
    from datetime import datetime, timedelta

    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=7)

    bars = client.history.retrieve_bars(
        contract_id=contract.id,
        live=False,
        start_time=start_time,
        end_time=end_time,
        unit=TimeUnit.MINUTE,  # Minutes
        unit_number=15,  # 15-minute bars
        limit=10,
        include_partial_bar=True,
    )

    print(f"Received {len(bars)} historical bars:")
    for i, bar in enumerate(bars[:3]):  # Print first 3 bars
        print(
            f"  Bar {i+1}: Open: {bar.open}, High: {bar.high}, Low: {bar.low}, Close: {bar.close}"
        )

    # Check open positions
    print("Checking open positions...")
    positions = client.positions.search_open(account_id=account.id)

    if positions:
        print(f"Found {len(positions)} open positions:")
        for pos in positions:
            print(f"  {pos.contract_id}: Size: {pos.size}, Avg Price: {pos.average_price}")
    else:
        print("No open positions.")

    # Set up real-time updates
    print("Setting up real-time updates...")

    def on_order_update(order_data):
        print(f"Order update received: Order ID {order_data['id']}, Status: {order_data['status']}")

    def on_position_update(position_data):
        print(f"Position update received for {position_data['contractId']}")

    # Subscribe to updates
    client.realtime.user.subscribe_orders(account.id, callback=on_order_update)
    client.realtime.user.subscribe_positions(account.id, callback=on_position_update)

    # Start the real-time connection
    client.realtime.start()

    print("Real-time connection established. Listening for updates...")
    print("Press Ctrl+C to exit.")

    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        client.realtime.stop()


if __name__ == "__main__":
    if not USERNAME or not API_KEY:
        print("Please set PROJECTX_USERNAME and PROJECTX_API_KEY environment variables.")
    else:
        main()
