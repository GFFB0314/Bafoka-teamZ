# fake_bafoka.py
"""
Fake Bafoka API Server - EXACT MATCH with Real Bafoka Sandbox API
All endpoints, field names, and response structures match the Swagger documentation
Source: https://sandbox.bafoka.network/webjars/swagger-ui/index.html
"""
from flask import Flask, request, jsonify
import uuid
from datetime import datetime

app = Flask(__name__)

# In-memory storage
ACCOUNTS = {}  # phone -> account data
TRANSACTIONS = {}  # tx_id -> transaction data

# Groupement mapping (from real API /api/groupements)
GROUPEMENT_MAP = {
    1: ("Batoufam", "MBIP TSWEFAP"),
    2: ("Fondjomekwet", "MBAM"),
    3: ("Bameka", "MUNKAP")
}

@app.route("/api/account-creation", methods=["POST"])
def create_account():
    """
    Create user account
    EXACT MATCH with real API: POST /api/account-creation
    Schema: AccountCreationRequest
    """
    data = request.get_json() or {}
    phone = data.get("phoneNumber")
    full_name = data.get("fullName", "")
    age = str(data.get("age", "25"))  # STRING (real API requirement)
    sex = data.get("sex", "M")
    groupement_id = data.get("groupement_id", 3)  # INTEGER with underscore
    blockchain_address = data.get("blockchainAddress", "")
    
    if not phone:
        return jsonify({
            "code": 400,
            "message": "phoneNumber is required",
            "data": None,
            "success": False
        }), 400
    
    # Check if account already exists
    if phone in ACCOUNTS:
        return jsonify({
            "code": 400,
            "message": "Phone number already used",
            "data": None,
            "success": False
        }), 400
    
    # Validate groupement_id
    if groupement_id not in GROUPEMENT_MAP:
        return jsonify({
            "code": 400,
            "message": "Groupement doesn't exist",
            "data": None,
            "success": False
        }), 400
    
    groupement_name, currency = GROUPEMENT_MAP[groupement_id]
    
    # Generate blockchain address if not provided
    if not blockchain_address:
        blockchain_address = f"0x{uuid.uuid4().hex[:40]}"
    
    account_id = str(uuid.uuid4())
    
    ACCOUNTS[phone] = {
        "id": account_id,
        "phoneNumber": phone,
        "fullName": full_name,
        "age": age,
        "sex": sex,
        "groupement_id": groupement_id,
        "groupementName": groupement_name,
        "blockchainAddress": blockchain_address,
        "balance": 0,  # Match real API - starts at 0
        "currency": currency,
        "createdAt": datetime.utcnow().isoformat(),
        "status": "active"
    }
    
    # Match real API response structure EXACTLY
    # Note: Real API returns success=False even on successful operations!
    return jsonify({
        "code": 200,
        "message": "Account created successfully",
        "data": {
            "blockchainAddress": blockchain_address,
            "phoneNumber": phone,
            "fullName": full_name,
            "age": age,
            "sex": sex,
            "groupement_id": groupement_id
        },
        "success": False  # Real API quirk - always False
    }), 200

@app.route("/api/get-balance", methods=["POST"])
def get_balance():
    """
    Get wallet balance
    EXACT MATCH with real API: POST /api/get-balance
    Schema: AccountCreationRequest (yes, uses full schema!)
    """
    data = request.get_json() or {}
    phone = data.get("phoneNumber")
    
    if not phone:
        return jsonify({
            "code": 400,
            "message": "phoneNumber is required",
            "data": None,
            "success": False
        }), 400
    
    account = ACCOUNTS.get(phone)
    if not account:
        return jsonify({
            "code": 400,
            "message": "Account not found",
            "data": None,
            "success": False
        }), 400
    
    # Match real API response structure
    return jsonify({
        "code": 200,
        "message": "Balance retrieved successfully",
        "data": {
            "phoneNumber": phone,
            "balance": account["balance"],
            "currency": account["currency"],
            "groupement_id": account["groupement_id"],
            "blockchainAddress": account.get("blockchainAddress", "")
        },
        "success": False  # Real API quirk
    }), 200

