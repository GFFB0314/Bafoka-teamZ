# core_logic.py
from typing import List, Optional, Tuple, Dict
from .db import db
from .models import User, Offer, Agreement, Transaction
from datetime import datetime
import logging
import uuid

LOG = logging.getLogger("core_logic")
LOG.setLevel(logging.INFO)

# Community to currency mapping (canonical uppercase keys)
# Real mapping from Bafoka API /api/groupements:
# [{'id': 1, 'name': 'Batoufam'}, {'id': 2, 'name': 'Fondjomekwet'}, {'id': 3, 'name': 'Bameka'}]
COMMUNITY_TO_CURRENCY = {
    "BATOUFAM": "MBIP TSWEFAP",
    "FONDJOMEKWET": "MBAM",
    "FONDJOMENKWET": "MBAM",  # Alternative spelling
    "BAMEKA": "MUNKAP",
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

# Try to import real bafoka client; if missing, fallback to stubs for dev
try:
    # import transfer as bafoka_transfer so code below reads clearly
    from .bafoka_client import create_wallet, transfer as bafoka_transfer, get_balance
except Exception as e:
    LOG.warning("bafoka_client not available; using stubs: %s", e)

    def create_wallet(phone, name, community_id="BAMEKA", age=25):
        return {"id": f"mock-{phone}", "phoneNumber": phone}

    def bafoka_transfer(from_phone, to_phone, amount):
        return {"tx_id": f"mock-transfer-{from_phone}-{to_phone}-{amount}", "status": "pending"}

    def get_balance(phone):
        return {"balance": 0}


def get_user_by_phone(phone: str) -> Optional[User]:
    if not phone:
        return None
    return User.query.filter_by(phone=phone).first()


def register_user(phone: str, name: str = None, skill: str = None, community: str = None, local_name: str = None) -> Tuple[User, bool]:
    """
    Create or update user.
    When creating a new user, community is validated and currency name is set accordingly.
    On first creation, create a Bafoka wallet and attempt to credit 1000 units.
    We update local bafoka_balance only when external credit succeeds.
    Returns (user, created_bool)
    """
    phone = (phone or "").strip()

    # Validate and canonicalize community if provided
    canon_comm = canonicalize_community(community) if community else None
    if community and not canon_comm:
        raise ValueError("Invalid community. Allowed: BAMEKA, BATOUFAM, FONDJOMEKWET")

    user = get_user_by_phone(phone)
    created = False
    if not user:
        user = User(
            phone=phone,
            name=name,
            skill=skill,
            community=canon_comm or None,
            bafoka_local_name=(local_name or currency_for_community(canon_comm))
        )
        db.session.add(user)
        db.session.commit()
        created = True
    else:
        # Update fields if provided
        if name is not None:
            user.name = name
        if skill is not None:
            user.skill = skill
        if canon_comm is not None and user.community != canon_comm:
            user.community = canon_comm
            user.bafoka_local_name = currency_for_community(canon_comm)
        db.session.add(user)
        db.session.commit()

    # If newly created - ensure external wallet (idempotent)
    if created and not user.bafoka_wallet_id:
        try:
            # Convert community name to groupement_id (matching real API)
            # Mapping from Bafoka API /api/groupements:
            community_to_groupement = {
                "BATOUFAM": 1,
                "FONDJOMEKWET": 2,
                "FONDJOMENKWET": 2,  # Alternative spelling
                "BAMEKA": 3,
            }
            groupement_id = community_to_groupement.get(user.community.upper() if user.community else "", 3)
            
            # Call create_wallet with EXACT API parameter names
            resp = create_wallet(
                phoneNumber=phone,
                fullName=name or phone,
                groupement_id=groupement_id,
                age="25",  # String as required by API
                sex="M",   # Default
                blockchainAddress=""  # Empty for new accounts
            )
            # Real API response structure: {'code': 200, 'data': {'blockchainAddress': '0x...', ...}, ...}
            # Extract blockchain address from response
            if resp.get('code') == 200 and resp.get('data'):
                blockchain_addr = resp['data'].get('blockchainAddress')
                if blockchain_addr:
                    user.bafoka_wallet_id = blockchain_addr
                    # Real API starts with 0 balance - no automatic credit
                    # Balance remains 0 until user receives funds
                    db.session.add(user)
                    db.session.commit()
                    LOG.info(f"Bafoka wallet created for {phone}: {blockchain_addr}")
        except Exception as e:
            LOG.exception("Failed to create Bafoka wallet for user %s: %s", phone, e)

    return user, created


# compatibility wrapper used by your chatbot
def register_user_be1(whatsapp_number: str, name: str = None, skill: str = None) -> Tuple[User, bool]:
    return register_user(phone=whatsapp_number, name=name, skill=skill)


def create_offer_for_user(phone: str, description: str, title: Optional[str] = None, price: float = 0.0) -> Offer:
    user = get_user_by_phone(phone)
    if not user or not user.community:
        raise ValueError("User must be registered with a community before creating offers")
    offer = Offer(owner=user, title=(title or ""), description=description, price=price)
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
            # invalid community yields no results
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
    Perform a Bafoka transfer between two users (by phone). Records a Transaction row.
    Behavior:
      - Validate amount > 0
      - Ensure users & wallets exist
      - Check local balance of sender
      - Create Transaction row status='pending'
      - Optimistically debit sender and credit recipient locally
      - Call external Bafoka API; on success update tx.tx_id and status
      - On external failure, revert local balances and mark tx failed
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

    if not from_user.bafoka_wallet_id or not to_user.bafoka_wallet_id:
        raise ValueError("Both users must have bafoka_wallet_id")

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

    # call external
    try:
        # API uses phone numbers, not wallet IDs
        resp = bafoka_transfer(from_user.phone, to_user.phone, amount)
        external_tx_id = resp.get("tx_id") or resp.get("id") or resp.get("transaction_id")
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
    """
    Called by webhook to reconcile transaction state reported by external Bafoka API.
    - Revert local optimistic changes on failure if not already reverted.
    - Mark success if external confirms.
    """
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


# Account deletion
# Removes the user account and related data safely:
# - Deletes agreements where the user is requester
# - Deletes offers owned by the user (and their agreements via cascade)
# - Nullifies references in Transaction rows (from_user_id/to_user_id)
# Note: This is a hard delete. Consider soft-delete in production.

def delete_user(phone: str) -> Tuple[bool, str]:
    user = get_user_by_phone(phone)
    if not user:
        return False, "user_not_found"

    try:
        # Remove agreements where user is requester
        Agreement.query.filter_by(requester_id=user.id).delete(synchronize_session=False)

        # Delete offers owned by user (and cascade to their agreements)
        owned_offers = Offer.query.filter_by(owner_id=user.id).all()
        for off in owned_offers:
            db.session.delete(off)

        # Nullify transactions
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

        # Finally delete user
        db.session.delete(user)
        db.session.commit()
        return True, "deleted"
    except Exception as e:
        db.session.rollback()
        LOG.exception("delete_user failed for %s: %s", phone, e)
        return False, str(e)
