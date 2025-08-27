# core_logic.py
from typing import List, Optional, Tuple
from db import db
from models import User, Offer, Agreement
from datetime import datetime

def get_user_by_phone(phone: str) -> Optional[User]:
    return User.query.filter_by(phone=phone).first()

def register_user(phone: str, name: str = None, skill: str = None) -> Tuple[User, bool]:
    """
    Create or update user.
    Returns (user, created_bool)
    """
    phone = (phone or "").strip()
    user = get_user_by_phone(phone)
    if user:
        changed: bool = False
        if name and user.name != name:
            user.name = name
            changed = True
        if skill and user.skill != skill:
            user.skill = skill
            changed = True
        if changed:
            db.session.commit()
        return (user, False)
    user = User(phone=phone, name=name, skill=skill)
    db.session.add(user)
    db.session.commit()
    return (user, True)

def create_offer_for_user(phone: str, description: str, title: Optional[str] = None, price: float = 0.0) -> Offer:
    user, _ = register_user(phone)
    offer = Offer(owner=user, title=(title or ""), description=description, price=price)
    db.session.add(offer)
    db.session.commit()
    return offer

def find_offers_by_keyword(keyword: str, limit: int = 20) -> List[Offer]:
    q = f"%{keyword.strip().lower()}%"
    # case-insensitive match on title + description
    return (
        Offer.query.join(User, Offer.owner)
        .filter(Offer.status == "open")
        .filter(
            db.or_(
                db.func.lower(Offer.description).like(q),
                db.func.lower(Offer.title).like(q)
            )
        )
        .order_by(Offer.created_at.desc())
        .limit(limit)
        .all()
    )

def initiate_agreement(offer_id: int, requester_phone: str) -> Agreement:
    offer = Offer.query.get(offer_id)
    if not offer:
        raise ValueError("Offer not found")
    requester, _ = register_user(requester_phone)
    ag = Agreement(offer=offer, requester=requester, status="pending")
    offer.status = "matched"
    db.session.add(ag)
    db.session.commit()
    return ag

# convenience wrapper for BE1 naming
def register_user_be1(whatsapp_number: str, name: str, skill: str):
    return register_user(phone=whatsapp_number, name=name, skill=skill)
