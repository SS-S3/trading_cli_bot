"""
test_bot.py — Comprehensive test suite for the Binance Futures Trading Bot.

Covers:
  - Connectivity (ping)
  - MARKET orders: BUY / SELL on BTCUSDT and ETHUSDT
  - LIMIT orders:  BUY / SELL on BTCUSDT and ETHUSDT
  - Response field presence: orderId, status, executedQty, avgPrice, price
  - Validation errors: invalid side, invalid type, bad quantity, missing/bad price, missing args
  - Case normalisation: lowercase and mixed-case CLI inputs

Run:
    python3 -m pytest tests/test_bot.py -v
or:
    python3 tests/test_bot.py
"""

import subprocess
import sys
import pytest

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def cli(*args, env_override=None):
    """Run the CLI and return (returncode, combined_output)."""
    import os
    env = os.environ.copy()
    env["LOG_LEVEL"] = "INFO"          # suppress DEBUG noise in tests
    if env_override:
        env.update(env_override)

    result = subprocess.run(
        [sys.executable, "cli.py"] + list(args),
        capture_output=True,
        text=True,
        env=env,
    )
    return result.returncode, result.stdout + result.stderr


# ===========================================================================
# 1. CONNECTIVITY
# ===========================================================================

class TestConnectivity:
    def test_ping_succeeds(self):
        """Bot should be able to reach the Binance Demo Testnet."""
        code, out = cli("ping")
        assert code == 0, f"ping failed:\n{out}"
        assert "Connection successful" in out


# ===========================================================================
# 2. MARKET ORDERS
# ===========================================================================

class TestMarketOrders:
    def test_market_buy_btcusdt(self):
        code, out = cli("place", "-s", "BTCUSDT", "-d", "BUY",
                        "--order-type", "MARKET", "-q", "0.001")
        assert code == 0, out
        assert "SUCCESS" in out

    def test_market_sell_btcusdt(self):
        code, out = cli("place", "-s", "BTCUSDT", "-d", "SELL",
                        "--order-type", "MARKET", "-q", "0.001")
        assert code == 0, out
        assert "SUCCESS" in out

    def test_market_buy_ethusdt(self):
        # ETH notional minimum is $20; 0.05 ETH comfortably exceeds it
        code, out = cli("place", "-s", "ETHUSDT", "-d", "BUY",
                        "--order-type", "MARKET", "-q", "0.05")
        assert code == 0, out
        assert "SUCCESS" in out

    def test_market_sell_ethusdt(self):
        code, out = cli("place", "-s", "ETHUSDT", "-d", "SELL",
                        "--order-type", "MARKET", "-q", "0.05")
        assert code == 0, out
        assert "SUCCESS" in out

    def test_market_order_extra_price_flag_is_ignored(self):
        """MARKET orders do not require a price; passing one should still succeed."""
        code, out = cli("place", "-s", "BTCUSDT", "-d", "BUY",
                        "--order-type", "MARKET", "-q", "0.001", "-p", "99999")
        assert code == 0, out
        assert "SUCCESS" in out


# ===========================================================================
# 3. LIMIT ORDERS
# ===========================================================================

class TestLimitOrders:
    def test_limit_buy_btcusdt(self):
        code, out = cli("place", "-s", "BTCUSDT", "-d", "BUY",
                        "--order-type", "LIMIT", "-q", "0.001", "-p", "50000")
        assert code == 0, out
        assert "SUCCESS" in out

    def test_limit_sell_btcusdt(self):
        code, out = cli("place", "-s", "BTCUSDT", "-d", "SELL",
                        "--order-type", "LIMIT", "-q", "0.001", "-p", "120000")
        assert code == 0, out
        assert "SUCCESS" in out

    def test_limit_buy_ethusdt(self):
        # 0.05 ETH × $1500 = $75 → above $20 minimum notional
        code, out = cli("place", "-s", "ETHUSDT", "-d", "BUY",
                        "--order-type", "LIMIT", "-q", "0.05", "-p", "1500")
        assert code == 0, out
        assert "SUCCESS" in out

    def test_limit_sell_ethusdt(self):
        code, out = cli("place", "-s", "ETHUSDT", "-d", "SELL",
                        "--order-type", "LIMIT", "-q", "0.05", "-p", "5000")
        assert code == 0, out
        assert "SUCCESS" in out


# ===========================================================================
# 4. RESPONSE FIELD VALIDATION
# ===========================================================================

class TestResponseFields:
    """Ensure all required fields appear in the printed response table."""

    def _place_market(self):
        return cli("place", "-s", "BTCUSDT", "-d", "BUY",
                   "--order-type", "MARKET", "-q", "0.001")

    def _place_limit(self):
        return cli("place", "-s", "BTCUSDT", "-d", "BUY",
                   "--order-type", "LIMIT", "-q", "0.001", "-p", "50000")

    def test_market_has_order_id(self):
        code, out = self._place_market()
        assert code == 0 and "orderId" in out

    def test_market_has_status(self):
        code, out = self._place_market()
        assert code == 0 and "status" in out

    def test_market_has_executed_qty(self):
        code, out = self._place_market()
        assert code == 0 and "executedQty" in out

    def test_market_has_avg_price(self):
        code, out = self._place_market()
        assert code == 0 and "avgPrice" in out

    def test_limit_has_price(self):
        code, out = self._place_limit()
        assert code == 0 and "price" in out


# ===========================================================================
# 5. VALIDATION ERRORS
# ===========================================================================

