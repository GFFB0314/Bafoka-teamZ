# dev/core_logic.py
# Mirror of bot/core_logic.py but wired to the real Bafoka API and dev DB/models.
from typing import List, Optional, Tuple, Dict
from .db import db
from .models import User, Offer, Agreement, Transaction
import logging
import uuid
from . import api_client
import re

LOG = logging.getLogger("dev_core_logic")
LOG.setLevel(logging.INFO)

# Community to currency mapping (canonical uppercase keys)
COMMUNITY_TO_CURRENCY = {
    "BAMEKA": "MUNKAP",
    "BATOUFAM": "MBIP TSWEFAP",
    "FONDJOMEKWET": "MBAM",
}

def canonicalize_community(value: str) -> Optional[str]:
    if not value:
        return None
    key = value.strip().upper()
    return key if key in COMMUNITY_TO_CURRENCY else None

def currency_for_community(comm: Optional[str]) -> Optional[str]:
    if not comm:
        return None
    key = canonicalize_community(comm)
    return COMMUNITY_TO_CURRENCY.get(key) if key else None


def get_user_by_phone(phone: str) -> Optional[User]:
    if not phone:
        return None
    return User.query.filter_by(phone=phone).first()


def _derive_email_from_phone(phone: str) -> str:
    # Deterministic placeholder email to satisfy real API when user email isn't provided
    s = (phone or "").lower()
    s = s.replace("whatsapp:", "")
    s = re.sub(r"[^0-9a-zA-Z+]", "", s)
    s = s.replace("+", "")
    if not s:
        s = "user"
    return f"{s}@sandbox.bafoka.local"

def register_user(phone: str, name: str = None, email: str = None, skill: str = None, community: str = None, local_name: str = None) -> Tuple[User, bool]:
    """
    Mirror of bot.register_user but using the real Bafoka API.
    - Create/update local user with community and local currency name
    - Call POST /api/register to create a remote user and token
    - Fetch GET /api/user/balance to populate local bafoka_balance and currency name
    """
    phone = (phone or "").strip()
    if not email:
        raise ValueError("email is required")

    canon_comm = canonicalize_community(community) if community else None
    if community and not canon_comm:
        raise ValueError("Invalid community. Allowed: BAMEKA, BATOUFAM, FONDJOMEKWET")

    user = get_user_by_phone(phone)
    created = False
    if not user:
        user = User(
            phone=phone,
            name=name,
            email=email,
            skill=skill,
            community=canon_comm or None,
            bafoka_local_name=(local_name or currency_for_community(canon_comm))
        )
        db.session.add(user)
        db.session.commit()
        created = True
    else:
        if name is not None:
            user.name = name
        if email is not None:
            user.email = email
        if skill is not None:
            user.skill = skill
        if canon_comm is not None and user.community != canon_comm:
            user.community = canon_comm
            user.bafoka_local_name = currency_for_community(canon_comm)
        db.session.add(user)
        db.session.commit()

    # Register with real API (idempotent on server side expected)
    try:
        # Derive email to satisfy API payload while mirroring bot command inputs
        payload = {
            "name": name or phone,
            "phone": phone,
            "email": email,
        }
        resp = api_client.register_user(payload)
        data_user = (resp or {}).get("user") or {}
        token = (resp or {}).get("token")
        if token:
            user.auth_token = token
        # Persist returned remote identity info
        user.remote_user_id = data_user.get("id")
        user.blockchain_address = data_user.get("blockchain_address")
        if data_user.get("email"):
            user.email = data_user.get("email")
        db.session.add(user)
        db.session.commit()
        # Fetch balance and currency
        if user.auth_token:
            try:
                bal = api_client.get_user_balance(user.auth_token)
                user.bafoka_balance = int(bal.get("balance") or (user.bafoka_balance or 0))
                # Prefer remote currency if present; else keep mapped
                user.bafoka_local_name = bal.get("currency") or user.bafoka_local_name or currency_for_community(user.community)
                db.session.add(user)
                db.session.commit()
            except Exception as e:
                LOG.info("Unable to fetch balance after register: %s", e)
    except Exception as e:
        LOG.exception("Failed to register with real Bafoka API for %s: %s", phone, e)

    # Mirror bot behavior: ensure local signup bonus of 1000 exactly once per user
    try:
        if not getattr(user, "signup_bonus_granted", False):
            if (user.bafoka_balance or 0) < 1000:
                user.bafoka_balance = 1000
            user.signup_bonus_granted = True
            db.session.add(user)
            db.session.commit()
    except Exception as e:
        LOG.info("Unable to set local signup bonus: %s", e)

    return user, created

