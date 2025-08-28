# dev/bafoka_client.py
# Thin wrapper to mirror bot.bafoka_client.get_balance interface in dev
from . import api_client

def get_balance(token: str) -> dict:
    # Real API requires token, not wallet id
    return api_client.get_user_balance(token)
