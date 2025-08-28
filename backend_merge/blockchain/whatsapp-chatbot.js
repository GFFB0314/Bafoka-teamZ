// WhatsApp Chatbot for Troc-Service
// This chatbot works directly in WhatsApp without backend logic

class TrocServiceChatbot {
    constructor() {
        this.users = new Map(); // Store user data in memory
        this.offers = new Map(); // Store service offers
        this.agreements = new Map(); // Store agreements
        this.userStates = new Map(); // Track user conversation state
    }

    // Main message handler
    handleMessage(phoneNumber, message) {
        const user = this.getOrCreateUser(phoneNumber);
        const upperMessage = message.toUpperCase().trim();

        // Handle commands
        if (upperMessage === 'HELP' || upperMessage === 'AIDE') {
            return this.getHelpMessage();
        }

        if (upperMessage === 'REGISTER' || upperMessage === 'INSCRIPTION') {
            return this.startRegistration(phoneNumber);
        }

        if (upperMessage === 'PROFILE') {
            return this.showProfile(phoneNumber);
        }

        if (upperMessage === 'MY_OFFERS' || upperMessage === 'MES_OFFRES') {
            return this.showMyOffers(phoneNumber);
        }

        if (upperMessage === 'MY_AGREEMENTS' || upperMessage === 'MES_ACCORDS') {
            return this.showMyAgreements(phoneNumber);
        }

        if (upperMessage.startsWith('OFFER ')) {
            return this.handleOffer(phoneNumber, message);
        }

        if (upperMessage.startsWith('SEARCH ') || upperMessage.startsWith('RECHERCHE ')) {
            return this.handleSearch(phoneNumber, message);
        }

        if (upperMessage.startsWith('NEED ')) {
            return this.handleNeed(phoneNumber, message);
        }

        // Handle conversation flow
        if (this.userStates.has(phoneNumber)) {
            return this.handleConversationFlow(phoneNumber, message);
        }

        // Default welcome message
        return this.getWelcomeMessage();
    }

    // Welcome message
    getWelcomeMessage() {
        return `🤝 Bienvenue sur Troc-Service !
La marketplace d'échange de services sans argent.

Tapez *HELP* pour voir les commandes disponibles.
Tapez *REGISTER* pour commencer votre inscription.`;
    }

    // Help message
    getHelpMessage() {
        return `📋 COMMANDES DISPONIBLES :

*REGISTER* - S'inscrire sur la plateforme
*OFFER* [service] [heures] - Proposer un service
*SEARCH* [service] - Rechercher un service
*NEED* [service] - Indiquer vos besoins
*MY_OFFERS* - Voir vos offres
*MY_AGREEMENTS* - Voir vos accords
*PROFILE* - Voir votre profil
*HELP* - Afficher cette aide

Exemples :
OFFER design logo 3
SEARCH comptabilité
NEED comptabilité`;
    }

    // Start registration
    startRegistration(phoneNumber) {
        this.userStates.set(phoneNumber, 'REGISTER_NAME');
        return `📝 INSCRIPTION TROC-SERVICE

Pour commencer, donnez-moi votre nom complet :`;
    }

