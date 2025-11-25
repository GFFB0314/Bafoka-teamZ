# bafoka_client.py
"""
Bafoka API Client with automatic fallback to fake API
Seamlessly switches between real sandbox and fake API without user noticing
Updated to match REAL Bafoka API schema from Swagger docs
"""
import os
import requests
from typing import Optional, Dict
import logging

LOG = logging.getLogger("bafoka_client")
LOG.setLevel(logging.INFO)

# Configuration
BAFOKA_API_URL = os.getenv("BAFOKA_API_URL", "https://sandbox.bafoka.network")
FAKE_API_URL = os.getenv("FAKE_BAFOKA_URL", "http://localhost:9000")
BAFOKA_API_KEY = os.getenv("BAFOKA_API_KEY", "")
USE_FAKE_API = os.getenv("USE_FAKE_BAFOKA", "false").lower() == "true"

HEADERS = {
    "Content-Type": "application/json",
    # Add Authorization if the API requires a global API key
    # "Authorization": f"Bearer {BAFOKA_API_KEY}" 
}

# Track which API is being used
_current_api_url = None
_api_checked = False

def check_api_health() -> str:
    """
    Check which API is available and return its URL.
    Priority: Real API > Fake API
    """
    global _current_api_url, _api_checked
    
    if _api_checked and _current_api_url:
        return _current_api_url
    
    # If explicitly set to use fake API
    if USE_FAKE_API:
        LOG.info("Using FAKE Bafoka API (forced by env variable)")
        _current_api_url = FAKE_API_URL
        _api_checked = True
        return FAKE_API_URL
    
    # Try real API first
    try:
        # Try the Swagger docs endpoint as health check
        response = requests.get(f"{BAFOKA_API_URL}/v3/api-docs", timeout=3)
        if response.status_code == 200:
            LOG.info("Using REAL Bafoka Sandbox API")
            _current_api_url = BAFOKA_API_URL
            _api_checked = True
            return BAFOKA_API_URL
    except Exception as e:
        LOG.warning(f"Real Bafoka API not reachable: {e}")
    
    # Fallback to fake API
    try:
        response = requests.get(f"{FAKE_API_URL}/api/health", timeout=2)
        if response.status_code == 200:
            LOG.info("Using FAKE Bafoka API (real API unavailable)")
            _current_api_url = FAKE_API_URL
            _api_checked = True
            return FAKE_API_URL
    except Exception as e:
        LOG.warning(f"Fake Bafoka API not reachable: {e}")
    
    # Default to real API URL (will fail gracefully in actual calls)
    LOG.warning("No Bafoka API available, defaulting to real API URL")
    _current_api_url = BAFOKA_API_URL
    _api_checked = True
    return BAFOKA_API_URL

def get_api_url() -> str:
    """Get the current API URL (with caching)"""
    return check_api_health()

def create_wallet(phoneNumber: str, fullName: str, groupement_id: int, age: str = "25", sex: str = "M", blockchainAddress: str = "") -> Dict:
    """
    Creates a new account/wallet on Bafoka.
    Endpoint: POST /api/account-creation
    
    REAL API Schema (from Swagger):
    {
      "phoneNumber": "string",       # Phone number with country code
      "fullName": "string",           # User's full name
      "age": "string",                # Age as STRING (not integer!)
      "sex": "string",                # Gender: "M" or "F"
      "groupement_id": integer,       # Community ID (underscore, not camelCase!)
      "blockchainAddress": "string"   # Optional blockchain address
    }
    
    Parameters use EXACT API field names for clarity.
    """
    api_url = get_api_url()
    
    # Build payload with EXACT API field names
    payload = {
        "phoneNumber": phoneNumber,
        "fullName": fullName,
        "age": str(age),  # Ensure it's a string
        "sex": sex,
        "groupement_id": groupement_id,
        "blockchainAddress": blockchainAddress
    }
    
    try:
        url = f"{api_url}/api/account-creation"
        LOG.info(f"Creating wallet at {url} with payload {payload}")
        r = requests.post(url, json=payload, headers=HEADERS, timeout=15)
        r.raise_for_status()
        response = r.json()
        LOG.info(f"Wallet created successfully: {response}")
        return response
    except requests.exceptions.RequestException as e:
        LOG.error(f"Failed to create wallet: {e}")
        
        # Try fallback to fake API if using real API
        if api_url == BAFOKA_API_URL:
            LOG.info("Attempting fallback to fake API...")
            try:
                # Fake API now uses SAME payload format as real API
                # No need to change anything - use the same payload!
                url = f"{FAKE_API_URL}/api/account-creation"
                r = requests.post(url, json=payload, headers=HEADERS, timeout=10)
                r.raise_for_status()
                response = r.json()
                LOG.info(f"Wallet created via fake API: {response}")
                global _current_api_url
                _current_api_url = FAKE_API_URL
                return response
            except Exception as fallback_error:
                LOG.error(f"Fallback also failed: {fallback_error}")
        
        raise

