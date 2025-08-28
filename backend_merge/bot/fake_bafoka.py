# fake_bafoka.py
from flask import Flask, request, jsonify
import uuid

app = Flask(__name__)
WALLETS = {}
TXS = {}

@app.route("/wallets", methods=["POST"])
def create_wallet():
    j = request.get_json() or {}
    wid = str(uuid.uuid4())
    WALLETS[wid] = {"display_name": j.get("display_name"), "balance": 0, "metadata": j.get("metadata", {})}
    return jsonify({"wallet_id": wid, "address": "0xFAKE"})

@app.route("/wallets/<wallet_id>/credit", methods=["POST"])
def credit(wallet_id):
    if wallet_id not in WALLETS:
        return jsonify({"error":"wallet not found"}), 404
    j = request.get_json() or {}
    amount = int(j.get("amount",0))
    WALLETS[wallet_id]["balance"] += amount
    txid = str(uuid.uuid4())
    TXS[txid] = {"tx_id": txid, "status":"success", "to": wallet_id, "amount": amount}
    return jsonify({"tx_id": txid, "status":"success"})

@app.route("/transactions", methods=["POST"])
def transfer():
    j = request.get_json() or {}
    fw = j.get("from_wallet")
    tw = j.get("to_wallet")
    amount = int(j.get("amount", 0))
    if fw not in WALLETS or tw not in WALLETS:
        return jsonify({"error":"wallet not found"}), 404
    WALLETS[fw]["balance"] -= amount
    WALLETS[tw]["balance"] += amount
    txid = str(uuid.uuid4())
    TXS[txid] = {"tx_id": txid, "status":"pending", "from": fw, "to": tw, "amount": amount}
    return jsonify({"tx_id": txid, "status":"pending"})

@app.route("/wallets/<wallet_id>/balance", methods=["GET"])
def balance(wallet_id):
    w = WALLETS.get(wallet_id)
    if not w:
        return jsonify({"error":"wallet not found"}), 404
    return jsonify({"balance": w["balance"]})

if __name__ == "__main__":
    app.run(port=9000, debug=True)
