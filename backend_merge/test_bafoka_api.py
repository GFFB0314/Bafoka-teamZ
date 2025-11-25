#!/usr/bin/env python
"""
Test Bafoka API Integration with Fresh Users
Tests real API first, falls back to fake API if needed
"""
import sys
import os
import random

# Add bot directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bot'))

from bot import bafoka_client
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def print_section(title):
    print(f"\n{'='*60}")
    print(title)
    print('='*60)

def main():
    print("="*60)
    print("BAFOKA API INTEGRATION TEST - FRESH USERS")
    print("="*60)
    
    # Check which API is being used
    api_info = bafoka_client.get_current_api_info()
    print(f"\nAPI Status:")
    print(f"   URL: {api_info['api_url']}")
    print(f"   Type: {api_info['api_type']}")
    print(f"   Is Fake: {api_info['is_fake_api']}")
    print(f"   Is Real: {api_info['is_real_api']}")
    
    # Generate FRESH phone numbers to avoid conflicts with existing accounts
    emma_phone = f"+237{random.randint(650000000, 659999999)}"
    frank_phone = f"+237{random.randint(650000000, 659999999)}"
    
    print(f"\nGenerated fresh phone numbers:")
    print(f"   Emma: {emma_phone}")
    print(f"   Frank: {frank_phone}")
    
    print_section(f"TEST 1: Create Account for Emma ({emma_phone})")
    try:
        emma_wallet = bafoka_client.create_wallet(
            phoneNumber=emma_phone,
            fullName="Emma Kamga",
            groupement_id=3,  # BAMEKA
            age="28",
            sex="F",
            blockchainAddress=""
        )
        print(f"SUCCESS: {emma_wallet}")
    except Exception as e:
        print(f"FAILED: {e}")
    
    print_section(f"TEST 2: Create Account for Frank ({frank_phone})")
    try:
        frank_wallet = bafoka_client.create_wallet(
            phoneNumber=frank_phone,
            fullName="Frank Nkeng",
            groupement_id=3,  # BAMEKA
            age="32",
            sex="M",
            blockchainAddress=""
        )
        print(f"SUCCESS: {frank_wallet}")
    except Exception as e:
        print(f"FAILED: {e}")
    
    print_section(f"TEST 3: Check Emma's Balance")
    try:
        emma_balance = bafoka_client.get_balance(phone=emma_phone)
        print(f"SUCCESS: {emma_balance}")
    except Exception as e:
        print(f"FAILED: {e}")
    
    print_section(f"TEST 4: Check Frank's Balance")
    try:
        frank_balance = bafoka_client.get_balance(phone=frank_phone)
        print(f"SUCCESS: {frank_balance}")
    except Exception as e:
        print(f"FAILED: {e}")
    
    print_section(f"TEST 5: Transfer (will fail due to 0 balance)")
    print("NOTE: Accounts start with 0 balance (matching real API)")
    print("      This test will fail with 'Insufficient balance' - this is CORRECT")
    try:
        transfer = bafoka_client.transfer(
            from_phone=emma_phone,
            to_phone=frank_phone,
            amount=50
        )
        print(f"SUCCESS: {transfer}")
    except Exception as e:
        print(f"EXPECTED FAILURE: {e}")
    
    print_section("TEST COMPLETE")
    print("\nReview the logs above to see which API was used:")
    print("  - Look for 'Using REAL Bafoka Sandbox API'")
    print("  - Or 'Attempting fallback to fake API...'")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
