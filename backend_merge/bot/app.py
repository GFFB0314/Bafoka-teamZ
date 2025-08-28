# app.py
"""
Main Flask app for Troc-Service:
- preserves your Twilio/WhatsApp chatbot webhook commands
- provides REST endpoints for Bafoka integration and app features
"""

import os
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from twilio.twiml.messaging_response import MessagingResponse
from sqlalchemy import text

load_dotenv()

# Support both package execution (python -m bot.app) and direct script (python bot/app.py)
try:
    from .db import db
    from . import core_logic as core
    from .models import User, Offer, Agreement, Transaction
    from . import chain  # placeholder for on-chain calls
    try:
        from .bafoka_client import get_balance as bafoka_get_balance
    except Exception:
        bafoka_get_balance = None
except ImportError:
    # Fallback for direct script execution
    import sys as _sys, os as _os
    _sys.path.insert(0, _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..")))
    from bot.db import db
    from bot import core_logic as core
    from bot.models import User, Offer, Agreement, Transaction
    from bot import chain  # placeholder for on-chain calls
    try:
        from bot.bafoka_client import get_balance as bafoka_get_balance
    except Exception:
        bafoka_get_balance = None

LOG = logging.getLogger("troc_service")
LOG.setLevel(logging.INFO)


def normalize_phone(raw: str) -> str:
    """Normalize phone string from Twilio or user input.
    Keeps Twilio format 'whatsapp:+2376...' if present, else returns stripped string.
    """
    if not raw:
        return raw
    s = raw.strip()
    # Twilio uses "whatsapp:+12345". If user passed +12345, keep it.
    return s


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///whatsapp_app.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # init db
    db.init_app(app)

    with app.app_context():
        # Quick dev: create tables if missing. Use Alembic in prod.
        db.create_all()
        # Minimal SQLite auto-migration for newly added columns (dev convenience)
        try:
            dburi = app.config.get("SQLALCHEMY_DATABASE_URI", "")
            if dburi.startswith("sqlite"):
                info = db.session.execute(text("PRAGMA table_info('users')")).fetchall()
                cols = {row[1] for row in info}
                if "community" not in cols:
                    db.session.execute(text("ALTER TABLE users ADD COLUMN community VARCHAR(120)"))
                if "bafoka_wallet_id" not in cols:
                    db.session.execute(text("ALTER TABLE users ADD COLUMN bafoka_wallet_id VARCHAR(200)"))
                if "bafoka_local_name" not in cols:
                    db.session.execute(text("ALTER TABLE users ADD COLUMN bafoka_local_name VARCHAR(120)"))
                if "bafoka_balance" not in cols:
                    db.session.execute(text("ALTER TABLE users ADD COLUMN bafoka_balance INTEGER NOT NULL DEFAULT 0"))
                db.session.commit()
        except Exception as e:
            LOG.warning("SQLite auto-migrate skipped/failed: %s", e)

    #
    # ----- Twilio / WhatsApp chatbot webhook (keeps your original handlers) -----
    #
    @app.route("/webhook", methods=["POST"])
    def twilio_chatbot_webhook():
        from_phone = request.values.get("From", "").strip()
        body = request.values.get("Body", "").strip()
        LOG.info("Incoming message: from=%s body=%s", from_phone, body)
        resp = MessagingResponse()

        if not from_phone:
            resp.message("No sender info.")
            return str(resp)

        phone = normalize_phone(from_phone)
        txt = body or ""
        low = txt.lower().strip()

        # Process destructive or identity commands before auto-registration
        # === /delete ===
        if low.startswith("/delete"):
            try:
                ok, info = core.delete_user(phone)
                if ok:
                    resp.message("Your account has been deleted ✅")
                else:
                    resp.message(f"Deletion not performed: {info}")
            except Exception as e:
                resp.message(f"Deletion error: {str(e)}")
            return str(resp)

        # === /register COMMUNITY | Name | Skill ===
        if low.startswith("/register"):
            payload = txt[len("/register"):].strip()
            parts = [p.strip() for p in payload.split("|")]
            if len(parts) < 1 or not parts[0]:
                resp.message("Usage: /register <COMMUNITY> | <Name> | <Skill>\nCommunities: BAMEKA, BATOUFAM, FONDJOMEKWET")
                return str(resp)
            community = parts[0]
            name = parts[1] if len(parts) > 1 and parts[1] else None
            skill = parts[2] if len(parts) > 2 and parts[2] else None
            try:
                user, created = core.register_user(phone, name=name, skill=skill, community=community)
                if created:
                    resp.message(f"Registered ✅\nCommunity: {user.community}\nCurrency: {user.bafoka_local_name}\nName: {user.name}\nSkill: {user.skill or '—'}")
                else:
                    resp.message(f"Updated profile ✅\nCommunity: {user.community}\nCurrency: {user.bafoka_local_name}\nName: {user.name}\nSkill: {user.skill or '—'}")
            except Exception as e:
                resp.message(str(e))
            return str(resp)


        # === /offer ===
        if low.startswith("/offer"):
            # Require registration with community
            u = core.get_user_by_phone(phone)
            if not u or not u.community:
                resp.message("Please register first: /register <COMMUNITY> | <Name> | <Skill>\nCommunities: BAMEKA, BATOUFAM, FONDJOMEKWET")
                return str(resp)
            payload = txt[len("/offer"):].strip()
            parts = [p.strip() for p in payload.split("|")]
            if len(parts) < 1 or not parts[0]:
                resp.message("Usage: /offer description | optional title | optional price")
                return str(resp)
            description = parts[0]
            title = parts[1] if len(parts) > 1 else None
            try:
                price = float(parts[2]) if len(parts) > 2 and parts[2] else 0.0
            except Exception:
                price = 0.0
            try:
                offer = core.create_offer_for_user(phone, description, title=title, price=price)
                resp.message(f"Offer created ✅\nID:{offer.id}\nTitle:{offer.title}\nPrice:{offer.price}")
            except Exception as e:
                resp.message(str(e))
            return str(resp)

        # === /search ===
        if low.startswith("/search"):
            # Require registration to scope search by community
            u = core.get_user_by_phone(phone)
            if not u or not u.community:
                resp.message("Please register first: /register <COMMUNITY> | <Name> | <Skill>\nCommunities: BAMEKA, BATOUFAM, FONDJOMEKWET")
                return str(resp)
            payload = txt[len("/search"):].strip()
            if not payload:
                resp.message("Usage: /search <keyword>")
                return str(resp)
            offers = core.find_offers_by_keyword(payload, community=u.community)
            if not offers:
                resp.message("No open offers found.")
                return str(resp)
            lines = []
            for o in offers:
                lines.append(f"ID:{o.id} | {o.title or '—'} | {o.price} | Owner:{o.owner.phone}\n{o.description[:80]}")
            resp.message("Found offers:\n\n" + "\n\n".join(lines))
            return str(resp)

        # === /agree ===
        if low.startswith("/agree"):
            # Require registration with community
            u = core.get_user_by_phone(phone)
            if not u or not u.community:
                resp.message("Please register first: /register <COMMUNITY> | <Name> | <Skill>\nCommunities: BAMEKA, BATOUFAM, FONDJOMEKWET")
                return str(resp)
            payload = txt[len("/agree"):].strip()
            if not payload.isdigit():
                resp.message("Usage: /agree <offer_id>")
                return str(resp)
            offer_id = int(payload)
            try:
                ag = core.initiate_agreement(offer_id, phone)
            except Exception as e:
                resp.message(str(e))
                return str(resp)
            # best-effort on-chain call; don't block user if chain fails
            try:
                tx = chain.create_agreement_on_chain(ag.id, ag.offer.id, requester_addr="0xMOCK")
                ag.chain_tx = tx.get("tx_hash")
                ag.status = "created_on_chain"
                db.session.add(ag)
                db.session.commit()
            except Exception as e:
                LOG.info("Chain create_agreement_on_chain failed (non-blocking): %s", e)
            resp.message(f"Agreement created (db id: {ag.id}). On-chain tx: {ag.chain_tx or 'n/a'}")
            return str(resp)

        # === /me ===
        if low.startswith("/me"):
            user = core.get_user_by_phone(phone)
            if not user:
                resp.message("No user record.")
            else:
                resp.message(
                    f"Registered: {user.phone}\nName: {user.name or '—'}\nSkill: {user.skill or '—'}\n"
                    f"Offers: {len(user.offers)}\nBalance: {user.bafoka_balance} {user.bafoka_local_name or 'Bafoka'}"
                )
            return str(resp)

        # === /balance (chat) ===
        if low.startswith("/balance") or low.startswith("/solde"):
            user = core.get_user_by_phone(phone)
            if not user or not user.community:
                resp.message("Please register first: /register <COMMUNITY> | <Name> | <Skill>\nCommunities: BAMEKA, BATOUFAM, FONDJOMEKWET")
                return str(resp)
            local_balance = user.bafoka_balance
            if user.bafoka_wallet_id and bafoka_get_balance:
                try:
                    ext = bafoka_get_balance(user.bafoka_wallet_id)
                    ext_bal = ext.get("balance")
                    resp.message(
                        f"Local balance: {local_balance} {user.bafoka_local_name or 'Bafoka'}\nExternal balance: {ext_bal}"
                    )
                except Exception:
                    resp.message(
                        f"Local balance: {local_balance} {user.bafoka_local_name or 'Bafoka'}\nUnable to reach Bafoka API."
                    )
            else:
                resp.message(f"Local balance: {local_balance} {user.bafoka_local_name or 'Bafoka'}")
            return str(resp)

        # === /transfer (chat) ===
        if low.startswith("/transfer") or low.startswith("/pay"):
            # Require registration with community
            u = core.get_user_by_phone(phone)
            if not u or not u.community:
                resp.message("Please register first: /register <COMMUNITY> | <Name> | <Skill>\nCommunities: BAMEKA, BATOUFAM, FONDJOMEKWET")
                return str(resp)
            parts = txt.split()
            if len(parts) < 3:
                resp.message("Usage: /transfer <to_phone> <amount>")
                return str(resp)
            to_phone = normalize_phone(parts[1])
            try:
                amount = int(parts[2])
            except Exception:
                resp.message("Invalid amount; use an integer.")
                return str(resp)
            try:
                res = core.transfer_bafoka(phone, to_phone, amount)
                resp.message(f"Transfer initiated (tx:{res.get('tx_id')}). Status: {res.get('status')}")
            except Exception as e:
                resp.message(f"Transfer error: {str(e)}")
            return str(resp)

        # fallback: help
        resp.message(
            "Commands:\n/register <COMMUNITY> | <Name> | <Skill>\n/offer description | title | price\n/search <keyword>\n"
            "/agree <offer_id>\n/me\n/balance\n/transfer <to_phone> <amount>\n/delete\n"
            "Communities: BAMEKA (MUNKAP), BATOUFAM (MBIP TSWEFAP), FONDJOMEKWET (MBAM)"
        )
        return str(resp)

    # Aliases for Twilio webhook (common misconfigurations)
    @app.route("/", methods=["POST"])
    def root_incoming():
        return twilio_chatbot_webhook()

    @app.route("/sms", methods=["POST"])
    def sms_incoming():
        return twilio_chatbot_webhook()

    @app.route("/whatsapp", methods=["POST"])
    def whatsapp_incoming():
        return twilio_chatbot_webhook()

    @app.route("/webhook", methods=["GET"])
    def twilio_webhook_get():
        return "OK", 200

    #
    # ----- REST endpoints for UI/BE and Bafoka integration -----
    #

    @app.route("/api/offers", methods=["GET", "POST"])
    def api_offers():
        if request.method == "GET":
            q = request.args.get("q", "")
            if not q:
                offers = Offer.query.filter_by(status="open").limit(50).all()
            else:
                offers = core.find_offers_by_keyword(q)
            return jsonify([{"id": o.id, "title": o.title, "desc": o.description, "price": o.price, "owner_phone": o.owner.phone} for o in offers])
        data = request.get_json() or {}
        phone = normalize_phone(data.get("phone") or "")
        description = data.get("description", "")
        title = data.get("title")
        try:
            price = float(data.get("price", 0))
        except Exception:
            price = 0.0
        offer = core.create_offer_for_user(phone, description, title=title, price=price)
        return jsonify({"id": offer.id, "title": offer.title, "owner_phone": offer.owner.phone})

    @app.route("/api/register", methods=["POST"])
    def api_register():
        data = request.get_json() or {}
        phone = normalize_phone(data.get("phone") or "")
        name = data.get("name")
        skill = data.get("skill")
        community = data.get("community")
        local_name = data.get("local_name")
        if not phone:
            return jsonify({"error": "phone required"}), 400
        user, created = core.register_user(phone=phone, name=name, skill=skill, community=community, local_name=local_name)
        return jsonify({
            "id": user.id,
            "phone": user.phone,
            "name": user.name,
            "community": user.community,
            "bafoka_wallet_id": user.bafoka_wallet_id,
            "bafoka_balance": user.bafoka_balance,
            "created": created
        })

    @app.route("/api/transfer", methods=["POST"])
    def api_transfer():
        data = request.get_json() or {}
        from_phone = normalize_phone(data.get("from_phone") or "")
        to_phone = normalize_phone(data.get("to_phone") or "")
        try:
            amount = int(data.get("amount", 0))
        except Exception:
            return jsonify({"ok": False, "error": "amount must be integer"}), 400
        idempotency = data.get("idempotency_key")
        try:
            res = core.transfer_bafoka(from_phone, to_phone, amount, idempotency_key=idempotency)
            return jsonify({"ok": True, **res})
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)}), 400

    @app.route("/api/balance", methods=["GET"])
    def api_balance():
        phone = normalize_phone(request.args.get("phone") or "")
        if not phone:
            return jsonify({"error": "phone required (query param)"}), 400
        user = core.get_user_by_phone(phone)
        if not user:
            return jsonify({"error": "user not found"}), 404
        local = user.bafoka_balance
        external = None
        if user.bafoka_wallet_id and bafoka_get_balance:
            try:
                external = bafoka_get_balance(user.bafoka_wallet_id).get("balance")
            except Exception:
                external = None
        return jsonify({"phone": user.phone, "local_balance": local, "external_balance": external, "currency_name": user.bafoka_local_name or "Bafoka"})

    @app.route("/api/bafoka/webhook", methods=["POST"])
    def api_bafoka_webhook():
        payload = request.get_json() or {}
        data = payload.get("data", {}) or {}
        tx_id = data.get("tx_id") or data.get("transaction_id")
        status = data.get("status")
        if not tx_id or not status:
            return jsonify({"received": False, "reason": "missing tx_id or status"}), 400
        res = core.adjust_balances_on_external_update(tx_id, status, metadata=data)
        if res.get("ok"):
            return jsonify({"received": True, "action": res.get("action"), "status": res.get("status")}), 200
        else:
            return jsonify({"received": False, "error": res.get("error")}), 500

    @app.route("/api/agreements", methods=["POST"])
    def api_create_agreement():
        data = request.get_json() or {}
        offer_id = int(data.get("offer_id"))
        requester_phone = normalize_phone(data.get("requester_phone") or "")
        ag = core.initiate_agreement(offer_id, requester_phone)
        return jsonify({"agreement_id": ag.id, "status": ag.status})

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
