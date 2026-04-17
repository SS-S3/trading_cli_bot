from binance.exceptions import BinanceAPIException, BinanceOrderException
from bot.logging_config import logger
from bot.client import BinanceFuturesClient

class OrderManager:
    """Handles order placement and response formatting."""

    def __init__(self, client: BinanceFuturesClient):
        self.client = client

    def place_order(self, symbol: str, side: str, order_type: str, quantity: float, price: float = None, stop_price: float = None):
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
        elif order_type == "STOP_LIMIT":
            # Binance Futures API uses type=STOP for stop-limit orders
            params["type"] = "STOP"
            params["price"] = price
            params["stopPrice"] = stop_price
            params["timeInForce"] = "GTC"

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
        """Formats the API response for clear CLI output.
        
        Handles both standard order responses and algo/conditional order 
        responses (e.g., STOP_LIMIT returns algoId, algoStatus, etc.).
        """
        # Detect if this is an algo/conditional order response
        is_algo = "algoId" in response

        if is_algo:
            summary = {
                "orderId": response.get("algoId", "N/A"),
                "symbol": response.get("symbol", "N/A"),
                "status": response.get("algoStatus", "N/A"),
                "side": response.get("side", "N/A"),
                "type": response.get("orderType", response.get("algoType", "N/A")),
                "quantity": response.get("quantity", "0.0"),
                "price": response.get("price", "0.0"),
                "triggerPrice": response.get("triggerPrice", "N/A"),
            }
        else:
            summary = {
                "orderId": response.get("orderId", "N/A"),
                "symbol": response.get("symbol", "N/A"),
                "status": response.get("status", "N/A"),
                "side": response.get("side", "N/A"),
                "type": response.get("type", "N/A"),
                "executedQty": response.get("executedQty", "0.0"),
                "avgPrice": response.get("avgPrice", "0.0"),
                "origQty": response.get("origQty", "0.0"),
                "price": response.get("price", "0.0"),
            }
        return summary

