import requests
import sys

BASE_URL = "http://localhost:5000"

def test_voice_endpoint_availability():
    print("Testing /api/voice/process availability...")
    try:
        # Send empty request, expect 400 error (audio_url required)
        response = requests.post(f"{BASE_URL}/api/voice/process", json={})
        
        if response.status_code == 400:
            print("[OK] Endpoint is reachable and correctly validates input (returned 400 as expected)")
            print(f"   Response: {response.json()}")
            return True
        elif response.status_code == 404:
            print("[FAIL] Endpoint not found (404)")
            return False
        else:
            print(f"[FAIL] Unexpected status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Failed to connect: {e}")
        return False

if __name__ == "__main__":
    if test_voice_endpoint_availability():
        sys.exit(0)
    else:
        sys.exit(1)
