"""
Natural Language Understanding (NLU) for voice commands
Interprets natural speech and converts to bot commands
"""
import re
from typing import Optional, Tuple

def extract_intent_and_entities(text: str) -> Tuple[str, dict]:
    """
    Extract user intent and entities from natural language text.
    
    Returns:
        (intent, entities) where intent is the command type and entities are parameters
    
    Supported intents:
    - register: User wants to register
    - balance: User wants to check balance
    - transfer: User wants to send money
    - offer: User wants to post a service offer
    - search: User wants to find services
    - help: User needs help
    """
    text_lower = text.lower().strip()
    entities = {}
    
    # INTENT: Registration
    register_patterns = [
        r'register|sign up|create account|join|new account',
        r'my name is (\w+)',
        r'i am (\w+)',
        r'call me (\w+)',
    ]
    
    for pattern in register_patterns:
        if re.search(pattern, text_lower):
            # Extract name if mentioned
            name_match = re.search(r'(?:my name is|i am|call me)\s+(\w+)', text_lower)
            if name_match:
                entities['name'] = name_match.group(1).title()
            
            # Extract community if mentioned
            community_match = re.search(r'(?:in|from|community)\s+(bameka|batoufam|fondjomekwet|fondjomenkwet)', text_lower)
            if community_match:
                entities['community'] = community_match.group(1).upper()
            
            return ('register', entities)
    
    # INTENT: Balance Check
    balance_patterns = [
        r'balance|how much|my money|check.*balance|what.*balance',
        r'how much do i have',
        r'show.*balance',
    ]
    
    for pattern in balance_patterns:
        if re.search(pattern, text_lower):
            return ('balance', entities)
    
    # INTENT: Transfer/Send Money
    transfer_patterns = [
        r'transfer|send|pay|give',
    ]
    
    for pattern in transfer_patterns:
        if re.search(pattern, text_lower):
            # Extract amount
            amount_match = re.search(r'(\d+)', text)
            if amount_match:
                entities['amount'] = int(amount_match.group(1))
            
            # Extract phone number
            phone_match = re.search(r'\+?\d{10,15}', text)
            if phone_match:
                entities['to_phone'] = phone_match.group(0)
            
            return ('transfer', entities)
    
    # INTENT: Offer Service
    offer_patterns = [
        r'offer|provide|i can|i do|my service',
        r'plumb|electrician|carpenter|teacher|mechanic|tailor',
    ]
    
    for pattern in offer_patterns:
        if re.search(pattern, text_lower):
            # Extract service type
            service_match = re.search(r'(plumb\w*|electric\w*|carpent\w*|teach\w*|mechanic|tailor\w*|cook\w*|clean\w*)', text_lower)
            if service_match:
                entities['service'] = service_match.group(1)
            
            # Extract price
            price_match = re.search(r'(\d+)', text)
            if price_match:
                entities['price'] = int(price_match.group(1))
            
            return ('offer', entities)
    
    # INTENT: Search Services
    search_patterns = [
        r'search|find|looking for|need|want',
        r'who (?:can|does|offers)',
    ]
    
    for pattern in search_patterns:
        if re.search(pattern, text_lower):
            # Extract search query (everything after search/find/looking for)
            query_match = re.search(r'(?:search|find|looking for|need|want)\s+(.+)', text_lower)
            if query_match:
                entities['query'] = query_match.group(1).strip()
            
            return ('search', entities)
    
    # INTENT: Help
    help_patterns = [
        r'help|how|what can|commands|start',
    ]
    
    for pattern in help_patterns:
        if re.search(pattern, text_lower):
            return ('help', entities)
    
    # Default: Unknown intent
    return ('unknown', entities)


def natural_language_to_command(text: str, phone: str) -> str:
    """
    Convert natural language text to bot command format.
    
    Args:
        text: Natural language input from user
        phone: User's phone number
    
    Returns:
        Command string in bot format (e.g., "/balance", "/transfer 100 +237...")
    """
    intent, entities = extract_intent_and_entities(text)
    
    if intent == 'register':
        # Build registration command
        parts = ['/register']
        if entities.get('name'):
            parts.append(entities['name'])
        if entities.get('community'):
            parts.append(entities['community'])
        return ' '.join(parts)
    
    elif intent == 'balance':
        return '/balance'
    
    elif intent == 'transfer':
        # Need both amount and recipient
        if 'amount' in entities and 'to_phone' in entities:
            return f"/transfer {entities['amount']} {entities['to_phone']}"
        else:
            # Incomplete transfer - ask for missing info
            if 'amount' not in entities:
                return "How much would you like to transfer?"
            if 'to_phone' not in entities:
                return "Who would you like to send money to? Please provide their phone number."
    
    elif intent == 'offer':
        # Build offer command
        if 'service' in entities and 'price' in entities:
            return f"/offer {entities['service']} {entities['price']}"
        else:
            # Incomplete offer
            if 'service' not in entities:
                return "What service would you like to offer?"
            if 'price' not in entities:
                return "How much would you charge for this service?"
    
    elif intent == 'search':
        if 'query' in entities:
            return f"/search {entities['query']}"
        else:
            return "What service are you looking for?"
    
    elif intent == 'help':
        return '/start'
    
    else:
        # Unknown intent - provide helpful response
        return (
            "I didn't quite understand that. You can:\n"
            "• Say 'check my balance' to see your balance\n"
            "• Say 'transfer 100 to +237...' to send money\n"
            "• Say 'I offer plumbing for 500' to post a service\n"
            "• Say 'search for plumber' to find services\n"
            "• Say 'help' for more options"
        )


def enhance_command_with_nlu(text: str, phone: str) -> str:
    """
    Main function to enhance text with NLU.
    If text looks like a command (starts with /), use it as-is.
    Otherwise, try to interpret it as natural language.
    
    Args:
        text: User input (command or natural language)
        phone: User's phone number
    
    Returns:
        Command string or helpful response
    """
    text = text.strip()
    
    # If it's already a command, use it as-is
    if text.startswith('/'):
        return text
    
    # Otherwise, interpret as natural language
    return natural_language_to_command(text, phone)
