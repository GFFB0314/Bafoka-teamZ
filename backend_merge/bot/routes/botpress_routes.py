# bot/routes/botpress_routes.py
from flask import Blueprint, request, jsonify, current_app
from bot.services.transcription_service import TranscriptionService
from bot.services.user_service import UserService
from bot.services.market_service import MarketService
from bot.services.wallet_service import WalletService
import logging

botpress_bp = Blueprint('botpress', __name__, url_prefix='/api/v1/botpress')
LOG = logging.getLogger(__name__)

# Helper to format response
def format_response(text: str, audio_rel_path: str = None):
    # Construct full audio URL if path exists
    audio_url = None
    if audio_rel_path:
        # Assuming http for dev; use https in prod
        base_url = request.host_url.rstrip("/")
        audio_url = f"{base_url}/static/{audio_rel_path}"
    
    return jsonify({
        "text": text,
        "audio_url": audio_url
    })

def process_command_logic(phone: str, text: str) -> str:
    """Interpret text command and execute service logic."""
    parts = text.strip().split()
    if not parts: return "I didn't hear a command."
    cmd = parts[0].lower()

    try:
        if cmd == "/register":
            # Format: /register BAMEKA | Name | Skill
            content = " ".join(parts[1:])
            if "|" not in content: return "Usage: /register COMMUNITY | Name | Skill"
            sub = [s.strip() for s in content.split("|")]
            if len(sub) < 3: return "Usage: /register COMMUNITY | Name | Skill"
            
            user, created = UserService.register_user(phone, sub[1], sub[2], sub[0])
            bal = WalletService.get_balance(phone).get("balance", 0)
            return f"Welcome {user.name}! Your {user.community} wallet is ready. Balance: {bal} {user.bafoka_local_name}"

        elif cmd == "/offer":
            # Format: /offer Title | Description | Price
            content = " ".join(parts[1:])
            if "|" not in content: return "Usage: /offer Title | Description | Price"
            sub = [s.strip() for s in content.split("|")]
            price = float(sub[2]) if len(sub) >= 3 else 0
            
            offer = MarketService.create_offer(phone, sub[1], sub[0], price)
            return f"Offer #{offer.id} created: {offer.title} for {offer.price}"

        elif cmd == "/search":
            keyword = " ".join(parts[1:])
            user = UserService.get_user_by_phone(phone)
            # Filter by user's community if registered
            comm = user.community if user else None
            offers = MarketService.find_offers(keyword, community=comm)
            if not offers: return f"No offers found for '{keyword}'."
            return "\n".join([f"#{o.id} {o.title}: {o.price}" for o in offers[:5]])

        elif cmd == "/balance":
            user = UserService.get_user_by_phone(phone)
            if not user: return "You are not registered."
            res = WalletService.get_balance(phone)
            ext_bal = res.get("balance", "N/A")
            return f"Local: {user.bafoka_balance}. Bafoka Network: {ext_bal} {user.bafoka_local_name}"

        elif cmd == "/transfer":
            # Format: /transfer ReceiverPhone Amount
            if len(parts) < 3: return "Usage: /transfer PHONE AMOUNT"
            res = WalletService.transfer(phone, parts[1], int(parts[2]))
            return f"Transfer successful. TX: {res.get('tx_id')}"

        elif cmd == "/agree":
            # Format: /agree OfferID
            if len(parts) < 2: return "Usage: /agree OFFER_ID"
            try:
                offer_id = int(parts[1])
                ag = MarketService.initiate_agreement(offer_id, phone)
                return f"Agreement initiated for Offer #{offer_id}. Status: {ag.status}"
            except ValueError:
                return "Invalid Offer ID."
        
        else:
            return f"Unknown command: {cmd}"

    except Exception as e:
        LOG.error(f"Command execution error: {e}")
        return f"Error executing command: {str(e)}"

@botpress_bp.route('/voice', methods=['POST'])
def handle_voice():
    """
    Main entry point for Botpress Voice.
    Input: { "phone": "...", "audio_url": "..." }
    Output: { "text": "...", "audio_url": "..." }
    """
    data = request.json or {}
    phone = data.get("phone")
    audio_url = data.get("audio_url")

    if not phone or not audio_url:
        return jsonify({"error": "Missing phone or audio_url"}), 400

    start_text = "Processing your voice command..."
    # Optionally we could return early, but Botpress likely waits for sync response or callback
    
    try:
        ts = TranscriptionService(current_app.config['AUDIO_UPLOAD_DIR'])
        
        # 1. Transcribe
        transcribed_text = ts.process_incoming_audio_url(audio_url)
        LOG.info(f"User {phone} said: {transcribed_text}")
        
        # 2. Execute Command (Check if text starts with command-like patterns or generic NLP)
        # For now, treat transcription as direct command input logic, maybe requiring regex flexibility later
        # Making simple heuristic: If user says "register", prepend /register
        
        # Simple keywords to command mapper for voice friendliness
        lower = transcribed_text.lower()
        processed_cmd = transcribed_text
        if "register" in lower and "/" not in lower: processed_cmd = "/register " + transcribed_text.replace("register", "", 1)
        elif "balance" in lower and "/" not in lower: processed_cmd = "/balance"
        elif "offer" in lower and "/" not in lower: processed_cmd = "/offer " + transcribed_text.replace("offer", "", 1)
        elif "search" in lower and "/" not in lower: processed_cmd = "/search " + transcribed_text.replace("search", "", 1)
        
        response_text = process_command_logic(phone, processed_cmd)
        
        # 3. TTS
        audio_file = ts.generate_response_audio(response_text)
        
        return format_response(response_text, audio_file)

    except Exception as e:
        LOG.exception("Voice handling failed")
        return jsonify({"error": str(e)}), 500

@botpress_bp.route('/command', methods=['POST'])
def handle_command():
    """
    Entry point for Text commands.
    Input: { "phone": "...", "text": "..." }
    """
    data = request.json or {}
    phone = data.get("phone")
    text = data.get("text")
    
    if not phone or not text:
        return jsonify({"error": "Missing phone or text"}), 400
        
    response_text = process_command_logic(phone, text)
    return format_response(response_text)
