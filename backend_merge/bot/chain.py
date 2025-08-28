# chain.py
# Minimal placeholder for blockchain integration. BE2 will call this when FS/BC has deployed the contract.
# Replace mock calls with web3.py calls to your contract (ABI + address).
import logging
def create_agreement_on_chain(agreement_id: int, offer: dict, requester_addr: str, provider=None):
    """
    Placeholder: call smart contract createAgreement(...)
    Return dict with tx_hash and status
    """
    logging.info("Pretend to call chain for agreement %s", agreement_id)
    # TODO: use web3.py: contract.functions.createAgreement(...).transact(...)
    return {"tx_hash": f"0xMOCKTX{agreement_id}", "status": "mocked"}

def confirm_agreement_on_chain(chain_tx: str) -> dict[str, str]:
    # TODO: call confirm
    return {"tx_hash": chain_tx, "status": "mocked-confirm"}
