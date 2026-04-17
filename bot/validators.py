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
    if order_type not in ["MARKET", "LIMIT", "STOP_LIMIT"]:
        raise ValueError(f"Invalid order type: {order_type}. Must be MARKET, LIMIT, or STOP_LIMIT.")
    return order_type

def validate_quantity(quantity: float) -> float:
    """Validates the quantity is positive and a valid number."""
    try:
        qty = float(quantity)
        if qty <= 0:
            raise ValueError(f"Quantity must be greater than 0. Got: {qty}")
        return qty
    except (TypeError, ValueError) as e:
        if isinstance(e, ValueError) and "greater than 0" in str(e):
            raise e
        raise ValueError(f"Invalid quantity: {quantity}. Must be a positive number.")

def validate_price(price: float, order_type: str) -> float:
    """Validates the price if order type is LIMIT or STOP_LIMIT."""
    if order_type.upper() in ["LIMIT", "STOP_LIMIT"]:
        if price is None:
            raise ValueError(f"Price is required for {order_type} orders.")
        try:
            p = float(price)
            if p <= 0:
                raise ValueError(f"Price must be greater than 0. Got: {p}")
            return p
        except (TypeError, ValueError) as e:
            if isinstance(e, ValueError) and "greater than 0" in str(e):
                raise e
            raise ValueError(f"Invalid price: {price}. Must be a positive number for {order_type} orders.")
    return None

def validate_stop_price(stop_price: float, order_type: str) -> float:
    """Validates the stop price if order type is STOP_LIMIT."""
    if order_type.upper() == "STOP_LIMIT":
        if stop_price is None:
            raise ValueError("Stop Price is required for STOP_LIMIT orders.")
        try:
            sp = float(stop_price)
            if sp <= 0:
                raise ValueError(f"Stop Price must be greater than 0. Got: {sp}")
            return sp
        except (TypeError, ValueError) as e:
            if isinstance(e, ValueError) and "greater than 0" in str(e):
                raise e
            raise ValueError(f"Invalid stop price: {stop_price}. Must be a positive number for STOP_LIMIT orders.")
    return None
