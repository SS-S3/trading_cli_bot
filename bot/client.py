import os
from binance.client import Client
from binance.exceptions import BinanceAPIException
from bot.logging_config import logger
from dotenv import load_dotenv

load_dotenv()

class BinanceFuturesClient:
    """Wrapper for Binance Futures Testnet client."""
    
    BASE_URL = "https://demo-fapi.binance.com/"

    def __init__(self, api_key: str = None, api_secret: str = None):
        self.api_key = (api_key or os.getenv("BINANCE_API_KEY", "")).strip()
        self.api_secret = (api_secret or os.getenv("BINANCE_API_SECRET", "")).strip()
        
        if not self.api_key or not self.api_secret:
            logger.error("API Key or Secret missing. Please set BINANCE_API_KEY and BINANCE_API_SECRET in .env file.")
            raise ValueError("API Key or Secret missing.")

        # Diagnostic logging (masked)
        masked_key = f"{self.api_key[:6]}...{self.api_key[-4:]}" if len(self.api_key) > 10 else "***"
        logger.debug(f"Initializing client with API Key: {masked_key} (length: {len(self.api_key)})")
        logger.debug(f"API Secret length: {len(self.api_secret)}")

        try:
            # Initialize the client with testnet=True to ensure correct internal URL and signing configuration
            self.client = Client(self.api_key, self.api_secret, testnet=True)
            
            # Use the Demo Testnet URL (this is the one for the Binance Futures Testnet UI)
            # Standard testnet URL in python-binance is often different from the Demo Trading one.
            self.client.FUTURES_URL = os.getenv("BINANCE_FUTURES_URL", "https://demo-fapi.binance.com/fapi")
            
            logger.info(f"Binance Futures Client initialized. Using URL: {self.client.FUTURES_URL}")
        except Exception as e:
            logger.error(f"Failed to initialize Binance client: {str(e)}")
            raise

    def ping(self):
        """Check connection to the testnet."""
        try:
            self.client.futures_ping()
            return True
        except Exception as e:
            logger.error(f"Ping failed: {str(e)}")
            return False
