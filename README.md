# Binance Futures Trading Bot

A high-performance, structured Python trading bot designed to interface with the **Binance Futures Demo (Testnet) API**. This bot provides a premium CLI experience for managing USDT-M Futures orders with robust validation and advanced logging.

---

## Features

- **Order Types**: Full support for `MARKET`, `LIMIT`, and `STOP_LIMIT` orders.
- **Both Sides**: `BUY` and `SELL` on any valid Binance Futures symbol.
- **Advanced Diagnostics**: Automatic API key format verification and masking.
- **Premium CLI**: Interactive and aesthetically pleasing output using `Typer` and `Rich`.
- **Configurable Logging**: Dual-stream logging (Console + File) with environment-based log levels.
- **Robust Validation**: Pre-flight validation for symbols, sides, order types, quantities, and prices.
- **Case Normalisation**: Inputs are accepted in any case (e.g., `buy`, `Buy`, `BUY`).
- **Error Intelligence**: Specific hints for common Binance API errors (e.g., key length, permissions).

---

## Technical Specifications

| Item              | Detail                                  |
|-------------------|-----------------------------------------|
| Language          | Python 3.8+                             |
| API Library       | `python-binance`                        |
| CLI Framework     | `Typer`                                 |
| Output Styling    | `Rich`                                  |
| Configuration     | `python-dotenv`                         |
| Testnet URL       | `https://demo-fapi.binance.com/fapi`    |

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── client.py          # BinanceFuturesClient wrapper + Demo URL config
│   ├── orders.py          # OrderManager — placement + response formatting
│   ├── validators.py      # Input validation (symbol, side, type, qty, price)
│   └── logging_config.py  # Dual-stream logging setup (console + file)
├── tests/
│   └── test_bot.py        # Full test suite (28 tests)
├── cli.py                 # Main CLI entry point (Typer)
├── bot.log                # Persistent log of all trading activity
├── .env                   # API credentials (not committed)
├── .env.example           # Credential template
└── requirements.txt
```

---

## Logic & Architecture

### 1. Initialization Flow
- **Environment Loading**: Credentials are loaded from `.env` via `python-dotenv`.
- **Client Configuration**: `BinanceFuturesClient` initialises `python-binance` with `testnet=True` and overrides the base URL to `https://demo-fapi.binance.com/fapi`.
- **Diagnostics**: The client logs a masked API key (`mA83Ug...TeVA`) and key length at `DEBUG` level.

### 2. Order Placement Logic
- **Validation**: Every input is validated in `bot/validators.py` before any network call.
- **Parameter Mapping**: `OrderManager` translates validated CLI options into the exact dict format expected by the Binance Futures REST API.
- **STOP_LIMIT**: Mapped to Binance's `type=STOP` algo-order endpoint, which returns a different response shape (`algoId`, `algoStatus`, `triggerPrice`). The response formatter detects this automatically.
- **Exception Handling**: Distinguishes `BinanceAPIException`, `BinanceOrderException`, `ValueError` (validation), and unexpected errors — each with a context-aware message.