def get_balance(phone: str) -> Dict:
    """
    Checks balance.
    Endpoint: POST /api/get-balance
    
    REAL API uses AccountCreationRequest schema (same as create_wallet!)
    This is unusual but matches the Swagger documentation.
    """
    api_url = get_api_url()
    
    # Real API requires full AccountCreationRequest schema
    payload = {
        "phoneNumber": phone,
        "fullName": "",  # Can be empty for balance check
        "age": "0",
        "sex": "",
        "groupement_id": 0,
        "blockchainAddress": ""
    }
    
    try:
        url = f"{api_url}/api/get-balance"
        LOG.info(f"Getting balance from {url} for {phone}")
        r = requests.post(url, json=payload, headers=HEADERS, timeout=15)
        r.raise_for_status()
        response = r.json()
        LOG.info(f"Balance retrieved: {response}")
        return response
    except requests.exceptions.RequestException as e:
        LOG.error(f"Failed to get balance: {e}")
        
        # Try fallback to fake API
        if api_url == BAFOKA_API_URL:
            LOG.info("Attempting fallback to fake API...")
            try:
                fake_payload = {"phoneNumber": phone}
                url = f"{FAKE_API_URL}/api/get-balance"
                r = requests.post(url, json=fake_payload, headers=HEADERS, timeout=10)
                r.raise_for_status()
                response = r.json()
                LOG.info(f"Balance retrieved via fake API: {response}")
                global _current_api_url
                _current_api_url = FAKE_API_URL
                return response
            except Exception as fallback_error:
                LOG.error(f"Fallback also failed: {fallback_error}")
        
        raise

def transfer(from_phone: str, to_phone: str, amount: int) -> Dict:
    """
    Initiates a transaction.
    
    ⚠️ WARNING: The real Bafoka API does NOT have a transfer/transaction endpoint
    in the Swagger documentation! This function will ALWAYS use the fake API.
    
    The real API may have this endpoint but it's not documented.
    """
    LOG.warning("Transfer endpoint not found in real Bafoka API documentation!")
    LOG.info("Using fake API for transfers...")
    
    payload = {
        "senderPhoneNumber": from_phone,
        "receiverPhoneNumber": to_phone,
        "amount": amount
    }
    
    try:
        url = f"{FAKE_API_URL}/api/initiate-transaction"
        LOG.info(f"Initiating transfer at {url} (fake API)")
        r = requests.post(url, json=payload, headers=HEADERS, timeout=15)
        r.raise_for_status()
        response = r.json()
        LOG.info(f"Transfer completed via fake API: {response}")
        return response
    except requests.exceptions.RequestException as e:
        LOG.error(f"Failed to transfer: {e}")
        raise RuntimeError(
            "Transfer failed. The real Bafoka API does not have a documented transfer endpoint. "
            "Make sure the fake Bafoka API is running on port 9000."
        )

# Deprecated/Internal helpers
def credit_wallet(wallet_id: str, amount: int, reason: str = "signup") -> Dict:
    """
    Not available in public API, assuming initial credit happens on creation or manually
    """
    LOG.warning("credit_wallet called but not supported by real API")
    return {"status": "skipped"}

def get_current_api_info() -> Dict:
    """
    Get information about which API is currently being used.
    Useful for debugging and monitoring.
    """
    api_url = get_api_url()
    is_fake = api_url == FAKE_API_URL
    
    return {
        "api_url": api_url,
        "is_fake_api": is_fake,
        "is_real_api": not is_fake,
        "api_type": "FAKE" if is_fake else "REAL"
    }


