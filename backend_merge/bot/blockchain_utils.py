from web3 import Web3
import json
import logging

# Initialize a web3 instance
web3 = Web3(Web3.HTTPProvider('http://localhost:8545'))  # Replace with actual RPC URL

# Load contract ABI
try:
    with open('../blockchain/deployments/hardhat-deployment.json', 'r') as abi_file:  # Use hardhat-deployment.json as ABI
        abi_content = json.load(abi_file)
        contract_abi = abi_content["abi"]
    
    # Contract details
    contract_address = '0xFFD840e78695a3faf29e877AF417258b4FAaE435'
    contract = web3.eth.contract(address=contract_address, abi=contract_abi)
except Exception as e:
    logging.warning("Failed to load blockchain contract: %s. Blockchain features will be unavailable.", e)
    contract_abi = None
    contract = None

# Function to create agreement on blockchain
def create_agreement_on_chain(agreement_id: int, offer: dict, requester_addr: str, provider=None):
    if not contract:
        logging.warning("Contract not available, skipping blockchain operation")
        return {"status": "failure", "error": "Blockchain contract not available"}
    
    try:
        tx = contract.functions.createAgreement(agreement_id, offer, requester_addr).transact({'from': web3.eth.accounts[0]})
        receipt = web3.eth.waitForTransactionReceipt(tx)
        logging.info("Successfully created agreement on chain: %s", agreement_id)
        return {"tx_hash": receipt.transactionHash.hex(), "status": "success"}
    except Exception as e:
        logging.error("Error creating agreement on chain: %s", e)
        return {"status": "failure", "error": str(e)}

# Function to confirm agreement on blockchain
def confirm_agreement_on_chain(chain_tx: str):
    if not contract:
        logging.warning("Contract not available, skipping blockchain operation")
        return {"status": "failure", "error": "Blockchain contract not available"}
    
    try:
        tx = contract.functions.confirmAgreement(chain_tx).transact({'from': web3.eth.accounts[0]})
        receipt = web3.eth.waitForTransactionReceipt(tx)
        logging.info("Successfully confirmed agreement on chain: %s", chain_tx)
        return {"tx_hash": receipt.transactionHash.hex(), "status": "success"}
    except Exception as e:
        logging.error("Error confirming agreement on chain: %s", e)
        return {"status": "failure", "error": str(e)}