---

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Keys
Create a `.env` file in the project root:
```env
BINANCE_API_KEY=your_64_char_testnet_api_key
BINANCE_API_SECRET=your_64_char_testnet_api_secret
```
> Keys must be from [https://testnet.binancefuture.com](https://testnet.binancefuture.com) — **not** mainnet keys.

---

## Usage

### Check connectivity
```bash
python3 cli.py ping
```

### Place a MARKET order
```bash
python3 cli.py place --symbol BTCUSDT --side BUY --order-type MARKET --quantity 0.001
```

### Place a LIMIT order
```bash
python3 cli.py place --symbol BTCUSDT --side SELL --order-type LIMIT --quantity 0.001 --price 120000
```

### Place a STOP_LIMIT order
```bash
python3 cli.py place --symbol BTCUSDT --side BUY --order-type STOP_LIMIT --quantity 0.002 --price 90000 --stop-price 89000
```

### Enable DEBUG logging
```bash
LOG_LEVEL=DEBUG python3 cli.py place --symbol BTCUSDT --side BUY --order-type MARKET --quantity 0.001
```

### Short-form flags
```bash
python3 cli.py place -s BTCUSDT -d BUY -t MARKET -q 0.001
```

### Help
```bash
python3 cli.py --help
python3 cli.py place --help
```

---

## Sample Output

```
╭────── Step 1: Request ───────╮
│ Order Request Summary        │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ Symbol:      BTCUSDT         │
│ Side:        BUY             │
│ Type:        MARKET          │
│ Quantity:    0.001           │
│                              │
╰──────────────────────────────╯
INFO: Binance Futures Client initialized. Using URL: https://demo-fapi.binance.com/fapi
INFO: Placing MARKET BUY order for 0.001 BTCUSDT...

Step 2: Order Response Details
 Field            Value
 orderId          13043394051
 symbol           BTCUSDT
 status           NEW
 side             BUY
 type             MARKET
 executedQty      0.0000
 avgPrice         0.00
 origQty          0.0010
 price            0.00

✔ SUCCESS: Order placed and processed.
```

---

## Test Suite

The project ships with a comprehensive test suite in `tests/test_bot.py` covering **28 scenarios**.

### Run with pytest
```bash
pip install pytest
python3 -m pytest tests/test_bot.py -v
```

### Run standalone (no pytest required)
```bash
python3 tests/test_bot.py
```

### Test Results (28/28 passed)

| # | Category | Test | Result |
|---|----------|------|--------|
| 1 | Connectivity | Ping Demo Testnet | ✅ PASS |
| 2 | Market Orders | MARKET BUY BTCUSDT 0.001 | ✅ PASS |
| 3 | Market Orders | MARKET SELL BTCUSDT 0.001 | ✅ PASS |
| 4 | Market Orders | MARKET BUY ETHUSDT 0.05 | ✅ PASS |
| 5 | Market Orders | MARKET SELL ETHUSDT 0.05 | ✅ PASS |
| 6 | Market Orders | MARKET BUY with extra --price flag (ignored) | ✅ PASS |
| 7 | Limit Orders | LIMIT BUY BTCUSDT @50000 | ✅ PASS |
| 8 | Limit Orders | LIMIT SELL BTCUSDT @120000 | ✅ PASS |
| 9 | Limit Orders | LIMIT BUY ETHUSDT @1500 | ✅ PASS |
| 10 | Limit Orders | LIMIT SELL ETHUSDT @5000 | ✅ PASS |
| 11 | Response Fields | Response contains `orderId` | ✅ PASS |
| 12 | Response Fields | Response contains `status` | ✅ PASS |
| 13 | Response Fields | Response contains `executedQty` | ✅ PASS |
| 14 | Response Fields | Response contains `avgPrice` | ✅ PASS |
| 15 | Response Fields | LIMIT response contains `price` | ✅ PASS |
| 16 | Validation | Invalid side: LONG → error | ✅ PASS |
| 17 | Validation | Invalid side: SHORT → error | ✅ PASS |
| 18 | Validation | Invalid type: STOP → error | ✅ PASS |
| 19 | Validation | Invalid type: FUTURES → error | ✅ PASS |
| 20 | Validation | Negative quantity (-1) → error | ✅ PASS |
| 21 | Validation | Zero quantity (0) → error | ✅ PASS |
| 22 | Validation | LIMIT missing --price → error | ✅ PASS |
| 23 | Validation | LIMIT --price=0 → error | ✅ PASS |
| 24 | Validation | LIMIT --price=-100 → error | ✅ PASS |
| 25 | Validation | Missing --symbol → usage error | ✅ PASS |
| 26 | Validation | Missing --side → usage error | ✅ PASS |
| 27 | Case Normalisation | lowercase `buy` + `market` | ✅ PASS |
| 28 | Case Normalisation | lowercase `sell` + `MARKET` | ✅ PASS |
| 29 | Case Normalisation | Mixed case `Buy` + `Limit` | ✅ PASS |

> **Note on minimum notional**: Binance enforces a minimum order value per symbol (`$20` for ETH, `$100` for BTC STOP orders). Tests use quantities that satisfy these exchange constraints. This is an exchange-side rule, not a bot limitation.

---

## Logging

All activity is written to `bot.log` in the project root:

```
2026-04-17 23:19:44 - trading_bot - INFO  - Binance Futures Client initialized. Using URL: https://demo-fapi.binance.com/fapi
2026-04-17 23:19:44 - trading_bot - INFO  - CLI: Placing MARKET BUY order for 0.001 BTCUSDT...
2026-04-17 23:19:44 - trading_bot - INFO  - Placing MARKET BUY order for 0.001 BTCUSDT...
2026-04-17 23:19:44 - trading_bot - INFO  - Order placed successfully. Response: {orderId: 13043379891, ...}
2026-04-17 23:19:25 - trading_bot - ERROR - Validation Error: Price is required for LIMIT orders.
```