class TestValidationErrors:
    """Every bad input must exit with code 1 and a descriptive message."""

    # --- Side ---
    def test_invalid_side_long(self):
        code, out = cli("place", "-s", "BTCUSDT", "-d", "LONG",
                        "--order-type", "MARKET", "-q", "0.001")
        assert code == 1
        assert "Must be BUY or SELL" in out

    def test_invalid_side_short(self):
        code, out = cli("place", "-s", "BTCUSDT", "-d", "SHORT",
                        "--order-type", "MARKET", "-q", "0.001")
        assert code == 1
        assert "Must be BUY or SELL" in out

    # --- Order Type ---
    def test_invalid_type_stop(self):
        code, out = cli("place", "-s", "BTCUSDT", "-d", "BUY",
                        "--order-type", "STOP", "-q", "0.001")
        assert code == 1
        assert "Must be MARKET, LIMIT" in out

    def test_invalid_type_futures(self):
        code, out = cli("place", "-s", "BTCUSDT", "-d", "BUY",
                        "--order-type", "FUTURES", "-q", "0.001")
        assert code == 1
        assert "Must be MARKET, LIMIT" in out

    # --- Quantity ---
    def test_negative_quantity(self):
        code, out = cli("place", "-s", "BTCUSDT", "-d", "BUY",
                        "--order-type", "MARKET", "-q", "-1")
        assert code == 1
        assert "greater than 0" in out

    def test_zero_quantity(self):
        code, out = cli("place", "-s", "BTCUSDT", "-d", "BUY",
                        "--order-type", "MARKET", "-q", "0")
        assert code == 1
        assert "greater than 0" in out

    # --- Price (LIMIT) ---
    def test_limit_missing_price(self):
        code, out = cli("place", "-s", "BTCUSDT", "-d", "BUY",
                        "--order-type", "LIMIT", "-q", "0.001")
        assert code == 1
        assert "Price is required" in out

    def test_limit_zero_price(self):
        code, out = cli("place", "-s", "BTCUSDT", "-d", "BUY",
                        "--order-type", "LIMIT", "-q", "0.001", "-p", "0")
        assert code == 1
        assert "greater than 0" in out

    def test_limit_negative_price(self):
        code, out = cli("place", "-s", "BTCUSDT", "-d", "BUY",
                        "--order-type", "LIMIT", "-q", "0.001", "-p", "-100")
        assert code == 1
        assert "greater than 0" in out

    # --- Missing required args (Typer exits with code 2) ---
    def test_missing_symbol(self):
        code, _ = cli("place", "-d", "BUY", "--order-type", "MARKET", "-q", "0.001")
        assert code == 2, "Missing --symbol should cause a usage error (exit 2)"

    def test_missing_side(self):
        code, _ = cli("place", "-s", "BTCUSDT", "--order-type", "MARKET", "-q", "0.001")
        assert code == 2, "Missing --side should cause a usage error (exit 2)"


# ===========================================================================
# 6. CASE NORMALISATION
# ===========================================================================

class TestCaseNormalisation:
    """CLI inputs should be accepted in lowercase / mixed-case."""

    def test_lowercase_buy_market(self):
        code, out = cli("place", "-s", "btcusdt", "-d", "buy",
                        "--order-type", "market", "-q", "0.001")
        assert code == 0, out
        assert "SUCCESS" in out

    def test_lowercase_sell_market(self):
        code, out = cli("place", "-s", "BTCUSDT", "-d", "sell",
                        "--order-type", "MARKET", "-q", "0.001")
        assert code == 0, out
        assert "SUCCESS" in out

    def test_mixed_case_buy_limit(self):
        code, out = cli("place", "-s", "BTCUSDT", "-d", "Buy",
                        "--order-type", "Limit", "-q", "0.001", "-p", "50000")
        assert code == 0, out
        assert "SUCCESS" in out


# ===========================================================================
# Standalone runner (no pytest required)
# ===========================================================================

if __name__ == "__main__":
    import os, textwrap

    GREEN = "\033[92m"
    RED   = "\033[91m"
    RESET = "\033[0m"

    suites = [
        TestConnectivity,
        TestMarketOrders,
        TestLimitOrders,
        TestResponseFields,
        TestValidationErrors,
        TestCaseNormalisation,
    ]

    total, passed_count, failures = 0, 0, []

    print("\n" + "=" * 60)
    print("  BINANCE FUTURES TESTNET — FULL TEST SUITE")
    print("=" * 60)

    for suite_cls in suites:
        suite_name = suite_cls.__name__.replace("Test", "").replace("_", " ").upper()
        print(f"\n--- {suite_name} ---")
        instance = suite_cls()
        methods = [m for m in dir(instance) if m.startswith("test_")]
        for method_name in methods:
            total += 1
            label = method_name.replace("test_", "").replace("_", " ")
            try:
                getattr(instance, method_name)()
                print(f"  {GREEN}✔ PASS{RESET}  {label}")
                passed_count += 1
            except AssertionError as e:
                print(f"  {RED}✘ FAIL{RESET}  {label}")
                failures.append((label, str(e)))
            except Exception as e:
                print(f"  {RED}✘ ERROR{RESET} {label}: {e}")
                failures.append((label, str(e)))

    print("\n" + "=" * 60)
    print(f"  RESULT: {passed_count}/{total} tests passed")
    if not failures:
        print(f"  {GREEN}✔ All tests passed!{RESET}")
    else:
        print(f"  {RED}✘ {len(failures)} failed:{RESET}")
        for lbl, msg in failures:
            print(f"     • {lbl}")
            if msg:
                print(textwrap.indent(msg[:200], "       "))
    print("=" * 60 + "\n")
    sys.exit(0 if not failures else 1)
