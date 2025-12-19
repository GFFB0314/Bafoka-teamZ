# bot/services/user_service.py
from bot.models import User
from bot.db import db
from bot.services.wallet_service import WalletService
import logging

LOG = logging.getLogger(__name__)

# Community to currency mapping
COMMUNITY_TO_CURRENCY = {
    "BAMEKA": "MUNKAP",
    "BATOUFAM": "MBIP TSWEFAP",
    "FONDJOMEKWET": "MBAM",
}

class UserService:
    @staticmethod
    def canonicalize_community(value: str):
        if not value: return None
        key = value.strip().upper()
        return key if key in COMMUNITY_TO_CURRENCY else None

    @staticmethod
    def get_currency_for_community(comm: str):
        if not comm: return None
        key = UserService.canonicalize_community(comm)
        return COMMUNITY_TO_CURRENCY.get(key)

    @staticmethod
    def get_user_by_phone(phone: str) -> User:
        return User.query.filter_by(phone=phone).first()

    @staticmethod
    def register_user(phone: str, name: str, skill: str, community: str) -> tuple[User, bool]:
        """
        Register a new user or update existing one.
        Creates Bafoka wallet if new.
        Returns (User, created_bool)
        """
        phone = (phone or "").strip()
        canon_comm = UserService.canonicalize_community(community)
        
        if community and not canon_comm:
            raise ValueError(f"Invalid community. Allowed: {list(COMMUNITY_TO_CURRENCY.keys())}")

        user = UserService.get_user_by_phone(phone)
        created = False

        if not user:
            user = User(
                phone=phone,
                name=name,
                skill=skill,
                community=canon_comm,
                bafoka_local_name=UserService.get_currency_for_community(canon_comm)
            )
            db.session.add(user)
            db.session.commit()
            created = True
        else:
            # Update fields
            if name: user.name = name
            if skill: user.skill = skill
            if canon_comm and user.community != canon_comm:
                user.community = canon_comm
                user.bafoka_local_name = UserService.get_currency_for_community(canon_comm)
            db.session.add(user)
            db.session.commit()

        # Create external wallet if needed
        if created and not user.bafoka_wallet_id:
            try:
                # Assuming default age 25 for simplicity
                resp = WalletService.create_wallet(phone, name or phone, user.community, age=25)
                # Helper to get ID or fallback to phone
                wallet_id = resp.get("id") or phone
                user.bafoka_wallet_id = wallet_id
                db.session.add(user)
                db.session.commit()
            except Exception as e:
                LOG.error(f"Failed to create external wallet for {phone}: {e}")
                # We do NOT fail registration; we just log it. User can retry later or admin fix.
        
        return user, created
