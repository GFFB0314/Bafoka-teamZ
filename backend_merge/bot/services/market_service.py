# bot/services/market_service.py
from bot.models import Offer, Agreement, User
from bot.db import db
from bot.services.user_service import UserService
import logging

LOG = logging.getLogger(__name__)

class MarketService:
    @staticmethod
    def create_offer(phone: str, description: str, title: str = "", price: float = 0.0) -> Offer:
        user = UserService.get_user_by_phone(phone)
        if not user or not user.community:
            raise ValueError("User must be registered with a community before creating offers")
        
        offer = Offer(
            owner=user,
            title=(title or ""),
            description=description,
            price=price,
            status="open"
        )
        db.session.add(offer)
        db.session.commit()
        return offer

    @staticmethod
    def find_offers(keyword: str, community: str = None, limit: int = 20):
        """
        Search for offers by keyword.
        Optionally filter by community (canonicalized).
        """
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
            canon = UserService.canonicalize_community(community)
            if canon:
                query = query.filter(User.community == canon)
            else:
                return [] # Invalid community filter -> empty result

        return query.order_by(Offer.created_at.desc()).limit(limit).all()

    @staticmethod
    def initiate_agreement(offer_id: int, requester_phone: str) -> Agreement:
        offer = Offer.query.get(offer_id)
        if not offer:
            raise ValueError("Offer not found")
        
        requester = UserService.get_user_by_phone(requester_phone)
        if not requester or not requester.community:
            raise ValueError("Requester must be registered with a community")
            
        if not offer.owner or not offer.owner.community:
            raise ValueError("Offer owner has no community set")
            
        if requester.community != offer.owner.community:
            raise ValueError("Users must belong to the same community for agreements")
            
        ag = Agreement(
            offer=offer,
            requester=requester,
            status="pending"
        )
        # We might want to lock the offer or keep it open? Old logic set it to 'matched'
        offer.status = "matched" 
        
        db.session.add(ag)
        db.session.commit()
        return ag
