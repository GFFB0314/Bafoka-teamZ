# 📱 Script de Conversation WhatsApp - Troc-Service Bafoka

## 🎯 Vue d'ensemble

Ce script guide l'intégration WhatsApp avec le système de monnaie communautaire **Bafoka**. Chaque communauté a sa propre variante de monnaie (Fonjoka, Banjika, Bafouka) et les échanges sont limités aux membres de la même communauté.

## 🏘️ Communautés et Monnaies

- **1. Fondjomenkwet** → Monnaie : **Fonjoka**
- **2. Banja** → Monnaie : **Banjika**  
- **3. Bafouka** → Monnaie : **Bafouka**

## 💰 Système Bafoka

- **Distribution initiale** : 1000 Bafoka à l'inscription
- **Isolation communautaire** : Échanges uniquement dans la même communauté
- **Système de backers** : Commerçants locaux peuvent recharger les comptes

## 🔄 Flux de Conversation

### 1. **Accueil et Inscription**
```
🤖 : "Bienvenue sur Troc-Service ! 🌟
     Choisissez votre communauté pour commencer :

     1️⃣ Fondjomenkwet (Fonjoka)
     2️⃣ Banja (Banjika)  
     3️⃣ Bafouka (Bafouka)

     Répondez par le numéro de votre communauté."

👤 : "1"

🤖 : "Parfait ! Vous rejoignez la communauté Fondjomenkwet.
     Entrez votre nom d'utilisateur :"

👤 : "Alice"

🤖 : "🎉 Félicitations Alice ! Vous êtes maintenant membre de Fondjomenkwet !
     💰 Votre solde : 1000 Fonjoka
     🏘️ Communauté : Fondjomenkwet
     ⭐ Réputation : 50/100

     Tapez *MENU* pour voir les commandes disponibles."
```

### 2. **Menu Principal**
```
🤖 : "📋 MENU PRINCIPAL - Troc-Service

     💰 *SOLDE* - Voir votre solde Fonjoka
     🔍 *RECHERCHER* - Trouver des services
     📤 *OFFRIR* - Proposer vos services
     🤝 *ECHANGER* - Créer un échange
     📊 *PROFIL* - Voir votre profil
     🏪 *BACKERS* - Trouver des recharges
     ❓ *AIDE* - Aide et commandes
     🔄 *COMMUNAUTE* - Info communauté"
```

### 3. **Recherche de Services**
```
👤 : "RECHERCHER"

🤖 : "🔍 Que recherchez-vous ?
     Exemples : couture, coiffure, réparation, cours...

     Entrez votre recherche :"

👤 : "couture"

🤖 : "👗 Services de couture disponibles dans Fondjomenkwet :

     👤 Marie - 150 Fonjoka
        "Couture sur mesure, robes traditionnelles"
        ⭐ Réputation : 85/100
        📍 Quartier : Centre-ville

     👤 Fatou - 200 Fonjoka  
        "Couture moderne, vêtements d'occasion"
        ⭐ Réputation : 92/100
        📍 Quartier : Marché central

     💰 Votre solde : 1000 Fonjoka

     Pour proposer un échange, tapez :
     *PROPOSER [nom] [service] [montant]*"
```

### 4. **Proposition d'Échange**
```
👤 : "PROPOSER Marie couture 150"

🤖 : "🤝 Proposition d'échange créée !

     📋 Détails :
     👤 Vous → Marie
     🎯 Service : Couture
     💰 Montant : 150 Fonjoka
     ⏰ Délai : 24h
     📍 Communauté : Fondjomenkwet

     ✅ Votre solde réservé : 850 Fonjoka
     ⏳ En attente de confirmation de Marie

     Marie recevra une notification et pourra confirmer l'échange."
```

### 5. **Confirmation d'Échange**
```
🤖 : "🔔 NOUVELLE DEMANDE D'ÉCHANGE !

     👤 Alice souhaite vos services de couture
     💰 Montant : 150 Fonjoka
     ⏰ Délai : 24h

     Pour accepter, tapez : *ACCEPTER [ID]*
     Pour refuser, tapez : *REFUSER [ID]*

     ID de l'échange : #12345"

👤 : "ACCEPTER 12345"

🤖 : "✅ Échange confirmé ! 

     📋 Échange #12345
     👤 Alice → Marie
     🎯 Service : Couture
     💰 Montant : 150 Fonjoka
     📍 Communauté : Fondjomenkwet
     ⏰ Délai : 24h

     💡 Conseil : Contactez Alice pour organiser le service.
     Une fois terminé, tapez *TERMINE 12345*"
```

### 6. **Finalisation d'Échange**
```
👤 : "TERMINE 12345"

🤖 : "🎉 Service marqué comme terminé !

     📋 Échange #12345
     ✅ Statut : Terminé
     💰 Montant : 150 Fonjoka

     Maintenant, évaluez Alice (1-5 étoiles) :
     *EVALUER 12345 [note] [commentaire]*

     Exemple : *EVALUER 12345 5 Excellent service !*"

👤 : "EVALUER 12345 5 Très satisfaite du travail !"

🤖 : "⭐ Évaluation enregistrée !

     📊 Votre réputation : 85 → 86/100
     💰 150 Fonjoka transférés sur votre compte
     📈 Total échanges : 15

     🎯 Prochain objectif : 20 échanges pour le badge "Expert" !
     
     Tapez *MENU* pour continuer."
```

