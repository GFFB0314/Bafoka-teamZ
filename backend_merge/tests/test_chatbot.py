import os
import re
import uuid
import pytest

# Ensure the project root is on sys.path even if conftest is not picked up
import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
# Ensure we import the app factory and core to monkeypatch stubs
from bot import app as app_module
from bot import core_logic as core

@pytest.fixture()
def client(tmp_path, monkeypatch):
    # Use a temp sqlite DB per test session
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

    # Stub external Bafoka functions to avoid HTTP
    def _stub_create_wallet(display_name, metadata=None):
        return {"wallet_id": f"mock-{uuid.uuid4()}", "address": "0xMOCK"}

    def _stub_credit_wallet(wallet_id, amount, reason="signup"):
        return {"tx_id": f"mock-credit-{wallet_id}", "status": "success"}

    def _stub_transfer(from_wallet_id, to_wallet_id, amount, idempotency_key=None):
        return {"tx_id": f"mock-tx-{uuid.uuid4()}", "status": "pending"}

    def _stub_get_balance(wallet_id):
        return {"balance": 999}

    monkeypatch.setattr(core, "create_wallet", _stub_create_wallet, raising=True)
    monkeypatch.setattr(core, "credit_wallet", _stub_credit_wallet, raising=True)
    monkeypatch.setattr(core, "bafoka_transfer", _stub_transfer, raising=True)
    # The Flask route uses app_module.bafoka_get_balance
    monkeypatch.setattr(app_module, "bafoka_get_balance", _stub_get_balance, raising=False)

    # Build app and client
    test_app = app_module.create_app()
    return test_app.test_client()


def send(client, phone, text):
    resp = client.post("/webhook", data={"From": phone, "Body": text})
    assert resp.status_code == 200
    return resp.data.decode("utf-8")


def extract_offer_id(s):
    # Finds 'ID:<num>' in the response
    m = re.search(r"ID:(\d+)", s)
    return int(m.group(1)) if m else None


def test_chatbot_commands_end_to_end(client):
    phone1 = "whatsapp:+1111111111"
    phone2 = "whatsapp:+1222222222"

    # 1) Register + profile with community
    out = send(client, phone1, "/register BAMEKA | Alice | Carpentry")
    assert "Registered" in out or "Updated profile" in out

    out = send(client, phone1, "/me")
    assert "Registered: whatsapp:+1111111111" in out
    assert "Carpentry" in out

    # 2) Offer + search within same community
    out = send(client, phone1, "/offer Fix door | Door fix | 10")
    assert "Offer created" in out
    offer_id = extract_offer_id(out)
    assert isinstance(offer_id, int)

    out = send(client, phone1, "/search door")
    assert f"ID:{offer_id}" in out

    # 3) Second user same community agrees, third user other community cannot
    out = send(client, phone2, "/register BAMEKA | Bob | Plumbing")
    assert "Registered" in out or "Updated profile" in out

    out = send(client, phone2, f"/agree {offer_id}")
    assert "Agreement created" in out

    # User in other community
    phone3 = "whatsapp:+1333333333"
    out = send(client, phone3, "/register BATOUFAM | Charlie | Painting")
    assert "Registered" in out or "Updated profile" in out

    # Cross-community search yields no results
    out = send(client, phone3, "/search door")
    assert "No open offers found" in out

    # 4) Balance shows community currency name
    out = send(client, phone1, "/balance")
    assert ("Solde local: 1000 MUNKAP" in out) or ("Local balance: 1000 MUNKAP" in out)
    assert ("Solde externe: 999" in out) or ("External balance: 999" in out)

    # 5) Transfer from phone1 (BAMEKA) to phone2 (BAMEKA) succeeds
    out = send(client, phone1, f"/transfer {phone2} 100")
    assert ("Transfert initié" in out) or ("Transfer initiated" in out)

    # 5b) Transfer from phone1 (BAMEKA) to phone3 (BATOUFAM) fails
    out = send(client, phone1, f"/transfer {phone3} 50")
    assert "community" in out.lower()

    # 6) Delete account and verify
    out = send(client, phone1, "/delete")
    assert "deleted" in out.lower() or "supprim" in out.lower()

    out = send(client, phone1, "/me")
    assert "No user record" in out

    # 7) Help shows /delete and communities
    out = send(client, phone2, "/help")
    assert "/delete" in out
    assert "BAMEKA" in out and "BATOUFAM" in out and "FONDJOMEKWET" in out

