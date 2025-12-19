import os
import sys
import logging
from dotenv import load_dotenv

load_dotenv()

# Add current dir to path so we can import bot modules
sys.path.insert(0, os.path.abspath("."))

from bot import bafoka_client

# Setup logging
logging.basicConfig(level=logging.INFO)

def test_connectivity():
    print("Testing Bafoka API Connectivity...")
    print(f"URL: {bafoka_client.BAFOKA_API_URL}")
    print(f"Key: {bafoka_client.BAFOKA_API_KEY}")

    # Try to get balance for a random number (should fail with 404 or 400 if auth works, or 401/403 if auth fails)
    # or maybe just create a wallet?
    
    import uuid
    random_phone = f"237{uuid.uuid4().int % 1000000000}"
    print(f"Attempting to create wallet for {random_phone}...")

    try:
        res = bafoka_client.create_wallet(random_phone, "Test User")
        print("SUCCESS: Wallet created!")
        print(res)
    except Exception as e:
        print(f"FAILURE: {e}")
        # If it's a request exception, print status code
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status Code: {e.response.status_code}")
            print(f"Response: {e.response.text}")

if __name__ == "__main__":
    test_connectivity()
