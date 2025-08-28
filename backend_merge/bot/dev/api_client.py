# dev/api_client.py
# Real Bafoka API client for dev backend
import os
import requests
from typing import Dict, Any, Optional

BAFOKA_BASE_URL = os.getenv("BAFOKA_BASE_URL", "https://sandbox.bafoka.network")
BAFOKA_API_PREFIX = os.getenv("BAFOKA_API_PREFIX", "/api")
API_BASE = BAFOKA_BASE_URL.rstrip("/") + BAFOKA_API_PREFIX

DEFAULT_TIMEOUT = float(os.getenv("BAFOKA_TIMEOUT", "15"))


def _headers(token: Optional[str] = None) -> Dict[str, str]:
    h = {"Content-Type": "application/json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def register_user(payload: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{API_BASE}/register"
    r = requests.post(url, json=payload, headers=_headers(), timeout=DEFAULT_TIMEOUT)
    r.raise_for_status()
    return r.json()


def get_user_balance(token: str) -> Dict[str, Any]:
    url = f"{API_BASE}/user/balance"
    r = requests.get(url, headers=_headers(token), timeout=DEFAULT_TIMEOUT)
    r.raise_for_status()
    return r.json()


def list_products(token: Optional[str] = None) -> Any:
    url = f"{API_BASE}/products"
    r = requests.get(url, headers=_headers(token), timeout=DEFAULT_TIMEOUT)
    r.raise_for_status()
    return r.json()


def create_product(token: str, name: str, description: str, price: float) -> Dict[str, Any]:
    url = f"{API_BASE}/products"
    payload = {"name": name, "description": description, "price": price}
    r = requests.post(url, json=payload, headers=_headers(token), timeout=DEFAULT_TIMEOUT)
    r.raise_for_status()
    return r.json()


def purchase(token: str, seller_id: int, amount: int, description: Optional[str] = None) -> Dict[str, Any]:
    url = f"{API_BASE}/purchase"
    payload = {"seller_id": seller_id, "amount": int(amount)}
    if description:
        payload["description"] = description
    r = requests.post(url, json=payload, headers=_headers(token), timeout=DEFAULT_TIMEOUT)
    r.raise_for_status()
    return r.json()


def list_transactions(token: str) -> Any:
    url = f"{API_BASE}/transaction"
    r = requests.get(url, headers=_headers(token), timeout=DEFAULT_TIMEOUT)
    r.raise_for_status()
    return r.json()

