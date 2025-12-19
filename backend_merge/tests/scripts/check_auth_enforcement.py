import requests
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

def test_no_auth():
    url = "https://sandbox.bafoka.network/api/account-creation"
    print(f"Testing {url} WITHOUT Authorization header...")

    payload = {
        "phoneNumber": "237699999999",
        "fullName": "Test No Auth",
        "age": 25,
        "groupementId": "BAMEKA"
    }
    
    # No headers, specifically no Authorization
    headers = {
        "Content-Type": "application/json"
    }

    try:
        r = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"Status Code: {r.status_code}")
        print(f"Response: {r.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_no_auth()