# compatibility wrapper used by your chatbot

def register_user_be1(whatsapp_number: str, name: str = None, skill: str = None) -> Tuple[User, bool]:
    return register_user(phone=whatsapp_number, name=name, skill=skill)


def create_offer_for_user(phone: str, description: str, title: Optional[str] = None, price: float = 0.0) -> Offer:
    user = get_user_by_phone(phone)
    if not user or not user.community:
        raise ValueError("User must be registered with a community before creating offers")
    # Create product remotely if token exists
    remote_id = None
    try:
        if user.auth_token:
            resp = api_client.create_product(user.auth_token, name=(title or ""), description=description, price=price)
            remote_id = resp.get("id") or resp.get("product_id")
    except Exception as e:
        LOG.info("Remote product create failed (non-blocking): %s", e)
    offer = Offer(owner=user, title=(title or ""), description=description, price=price, remote_product_id=remote_id)
    db.session.add(offer)
    db.session.commit()
    return offer


def find_offers_by_keyword(keyword: str, limit: int = 20, community: Optional[str] = None) -> List[Offer]:
    q = f"%{keyword.strip().lower()}%"
    query = (
        Offer.query.join(User, Offer.owner)
        .filter(Offer.status == "open")
        .filter(
            db.or_(
                db.func.lower(Offer.description).like(q),
                db.func.lower(Offer.title).like(q)
            )
        )
    )
    if community:
        canon = canonicalize_community(community)
        if canon:
            query = query.filter(User.community == canon)
        else:
            return []
    return query.order_by(Offer.created_at.desc()).limit(limit).all()


def initiate_agreement(offer_id: int, requester_phone: str) -> Agreement:
    offer = Offer.query.get(offer_id)
    if not offer:
        raise ValueError("Offer not found")
    requester = get_user_by_phone(requester_phone)
    if not requester or not requester.community:
        raise ValueError("Requester must be registered with a community")
    if not offer.owner or not offer.owner.community:
        raise ValueError("Offer owner has no community set")
    if requester.community != offer.owner.community:
        raise ValueError("Users must belong to the same community for agreements")
    ag = Agreement(offer=offer, requester=requester, status="pending")
    offer.status = "matched"
    db.session.add(ag)
    db.session.commit()
    return ag


