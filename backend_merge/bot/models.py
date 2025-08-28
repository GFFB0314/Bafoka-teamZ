# models.py
from datetime import datetime
from .db import db

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(80), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=True)
    skill = db.Column(db.String(120), nullable=True)

    community = db.Column(db.String(120), nullable=True)
    bafoka_wallet_id = db.Column(db.String(200), nullable=True)
    bafoka_local_name = db.Column(db.String(120), nullable=True)

    # Start local mirror at 0 — we'll add 1000 only when external credit succeeds.
    bafoka_balance = db.Column(db.Integer, default=0, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    offers = db.relationship("Offer", back_populates="owner", cascade="all, delete-orphan")
    requests = db.relationship("Agreement", back_populates="requester", foreign_keys='Agreement.requester_id')

    @property
    def whatsapp_number(self):
        return self.phone


class Offer(db.Model):
    __tablename__ = "offers"
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(30), default="open", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    owner = db.relationship("User", back_populates="offers")
    agreements = db.relationship("Agreement", back_populates="offer", cascade="all, delete-orphan")


class Agreement(db.Model):
    __tablename__ = "agreements"
    id = db.Column(db.Integer, primary_key=True)
    offer_id = db.Column(db.Integer, db.ForeignKey("offers.id"), nullable=False)
    requester_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(30), default="pending", nullable=False)
    chain_tx = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    offer = db.relationship("Offer", back_populates="agreements")
    requester = db.relationship("User", back_populates="requests")


class Transaction(db.Model):
    __tablename__ = "bafoka_transactions"
    id = db.Column(db.Integer, primary_key=True)
    tx_id = db.Column(db.String(200), nullable=True, index=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    to_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    amount = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default="pending")
    _metadata = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    reverted = db.Column(db.Boolean, default=False, nullable=False)

    from_user = db.relationship("User", foreign_keys=[from_user_id])
    to_user = db.relationship("User", foreign_keys=[to_user_id])
