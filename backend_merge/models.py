# models.py
from datetime import datetime
from db import db

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    # single canonical column name: phone (store Twilio "whatsapp:+...") 
    phone = db.Column(db.String(80), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=True)
    skill = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # relationships
    offers = db.relationship("Offer", back_populates="owner", cascade="all, delete-orphan")
    requests = db.relationship("Agreement", back_populates="requester", foreign_keys="Agreement.requester_id")

    @property
    def whatsapp_number(self):
        # Backwards compatibility for BE1 code referencing whatsapp_number
        return self.phone

class Offer(db.Model):
    __tablename__ = "offers"
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(30), default="open", nullable=False)  # open, matched, pending
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
