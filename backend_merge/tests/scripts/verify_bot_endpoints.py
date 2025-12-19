# tests/scripts/verify_bot_endpoints.py
import requests
import logging

logging.basicConfig(level=logging.INFO)

BASE_URL = "http://localhost:5000/api/v1/botpress"

def test_text_command():
    print("Testing Text Command Endpoint...")
    url = f"{BASE_URL}/command"
    payload = {
        "phone": "237699999999",
        "text": "/balance"
    }
    try:
        r = requests.post(url, json=payload, timeout=5)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.json()}")
        if r.status_code == 200:
            print("SUCCESS: Text command processed.")
        else:
            print("FAILURE: Text command returned non-200.")
    except Exception as e:
        print(f"FAILURE: Could not connect to bot: {e}")

def test_voice_endpoint_sanity():
    print("\nTesting Voice Endpoint Sanity (No Audio)...")
    url = f"{BASE_URL}/voice"
    payload = {
        "phone": "237699999999"
        # Missing audio_url should trigger error
    }
    try:
        r = requests.post(url, json=payload, timeout=5)
        print(f"Status: {r.status_code}")
        # Expecting 400 because audio_url is missing
        if r.status_code == 400:
            print("SUCCESS: Voice endpoint is reachable and validating input.")
        else:
            print(f"WARNING: Unexpected status code {r.status_code}.")
    except Exception as e:
        print(f"FAILURE: Could not connect to bot: {e}")

if __name__ == "__main__":
    test_text_command()
    test_voice_endpoint_sanity()