def transfer_bafoka(from_phone: str, to_phone: str, amount: int, idempotency_key: str = None) -> Dict:
    """
    Mirror of bot.transfer_bafoka, but calls real API POST /api/purchase.
    """
    if amount <= 0:
        raise ValueError("Amount must be positive integer")

    from_user = get_user_by_phone(from_phone)
    to_user = get_user_by_phone(to_phone)
    if not from_user or not to_user:
        raise ValueError("Both users must exist")

    if not from_user.community or not to_user.community:
        raise ValueError("Both users must be registered with a community")

    if from_user.community != to_user.community:
        raise ValueError("Transfers are only allowed within the same community")

    if not from_user.auth_token or not to_user.remote_user_id:
        raise ValueError("Missing auth token or remote user id")

    if (from_user.bafoka_balance or 0) < amount:
        raise ValueError("Insufficient balance")

    # create transaction record
    tx = Transaction(tx_id=None, from_user_id=from_user.id, to_user_id=to_user.id, amount=amount, status="pending", _metadata=None, reverted=False)
    db.session.add(tx)
    db.session.commit()

    # optimistic local update
    try:
        from_user.bafoka_balance = (from_user.bafoka_balance or 0) - amount
        to_user.bafoka_balance = (to_user.bafoka_balance or 0) + amount
        db.session.add(from_user)
        db.session.add(to_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        tx.status = "failed"
        tx._metadata = f"local-update-failed: {str(e)}"
        db.session.add(tx)
        db.session.commit()
        raise

    # call real API purchase
    try:
        resp = api_client.purchase(from_user.auth_token, seller_id=int(to_user.remote_user_id), amount=int(amount))
        external_tx_id = resp.get("id") or resp.get("tx_id") or resp.get("transaction_id")
        status = resp.get("status", "pending")
        tx.tx_id = external_tx_id
        tx.status = status
        tx._metadata = str(resp)
        db.session.add(tx)
        db.session.commit()
        return {"tx_id": tx.tx_id, "status": tx.status}
    except Exception as e:
        # revert local balances
        try:
            from_user.bafoka_balance = (from_user.bafoka_balance or 0) + amount
            to_user.bafoka_balance = (to_user.bafoka_balance or 0) - amount
            db.session.add(from_user)
            db.session.add(to_user)
            tx.status = "failed"
            tx._metadata = f"external-transfer-failed: {str(e)}"
            db.session.add(tx)
            db.session.commit()
        except Exception:
            db.session.rollback()
            tx.status = "failed"
            tx._metadata = f"external-transfer-failed-and-revert_failed: {str(e)}"
            db.session.add(tx)
            db.session.commit()
        raise


def adjust_balances_on_external_update(tx_id: str, new_status: str, metadata: dict = None) -> Dict:
    tx = Transaction.query.filter_by(tx_id=tx_id).first()
    if not tx:
        return {"ok": False, "reason": "tx not found"}

    if tx.status == new_status:
        return {"ok": True, "status": tx.status}

    failure_states = {"failed", "rejected", "cancelled", "error"}
    success_states = {"success", "confirmed", "completed"}

    from_user = User.query.get(tx.from_user_id) if tx.from_user_id else None
    to_user = User.query.get(tx.to_user_id) if tx.to_user_id else None

    lower_status = (new_status or "").lower()

    if lower_status in failure_states and not tx.reverted:
        try:
            if from_user:
                from_user.bafoka_balance = (from_user.bafoka_balance or 0) + tx.amount
                db.session.add(from_user)
            if to_user:
                to_user.bafoka_balance = (to_user.bafoka_balance or 0) - tx.amount
                db.session.add(to_user)
            tx.reverted = True
            tx.status = new_status
            tx._metadata = str(metadata) if metadata else tx._metadata
            db.session.add(tx)
            db.session.commit()
            return {"ok": True, "action": "reverted", "status": tx.status}
        except Exception as e:
            db.session.rollback()
            return {"ok": False, "error": f"revert_failed: {str(e)}"}

    if lower_status in success_states:
        tx.status = new_status
        tx._metadata = str(metadata) if metadata else tx._metadata
        db.session.add(tx)
        db.session.commit()
        return {"ok": True, "action": "confirmed", "status": tx.status}

    tx.status = new_status
    tx._metadata = str(metadata) if metadata else tx._metadata
    db.session.add(tx)
    db.session.commit()
    return {"ok": True, "status": tx.status}


def delete_user(phone: str) -> Tuple[bool, str]:
    user = get_user_by_phone(phone)
    if not user:
        return False, "user_not_found"

    try:
        Agreement.query.filter_by(requester_id=user.id).delete(synchronize_session=False)
        owned_offers = Offer.query.filter_by(owner_id=user.id).all()
        for off in owned_offers:
            db.session.delete(off)
        txs = (
            Transaction.query
            .filter(db.or_(Transaction.from_user_id == user.id, Transaction.to_user_id == user.id))
            .all()
        )
        for t in txs:
            if t.from_user_id == user.id:
                t.from_user_id = None
            if t.to_user_id == user.id:
                t.to_user_id = None
            t._metadata = (t._metadata or "") + " | user_deleted"
            db.session.add(t)
        db.session.delete(user)
        db.session.commit()
        return True, "deleted"
    except Exception as e:
        db.session.rollback()
        LOG.exception("delete_user failed for %s: %s", phone, e)
        return False, str(e)

