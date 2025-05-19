# ProjectX SDK Examples

This directory contains example scripts that demonstrate how to use the ProjectX SDK for various trading and market data tasks.

## Example Overview

- **basic_usage.py** - A simple introduction to the SDK that demonstrates basic functionality including connecting to the API, searching for contracts, fetching historical data, and setting up real-time updates.

- **order_placement.py** - Demonstrates how to place, monitor, and cancel orders using the SDK's order management functionality.

- **historical_data_analysis.py** - Shows how to retrieve historical market data for different timeframes and perform basic analysis including moving averages and visualization.

- **market_data_streaming.py** - Demonstrates how to subscribe to and handle real-time market data streams including price updates and trades.

- **trade_analysis.py** - Analyzes past trading activity to calculate performance metrics such as profit/loss, win rate, and trading statistics by contract.

## Getting Started

1. Make sure you have set the following environment variables:
   ```
   PROJECTX_USERNAME=your_username
   PROJECTX_API_KEY=your_api_key
   PROJECTX_ENVIRONMENT=demo  # or "live" for production
   ```

2. Install required dependencies:
   ```
   pip install pandas matplotlib
   ```

3. Run any example:
   ```
   python examples/basic_usage.py
   ```

## Additional Requirements

Some examples require additional Python packages:
- `pandas` and `matplotlib` for data analysis and visualization
- `threading` for asynchronous data handling

## Notes

- All examples connect to the demo environment by default. To use the live environment, set the `PROJECTX_ENVIRONMENT` environment variable to "live".
- The examples are designed to be interactive and will prompt for user input when needed.
- Make sure your API credentials have the necessary permissions for the actions demonstrated in each example.
