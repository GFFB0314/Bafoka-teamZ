import os
import re
import uuid
import pytest

# Ensure the project root is on sys.path
import sys, os as _os
ROOT = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), _os.pardir))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from bot import app as app_module
from bot import core_logic as core

@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

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
    monkeypatch.setattr(app_module, "bafoka_get_balance", _stub_get_balance, raising=False)

    test_app = app_module.create_app()
    return test_app.test_client()


def send(client, phone, text):
    resp = client.post("/webhook", data={"From": phone, "Body": text})
    assert resp.status_code == 200
    return resp.data.decode("utf-8")


def extract_offer_id(s):
    m = re.search(r"ID:(\d+)", s)
    return int(m.group(1)) if m else None


def test_register_me_displays_currency(client):
    phone = "whatsapp:+1000000000"
    out = send(client, phone, "/register BATOUFAM | Bob | Plumbing")
    assert "Registered" in out or "Updated profile" in out
    out = send(client, phone, "/me")
    assert "Registered: whatsapp:+1000000000" in out
    assert "Balance: 1000 MBIP TSWEFAP" in out


def test_offer_and_search_same_community(client):
    p1 = "whatsapp:+2000000000"
    send(client, p1, "/register BAMEKA | Alice | Carpentry")
    out = send(client, p1, "/offer Fix door | Door fix | 10")
    assert "Offer created" in out
    oid = extract_offer_id(out)
    out = send(client, p1, "/search door")
    assert f"ID:{oid}" in out


def test_agree_same_and_cross_community(client):
    p1 = "whatsapp:+3000000000"
    p2 = "whatsapp:+3000000001"
    p3 = "whatsapp:+3000000002"
    send(client, p1, "/register BAMEKA | Alice | Carpentry")
    send(client, p2, "/register BAMEKA | Bob | Plumbing")
    send(client, p3, "/register BATOUFAM | Charlie | Painting")

    out = send(client, p1, "/offer Paint fence | Paint | 20")
    oid = extract_offer_id(out)

    out = send(client, p2, f"/agree {oid}")
    assert "Agreement created" in out

    out = send(client, p3, f"/agree {oid}")
    assert "same community" in out.lower() or "community" in out.lower()


def test_balance_and_transfer_rules(client):
    p1 = "whatsapp:+4000000000"
    p2 = "whatsapp:+4000000001"
    p3 = "whatsapp:+4000000002"

    send(client, p1, "/register BAMEKA | Alice | Carpentry")
    send(client, p2, "/register BAMEKA | Bob | Plumbing")
    send(client, p3, "/register FONDJOMEKWET | Carol | Sewing")

    out = send(client, p1, "/balance")
    assert ("Solde local: 1000 MUNKAP" in out) or ("Local balance: 1000 MUNKAP" in out)

    out = send(client, p1, f"/transfer {p2} 50")
    assert ("Transfert initié" in out) or ("Transfer initiated" in out)

    out = send(client, p1, f"/transfer {p3} 10")
    assert "community" in out.lower()


def test_delete_and_help(client):
    p = "whatsapp:+5000000000"
    send(client, p, "/register BAMEKA | Dee | Cooking")
    out = send(client, p, "/delete")
    assert "deleted" in out.lower() or "supprim" in out.lower()
    out = send(client, p, "/me")
    assert "No user record" in out
    out = send(client, p, "/help")
    assert "/delete" in out and "BAMEKA" in out and "BATOUFAM" in out and "FONDJOMEKWET" in out

