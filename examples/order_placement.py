"""Example demonstrating order placement with the ProjectX SDK."""

import os
import sys
import time

from projectx_sdk import OrderSide, OrderType, ProjectXClient

# Get API credentials from environment variables
USERNAME = os.environ.get("PROJECTX_USERNAME")
API_KEY = os.environ.get("PROJECTX_API_KEY")
ENVIRONMENT = os.environ.get("PROJECTX_ENVIRONMENT", "demo")


def place_order():
    """Place and manage an order using the ProjectX SDK."""

    # Initialize the client
    client = ProjectXClient(username=USERNAME, api_key=API_KEY, environment=ENVIRONMENT)

    # Get active accounts
    accounts = client.accounts.search(only_active_accounts=True)

    if not accounts:
        print("No active accounts found.")
        return

    account = accounts[0]
    print(f"Using account: {account.name} (ID: {account.id})")

    # Search for a contract to trade
    symbol = input("Enter a symbol to search for (e.g., MNQ, ES): ")

    contracts = client.contracts.search(search_text=symbol, live=False)

    if not contracts:
        print(f"No contracts found matching '{symbol}'.")
        return

    # Display available contracts
    print("\nAvailable contracts:")
    for i, contract in enumerate(contracts[:5]):  # Show first 5 matches
        print(
            f"{i+1}. {contract.name} - {contract.description} (Tick Size: {contract.tick_size}, Tick Value: {contract.tick_value})"  # noqa: E501
        )

    # Select a contract
    selection = int(input("\nSelect a contract (enter number): ")) - 1
    if selection < 0 or selection >= len(contracts):
        print("Invalid selection.")
        return

    contract = contracts[selection]
    print(f"Selected contract: {contract.name}")

    # Get order details
    try:
        order_side = input("Buy or Sell? (b/s): ").lower()
        if order_side == "b":
            side = OrderSide.BUY
            side_name = "BUY"
        elif order_side == "s":
            side = OrderSide.SELL
            side_name = "SELL"
        else:
            print("Invalid side. Please enter 'b' for buy or 's' for sell.")
            return

        order_type_input = input("Order type - (1) Market, (2) Limit, (3) Stop: ")
        if order_type_input == "1":
            order_type = OrderType.MARKET
            type_name = "MARKET"
            limit_price = None
            stop_price = None
        elif order_type_input == "2":
            order_type = OrderType.LIMIT
            type_name = "LIMIT"
            limit_price = float(input("Enter limit price: "))
            stop_price = None
        elif order_type_input == "3":
            order_type = OrderType.STOP
            type_name = "STOP"
            limit_price = None
            stop_price = float(input("Enter stop price: "))
        else:
            print("Invalid order type.")
            return

        size = int(input("Enter quantity: "))

        # Confirm order
        print("\nOrder details:")
        print(f"Account: {account.name}")
        print(f"Contract: {contract.name} ({contract.description})")
        print(f"Action: {side_name}")
        print(f"Type: {type_name}")
        if limit_price:
            print(f"Limit Price: {limit_price}")
        if stop_price:
            print(f"Stop Price: {stop_price}")
        print(f"Quantity: {size}")

        confirm = input("\nConfirm order? (y/n): ").lower()

        if confirm != "y":
            print("Order cancelled.")
            return

        # Set up real-time order updates before placing the order
        def on_order_update(order_data):
            print(f"\nOrder update received: Order ID {order_data['id']}")
            print(f"Status: {order_data['status']}")
            print(f"Size: {order_data['size']}")
            if "limitPrice" in order_data and order_data["limitPrice"] is not None:
                print(f"Limit Price: {order_data['limitPrice']}")
            if "stopPrice" in order_data and order_data["stopPrice"] is not None:
                print(f"Stop Price: {order_data['stopPrice']}")

        # Subscribe to order updates
        client.realtime.user.subscribe_orders(account.id, callback=on_order_update)
        client.realtime.start()

        print("\nPlacing order...")

        # Place the order
        order_id = client.orders.place(
            account_id=account.id,
            contract_id=contract.id,
            order_type=order_type,
            side=side,
            size=size,
            limit_price=limit_price,
            stop_price=stop_price,
        )

        print(f"\nOrder placed successfully! Order ID: {order_id}")

        # Wait for updates
        print("\nListening for order updates. Press Ctrl+C to exit.")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nExiting...")

            # Check if we should cancel the order
            if input("\nDo you want to cancel the order? (y/n): ").lower() == "y":
                cancel_result = client.orders.cancel(account_id=account.id, order_id=order_id)

                if cancel_result:
                    print("Order cancelled successfully.")
                else:
                    print("Failed to cancel order.")

        # Stop the real-time connection
        client.realtime.stop()

    except Exception as e:
        print(f"Error: {str(e)}")
        client.realtime.stop()


if __name__ == "__main__":
    if not USERNAME or not API_KEY:
        print("Please set PROJECTX_USERNAME and PROJECTX_API_KEY environment variables.")
        sys.exit(1)

    place_order()
