import pytest
from unittest.mock import patch
from bot.app import create_app
from bot.models import Agreement, Offer, User
from bot import web3
from bot.db import db

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.app_context():
        # Drop and recreate all tables for each test to ensure clean state
        db.drop_all()
        db.create_all()
        with app.test_client() as client:
            yield client

@patch('bot.web3.create_agreement_on_chain')
@patch('bot.web3.confirm_agreement_on_chain')
def test_create_agreement_on_chain(mock_confirm, mock_create, client):
    mock_create.return_value = {"tx_hash": "0x123", "status": "success"}
    mock_confirm.return_value = {"tx_hash": "0x123", "status": "success"}
    
    # Create a user with valid community for both offer owner and requester
    user = User(phone="+123456789", community="BAMEKA")  # Use valid community
    db.session.add(user)
    db.session.commit()  # Commit to get the auto-generated ID
    
    # Create offer with proper owner_id
    offer = Offer(title="Test Offer", description="Test Desc", price=10.0, owner_id=user.id)
    db.session.add(offer)
    db.session.commit()

    response = client.post('/api/agreements', json={
        'offer_id': offer.id,
        'requester_phone': '+123456789'
    })

    assert response.status_code == 200
    data = response.get_json()
    
    # Verify response structure
    assert "agreement_id" in data
    assert "status" in data
    
    # The API should now return status="created_on_chain" after blockchain integration
    assert data["status"] == "created_on_chain"
    
    # Verify that blockchain functions were called correctly
    mock_create.assert_called_once_with(data["agreement_id"], offer.id, requester_addr="0xMOCK")
    mock_confirm.assert_called_once_with("0x123")
