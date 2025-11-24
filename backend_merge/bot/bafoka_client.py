# bafoka_client.py
import os
import requests
from typing import Optional, Dict
import logging

LOG = logging.getLogger("bafoka_client")

# Use the sandbox URL by default
BAFOKA_API_URL = os.getenv("BAFOKA_API_URL", "https://sandbox.bafoka.network")
# API Key might be needed if there's a global auth, otherwise specific endpoints might need tokens
BAFOKA_API_KEY = os.getenv("BAFOKA_API_KEY", "")

HEADERS = {
    "Content-Type": "application/json",
    # Add Authorization if the API requires a global API key
    # "Authorization": f"Bearer {BAFOKA_API_KEY}" 
}

def create_wallet(phone: str, name: str, community_id: str = "BAMEKA", age: int = 25) -> Dict:
    """
    Creates a new account/wallet on Bafoka.
    Endpoint: POST /api/account-creation
    """
    payload = {
        "phoneNumber": phone,
        "fullName": name,
        "age": age,
        "groupementId": community_id
    }
    try:
        url = f"{BAFOKA_API_URL}/api/account-creation"
        LOG.info(f"Creating wallet at {url} with payload {payload}")
        r = requests.post(url, json=payload, headers=HEADERS, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        LOG.error(f"Failed to create wallet: {e}")
        # Return a mock success for hackathon continuity if API fails/is strict
        # return {"id": "mock_id", "phoneNumber": phone} 
        raise

def get_balance(phone: str) -> Dict:
    """
    Checks balance.
    Endpoint: POST /api/get-balance
    """
    payload = {"phoneNumber": phone}
    try:
        url = f"{BAFOKA_API_URL}/api/get-balance"
        r = requests.post(url, json=payload, headers=HEADERS, timeout=15)
        r.raise_for_status()
        # Expected response: {"balance": 1000, "currency": "MUNKAP", ...}
        return r.json()
    except Exception as e:
        LOG.error(f"Failed to get balance: {e}")
        raise

def transfer(from_phone: str, to_phone: str, amount: int) -> Dict:
    """
    Initiates a transaction.
    Endpoint: POST /api/initiate-transaction
    """
    payload = {
        "senderPhoneNumber": from_phone,
        "receiverPhoneNumber": to_phone,
        "amount": amount
    }
    try:
        url = f"{BAFOKA_API_URL}/api/initiate-transaction"
        LOG.info(f"Initiating transfer at {url}")
        r = requests.post(url, json=payload, headers=HEADERS, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        LOG.error(f"Failed to transfer: {e}")
        raise

# Deprecated/Internal helpers
def credit_wallet(wallet_id: str, amount: int, reason: str = "signup") -> Dict:
    # Not available in public API, assuming initial credit happens on creation or manually
    LOG.warning("credit_wallet called but not supported by real API")
    return {"status": "skipped"}
