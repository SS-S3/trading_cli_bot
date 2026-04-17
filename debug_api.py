import os
import requests
import time
import hmac
import hashlib
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("BINANCE_API_KEY").strip()
api_secret = os.getenv("BINANCE_API_SECRET").strip()

def test_ping(base_url, path):
    full_url = f"{base_url}{path}"
    print(f"\nTesting: {full_url}")
    try:
        response = requests.get(full_url)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

test_ping("https://demo-fapi.binance.com", "/fapi/v1/ping")
test_ping("https://demo-fapi.binance.com", "/v1/ping")
