import requests
import json

# Test registration endpoint
url = "http://localhost:5000/api/register"
payload = {
    "phone": "+237600000000",
    "name": "Test User",
    "community": "BAMEKA",
    "skill": "Farming"
}

print("Testing registration endpoint...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, json=payload)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"\nError: {e}")
    if hasattr(e, 'response'):
        print(f"Response text: {e.response.text}")