### 7. **Système de Backers (Recharge)**
```
👤 : "BACKERS"

🤖 : "🏪 Backers disponibles dans Fondjomenkwet :

     🏪 Épicerie du Centre
        📍 Rue principale, face au marché
        💰 Recharge : 100 Fonjoka = 1 régime de plantain
        📞 Contact : 237 XXX XXX XXX

     🏪 Boulangerie Traditionnelle  
        📍 Quartier résidentiel
        💰 Recharge : 200 Fonjoka = 2 pains traditionnels
        📞 Contact : 237 XXX XXX XXX

     💡 Pour recharger, rendez-vous chez un backer avec des biens.
     Ils rechargeront votre compte en échange.

     Votre solde actuel : 50 Fonjoka"
```

### 8. **Gestion du Profil**
```
👤 : "PROFIL"

🤖 : "👤 PROFIL - Alice

     🏘️ Communauté : Fondjomenkwet
     💰 Monnaie locale : Fonjoka
     💳 Solde actuel : 50 Fonjoka
     ⭐ Réputation : 86/100
     📊 Total échanges : 15
     📅 Membre depuis : 15 jours
     🏆 Badge : Membre actif

     📈 Statistiques :
     ✅ Échanges réussis : 14
     ⚠️ Échanges en cours : 1
     ❌ Échanges annulés : 0

     🎯 Prochain objectif : 20 échanges (Expert)"
```

### 9. **Informations Communautaires**
```
👤 : "COMMUNAUTE"

🤖 : "🏘️ FONDJOMENKWET - Communauté

     💰 Monnaie : Fonjoka
     👥 Membres : 1,247
     🔄 Transactions : 3,456
     📅 Créée : 6 mois

     🏆 Top membres :
     1. Marie - 98/100 (Expert couture)
     2. Jean - 95/100 (Réparateur)
     3. Fatou - 92/100 (Couturière)

     📊 Activité du mois :
     🔺 Nouveaux membres : +23
     🔺 Transactions : +156
     🔺 Fonjoka en circulation : 1,247,000

     💡 Conseil : Plus vous échangez, plus la communauté grandit !"
```

## 🚨 Gestion des Erreurs

### **Solde insuffisant**
```
🤖 : "❌ Solde insuffisant !

     💰 Solde actuel : 50 Fonjoka
     💰 Montant requis : 150 Fonjoka
     ❌ Manque : 100 Fonjoka

     💡 Solutions :
     1. Rendez-vous chez un backer pour recharger
     2. Attendez d'autres échanges pour gagner des Fonjoka
     3. Proposez vos propres services

     Tapez *BACKERS* pour trouver des recharges."
```

### **Communauté différente**
```
🤖 : "❌ Impossible d'échanger avec cette personne !

     🏘️ Votre communauté : Fondjomenkwet (Fonjoka)
     🏘️ Leur communauté : Banja (Banjika)

     💡 Les échanges sont limités à votre communauté
     pour maintenir l'économie locale.

     🔍 Recherchez des services dans Fondjomenkwet."
```

### **Échange expiré**
```
🤖 : "⏰ Échange expiré !

     📋 Échange #12345
     ⏰ Délai dépassé : 24h
     ❌ Statut : Expiré

     💰 150 Fonjoka remboursés sur votre compte
     📊 Nouveau solde : 200 Fonjoka

     💡 Créez un nouvel échange avec un délai plus long."
```

## 🔧 Commandes Techniques

### **Commandes de base**
- `*MENU*` - Menu principal
- `*SOLDE*` - Voir solde Bafoka
- `*PROFIL*` - Profil utilisateur
- `*AIDE*` - Aide et commandes

### **Commandes d'échange**
- `*RECHERCHER [service]*` - Rechercher des services
- `*OFFRIR [service] [prix]*` - Proposer un service
- `*PROPOSER [nom] [service] [montant]*` - Créer un échange
- `*ACCEPTER [ID]*` - Accepter un échange
- `*TERMINE [ID]*` - Marquer comme terminé
- `*EVALUER [ID] [note] [commentaire]*` - Évaluer un échange

### **Commandes communautaires**
- `*COMMUNAUTE*` - Info communauté
- `*BACKERS*` - Liste des backers
- `*MEMBRES*` - Membres de la communauté

## 📱 Intégration WhatsApp

### **Webhook Twilio**
```javascript
// Endpoint pour recevoir les messages WhatsApp
app.post('/webhook', async (req, res) => {
  const { From, Body } = req.body;
  
  // Traiter le message et déterminer la réponse
  const response = await processWhatsAppMessage(From, Body);
  
  // Envoyer la réponse via Twilio
  await sendWhatsAppResponse(From, response);
  
  res.status(200).send('OK');
});
```

### **Gestion des états**
```javascript
// Maintenir l'état de conversation par utilisateur
const userStates = new Map();

function getNextState(userId, message) {
  const currentState = userStates.get(userId);
  
  switch(currentState) {
    case 'WAITING_COMMUNITY_CHOICE':
      return handleCommunityChoice(userId, message);
    case 'WAITING_USERNAME':
      return handleUsername(userId, message);
    case 'WAITING_SERVICE_SEARCH':
      return handleServiceSearch(userId, message);
    // ... autres états
  }
}
```

## 🎯 Points Clés de l'Expérience

1. **Simplicité** : Interface WhatsApp familière
2. **Localité** : Chaque communauté a sa monnaie
3. **Confiance** : Système de réputation blockchain
4. **Inclusivité** : Accessible sans compte bancaire
5. **Durabilité** : Backers connectent virtuel et réel

## 🚀 Déploiement

1. **Compiler le contrat** : `npx hardhat compile`
2. **Déployer** : `npx hardhat run scripts/deploy-bafoka-community.js --network mumbai`
3. **Tester** : `npx hardhat test`
4. **Intégrer WhatsApp** : Mettre à jour le bot avec les nouvelles commandes

---

**🎉 Votre Troc-Service avec monnaie communautaire Bafoka est prêt !** 