    // Handle conversation flow
    handleConversationFlow(phoneNumber, message) {
        const state = this.userStates.get(phoneNumber);
        const user = this.users.get(phoneNumber);

        switch (state) {
            case 'REGISTER_NAME':
                user.name = message;
                this.userStates.set(phoneNumber, 'REGISTER_PHONE');
                return `Merci ${message} !

Maintenant, quel est votre numéro de téléphone ?
(Format: +237 6 XX XX XX XX)`;

            case 'REGISTER_PHONE':
                user.phone = message;
                this.userStates.set(phoneNumber, 'REGISTER_EMAIL');
                return `Parfait ! Votre numéro est enregistré.

Quelle est votre adresse email ?`;

            case 'REGISTER_EMAIL':
                user.email = message;
                this.userStates.set(phoneNumber, 'REGISTER_SERVICES');
                return `Excellent ! Maintenant, dites-moi quels services vous proposez.

Format : *OFFER* [service] [heures]
Exemple : OFFER design graphique 5

Ou tapez *SKIP* pour ajouter plus tard.`;

            case 'REGISTER_SERVICES':
                if (message.toUpperCase() === 'SKIP') {
                    user.services = [];
                } else if (message.toUpperCase().startsWith('OFFER ')) {
                    const serviceInfo = this.parseOfferMessage(message);
                    if (serviceInfo) {
                        user.services = [serviceInfo];
                    }
                }
                this.userStates.set(phoneNumber, 'REGISTER_NEEDS');
                return `Parfait ! Vos services ont été enregistrés.

Maintenant, quels services recherchez-vous ?

Format : *NEED* [service]
Exemple : NEED comptabilité

Ou tapez *SKIP* pour ajouter plus tard.`;

            case 'REGISTER_NEEDS':
                if (message.toUpperCase() === 'SKIP') {
                    user.needs = [];
                } else if (message.toUpperCase().startsWith('NEED ')) {
                    const need = message.substring(5).trim();
                    user.needs = [need];
                }
                
                // Registration complete
                this.userStates.delete(phoneNumber);
                return `🎉 Inscription terminée !

Votre profil Troc-Service a été créé avec succès.

Tapez *PROFILE* pour voir vos informations.
Tapez *OFFER* pour ajouter un service.
Tapez *SEARCH* pour trouver des services.`;

            default:
                this.userStates.delete(phoneNumber);
                return this.getWelcomeMessage();
        }
    }

    // Handle offer command
    handleOffer(phoneNumber, message) {
        const user = this.users.get(phoneNumber);
        if (!user || !user.name) {
            return `❌ Vous devez d'abord vous inscrire.
Tapez *REGISTER* pour commencer.`;
        }

        const offerInfo = this.parseOfferMessage(message);
        if (!offerInfo) {
            return `❌ Format incorrect. Utilisez : OFFER [service] [heures]
Exemple : OFFER design logo 3`;
        }

        // Store the offer
        if (!this.offers.has(phoneNumber)) {
            this.offers.set(phoneNumber, []);
        }
        this.offers.get(phoneNumber).push(offerInfo);

        return `✅ Service enregistré !
Service: ${offerInfo.service}
Heures: ${offerInfo.hours}

Tapez *MY_OFFERS* pour voir vos offres.`;
    }

    // Handle search command
    handleSearch(phoneNumber, message) {
        const searchTerm = message.substring(message.indexOf(' ') + 1).trim();
        if (!searchTerm) {
            return `❌ Veuillez spécifier un service à rechercher.
Exemple : SEARCH design`;
        }

        const results = [];
        for (const [phone, offers] of this.offers) {
            for (const offer of offers) {
                if (offer.service.toLowerCase().includes(searchTerm.toLowerCase())) {
                    const user = this.users.get(phone);
                    results.push({
                        name: user ? user.name : 'Utilisateur',
                        service: offer.service,
                        hours: offer.hours
                    });
                }
            }
        }

        if (results.length === 0) {
            return `🔍 Aucun service trouvé pour "${searchTerm}".
Essayez avec d'autres mots-clés.`;
        }

        let response = `🔍 Services trouvés pour "${searchTerm}":\n\n`;
        results.forEach((result, index) => {
            response += `${index + 1}. ${result.name} - ${result.service} (${result.hours}h)\n`;
        });

        response += `\nPour contacter un prestataire, partagez votre numéro.`;
        return response;
    }

    // Handle need command
    handleNeed(phoneNumber, message) {
        const user = this.users.get(phoneNumber);
        if (!user || !user.name) {
            return `❌ Vous devez d'abord vous inscrire.
Tapez *REGISTER* pour commencer.`;
        }

        const need = message.substring(5).trim();
        if (!need) {
            return `❌ Veuillez spécifier un service dont vous avez besoin.
Exemple : NEED comptabilité`;
        }

        if (!user.needs) user.needs = [];
        user.needs.push(need);

        return `✅ Besoin enregistré : ${need}

Tapez *PROFILE* pour voir tous vos besoins.`;
    }

