# bafoka_client.py
import os
import requests
from typing import Optional, Dict
import logging

LOG = logging.getLogger("bafoka_client")

# Use the sandbox URL by default
BAFOKA_API_URL = os.getenv("BAFOKA_API_URL", "http://localhost:9000")
# API Key is REQUIRED for the real API
BAFOKA_API_KEY = os.getenv("BAFOKA_API_KEY", "")

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {BAFOKA_API_KEY}" 
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
        LOG.info(f"Creating wallet at {url} for {phone}")
        # Ensure headers include auth
        r = requests.post(url, json=payload, headers=HEADERS, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        LOG.error(f"Failed to create wallet: {e}")
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
        LOG.info(f"Initiating transfer at {url} from {from_phone} to {to_phone}")
        r = requests.post(url, json=payload, headers=HEADERS, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        LOG.error(f"Failed to transfer: {e}")
        raise
