# bafoka_client.py
"""
Lightweight client for Bafoka API.

Expected endpoints (fake local server for now):
- POST /wallets                -> create wallet, returns {"wallet_id":"..."}
- POST /wallets/<wallet_id>/credit -> credit wallet
- POST /transactions           -> create a transfer, returns {"tx_id":"...", "status":"pending"}
- GET  /wallets/<wallet_id>/balance -> {"balance": 1000}

Set env: BAFOKA_API_URL, BAFOKA_API_KEY
"""
# bafoka_client.py
import os
import requests
from typing import Optional, Dict

BAFOKA_API_URL = os.getenv("BAFOKA_API_URL", "http://localhost:9000")
BAFOKA_API_KEY = os.getenv("BAFOKA_API_KEY", "")

HEADERS = {"Authorization": f"Bearer {BAFOKA_API_KEY}", "Content-Type": "application/json"}

def create_wallet(display_name: str, metadata: Optional[Dict] = None) -> Dict:
    payload = {"display_name": display_name, "metadata": metadata or {}}
    r = requests.post(f"{BAFOKA_API_URL}/wallets", json=payload, headers=HEADERS, timeout=10)
    r.raise_for_status()
    return r.json()

def credit_wallet(wallet_id: str, amount: int, reason: str = "signup") -> Dict:
    payload = {"amount": amount, "reason": reason}
    r = requests.post(f"{BAFOKA_API_URL}/wallets/{wallet_id}/credit", json=payload, headers=HEADERS, timeout=10)
    r.raise_for_status()
    return r.json()

def transfer(from_wallet_id: str, to_wallet_id: str, amount: int, idempotency_key: str = None) -> Dict:
    payload = {"from_wallet": from_wallet_id, "to_wallet": to_wallet_id, "amount": amount}
    headers = HEADERS.copy()
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key
    r = requests.post(f"{BAFOKA_API_URL}/transactions", json=payload, headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()

def get_balance(wallet_id: str) -> Dict:
    r = requests.get(f"{BAFOKA_API_URL}/wallets/{wallet_id}/balance", headers=HEADERS, timeout=10)
    r.raise_for_status()
    return r.json()