    // Show user profile
    showProfile(phoneNumber) {
        const user = this.users.get(phoneNumber);
        if (!user || !user.name) {
            return `❌ Vous devez d'abord vous inscrire.
Tapez *REGISTER* pour commencer.`;
        }

        let response = `👤 PROFIL UTILISATEUR\n\n`;
        response += `Nom: ${user.name}\n`;
        response += `Téléphone: ${user.phone || 'Non renseigné'}\n`;
        response += `Email: ${user.email || 'Non renseigné'}\n\n`;

        if (user.services && user.services.length > 0) {
            response += `📤 Services proposés:\n`;
            user.services.forEach(service => {
                response += `- ${service.service} (${service.hours}h)\n`;
            });
            response += `\n`;
        }

        if (user.needs && user.needs.length > 0) {
            response += `🔍 Services recherchés:\n`;
            user.needs.forEach(need => {
                response += `- ${need}\n`;
            });
        }

        return response;
    }

    // Show user's offers
    showMyOffers(phoneNumber) {
        const user = this.users.get(phoneNumber);
        if (!user || !user.name) {
            return `❌ Vous devez d'abord vous inscrire.
Tapez *REGISTER* pour commencer.`;
        }

        const offers = this.offers.get(phoneNumber) || [];
        if (offers.length === 0) {
            return `📤 Vous n'avez pas encore proposé de services.
Tapez *OFFER* [service] [heures] pour en créer un.`;
        }

        let response = `📤 VOS SERVICES PROPOSÉS:\n\n`;
        offers.forEach((offer, index) => {
            response += `${index + 1}. ${offer.service} (${offer.hours}h)\n`;
        });

        return response;
    }

    // Show user's agreements
    showMyAgreements(phoneNumber) {
        const user = this.users.get(phoneNumber);
        if (!user || !user.name) {
            return `❌ Vous devez d'abord vous inscrire.
Tapez *REGISTER* pour commencer.`;
        }

        const agreements = this.agreements.get(phoneNumber) || [];
        if (agreements.length === 0) {
            return `🤝 Vous n'avez pas encore d'accords.
Utilisez *SEARCH* pour trouver des services.`;
        }

        let response = `🤝 VOS ACCORDS:\n\n`;
        agreements.forEach((agreement, index) => {
            response += `${index + 1}. ${agreement.description} avec ${agreement.partner}\n`;
        });

        return response;
    }

    // Parse offer message
    parseOfferMessage(message) {
        const parts = message.split(' ');
        if (parts.length < 3) return null;

        const hours = parseInt(parts[parts.length - 1]);
        if (isNaN(hours) || hours <= 0) return null;

        const service = parts.slice(1, -1).join(' ');
        if (!service) return null;

        return { service, hours };
    }

    // Get or create user
    getOrCreateUser(phoneNumber) {
        if (!this.users.has(phoneNumber)) {
            this.users.set(phoneNumber, {
                phone: phoneNumber,
                name: '',
                email: '',
                services: [],
                needs: []
            });
        }
        return this.users.get(phoneNumber);
    }

    // Reset user state (for testing)
    resetUser(phoneNumber) {
        this.users.delete(phoneNumber);
        this.userStates.delete(phoneNumber);
        this.offers.delete(phoneNumber);
        this.agreements.delete(phoneNumber);
    }
}

// Export for use
module.exports = TrocServiceChatbot;

// Example usage:
/*
const chatbot = new TrocServiceChatbot();

// Simulate WhatsApp messages
console.log(chatbot.handleMessage('+1234567890', 'HELP'));
console.log(chatbot.handleMessage('+1234567890', 'REGISTER'));
console.log(chatbot.handleMessage('+1234567890', 'John Doe'));
console.log(chatbot.handleMessage('+1234567890', '+1234567890'));
console.log(chatbot.handleMessage('+1234567890', 'john@example.com'));
console.log(chatbot.handleMessage('+1234567890', 'OFFER design logo 3'));
console.log(chatbot.handleMessage('+1234567890', 'SKIP'));
console.log(chatbot.handleMessage('+1234567890', 'SKIP'));
console.log(chatbot.handleMessage('+1234567890', 'PROFILE'));
*/
