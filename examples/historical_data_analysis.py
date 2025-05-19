"""Example demonstrating historical data retrieval and analysis with the ProjectX SDK."""

import os
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import pandas as pd

from projectx_sdk import ProjectXClient, TimeUnit

# Get API credentials from environment variables
USERNAME = os.environ.get("PROJECTX_USERNAME")
API_KEY = os.environ.get("PROJECTX_API_KEY")
ENVIRONMENT = os.environ.get("PROJECTX_ENVIRONMENT", "demo")


def analyze_historical_data():
    """Retrieve and analyze historical market data."""
    # Initialize the client
    client = ProjectXClient(username=USERNAME, api_key=API_KEY, environment=ENVIRONMENT)

    # Search for a contract
    symbol = input("Enter a symbol to analyze (e.g., ES, NQ, MNQ): ")
    contracts = client.contracts.search(search_text=symbol, live=False)

    if not contracts:
        print(f"No contracts found matching '{symbol}'.")
        return

    # Display available contracts
    print("\nAvailable contracts:")
    for i, contract in enumerate(contracts[:5]):  # Show first 5 matches
        print(f"{i+1}. {contract.name} - {contract.description}")

    # Select a contract
    selection = int(input("\nSelect a contract (enter number): ")) - 1
    if selection < 0 or selection >= len(contracts):
        print("Invalid selection.")
        return

    contract = contracts[selection]
    print(f"Selected contract: {contract.name}")

    # Select time period
    period_options = {
        "1": {
            "days": 1,
            "unit": TimeUnit.MINUTE,
            "unit_number": 1,
            "label": "1-minute bars for the past day",
        },
        "2": {
            "days": 5,
            "unit": TimeUnit.MINUTE,
            "unit_number": 5,
            "label": "5-minute bars for the past 5 days",
        },
        "3": {
            "days": 30,
            "unit": TimeUnit.MINUTE,
            "unit_number": 15,
            "label": "15-minute bars for the past month",
        },
        "4": {
            "days": 90,
            "unit": TimeUnit.HOUR,
            "unit_number": 1,
            "label": "1-hour bars for the past 3 months",
        },
        "5": {
            "days": 365,
            "unit": TimeUnit.DAY,
            "unit_number": 1,
            "label": "Daily bars for the past year",
        },
    }

    print("\nSelect time period:")
    for key, value in period_options.items():
        print(f"{key}. {value['label']}")

    period_selection = input("\nEnter selection: ")
    if period_selection not in period_options:
        print("Invalid selection.")
        return

    selected_period = period_options[period_selection]

    # Calculate date range
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=selected_period["days"])

    print(f"\nFetching {selected_period['label']}...")
    print(f"Date range: {start_time.date()} to {end_time.date()}")

    # Retrieve historical data
    bars = client.history.retrieve_bars(
        contract_id=contract.id,
        live=False,
        start_time=start_time,
        end_time=end_time,
        unit=selected_period["unit"],
        unit_number=selected_period["unit_number"],
        include_partial_bar=False,
    )

    if not bars:
        print("No historical data available for the selected time period.")
        return

    print(f"Retrieved {len(bars)} bars of historical data.")

    # Convert to pandas DataFrame for analysis
    data = []
    for bar in bars:
        data.append(
            {
                "timestamp": bar.timestamp,
                "open": bar.open,
                "high": bar.high,
                "low": bar.low,
                "close": bar.close,
                "volume": bar.volume,
            }
        )

    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df.set_index("timestamp", inplace=True)

    # Basic statistics
    print("\nBasic Statistics:")
    print(f"Average price: {df['close'].mean():.2f}")
    print(f"Minimum price: {df['low'].min():.2f}")
    print(f"Maximum price: {df['high'].max():.2f}")
    print(f"Price range: {df['high'].max() - df['low'].min():.2f}")

    # Calculate simple moving averages
    df["SMA20"] = df["close"].rolling(window=20).mean()
    df["SMA50"] = df["close"].rolling(window=50).mean()

    # Volatility (standard deviation of returns)
    df["returns"] = df["close"].pct_change()
    volatility = df["returns"].std() * (252**0.5)  # Annualized
    print(f"Annualized volatility: {volatility:.2%}")

    # Plot the data
    try:
        plt.figure(figsize=(12, 8))

        # Price and moving averages
        plt.subplot(2, 1, 1)
        plt.plot(df.index, df["close"], label="Close Price")
        plt.plot(df.index, df["SMA20"], label="20-period SMA")
        plt.plot(df.index, df["SMA50"], label="50-period SMA")
        plt.title(f"{contract.name} - {contract.description}")
        plt.ylabel("Price")
        plt.legend()
        plt.grid(True)

        # Volume
        plt.subplot(2, 1, 2)
        plt.bar(df.index, df["volume"])
        plt.ylabel("Volume")
        plt.grid(True)

        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"Error creating chart: {str(e)}")
        print("Plot functionality requires matplotlib. Install with: pip install matplotlib")


if __name__ == "__main__":
    if not USERNAME or not API_KEY:
        print("Please set PROJECTX_USERNAME and PROJECTX_API_KEY environment variables.")
    else:
        analyze_historical_data()
