# whatsapp-flask-integration.py
# Intégration WhatsApp + Backend Flask + Bafoka Blockchain
import os
import requests
import json
from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Configuration
FLASK_BACKEND_URL = os.getenv("FLASK_BACKEND_URL", "http://localhost:5000")
TWILIO_WEBHOOK_URL = os.getenv("TWILIO_WEBHOOK_URL", "/webhook")

class WhatsAppFlaskIntegration:
    """
    Intégration entre WhatsApp et votre backend Flask existant
    """
    
    def __init__(self):
        self.backend_url = FLASK_BACKEND_URL
    
    def send_to_backend(self, endpoint: str, data: dict) -> dict:
        """
        Envoie une requête à votre backend Flask
        """
        try:
            response = requests.post(
                f"{self.backend_url}{endpoint}",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            return response.json() if response.status_code == 200 else {"error": response.text}
        except Exception as e:
            return {"error": str(e)}
    
    def process_whatsapp_message(self, phone: str, message: str) -> str:
        """
        Traite un message WhatsApp et l'envoie au backend
        """
        message = message.strip()
        lower_message = message.lower()
        
        # Commandes WhatsApp avec intégration backend
        if lower_message.startswith("/register"):
            return self.handle_register(phone, message)
        elif lower_message.startswith("/offer"):
            return self.handle_offer(phone, message)
        elif lower_message.startswith("/search"):
            return self.handle_search(phone, message)
        elif lower_message.startswith("/agree"):
            return self.handle_agree(phone, message)
        elif lower_message.startswith("/me"):
            return self.handle_profile(phone)
        elif lower_message.startswith("/balance"):
            return self.handle_balance(phone)
        elif lower_message.startswith("/complete"):
            return self.handle_complete(phone, message)
        elif lower_message.startswith("/finalize"):
            return self.handle_finalize(phone, message)
        elif lower_message.startswith("/help"):
            return self.get_help_message()
        else:
            return self.get_welcome_message()
    
    def handle_register(self, phone: str, message: str) -> str:
        """
        Gère l'inscription d'un utilisateur
        """
        try:
            # Parse: /register Name | Skill
            payload = message[len("/register"):].strip()
            parts = [p.strip() for p in payload.split("|")]
            name = parts[0] if len(parts) > 0 and parts[0] else None
            skill = parts[1] if len(parts) > 1 and parts[1] else None
            
            if not name:
                return "❌ Usage: /register Nom | Compétence\nExemple: /register Jean Dupont | Design"
            
            # Envoyer au backend
            data = {
                "phone": phone,
                "name": name,
                "skill": skill
            }
            
            result = self.send_to_backend("/api/users/register", data)
            
            if "error" not in result:
                return f"✅ Inscription réussie!\n👤 Nom: {name}\n🛠️ Compétence: {skill or 'Non spécifiée'}\n💰 Solde Bafoka: 1000 BAFOKA\n🔗 Adresse: {result.get('bafoka_address', 'En cours...')}"
            else:
                return f"❌ Erreur d'inscription: {result['error']}"
                
        except Exception as e:
            return f"❌ Erreur: {str(e)}"
    
    def handle_offer(self, phone: str, message: str) -> str:
        """
        Gère la création d'une offre de service
        """
        try:
            # Parse: /offer Description | Titre | Heures
            payload = message[len("/offer"):].strip()
            parts = [p.strip() for p in payload.split("|")]
            
            if len(parts) < 1:
                return "❌ Usage: /offer Description | Titre | Heures\nExemple: /offer Design de logo professionnel | Logo Design | 3"
            
            description = parts[0]
            title = parts[1] if len(parts) > 1 else None
            hours = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 1
            
            # Calculer le coût en Bafoka (1 heure = 100 Bafoka)
            bafoka_cost = hours * 100
            
            # Envoyer au backend
            data = {
                "phone": phone,
                "description": description,
                "title": title,
                "hours": hours,
                "bafoka_cost": bafoka_cost
            }
            
            result = self.send_to_backend("/api/offers", data)
            
            if "error" not in result:
                return f"✅ Offre créée!\n🆔 ID: {result.get('id')}\n📝 Titre: {title or 'Non spécifié'}\n⏱️ Heures: {hours}h\n💰 Coût: {bafoka_cost} BAFOKA\n📋 Description: {description[:50]}..."
            else:
                return f"❌ Erreur création offre: {result['error']}"
                
        except Exception as e:
            return f"❌ Erreur: {str(e)}"
    
    def handle_search(self, phone: str, message: str) -> str:
        """
        Gère la recherche d'offres
        """
        try:
            # Parse: /search mot-clé
            keyword = message[len("/search"):].strip()
            
            if not keyword:
                return "❌ Usage: /search <mot-clé>\nExemple: /search design"
            
            # Envoyer au backend
            result = self.send_to_backend(f"/api/offers?q={keyword}", {})
            
            if "error" not in result:
                offers = result
                if not offers:
                    return f"🔍 Aucune offre trouvée pour '{keyword}'"
                
                response = f"🔍 Offres trouvées pour '{keyword}':\n\n"
                for offer in offers[:5]:  # Limiter à 5 résultats
                    response += f"🆔 {offer['id']} | {offer['title'] or '—'} | ⏱️ {offer.get('hours', 1)}h | 💰 {offer.get('bafoka_cost', 0)} BAFOKA\n"
                    response += f"📋 {offer['desc'][:60]}...\n\n"
                
                return response
            else:
                return f"❌ Erreur recherche: {result['error']}"
                
        except Exception as e:
            return f"❌ Erreur: {str(e)}"
    
    def handle_agree(self, phone: str, message: str) -> str:
        """
        Gère la création d'un accord
        """
        try:
            # Parse: /agree offer_id
            offer_id = message[len("/agree"):].strip()
            
            if not offer_id.isdigit():
                return "❌ Usage: /agree <ID_offre>\nExemple: /agree 123"
            
            # Envoyer au backend
            data = {
                "offer_id": int(offer_id),
                "requester_phone": phone
            }
            
            result = self.send_to_backend("/api/agreements", data)
            
            if "error" not in result:
                return f"✅ Accord créé!\n🆔 ID Accord: {result.get('agreement_id')}\n📊 Statut: {result.get('status')}\n💰 Coût: {result.get('bafoka_cost', 0)} BAFOKA\n\n📋 Vérifiez votre solde avec /balance"
            else:
                return f"❌ Erreur création accord: {result['error']}"
                
        except Exception as e:
            return f"❌ Erreur: {str(e)}"
    
    def handle_profile(self, phone: str) -> str:
        """
        Affiche le profil utilisateur
        """
        try:
            # Envoyer au backend
            result = self.send_to_backend(f"/api/users/profile?phone={phone}", {})
            
            if "error" not in result:
                user = result
                return f"👤 Profil Utilisateur\n📱 Téléphone: {user['phone']}\n👤 Nom: {user['name'] or 'Non défini'}\n🛠️ Compétence: {user['skill'] or 'Non définie'}\n💰 Solde Bafoka: {user.get('bafoka_balance', 0)} BAFOKA\n🔗 Adresse: {user.get('bafoka_address', 'Non enregistrée')}\n📅 Créé le: {user.get('created_at', 'N/A')}"
            else:
                return f"❌ Erreur profil: {result['error']}"
                
        except Exception as e:
            return f"❌ Erreur: {str(e)}"
    
    def handle_balance(self, phone: str) -> str:
        """
        Affiche le solde Bafoka
        """
        try:
            # Envoyer au backend
            result = self.send_to_backend(f"/api/users/balance?phone={phone}", {})
            
            if "error" not in result:
                balance = result
                return f"💰 Solde Bafoka\n💳 Solde actuel: {balance['balance']} BAFOKA\n🔗 Adresse: {balance.get('bafoka_address', 'Non enregistrée')}\n📊 Statut: {balance.get('status', 'Actif')}"
            else:
                return f"❌ Erreur solde: {result['error']}"
                
        except Exception as e:
            return f"❌ Erreur: {str(e)}"
    
    def handle_complete(self, phone: str, message: str) -> str:
        """
        Marque un accord comme complété
        """
        try:
            # Parse: /complete agreement_id
            agreement_id = message[len("/complete"):].strip()
            
            if not agreement_id.isdigit():
                return "❌ Usage: /complete <ID_accord>\nExemple: /complete 123"
            
            # Envoyer au backend
            data = {
                "agreement_id": int(agreement_id),
                "phone": phone,
                "action": "complete"
            }
            
            result = self.send_to_backend(f"/api/agreements/{agreement_id}/complete", data)
            
            if "error" not in result:
                return f"✅ Accord marqué comme complété!\n🆔 ID: {agreement_id}\n📊 Statut: Complété\n\n💡 Utilisez /finalize {agreement_id} 5 4 pour finaliser avec des ratings"
            else:
                return f"❌ Erreur: {result['error']}"
                
        except Exception as e:
            return f"❌ Erreur: {str(e)}"
    
    def handle_finalize(self, phone: str, message: str) -> str:
        """
        Finalise un accord avec des ratings
        """
        try:
            # Parse: /finalize agreement_id provider_rating receiver_rating
            payload = message[len("/finalize"):].strip()
            parts = payload.split()
            
            if len(parts) < 3:
                return "❌ Usage: /finalize <ID_accord> <rating_provider> <rating_receiver>\nExemple: /finalize 123 5 4"
            
            agreement_id = parts[0]
            provider_rating = int(parts[1])
            receiver_rating = int(parts[2])
            
            if not agreement_id.isdigit():
                return "❌ ID d'accord invalide"
            
            if not (1 <= provider_rating <= 5) or not (1 <= receiver_rating <= 5):
                return "❌ Les ratings doivent être entre 1 et 5"
            
            # Envoyer au backend
            data = {
                "agreement_id": int(agreement_id),
                "phone": phone,
                "provider_rating": provider_rating,
                "receiver_rating": receiver_rating,
                "action": "finalize"
            }
            
            result = self.send_to_backend(f"/api/agreements/{agreement_id}/finalize", data)
            
            if "error" not in result:
                return f"🎉 Accord finalisé!\n🆔 ID: {agreement_id}\n⭐ Rating Provider: {provider_rating}/5\n⭐ Rating Receiver: {receiver_rating}/5\n💰 Bafoka transférés: {result.get('bafoka_transferred', 0)}\n🔗 Transaction: {result.get('tx_hash', 'N/A')}"
            else:
                return f"❌ Erreur: {result['error']}"
                
        except Exception as e:
            return f"❌ Erreur: {str(e)}"
    
    def get_help_message(self) -> str:
        """
        Affiche l'aide des commandes
        """
        return """🤖 Troc-Service WhatsApp Bot - Aide

📝 **Commandes disponibles:**

👤 **Gestion de compte:**
/register Nom | Compétence - S'inscrire
/me - Voir mon profil
/balance - Voir mon solde Bafoka

💼 **Offres de service:**
/offer Description | Titre | Heures - Créer une offre
/search mot-clé - Rechercher des services
/agree ID_offre - Accepter une offre

📋 **Gestion des accords:**
/complete ID_accord - Marquer comme complété
/finalize ID_accord 5 4 - Finaliser avec ratings

💰 **Système Bafoka:**
• 1000 BAFOKA offerts à l'inscription
• 1 heure de service = 100 BAFOKA
• Transactions automatiques sur la blockchain

💡 **Exemples:**
/register Jean Dupont | Design
/offer Logo professionnel | Logo Design | 3
/search design
/agree 123
/complete 123
/finalize 123 5 4

🔗 Votre solde et transactions sont gérés automatiquement sur la blockchain Bafoka!"""
    
    def get_welcome_message(self) -> str:
        """
        Message de bienvenue
        """
        return """🤝 Bienvenue sur Troc-Service!

La marketplace d'échange de services sans argent, utilisant la blockchain Bafoka.

💡 Tapez /help pour voir toutes les commandes disponibles
👤 Tapez /register Nom | Compétence pour commencer

💰 Vous recevrez automatiquement 1000 BAFOKA à l'inscription!

Comment puis-je vous aider aujourd'hui?"""

# Instance globale
whatsapp_integration = WhatsAppFlaskIntegration()

@app.route(TWILIO_WEBHOOK_URL, methods=["POST"])
def webhook():
    """
    Webhook Twilio pour WhatsApp
    """
    try:
        # Récupérer les données Twilio
        from_phone = request.values.get("From", "").strip()
        body = request.values.get("Body", "").strip()
        
        if not from_phone:
            return "Erreur: Pas d'information d'expéditeur"
        
        # Traiter le message
        response_text = whatsapp_integration.process_whatsapp_message(from_phone, body)
        
        # Créer la réponse TwiML
        resp = MessagingResponse()
        resp.message(response_text)
        
        return str(resp)
        
    except Exception as e:
        # En cas d'erreur, envoyer un message d'aide
        resp = MessagingResponse()
        resp.message(f"❌ Erreur: {str(e)}\n\n💡 Tapez /help pour voir les commandes disponibles.")
        return str(resp)

@app.route("/health", methods=["GET"])
def health_check():
    """
    Vérification de santé du service
    """
    return jsonify({
        "status": "OK",
        "service": "WhatsApp Flask Integration",
        "backend_url": FLASK_BACKEND_URL,
        "timestamp": "2025-08-27"
    })

if __name__ == "__main__":
    port = int(os.getenv("PORT", 3000))
    print(f"🚀 WhatsApp Flask Integration Server démarré sur le port {port}")
    print(f"🔗 Backend Flask: {FLASK_BACKEND_URL}")
    print(f"📱 Webhook WhatsApp: {TWILIO_WEBHOOK_URL}")
    print(f"🤖 Bot: Troc-Service avec intégration Bafoka")
    
    app.run(host="0.0.0.0", port=port, debug=True)
