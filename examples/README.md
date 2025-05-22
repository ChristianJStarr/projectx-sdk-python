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

## Running the Examples

To run these examples, you'll need:

1. A ProjectX account with API access
2. Your username and API key

Set these as environment variables:

```bash
export PROJECTX_USERNAME=your_username
export PROJECTX_API_KEY=your_api_key
```

Then run an example:

```bash
python realtime_example.py
```

## Troubleshooting Realtime Connections

If you're experiencing issues with realtime connections, follow this troubleshooting guide:

### Common Issues and Solutions

#### No events being received

If you've subscribed to market events but aren't receiving any callbacks:

1. **Check Authentication**: Ensure your API key is valid and has appropriate permissions.
   ```python
   # Verify authentication is working
   accounts = client.accounts.get_accounts()
   print(accounts)  # If this fails, you have an authentication issue
   ```

2. **Verify Connection Establishment**: Add debug logging to check connection status.
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

3. **Check Method Names**: The exact method names must match between client and server.
   - SubscribeContractQuotes
   - SubscribeContractTrades
   - SubscribeContractMarketDepth

4. **Check Contract IDs**: Verify the contract ID is valid and properly formatted.
   ```python
   # Get all available contracts
   contracts = client.contracts.search_contracts()
   valid_ids = [c["id"] for c in contracts["contracts"]]
   print(valid_ids)
   ```

5. **Enable Signal-R Debug Mode**: Directly configure the SignalR connection:
   ```python
   # Add more debug logging
   import signalrcore.hub.errors
   signalrcore.hub.errors.HubError.verbose = True
   ```

6. **Verify Event Names**: The events from the server must match these exactly:
   - GatewayQuote
   - GatewayTrade
   - GatewayDepth

7. **Check Callback Function Signatures**: Your callbacks should accept 2 parameters:
   ```python
   def handle_quote(contract_id: str, data: dict):
       # Both parameters are required
       print(f"Contract: {contract_id}, Data: {data}")
   ```

8. **Connection Timing**: Ensure the connection is fully established before subscribing:
   ```python
   # Start first, then subscribe
   realtime.start()
   time.sleep(2)  # Give it time to connect
   market_hub.subscribe_quotes(contract_id, handle_quote)
   ```

#### Connection Drops or Errors

If the connection is unstable or drops frequently:

1. **Check Network Stability**: Realtime connections require stable internet.

2. **Implement Reconnect Logic**: Use the built-in reconnect functionality:
   ```python
   # The SDK handles reconnection automatically
   # You can also manually reconnect
   realtime.stop()
   time.sleep(1)
   realtime.start()  # This will reestablish connections and resubscribe
   ```

3. **Check for Credential Expiration**: Ensure your token hasn't expired.
   The SDK should handle this automatically, but you can verify:
   ```python
   # Force token refresh
   client.auth.validate_token()
   ```

### Debugging Tools

1. **Connection Testing Script**:
   ```python
   import time
   from projectx_sdk import ProjectXClient
   from projectx_sdk.realtime import RealtimeService

   # Enable verbose logging
   import logging
   logging.basicConfig(level=logging.DEBUG)

   client = ProjectXClient(username="...", api_key="...", environment="demo")
   realtime = RealtimeService(client)

   # Connection state callbacks
   def on_connect():
       print("CONNECTED!")

   def on_disconnect():
       print("DISCONNECTED!")

   # Manually attach to connection events
   realtime.market._connection.on_open(on_connect)
   realtime.market._connection.on_close(on_disconnect)

   # Start the connection
   realtime.start()

   # Keep alive
   try:
       while True:
           time.sleep(1)
   except KeyboardInterrupt:
       realtime.stop()
   ```

2. **Data Structure Inspection**:
   ```python
   def debug_callback(contract_id, data):
       import json
       print(f"CONTRACT: {contract_id}")
       print(f"DATA: {json.dumps(data, indent=2)}")

   market_hub.subscribe_quotes("CON.F.US.ENQ.H25", debug_callback)
   ```

### Advanced Troubleshooting

If basic troubleshooting doesn't resolve your issue:

1. **Direct SignalR Connection**: Bypass the SDK abstraction layer:
   ```python
   from signalrcore.hub_connection_builder import HubConnectionBuilder

   token = client.auth.get_token()
   hub_url = "https://gateway-api-demo.s2f.projectx.com/hubs/market"

   connection = (
       HubConnectionBuilder()
       .with_url(f"{hub_url}?access_token={token}")
       .with_automatic_reconnect({
           "type": "raw",
           "keep_alive_interval": 10,
           "reconnect_interval": 5,
           "max_attempts": 10,
       })
       .build()
   )

   connection.on("GatewayQuote", lambda contract_id, data:
       print(f"QUOTE: {contract_id} - {data}"))

   connection.start()
   connection.invoke("SubscribeContractQuotes", "CON.F.US.ENQ.H25")
   ```

2. **Network Traffic Analysis**: Use tools like Wireshark to inspect the WebSocket traffic.

3. **Check Server Status**: Verify the ProjectX API status and whether there are any known issues.
