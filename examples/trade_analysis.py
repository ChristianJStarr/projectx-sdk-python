"""Example demonstrating trade analysis and performance reporting with the ProjectX SDK."""

import os
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict

import matplotlib.pyplot as plt
import pandas as pd

from projectx_sdk import ProjectXClient

# Get API credentials from environment variables
USERNAME = os.environ.get("PROJECTX_USERNAME")
API_KEY = os.environ.get("PROJECTX_API_KEY")
ENVIRONMENT = os.environ.get("PROJECTX_ENVIRONMENT", "demo")


def analyze_trades():
    """Analyze past trades and generate performance metrics."""
    # Initialize the client
    print(f"Connecting to ProjectX {ENVIRONMENT} environment...")
    client = ProjectXClient(username=USERNAME, api_key=API_KEY, environment=ENVIRONMENT)

    # Get active accounts
    accounts = client.accounts.search(only_active_accounts=True)

    if not accounts:
        print("No active accounts found.")
        return

    # Allow user to select an account
    print("\nAvailable accounts:")
    for i, account in enumerate(accounts):
        print(f"{i+1}. {account.name} (ID: {account.id})")

    account_selection = int(input("\nSelect an account (enter number): ")) - 1
    if account_selection < 0 or account_selection >= len(accounts):
        print("Invalid selection.")
        return

    selected_account = accounts[account_selection]
    print(f"Selected account: {selected_account.name}")

    # Get time period for analysis
    print("\nSelect time period for analysis:")
    print("1. Past day")
    print("2. Past week")
    print("3. Past month")
    print("4. Past 3 months")
    print("5. Custom period")

    period_selection = input("\nEnter selection: ")

    end_time = datetime.utcnow()

    if period_selection == "1":
        start_time = end_time - timedelta(days=1)
        period_name = "Past day"
    elif period_selection == "2":
        start_time = end_time - timedelta(days=7)
        period_name = "Past week"
    elif period_selection == "3":
        start_time = end_time - timedelta(days=30)
        period_name = "Past month"
    elif period_selection == "4":
        start_time = end_time - timedelta(days=90)
        period_name = "Past 3 months"
    elif period_selection == "5":
        start_date = input("Enter start date (YYYY-MM-DD): ")
        try:
            start_time = datetime.strptime(start_date, "%Y-%m-%d")
            period_name = f"From {start_date} to {end_time.strftime('%Y-%m-%d')}"
        except ValueError:
            print("Invalid date format.")
            return
    else:
        print("Invalid selection.")
        return

    print(f"\nRetrieving trades for {period_name}...")

    # Fetch trades for the selected period
    trades = client.trades.search(
        account_id=selected_account.id, start_time=start_time, end_time=end_time
    )

    if not trades:
        print("No trades found for the selected period.")
        return

    print(f"Retrieved {len(trades)} trades.")

    # Convert trades to a DataFrame for analysis
    trade_data = []
    for trade in trades:
        trade_data.append(
            {
                "trade_id": trade.id,
                "contract_id": trade.contract_id,
                "timestamp": trade.timestamp,
                "size": trade.size,
                "price": trade.price,
                "side": trade.side.name,
                "order_id": trade.order_id,
                "commission": trade.commission,
            }
        )

    # Create DataFrame
    df = pd.DataFrame(trade_data)

    # Get contract details for each traded contract
    contracts = {}
    for contract_id in df["contract_id"].unique():
        try:
            contract = client.contracts.get(contract_id=contract_id)
            contracts[contract_id] = {
                "name": contract.name,
                "description": contract.description,
                "tick_size": contract.tick_size,
                "tick_value": contract.tick_value,
            }
        except Exception:
            contracts[contract_id] = {
                "name": f"Unknown ({contract_id})",
                "description": "Contract details not available",
                "tick_size": 0.01,
                "tick_value": 1.0,
            }

    # Add contract information to DataFrame
    df["contract_name"] = df["contract_id"].apply(
        lambda x: contracts[x]["name"] if x in contracts else "Unknown"
    )
    df["tick_size"] = df["contract_id"].apply(
        lambda x: contracts[x]["tick_size"] if x in contracts else 0.01
    )
    df["tick_value"] = df["contract_id"].apply(
        lambda x: contracts[x]["tick_value"] if x in contracts else 1.0
    )

    # Calculate profit/loss (P&L)
    df["trade_value"] = df["size"] * df["price"] * df["tick_value"] / df["tick_size"]
    df["trade_value_with_sign"] = df.apply(
        lambda row: row["trade_value"] * (-1 if row["side"] == "BUY" else 1), axis=1
    )

    # Group trades by order ID to calculate P&L per order
    order_groups = df.groupby("order_id")
    order_pnl = {}

    for order_id, group in order_groups:
        buy_value = group[group["side"] == "BUY"]["trade_value"].sum()
        sell_value = group[group["side"] == "SELL"]["trade_value"].sum()
        pnl = sell_value - buy_value
        order_pnl[order_id] = pnl

    # Calculate summary statistics
    total_pnl = sum(order_pnl.values())
    total_commission = df["commission"].sum()
    net_pnl = total_pnl - total_commission
    winning_trades = sum(1 for pnl in order_pnl.values() if pnl > 0)
    losing_trades = sum(1 for pnl in order_pnl.values() if pnl <= 0)
    total_trades = len(order_pnl)
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

    # Calculate statistics by contract
    contract_stats: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {
            "trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "total_pnl": 0,
            "commission": 0,
            "volume": 0,
        }
    )

    for order_id, pnl in order_pnl.items():
        order_trades = df[df["order_id"] == order_id]
        if not order_trades.empty:
            contract_id = order_trades.iloc[0]["contract_id"]
            contract_name = (
                contracts[contract_id]["name"] if contract_id in contracts else "Unknown"
            )

            contract_stats[contract_name]["trades"] += 1
            contract_stats[contract_name]["total_pnl"] += pnl
            contract_stats[contract_name]["commission"] += order_trades["commission"].sum()
            contract_stats[contract_name]["volume"] += order_trades["size"].sum()

            if pnl > 0:
                contract_stats[contract_name]["winning_trades"] += 1
            else:
                contract_stats[contract_name]["losing_trades"] += 1

    # Print overall performance summary
    print("\n" + "=" * 60)
    print(f"TRADING PERFORMANCE SUMMARY - {period_name}")
    print("=" * 60)

    print(f"\nTotal Trades: {total_trades}")
    print(f"Winning Trades: {winning_trades} ({win_rate:.1f}%)")
    print(f"Losing Trades: {losing_trades} ({100-win_rate:.1f}%)")
    print(f"Total P&L: ${total_pnl:.2f}")
    print(f"Total Commission: ${total_commission:.2f}")
    print(f"Net P&L: ${net_pnl:.2f}")

    # Print performance by contract
    print("\n" + "=" * 60)
    print("PERFORMANCE BY CONTRACT")
    print("=" * 60)

    for contract_name, stats in contract_stats.items():
        win_rate = (stats["winning_trades"] / stats["trades"] * 100) if stats["trades"] > 0 else 0
        net_pnl = stats["total_pnl"] - stats["commission"]

        print(f"\n{contract_name}:")
        print(f"  Trades: {stats['trades']}")
        print(f"  Win Rate: {win_rate:.1f}%")
        print(f"  Volume: {stats['volume']} contracts")
        print(f"  P&L: ${stats['total_pnl']:.2f}")
        print(f"  Commission: ${stats['commission']:.2f}")
        print(f"  Net P&L: ${net_pnl:.2f}")

    # Create visualizations
    try:
        # Prepare daily P&L data
        df["date"] = pd.to_datetime(df["timestamp"]).dt.date
        daily_pnl = df.groupby("date")["trade_value_with_sign"].sum()
        daily_commission = df.groupby("date")["commission"].sum()
        daily_net_pnl = daily_pnl - daily_commission

        # Plot daily P&L
        plt.figure(figsize=(12, 6))
        plt.bar(
            daily_net_pnl.index,
            daily_net_pnl.values,
            color=["g" if x > 0 else "r" for x in daily_net_pnl.values],
        )
        plt.title(f"Daily P&L - {period_name}")
        plt.xlabel("Date")
        plt.ylabel("Net P&L ($)")
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()

        # Plot cumulative P&L
        plt.figure(figsize=(12, 6))
        cumulative_pnl = daily_net_pnl.cumsum()
        plt.plot(cumulative_pnl.index, cumulative_pnl.values, marker="o")
        plt.title(f"Cumulative P&L - {period_name}")
        plt.xlabel("Date")
        plt.ylabel("Cumulative Net P&L ($)")
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.tight_layout()

        # Plot performance by contract
        if len(contract_stats) > 1:
            plt.figure(figsize=(12, 6))
            contract_names = list(contract_stats.keys())
            contract_pnls = [
                stats["total_pnl"] - stats["commission"] for stats in contract_stats.values()
            ]

            colors = ["g" if x > 0 else "r" for x in contract_pnls]
            plt.bar(contract_names, contract_pnls, color=colors)
            plt.title(f"P&L by Contract - {period_name}")
            plt.xlabel("Contract")
            plt.ylabel("Net P&L ($)")
            plt.xticks(rotation=45, ha="right")
            plt.grid(axis="y", linestyle="--", alpha=0.7)
            plt.tight_layout()

        # Display all plots
        plt.show()

    except Exception as e:
        print(f"Error creating visualizations: {str(e)}")
        print("Visualization requires matplotlib. Install with: pip install matplotlib")


if __name__ == "__main__":
    if not USERNAME or not API_KEY:
        print("Please set PROJECTX_USERNAME and PROJECTX_API_KEY environment variables.")
    else:
        analyze_trades()
