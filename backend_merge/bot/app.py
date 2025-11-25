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
    from . import blockchain_utils as web3  # placeholder for on-chain calls
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
    from bot import blockchain_utils as web3  # placeholder for on-chain calls
    try:
        from bot.bafoka_client import get_balance as bafoka_get_balance
    except Exception:
        bafoka_get_balance = None

try:
    from . import voice_utils
except ImportError:
    from bot import voice_utils


LOG = logging.getLogger("troc_service")
LOG.setLevel(logging.INFO)


def normalize_phone(raw: str) -> str:
    """Normalize phone string from Twilio or user input.
    Keeps Twilio format 'whatsapp:+2376...' if present, else returns stripped string.
    """
    if not raw:
        return raw
    if raw.startswith("whatsapp:"):
        return raw.replace("whatsapp:", "")
    return raw.strip()


def process_command(phone: str, text: str) -> str:
    """
    Core text processing logic with NLU integration.
    Used by both Twilio webhook and Voice API.
    """
    if not text:
        return "Please say something or send a command."
    
    # NLU Integration: Interpret natural language
    try:
        from . import nlu
    except ImportError:
        from bot import nlu
        
    # Enhance command with NLU
    interpreted_text = nlu.enhance_command_with_nlu(text, phone)
    
    # If NLU returned a helpful message (not a command), return it directly
    if not interpreted_text.startswith('/'):
        return interpreted_text
    
    parts = interpreted_text.strip().split()
    cmd = parts[0].lower()
    
    if cmd in ["/start", "hi", "hello", "bonjour"]:
        return "Welcome to Troc-Service! Commands:\n/register <COMMUNITY> | <Name> | <Skill>\n/offer <Title> | <Desc> | <Price>\n/search <Keyword>\n/balance\n/transfer <Phone> <Amount>"

    if cmd == "/register":
        # /register BAMEKA | Jean | Farming
        try:
            content = " ".join(parts[1:])
            if "|" in content:
                # Split by pipe
                subparts = [s.strip() for s in content.split("|")]
                if len(subparts) >= 3:
                    comm, name, skill = subparts[0], subparts[1], subparts[2]
                    user, created = core.register_user(phone, name=name, skill=skill, community=comm)
                    return f"Welcome {name}! Wallet created. Balance: {user.bafoka_balance} {user.bafoka_local_name}"
            return "Usage: /register <COMMUNITY> | <Name> | <Skill>"
        except Exception as e:
            return f"Error: {str(e)}"

    if cmd == "/balance":
        user = core.get_user_by_phone(phone)
        if not user:
            return "User not found. /register first."
        
        local = user.bafoka_balance
        ext_msg = ""
        if bafoka_get_balance:
            try:
                ext = bafoka_get_balance(user.phone)
                ext_msg = f"\nReal Bafoka: {ext.get('balance')} {ext.get('currency')}"
            except:
                ext_msg = "\n(Bafoka API unavailable)"
        return f"Local Balance: {local} {user.bafoka_local_name}{ext_msg}"

    if cmd == "/transfer":
        # /transfer +237... 100
        try:
            if len(parts) < 3:
                return "Usage: /transfer <Phone> <Amount>"
            to_phone = normalize_phone(parts[1])
            amount = int(parts[2])
            res = core.transfer_bafoka(phone, to_phone, amount)
            return f"Transfer successful! TX: {res['tx_id']}"
        except Exception as e:
            return f"Transfer failed: {str(e)}"

    if cmd == "/offer":
        # /offer Selling Maize | Fresh harvest | 5000
        try:
            content = " ".join(parts[1:])
            if "|" in content:
                subparts = [s.strip() for s in content.split("|")]
                if len(subparts) >= 3:
                    title, desc, price = subparts[0], subparts[1], float(subparts[2])
                    off = core.create_offer_for_user(phone, desc, title=title, price=price)
                    return f"Offer created! ID: {off.id}"
            return "Usage: /offer <Title> | <Desc> | <Price>"
        except Exception as e:
            return f"Error: {str(e)}"

    if cmd == "/search":
        try:
            keyword = " ".join(parts[1:])
            offers = core.find_offers_by_keyword(keyword)
            if not offers:
                return "No offers found."
            return "\n".join([f"#{o.id} {o.title}: {o.price} ({o.owner.phone})" for o in offers])
        except Exception as e:
            return f"Error: {str(e)}"

    if cmd == "/agree":
        try:
            offer_id = int(parts[1])
            ag = core.initiate_agreement(offer_id, phone)
            return f"Agreement initiated for Offer #{offer_id}. Status: {ag.status}"
        except Exception as e:
            return f"Error: {str(e)}"

    return "Unknown command. Try /start"


def twilio_chatbot_webhook():
    """
    Handles incoming Twilio/WhatsApp messages.
    """
    from_number = request.values.get("From", "")
    body = request.values.get("Body", "")
    phone = normalize_phone(from_number)
    
    response_text = process_command(phone, body)
    
    resp = MessagingResponse()
    resp.message(response_text)
    return str(resp)


