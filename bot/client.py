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
            
            # If the user specifically wants the Demo endpoint (different from standard Testnet)
            # we override it here, but testnet=True is still crucial for internal library behavior.
            if self.BASE_URL:
                self.client.FUTURES_URL = f"{self.BASE_URL.rstrip('/')}/fapi"
            
            logger.info(f"Successfully initialized Binance Futures Demo client using {self.client.FUTURES_URL}")
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
