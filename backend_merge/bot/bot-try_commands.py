import requests
import time

BASE_URL = "http://localhost:5000/webhook"
PHONE_NUMBER = "whatsapp:+237698594077" # Mock number for Gbetnkom

def send_command(command):
    print(f"Sending command: {command}")
    try:
        response = requests.post(
            BASE_URL,
            data={"From": PHONE_NUMBER, "Body": command}
        )
        print(f"Response Status: {response.status_code}")
        print(f"Response Body:\n{response.text}")
        print("-" * 40)
    except Exception as e:
        print(f"Error sending command: {e}")

def main():
    # 1. Register
    send_command("/register BAMEKA | Gbetnkom | Developer")
    time.sleep(1)

    # 2. Check Profile
    send_command("/me")
    time.sleep(1)

    # 3. Create Offer
    send_command("/offer Building a website | Web Dev | 500")
    time.sleep(1)

    # 4. Search
    send_command("/search Web")
    time.sleep(1)

    # 5. Check Balance
    send_command("/balance")

if __name__ == "__main__":
    main()
