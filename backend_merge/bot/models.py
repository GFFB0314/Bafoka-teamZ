# bot/models.py
from .db import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=True)
    skill = db.Column(db.String(120), nullable=True)
    community = db.Column(db.String(120), nullable=True)
    
    # Bafoka specifics
    bafoka_wallet_id = db.Column(db.String(200), nullable=True)
    bafoka_local_name = db.Column(db.String(120), nullable=True) # e.g. MUNKAP
    bafoka_balance = db.Column(db.Integer, default=0, nullable=False) # Local consistency check

    # Relationships
    offers = db.relationship('Offer', backref='owner', lazy=True, cascade="all, delete-orphan")
    agreements_requested = db.relationship('Agreement', backref='requester', lazy=True)

class Offer(db.Model):
    __tablename__ = 'offers'

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    price = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='open') # open, matched, closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    agreements = db.relationship('Agreement', backref='offer', lazy=True, cascade="all, delete-orphan")

class Agreement(db.Model):
    __tablename__ = 'agreements'

    id = db.Column(db.Integer, primary_key=True)
    offer_id = db.Column(db.Integer, db.ForeignKey('offers.id'), nullable=False)
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='pending') # pending, fulfilled, disputed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Metadata for execution
    chain_tx = db.Column(db.String(200), nullable=True)

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    tx_id = db.Column(db.String(120), nullable=True, unique=True) # External Bafoka TX ID
    from_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    to_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    amount = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    _metadata = db.Column(db.Text, nullable=True) # JSON store for extra info
    reverted = db.Column(db.Boolean, default=False)
