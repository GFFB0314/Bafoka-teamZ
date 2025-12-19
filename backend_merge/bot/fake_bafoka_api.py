# bot/fake_bafoka_api.py
from flask import Flask, request, jsonify
import logging
import uuid

app = Flask(__name__)

# In-memory storage
WALLETS = {}  # phone -> {balance, name, community, currency}
TRANSACTIONS = []

LOG = logging.getLogger("fake_bafoka")
logging.basicConfig(level=logging.INFO)

COMMUNITY_CURRENCIES = {
    "BAMEKA": "MUNKAP",
    "BATOUFAM": "MBIP TSWEFAP",
    "FONDJOMEKWET": "MBAM"
}

@app.route("/api/account-creation", methods=["POST"])
def create_account():
    data = request.json or {}
    phone = data.get("phoneNumber")
    name = data.get("fullName")
    comm = data.get("groupementId")
    
    if not phone or not comm:
        return jsonify({"code": 400, "message": "Missing fields", "success": False}), 400
        
    if phone in WALLETS:
        return jsonify({"code": 200, "message": "Account already exists", "success": True, "data": {"id": phone}})
    
    currency = COMMUNITY_CURRENCIES.get(comm, "BAFOKA_COIN")
    
    WALLETS[phone] = {
        "balance": 1000, # Initial air-drop for testing
        "name": name,
        "community": comm,
        "currency": currency
    }
    
    LOG.info(f"Created wallet for {phone} in {comm} with 1000 {currency}")
    
    return jsonify({
        "code": 201, 
        "message": "Account created", 
        "success": True, 
        "data": {"id": phone, "phoneNumber": phone}
    })

@app.route("/api/get-balance", methods=["POST"])
def get_balance():
    data = request.json or {}
    phone = data.get("phoneNumber")
    
    if phone not in WALLETS:
        return jsonify({"code": 404, "message": "Wallet not found", "success": False}), 404
        
    wallet = WALLETS[phone]
    return jsonify({
        "balance": wallet["balance"],
        "currency": wallet["currency"],
        "success": True
    })

@app.route("/api/initiate-transaction", methods=["POST"])
def transfer():
    data = request.json or {}
    sender = data.get("senderPhoneNumber")
    receiver = data.get("receiverPhoneNumber")
    amount = data.get("amount")
    
    if not sender or not receiver or amount is None:
        return jsonify({"code": 400, "message": "Missing fields", "success": False}), 400
        
    if sender not in WALLETS or receiver not in WALLETS:
        return jsonify({"code": 404, "message": "User not found", "success": False}), 404
        
    if WALLETS[sender]["balance"] < amount:
        return jsonify({"code": 400, "message": "Insufficient funds", "success": False}), 400
        
    # Execute
    WALLETS[sender]["balance"] -= amount
    WALLETS[receiver]["balance"] += amount
    
    tx_id = f"TX-{uuid.uuid4()}"
    TRANSACTIONS.append({
        "id": tx_id,
        "sender": sender,
        "receiver": receiver,
        "amount": amount,
        "status": "confirmed"
    })
    
    LOG.info(f"Transfer {amount} from {sender} to {receiver} [TX: {tx_id}]")
    
    return jsonify({
        "success": True,
        "tx_id": tx_id,
        "status": "confirmed",
        "message": "Transfer successful"
    })

if __name__ == "__main__":
    print("Starting Fake Bafoka API on port 9000...")
    app.run(host="0.0.0.0", port=9000, debug=True)
