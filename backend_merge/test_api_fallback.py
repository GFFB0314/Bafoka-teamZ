# test_api_fallback.py
"""
Test Bafoka API Fallback Mechanism
Demonstrates that real API is tried first, with automatic fallback to fake API
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def print_section(title):
    print("\n" + "="*70)
    print(title)
    print("="*70)

def test_register_user(phone, name, skill, community):
    """Test user registration via app.py REST endpoint"""
    print(f"\nRegistering user: {name} ({phone})")
    print(f"  Community: {community}, Skill: {skill}")
    
    response = requests.post(f"{BASE_URL}/api/register", json={
        "phone": phone,
        "name": name,
        "skill": skill,
        "community": community
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"  [SUCCESS] User registered")
        print(f"  - Wallet ID: {data.get('bafoka_wallet_id', 'N/A')}")
        print(f"  - Balance: {data.get('bafoka_balance')} {community}")
        print(f"  - Created: {data.get('created')}")
        return data
    else:
        print(f"  [FAILED] Status: {response.status_code}")
        print(f"  Response: {response.text}")
        return None

def test_check_balance(phone):
    """Test balance check via app.py REST endpoint"""
    print(f"\nChecking balance for: {phone}")
    
    response = requests.get(f"{BASE_URL}/api/balance", params={"phone": phone})
    
    if response.status_code == 200:
        data = response.json()
        print(f"  [SUCCESS] Balance retrieved")
        print(f"  - Local: {data.get('local_balance')}")
        print(f"  - External: {data.get('external_balance', 'N/A')}")
        print(f"  - Currency: {data.get('currency_name')}")
        return data
    else:
        print(f"  [FAILED] Status: {response.status_code}")
        print(f"  Response: {response.text}")
        return None

def test_transfer(from_phone, to_phone, amount):
    """Test transfer via app.py REST endpoint"""
    print(f"\nTransferring {amount} from {from_phone} to {to_phone}")
    
    response = requests.post(f"{BASE_URL}/api/transfer", json={
        "from_phone": from_phone,
        "to_phone": to_phone,
        "amount": amount
    })
    
    if response.status_code == 200:
        data = response.json()
        if data.get("ok"):
            print(f"  [SUCCESS] Transfer completed")
            print(f"  - TX ID: {data.get('tx_id')}")
            print(f"  - Status: {data.get('status')}")
            return data
        else:
            print(f"  [FAILED] {data.get('error')}")
            return None
    else:
        print(f"  [FAILED] Status: {response.status_code}")
        try:
            print(f"  Error: {response.json().get('error')}")
        except:
            print(f"  Response: {response.text}")
        return None

def main():
    print("\n" + "="*70)
    print("BAFOKA API FALLBACK MECHANISM TEST")
    print("="*70)
    print("\nThis test demonstrates:")
    print("1. Real API is tried FIRST for account creation and balance")
    print("2. Fake API is used as FALLBACK when real API fails")
    print("3. Transfers ALWAYS use fake API (not available in real API)")
    print("\nServers required:")
    print("  - Flask app.py: http://localhost:5000")
    print("  - Fake Bafoka: http://localhost:9000")
    
    # Test with NEW users (not Alice/Bob from previous tests)
    print_section("TEST 1: Register Charlie (New User)")
    charlie = test_register_user(
        phone="+237600000003",
        name="Charlie Test",
        skill="Carpentry",
        community="BAMEKA"
    )
    
    if charlie:
        print("\n  API Used: Check Flask logs to see if REAL or FAKE API was used")
    
    print_section("TEST 2: Register Diana (New User)")
    diana = test_register_user(
        phone="+237600000004",
        name="Diana Test",
        skill="Teaching",
        community="BAMEKA"
    )
    
    if diana:
        print("\n  API Used: Check Flask logs to see if REAL or FAKE API was used")
    
    print_section("TEST 3: Check Charlie's Balance")
    charlie_balance = test_check_balance("+237600000003")
    
    if charlie_balance:
        print("\n  API Used: Check Flask logs to see if REAL or FAKE API was used")
    
    print_section("TEST 4: Check Diana's Balance")
    diana_balance = test_check_balance("+237600000004")
    
    if diana_balance:
        print("\n  API Used: Check Flask logs to see if REAL or FAKE API was used")
    
    print_section("TEST 5: Transfer (Will use FAKE API)")
    print("\nNOTE: Real API doesn't have /api/initiate-transaction endpoint")
    print("      So transfers ALWAYS use fake API")
    print("\nSince accounts start with 0 balance, transfer will fail.")
    print("This is CORRECT behavior (matching real API).")
    
    transfer_result = test_transfer(
        from_phone="+237600000003",
        to_phone="+237600000004",
        amount=50
    )
    
    print_section("TEST COMPLETE")
    print("\nFallback Mechanism Verification:")
    print("1. Check Flask app logs (terminal running app.py)")
    print("2. Look for messages like:")
    print("   - 'Using REAL Bafoka API'")
    print("   - 'Real API failed, using FAKE API'")
    print("   - 'FAKE Bafoka API (port 9000)'")
    print("\n3. For account creation, you should see:")
    print("   - FIRST attempt: Real API (https://sandbox.bafoka.network)")
    print("   - If real fails: Automatic fallback to Fake API (localhost:9000)")
    print("\n4. For transfers, you should see:")
    print("   - Direct use of Fake API (real API doesn't have endpoint)")
    print("="*70)
    print("\nTo see real → fake fallback in action:")
    print("1. Stop fake_bafoka.py (Ctrl+C)")
    print("2. Run this test again")
    print("3. You'll see real API attempts (may get 400 for existing users)")
    print("4. Then restart fake_bafoka.py and test will use fake API")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
