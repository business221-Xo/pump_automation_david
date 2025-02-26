import requests
import json
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.keypair import Keypair
from solders.commitment_config import CommitmentLevel
from solders.rpc.requests import SendVersionedTransaction
from solders.rpc.config import RpcSendTransactionConfig
from config import MAINADDRESS, ADDRESS1, ADDRESS2, ADDRESS3, ADDRESS4

def send_local_create_tx():
    signer_keypair = Keypair.from_base58_string(MAINADDRESS)

    # Generate a random keypair for token
    mint_keypair = Keypair()
    print(str(mint_keypair.pubkey()))

    # Define token metadata
    form_data = {
        'name': 'UARUS',
        'symbol': 'UARUS',
        'description': 'Who will be winner',
        'twitter': 'https://x.com/a1lon9/status/1812970586420994083',
        'telegram': 'https://x.com/a1lon9/status/1812970586420994083',
        'website': 'https://pumpportal.fun',
        'showName': 'true'
    }

    # Read the image file
    with open('./butter.png', 'rb') as f:
        file_content = f.read()

    files = {
        'file': ('butter.png', file_content, 'image/png')
    }

    # Create IPFS metadata storage
    metadata_response = requests.post("https://pump.fun/api/ipfs", data=form_data, files=files)
    metadata_response_json = metadata_response.json()

    # Token metadata
    token_metadata = {
        'name': form_data['name'],
        'symbol': form_data['symbol'],
        'uri': metadata_response_json['metadataUri']
    }

    # Generate the create transaction
    response = requests.post(
        "https://pumpportal.fun/api/trade-local",
        headers={'Content-Type': 'application/json'},
        data=json.dumps({
            'publicKey': str(signer_keypair.pubkey()),
            'action': 'create',
            'tokenMetadata': token_metadata,
            'mint': str(mint_keypair.pubkey()),
            'denominatedInSol': 'true',
            'amount': 0.01, # Dev buy of 1 SOL
            'slippage': 10,
            'priorityFee': 0.0001,
            'pool': 'pump'
        })
    )

    tx = VersionedTransaction(VersionedTransaction.from_bytes(response.content).message, [mint_keypair, signer_keypair])

    commitment = CommitmentLevel.Confirmed
    config = RpcSendTransactionConfig(preflight_commitment=commitment)
    # txPayload = SendVersionedTransaction(tx, config)

    response = requests.post(
        url="https://api.mainnet-beta.solana.com/",
        headers={"Content-Type": "application/json"},
        data=SendVersionedTransaction(tx, config).to_json()
    )
    txSignature = response.json()['result']
    print(f'Transaction: https://solscan.io/tx/{txSignature}')

send_local_create_tx()