def create_app():
    app = Flask(__name__, static_folder='../static')
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
        if bafoka_get_balance:
            try:
                # New client uses phone number
                external = bafoka_get_balance(user.phone).get("balance")
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
        
        # best-effort on-chain call; don't block user if chain fails
        try:
            tx = web3.create_agreement_on_chain(ag.id, ag.offer.id, requester_addr="0xMOCK")
            ag.chain_tx = tx.get("tx_hash")
            ag.status = "created_on_chain"
            db.session.add(ag)
            db.session.commit()
            # Try to confirm on chain
            if ag.chain_tx:
                confirm_tx = web3.confirm_agreement_on_chain(ag.chain_tx)
                LOG.info("Agreement confirmation result: %s", confirm_tx)
        except Exception as e:
            LOG.info("Chain operations failed (non-blocking): %s", e)
            
        return jsonify({"agreement_id": ag.id, "status": ag.status})

    @app.route("/api/me", methods=["GET"])
    def api_me():
        phone = normalize_phone(request.args.get("phone") or "")
        if not phone:
            return jsonify({"error": "phone required"}), 400
        user = core.get_user_by_phone(phone)
        if not user:
            return jsonify({"error": "user not found"}), 404
        return jsonify({
            "phone": user.phone,
            "name": user.name,
            "skill": user.skill,
            "community": user.community,
            "bafoka_balance": user.bafoka_balance,
            "currency": user.bafoka_local_name,
            "offers_count": len(user.offers)
        })

    @app.route("/api/delete", methods=["POST"])
    def api_delete():
        data = request.get_json() or {}
        phone = normalize_phone(data.get("phone") or "")
        if not phone:
            return jsonify({"error": "phone required"}), 400
        try:
            ok, info = core.delete_user(phone)
            if ok:
                return jsonify({"success": True, "message": "Account deleted"})
            else:
                return jsonify({"success": False, "message": info}), 400
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/voice/process", methods=["POST"])
    def api_voice_process():
        """
        Enhanced Voice Processing Endpoint for Botpress Integration
        
        Supports:
        1. Audio URL or direct file upload
        2. Flexible output format (audio, text, or both)
        3. Automatic audio format conversion (via ffmpeg)
        4. Command execution with user context
        
        Request (JSON):
        {
          "audio_url": "https://...",  // OR use file upload
          "phone": "+237...",           // User's phone number
          "output_format": "both"       // "audio", "text", or "both" (default: "both")
        }
        
        OR multipart/form-data with 'audio' file field
        
        Response:
        {
          "transcription": "user's spoken text",
          "response_text": "bot's text response",
          "audio_url": "https://.../response.mp3",  // Only if output_format includes audio
          "success": true
        }
        """
        phone = None
        audio_path = None
        output_audio_path = None
        
        try:
            # Parse request - support both JSON and form data
            if request.is_json:
                data = request.get_json() or {}
                audio_url = data.get("audio_url")
                phone = normalize_phone(data.get("phone") or "")
                output_format = data.get("output_format", "both").lower()
                
                if not audio_url:
                    return jsonify({
                        "success": False,
                        "error": "audio_url required in JSON request"
                    }), 400
                
                # Download audio from URL
                LOG.info(f"Downloading audio from URL for {phone}")
                audio_path = voice_utils.download_audio(
                    audio_url, 
                    save_dir=os.path.join(app.static_folder, "audio", "input")
                )
                
            else:
                # Handle file upload
                if 'audio' not in request.files:
                    return jsonify({
                        "success": False,
                        "error": "audio file or audio_url required"
                    }), 400
                
                audio_file = request.files['audio']
                phone = normalize_phone(request.form.get("phone", ""))
                output_format = request.form.get("output_format", "both").lower()
                
                # Save uploaded file
                import uuid
                filename = f"upload_{uuid.uuid4().hex[:8]}{os.path.splitext(audio_file.filename)[1]}"
                audio_path = os.path.join(app.static_folder, "audio", "input", filename)
                os.makedirs(os.path.dirname(audio_path), exist_ok=True)
                audio_file.save(audio_path)
                LOG.info(f"Saved uploaded audio file: {audio_path}")
            
            # Validate output format
            if output_format not in ["audio", "text", "both"]:
                output_format = "both"
            
            LOG.info(f"Processing voice for {phone}, output_format: {output_format}")
            
            # Step 1: Transcribe audio to text (Whisper)
            LOG.info("Transcribing audio with Whisper...")
            transcribed_text = voice_utils.transcribe_audio(audio_path)
            LOG.info(f"Transcription: {transcribed_text}")
            
            if not transcribed_text or not transcribed_text.strip():
                return jsonify({
                    "success": False,
                    "error": "Could not transcribe audio - no speech detected",
                    "transcription": ""
                }), 400
            
            # Step 2: Execute command based on transcribed text
            LOG.info(f"Executing command: {transcribed_text}")
            response_text = process_command(phone, transcribed_text)
            LOG.info(f"Command response: {response_text}")
            
            # Step 3: Prepare response based on output format
            response_data = {
                "success": True,
                "transcription": transcribed_text,
                "response_text": response_text
            }
            
            # Step 4: Generate audio response if needed
            if output_format in ["audio", "both"]:
                LOG.info("Generating audio response with gTTS...")
                audio_rel_path = voice_utils.generate_speech(
                    response_text,
                    save_dir=os.path.join(app.static_folder, "audio", "output")
                )
                
                # Construct full URL for Botpress
                # Use request.host_url for proper URL construction
                audio_full_url = f"{request.host_url}static/audio/output/{os.path.basename(audio_rel_path)}"
                response_data["audio_url"] = audio_full_url
                LOG.info(f"Audio response URL: {audio_full_url}")
            
            # Cleanup input audio file
            try:
                if audio_path and os.path.exists(audio_path):
                    os.remove(audio_path)
                    LOG.info(f"Cleaned up input audio: {audio_path}")
            except Exception as cleanup_error:
                LOG.warning(f"Failed to cleanup input audio: {cleanup_error}")
            
            return jsonify(response_data), 200
            
        except Exception as e:
            LOG.exception("Voice processing failed")
            
            # Cleanup on error
            try:
                if audio_path and os.path.exists(audio_path):
                    os.remove(audio_path)
            except:
                pass
            
            return jsonify({
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }), 500




    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
