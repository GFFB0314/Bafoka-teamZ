import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Ensure backend_merge is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

@pytest.fixture
def client():
    from bot.app import create_app
    from bot.db import db
    
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

@patch("bot.bafoka_client.requests.post")
def test_register_user_integration(mock_post, client):
    """Test that /api/register calls the correct Bafoka endpoint"""
    # Mock Bafoka response
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"id": "mock-wallet-id", "phoneNumber": "+237600000000"}

    # Call Flask endpoint
    resp = client.post("/api/register", json={
        "phone": "+237600000000",
        "name": "Test User",
        "community": "BAMEKA",
        "skill": "Farming"
    })
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["bafoka_wallet_id"] == "mock-wallet-id" or data["bafoka_wallet_id"] == "+237600000000"
    
    # Verify Bafoka API was called correctly
    mock_post.assert_called()
    args, kwargs = mock_post.call_args
    assert "https://sandbox.bafoka.network/api/account-creation" in args[0]
    assert kwargs["json"]["phoneNumber"] == "+237600000000"
    assert kwargs["json"]["groupementId"] == "BAMEKA"

@patch("bot.bafoka_client.requests.post")
def test_transfer_integration(mock_post, client):
    """Test that /api/transfer calls the correct Bafoka endpoint"""
    from bot.models import User
    from bot.db import db
    
    # Setup users
    with client.application.app_context():
        u1 = User(phone="+237611111111", name="Sender", community="BAMEKA", bafoka_wallet_id="+237611111111", bafoka_balance=5000)
        u2 = User(phone="+237622222222", name="Receiver", community="BAMEKA", bafoka_wallet_id="+237622222222", bafoka_balance=0)
        db.session.add_all([u1, u2])
        db.session.commit()

    # Mock Bafoka response
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"transaction_id": "tx-123", "status": "success"}

    # Call Flask endpoint
    resp = client.post("/api/transfer", json={
        "from_phone": "+237611111111",
        "to_phone": "+237622222222",
        "amount": 1000
    })

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["tx_id"] == "tx-123"

    # Verify Bafoka API call
    mock_post.assert_called()
    args, kwargs = mock_post.call_args
    assert "https://sandbox.bafoka.network/api/initiate-transaction" in args[0]
    assert kwargs["json"]["senderPhoneNumber"] == "+237611111111"
    assert kwargs["json"]["receiverPhoneNumber"] == "+237622222222"
    assert kwargs["json"]["amount"] == 1000

@patch("bot.bafoka_client.requests.post")
def test_balance_integration(mock_post, client):
    """Test that /api/balance calls the correct Bafoka endpoint"""
    from bot.models import User
    from bot.db import db
    
    # Setup user
    with client.application.app_context():
        u1 = User(phone="+237633333333", name="BalanceUser", community="BAMEKA", bafoka_wallet_id="+237633333333", bafoka_balance=500)
        db.session.add(u1)
        db.session.commit()

    # Mock Bafoka response
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"balance": 9999, "currency": "MUNKAP"}

    # Call Flask endpoint
    resp = client.get("/api/balance?phone=+237633333333")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["local_balance"] == 500
    assert data["external_balance"] == 9999

    # Verify Bafoka API call
    mock_post.assert_called()
    args, kwargs = mock_post.call_args
    assert "https://sandbox.bafoka.network/api/get-balance" in args[0]
    assert kwargs["json"]["phoneNumber"] == "+237633333333"
