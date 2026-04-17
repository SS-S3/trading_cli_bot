from binance.exceptions import BinanceAPIException, BinanceOrderException
from bot.logging_config import logger
from bot.client import BinanceFuturesClient

class OrderManager:
    """Handles order placement and response formatting."""

    def __init__(self, client: BinanceFuturesClient):
        self.client = client

    def place_order(self, symbol: str, side: str, order_type: str, quantity: float, price: float = None):
        """Places an order on Binance Futures Testnet."""
        
        params = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity
        }

        if order_type == "LIMIT":
            params["price"] = price
            params["timeInForce"] = "GTC"  # Good Till Cancelled

        logger.info(f"Placing {order_type} {side} order for {quantity} {symbol}...")
        logger.debug(f"Order Params: {params}")

        try:
            response = self.client.client.futures_create_order(**params)
            logger.info(f"Order placed successfully. Response: {response}")
            return response
        except BinanceAPIException as e:
            logger.error(f"Binance API Error: Code={e.code}, Message={e.message}, Status={e.status_code}")
            logger.debug(f"Request Params: {params}")
            raise
        except BinanceOrderException as e:
            logger.error(f"Binance Order Error: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in OrderManager: {str(e)}")
            raise

    def format_response(self, response: dict):
        """Formats the API response for clear CLI output."""
        summary = {
            "orderId": response.get("orderId"),
            "status": response.get("status"),
            "executedQty": response.get("executedQty"),
            "avgPrice": response.get("avgPrice", "N/A"),
            "symbol": response.get("symbol"),
            "side": response.get("side"),
            "type": response.get("type")
        }
        return summary