@app.route("/api/initiate-transaction", methods=["POST"])
def initiate_transaction():
    """
    Transfer between accounts
    NOT IN REAL API - This is why fake API is required!
    """
    data = request.get_json() or {}
    sender_phone = data.get("senderPhoneNumber")
    receiver_phone = data.get("receiverPhoneNumber")
    amount = data.get("amount")
    
    # Validation
    if not sender_phone or not receiver_phone or amount is None:
        return jsonify({"error": "senderPhoneNumber, receiverPhoneNumber, and amount required"}), 400
    
    try:
        amount = int(amount)
    except (ValueError, TypeError):
        return jsonify({"error": "amount must be integer"}), 400
    
    if amount <= 0:
        return jsonify({"error": "amount must be positive"}), 400
    
    # Check accounts exist
    sender = ACCOUNTS.get(sender_phone)
    receiver = ACCOUNTS.get(receiver_phone)
    
    if not sender:
        return jsonify({"error": "Sender account not found"}), 404
    if not receiver:
        return jsonify({"error": "Receiver account not found"}), 404
    
    # Check same community
    if sender["groupement_id"] != receiver["groupement_id"]:
        return jsonify({"error": "Transfers only within same community"}), 400
    
    # Check sufficient balance
    if sender["balance"] < amount:
        return jsonify({"error": "Insufficient balance"}), 400
    
    # Execute transaction
    sender["balance"] -= amount
    receiver["balance"] += amount
    
    # Create transaction record
    tx_id = f"TX-{uuid.uuid4().hex[:12].upper()}"
    transaction = {
        "tx_id": tx_id,
        "transaction_id": tx_id,
        "senderPhoneNumber": sender_phone,
        "receiverPhoneNumber": receiver_phone,
        "amount": amount,
        "currency": sender["currency"],
        "status": "completed",
        "timestamp": datetime.utcnow().isoformat(),
        "groupement_id": sender["groupement_id"]
    }
    
    TRANSACTIONS[tx_id] = transaction
    
    return jsonify({
        "success": True,
        "message": "Transaction completed successfully",
        "tx_id": tx_id,
        "transaction_id": tx_id,
        "status": "completed",
        "senderBalance": sender["balance"],
        "receiverBalance": receiver["balance"]
    }), 200

@app.route("/api/groupements", methods=["GET"])
def list_groupements():
    """
    List all groupements/communities
    EXACT MATCH with real API: GET /api/groupements
    """
    return jsonify([
        {"id": 1, "name": "Batoufam"},
        {"id": 2, "name": "Fondjomekwet"},
        {"id": 3, "name": "Bameka"}
    ]), 200

@app.route("/api/check-account", methods=["POST"])
def check_account():
    """
    Check if account exists
    EXACT MATCH with real API: POST /api/check-account
    Returns: "success" or "failed" (string, not JSON)
    """
    data = request.get_json() or {}
    phone = data.get("phoneNumber")
    
    if phone and phone in ACCOUNTS:
        return "success", 200
    return "failed", 200

@app.route("/api/recipient-info", methods=["POST"])
def recipient_info():
    """
    Get recipient information for transfer
    EXACT MATCH with real API: POST /api/recipient-info
    Query params: senderPhone, recipientPhone
    """
    sender_phone = request.args.get("senderPhone")
    recipient_phone = request.args.get("recipientPhone")
    
    if not sender_phone or not recipient_phone:
        return jsonify({
            "code": 400,
            "message": "Both senderPhone and recipientPhone required",
            "data": None,
            "success": False
        }), 400
    
    sender = ACCOUNTS.get(sender_phone)
    recipient = ACCOUNTS.get(recipient_phone)
    
    if not recipient:
        return jsonify({
            "code": 400,
            "message": "Recipient phone number not found",
            "data": None,
            "success": False
        }), 400
    
    # Check if same groupement
    if sender and sender.get("groupement_id") != recipient.get("groupement_id"):
        return jsonify({
            "code": 400,
            "message": "Sender and recipient belong to different groupements",
            "data": None,
            "success": False
        }), 400
    
    return jsonify({
        "code": 200,
        "message": "Recipient information found",
        "data": {
            "phoneNumber": recipient_phone,
            "fullName": recipient.get("fullName", ""),
            "groupement_id": recipient.get("groupement_id")
        },
        "success": False
    }), 200

@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Fake Bafoka API - Exact Match",
        "accounts": len(ACCOUNTS),
        "transactions": len(TRANSACTIONS)
    }), 200

@app.route("/", methods=["GET"])
def root():
    """Root endpoint"""
    return jsonify({
        "message": "Fake Bafoka API Server - Exact Match with Real API",
        "version": "2.0.0",
        "documentation": "https://sandbox.bafoka.network/webjars/swagger-ui/index.html",
        "endpoints": {
            "account_creation": "POST /api/account-creation",
            "get_balance": "POST /api/get-balance",
            "initiate_transaction": "POST /api/initiate-transaction (NOT IN REAL API)",
            "groupements": "GET /api/groupements",
            "check_account": "POST /api/check-account",
            "recipient_info": "POST /api/recipient-info",
            "health": "GET /api/health"
        }
    }), 200

if __name__ == "__main__":
    print("\n" + "="*70)
    print("FAKE BAFOKA API SERVER - EXACT MATCH WITH REAL API")
    print("="*70)
    print("Endpoints (matching Swagger documentation):")
    print("  [OK] POST /api/account-creation")
    print("  [OK] POST /api/get-balance")
    print("  [!]  POST /api/initiate-transaction (NOT in real API - required for transfers)")
    print("  [OK] GET  /api/groupements")
    print("  [OK] POST /api/check-account")
    print("  [OK] POST /api/recipient-info")
    print("  [i]  GET  /api/health")
    print("\nKey Features:")
    print("  * Field names match real API (groupement_id not groupementId)")
    print("  * Response structure matches real API (code/message/data/success)")
    print("  * Initial balance = 0 (matching real API)")
    print("  * age field is STRING (matching real API)")
    print("\nRunning on: http://localhost:9000")
    print("="*70 + "\n")
    app.run(host="0.0.0.0", port=9000, debug=True)
