# app.py
import os
from flask import Flask, request, jsonify, current_app
from dotenv import load_dotenv
from twilio.twiml.messaging_response import MessagingResponse

load_dotenv()

from db import db
import core_logic as core
from models import User, Offer, Agreement
# chain placeholder
import chain

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///whatsapp_app.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route("/webhook", methods=["POST"])
    def webhook():
        from_phone = request.values.get("From", "").strip()
        body = request.values.get("Body", "").strip()
        resp = MessagingResponse()

        if not from_phone:
            resp.message("No sender info.")
            return str(resp)

        # Normalize phone (twilio uses "whatsapp:+123")
        phone = from_phone

        # quick register on any message
        core.register_user(phone)

        # PARSE COMMANDS
        txt = body.strip()
        low = txt.lower()

        if low.startswith("/register"):
            # format: /register Name | Skill
            payload = txt[len("/register"):].strip()
            parts = [p.strip() for p in payload.split("|")]
            name = parts[0] if len(parts) > 0 and parts[0] else None
            skill = parts[1] if len(parts) > 1 and parts[1] else None
            user, created = core.register_user_be1(phone, name=name, skill=skill)
            if created:
                resp.message(f"Registered ✅\nName: {user.name}\nSkill: {user.skill or '—'}")
            else:
                resp.message(f"Updated profile ✅\nName: {user.name}\nSkill: {user.skill or '—'}")
            return str(resp)

        if low.startswith("/offer"):
            payload = txt[len("/offer"):].strip()
            parts = [p.strip() for p in payload.split("|")]
            if len(parts) < 1:
                resp.message("Usage: /offer description | optional title | optional price")
                return str(resp)
            description = parts[0]
            title = parts[1] if len(parts) > 1 else None
            price = float(parts[2]) if len(parts) > 2 and parts[2] else 0.0
            offer = core.create_offer_for_user(phone, description, title=title, price=price)
            resp.message(f"Offer created ✅\nID:{offer.id}\nTitle:{offer.title}\nPrice:{offer.price}")
            return str(resp)

        if low.startswith("/search"):
            payload = txt[len("/search"):].strip()
            if not payload:
                resp.message("Usage: /search <keyword>")
                return str(resp)
            offers = core.find_offers_by_keyword(payload)
            if not offers:
                resp.message("No open offers found.")
                return str(resp)
            lines = []
            for o in offers:
                lines.append(f"ID:{o.id} | {o.title or '—'} | ${o.price} | Owner:{o.owner.phone}\n{o.description[:80]}")
            resp.message("Found offers:\n\n" + "\n\n".join(lines))
            return str(resp)

        if low.startswith("/agree"):
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
            # Optionally call chain.create_agreement_on_chain here or schedule background job
            # mock chain call for now:
            tx = chain.create_agreement_on_chain(ag.id, ag.offer.id, requester_addr="0xMOCK")
            ag.chain_tx = tx.get("tx_hash")
            ag.status = "created_on_chain"
            from db import db as _db
            _db.session.commit()
            resp.message(f"Agreement created (db id: {ag.id}). On-chain tx: {ag.chain_tx}")
            return str(resp)

        if low.startswith("/me"):
            user = core.get_user_by_phone(phone)
            if not user:
                resp.message("No user record.")
            else:
                resp.message(f"Registered: {user.phone}\nName: {user.name or '—'}\nSkill: {user.skill or '—'}\nOffers: {len(user.offers)}")
            return str(resp)

        # fallback help
        resp.message("Commands:\n/offer description | title | price\n/search <keyword>\n/agree <offer_id>\n/me")
        return str(resp)

    # Simple JSON APIs for BE1 to call if preferred
    @app.route("/api/offers", methods=["GET", "POST"])
    def api_offers():
        if request.method == "GET":
            q = request.args.get("q", "")
            if not q:
                offers = Offer.query.filter_by(status="open").limit(50).all()
            else:
                offers = core.find_offers_by_keyword(q)
            return jsonify([{"id":o.id,"title":o.title,"desc":o.description,"price":o.price,"owner_phone":o.owner.phone} for o in offers])
        data = request.get_json() or {}
        phone = data.get("phone")
        description = data.get("description","")
        title = data.get("title")
        price = float(data.get("price",0))
        offer = core.create_offer_for_user(phone, description, title=title, price=price)
        return jsonify({"id":offer.id,"title":offer.title,"owner_phone":offer.owner.phone})

    @app.route("/api/agreements", methods=["POST"])
    def api_create_agreement():
        data = request.get_json() or {}
        offer_id = int(data.get("offer_id"))
        requester_phone = data.get("requester_phone")
        ag = core.initiate_agreement(offer_id, requester_phone)
        return jsonify({"agreement_id":ag.id, "status":ag.status})

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
