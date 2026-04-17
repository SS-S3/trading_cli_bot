# Binance Futures Trading Bot

A high-performance, structured Python trading bot designed to interface with the **Binance Futures Demo (Testnet) API**. This bot provides a premium CLI experience for managing USDT-M Futures orders with robust validation and advanced logging.

## Features
- **Order Types**: Full support for `MARKET`, `LIMIT`, and `STOP_LIMIT` (Bonus) orders.
- **Advanced Diagnostics**: Automatic API key format verification and masking.
- **Premium CLI**: Interactive and aesthetically pleasing output using `Typer` and `Rich`.
- **Configurable Logging**: Dual-stream logging (Console + File) with environment-based log levels.
- **Robust Validation**: Pre-flight validation for symbols, sides, order types, quantities, and prices.
- **Error Intelligence**: Specific hints for common Binance API errors (e.g., key length, permissions).

## Technical Specifications
- **Language**: Python 3.8+
- **API Library**: `python-binance`
- **CLI Framework**: `Typer`
- **Output Styling**: `Rich`
- **Configuration**: `python-dotenv`
- **Validation**: `Pydantic` (custom logic)

## Logic & Architecture

### 1. Initialization Flow
- **Environment Loading**: The bot loads credentials from a `.env` file using `dotenv`.
- **Client Configuration**: The `BinanceFuturesClient` initializes the `python-binance` Client with `testnet=True`. It specifically overrides the base URL to point to the **Binance Demo Trading** endpoint (`https://demo-fapi.binance.com/fapi`).
- **Diagnostics**: Upon startup, the client verifies the API key format (checking for the standard 64-character length) and logs masked credentials for security auditing.

### 2. Order Placement Logic
- **Validation**: Every CLI input is passed through `bot/validators.py` before any API call is made. This ensures minimum quantities and valid symbol formats.
- **Parameter Mapping**: The `OrderManager` translates CLI options into the precise dictionary format expected by the Binance Futures API.
- **Exception Handling**: The bot distinguishes between `BinanceAPIException` (API-side errors), `BinanceOrderException` (order logic errors), and general system errors, providing context-aware hints for each.

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Configure API Keys**:
   Create a `.env` file in the root directory:
   ```env
   BINANCE_API_KEY=your_64_char_api_key
   BINANCE_API_SECRET=your_64_char_api_secret
   ```

## Usage

### Commands
- **Ping**: `python cli.py ping` - Test connection to the Demo API.
- **Place Order**: `python cli.py place --symbol BTCUSDT --side BUY --order-type MARKET --quantity 0.001`

### Debugging
You can enable detailed diagnostic logs by setting the `LOG_LEVEL` environment variable:
```bash
LOG_LEVEL=DEBUG python3 cli.py place --symbol BTCUSDT --side BUY --order-type MARKET --quantity 0.001
```

## Sample Output

```text
soumyashekhar@soumyas-MacBook-Air trading_bot % LOG_LEVEL=DEBUG python3 cli.py place --symbol BTCUSDT --side BUY --order-type MARKET --quantity 0.001

╭──────────────────────────────────────────────── Request ────────────────────────────────────────────────╮
│ Order Request Summary                                                                                  │
│ Symbol: BTCUSDT                                                                                        │
│ Side: BUY                                                                                              │
│ Type: MARKET                                                                                           │
│ Quantity: 0.001                                                                                        │
│                                                                                                        │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────╯
DEBUG: Initializing client with API Key: mA83Ug...TeVA (length: 64)
DEBUG: API Secret length: 64
INFO: Successfully initialized Binance Futures Demo client using https://demo-fapi.binance.com/fapi
INFO: Placing MARKET BUY order for 0.001 BTCUSDT...
DEBUG: Order Params: {'symbol': 'BTCUSDT', 'side': 'BUY', 'type': 'MARKET', 'quantity': 0.001}
INFO: Order placed successfully. Response: {'orderId': 13043349544, ...}

   Order Response Details    
┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Field       ┃ Value       ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ orderId     │ 13043349544 │
│ status      │ NEW         │
│ executedQty │ 0.0000      │
│ avgPrice    │ 0.00        │
│ symbol      │ BTCUSDT     │
│ side        │ BUY         │
│ type        │ MARKET      │
└─────────────┴─────────────┘
✔ Order placed successfully!
```

## Project Structure
- `bot/`: Core logic modules.
  - `client.py`: Client wrapper and demo-fapi configuration.
  - `orders.py`: Order placement and response formatting.
  - `validators.py`: Data integrity checks.
  - `logging_config.py`: Advanced logging setup.
- `cli.py`: Main CLI entry point.
- `bot.log`: Persistent log of all trading activities.
