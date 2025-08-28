# dev/chain.py
# Copy of bot/chain placeholder to avoid importing from bot
import logging

def create_agreement_on_chain(agreement_id: int, offer: dict, requester_addr: str, provider=None):
    logging.info("Pretend to call chain for agreement %s", agreement_id)
    return {"tx_hash": f"0xMOCKTX{agreement_id}", "status": "mocked"}

def confirm_agreement_on_chain(chain_tx: str) -> dict:
    return {"tx_hash": chain_tx, "status": "mocked-confirm"}
