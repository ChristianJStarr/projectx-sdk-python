# ProjectX Gateway API SDK for Python (Unofficial)

A Python client library for the ProjectX Gateway API, enabling proprietary trading firms and evaluation providers to interact with ProjectX's trading platform programmatically.

> **DISCLAIMER:** This is an **unofficial** SDK. The author(s) of this package are not affiliated with or endorsed by ProjectX. This is a community-developed tool to interact with their public API.

[![Python Tests](https://github.com/ChristianJStarr/projectx-sdk-python/actions/workflows/tests.yml/badge.svg?branch=master)](https://github.com/ChristianJStarr/projectx-sdk-python/actions/workflows/tests.yml)
[![PyPI version](https://badge.fury.io/py/projectx-sdk.svg)](https://badge.fury.io/py/projectx-sdk)
[![Python Version](https://img.shields.io/pypi/pyversions/projectx-sdk.svg)](https://pypi.org/project/projectx-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Features

- Complete coverage of ProjectX Gateway API endpoints
- Support for real-time WebSocket updates via SignalR
- Pythonic interface with proper error handling
- Support for all ProjectX environments

## Installation

```bash
pip install projectx-sdk
```

For development, you can install with additional tools:

```bash
pip install projectx-sdk[dev]
```

## Quick Start

```python
from projectx_sdk import ProjectXClient, OrderType, OrderSide

# Initialize with API key
client = ProjectXClient(
    username="your_username",
    api_key="your_api_key",
    environment="topstepx"  # Or another supported environment
)

# Get all active accounts
accounts = client.accounts.search(only_active_accounts=True)
account_id = accounts[0].id if accounts else None

if account_id:
    # Search for contracts
    contracts = client.contracts.search(search_text="NQ", live=False)

    if contracts:
        contract_id = contracts[0].id

        # Place a market order
        order = client.orders.place(
            account_id=account_id,
            contract_id=contract_id,
            type=OrderType.MARKET,
            side=OrderSide.BUY,
            size=1
        )

        print(f"Order placed with ID: {order['orderId']}")

        # Set up real-time order updates
        def on_order_update(order_data):
            print(f"Order update: {order_data}")

        client.realtime.user.subscribe_orders(account_id, callback=on_order_update)
        client.realtime.start()
```

## Environment Support

The SDK supports all ProjectX environments:

| Platform | SDK Key | Tested |
|----------|---------|--------|
| Alpha Ticks | `alphaticks` | ✅ |
| Blue Guardian | `blueguardian` | ❓ |
| Blusky | `blusky` | ❓ |
| E8X | `e8x` | ❓ |
| Funding Futures | `fundingfutures` | ❓ |
| The Futures Desk | `futuresdesk` | ❓ |
| Futures Elite | `futureselite` | ❓ |
| FXIFY Futures | `fxifyfutures` | ❓ |
| GoatFunded | `goatfunded` | ❓ |
| TickTickTrader | `tickticktrader` | ❓ |
| TopOneFutures | `toponefutures` | ❓ |
| TopstepX | `topstepx` | ✅ |
| TX3Funding | `tx3funding` | ❓ |

> Note: ✅ = Tested and confirmed working, ❓ = Not officially tested yet

## API Components

The SDK is organized into several components:

- **Client**: The main entry point that provides access to all API functionality
- **Authentication**: Handles authentication and token management
- **Endpoints**: Service modules for each API endpoint (accounts, contracts, orders, etc.)
- **Models**: Data classes for API entities (account, contract, order, etc.)
- **Real-time**: WebSocket functionality for real-time updates

## Development

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/ChristianJStarr/projectx-sdk-python.git
   cd projectx-sdk-python
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

### Running Tests

Run the entire test suite:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=projectx_sdk
```

Run specific test files:

```bash
pytest tests/test_client.py
```

### Code Quality Tools

- **Black**: Code formatter
  ```bash
  black projectx_sdk tests
  ```

- **isort**: Import sorter
  ```bash
  isort projectx_sdk tests
  ```

- **Flake8**: Linter
  ```bash
  flake8 projectx_sdk tests
  ```

- **mypy**: Type checker
  ```bash
  mypy projectx_sdk
  ```

## Building and Publishing

Build the package:

```bash
python -m build
```

Check the distribution:

```bash
twine check dist/*
```

Upload to PyPI:

```bash
twine upload dist/*
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Run the tests to ensure they pass
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

Please remember that this is an unofficial SDK and not affiliated with ProjectX.

## Documentation

For detailed information about the ProjectX API that this unofficial SDK interacts with, please visit the [ProjectX API Documentation](https://gateway.docs.projectx.com/docs/intro).

## License

This project is licensed under the MIT License - see the LICENSE file for details.
