# bot/services/wallet_service.py
import logging
from bot.bafoka_client import create_wallet as api_create_wallet, get_balance as api_get_balance, transfer as api_transfer

LOG = logging.getLogger(__name__)

class WalletService:
    """
    Service to handle Bafoka Wallet interactions.
    Acts as an abstraction layer over the raw API client.
    """

    @staticmethod
    def create_wallet(phone: str, name: str, community_id: str, age: int = 25) -> dict:
        """
        Create a wallet on the Bafoka network.
        """
        try:
            return api_create_wallet(phone, name, community_id, age)
        except Exception as e:
            LOG.error(f"WalletService: Failed to create wallet for {phone}: {e}")
            # In a real fallback scenario, we might return a mock ID or raise a specific custom exception
            # For now, re-raise to let the caller decide
            raise

    @staticmethod
    def get_balance(phone: str) -> dict:
        """
        Get wallet balance.
        """
        return api_get_balance(phone)

    @staticmethod
    def transfer(from_phone: str, to_phone: str, amount: int) -> dict:
        """
        Execute a transfer.
        """
        return api_transfer(from_phone, to_phone, amount)
