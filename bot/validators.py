import re
from bot.logging_config import logger

def validate_symbol(symbol: str) -> str:
    """Validates the symbol format (e.g., BTCUSDT)."""
    if not re.match(r"^[A-Z0-9]{3,12}$", symbol.upper()):
        raise ValueError(f"Invalid symbol format: {symbol}")
    return symbol.upper()

def validate_side(side: str) -> str:
    """Validates the order side."""
    side = side.upper()
    if side not in ["BUY", "SELL"]:
        raise ValueError(f"Invalid side: {side}. Must be BUY or SELL.")
    return side

def validate_order_type(order_type: str) -> str:
    """Validates the order type."""
    order_type = order_type.upper()
    if order_type not in ["MARKET", "LIMIT"]:
        raise ValueError(f"Invalid order type: {order_type}. Must be MARKET or LIMIT.")
    return order_type

def validate_quantity(quantity: float) -> float:
    """Validates the quantity is positive."""
    if quantity <= 0:
        raise ValueError(f"Quantity must be greater than 0: {quantity}")
    return float(quantity)

def validate_price(price: float, order_type: str) -> float:
    """Validates the price if order type is LIMIT."""
    if order_type.upper() == "LIMIT":
        if price is None or price <= 0:
            raise ValueError(f"Price is required and must be greater than 0 for LIMIT orders.")
    return float(price) if price is not None else None
