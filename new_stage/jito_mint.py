# pump token mint_buy
import requests
import base58
from solders.transaction import VersionedTransaction
from solders.keypair import Keypair
from config import MAINADDRESS, ADDRESS1, ADDRESS2, ADDRESS3, ADDRESS4

import base58
from solders.keypair import Keypair

# WALLETS_AMOUNT = 4
# generated_wallets = []
# def generate_wallet():
#     for x in range(WALLETS_AMOUNT):
#         account = Keypair()
#         publicKey = str(account.pubkey())
#         privateKey = base58.b58encode(account.secret() + base58.b58decode(str(account.pubkey()))).decode('utf-8')
#         wallet = {
#             "pubKey": publicKey,
#             "priKey": privateKey
#         }
#         generated_wallets.append(wallet)


def send_create_tx_bundle():
    signerKeypairs = [
        Keypair.from_base58_string(MAINADDRESS),
        Keypair.from_base58_string(ADDRESS1),
        Keypair.from_base58_string(ADDRESS2),
        Keypair.from_base58_string(ADDRESS3),
        Keypair.from_base58_string(ADDRESS4)
        # use up to 5 wallets
    ]

    # Generate a random keypair for token
    mint_keypair = Keypair()
    print(str(mint_keypair.pubkey()))

    # Define token metadata
    form_data = {
        'name': 'UAwar',
        'symbol': 'UAwar',
        'description': 'Who will be the winner',
        'twitter': 'https://x.com/a1lon9/status/1812970586420994083',
        'telegram': 'https://x.com/a1lon9/status/1812970586420994083',
        'website': 'https://UA-RUS.net',
        'showName': 'true'
    }

    with open('./bear.png', 'rb') as f:
        file_content = f.read()

    files = {
        'file': ('bear.png', file_content, 'image/png')
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

    bundledTransactionArgs = [
        {
            'publicKey': str(signerKeypairs[0].pubkey()),
            'action': 'create',
            'tokenMetadata': token_metadata,
            'mint': str(mint_keypair.pubkey()),
            'denominatedInSol': 'true',
            'amount': 0.1,
            'slippage': 10,
            'priorityFee': 0.0002,
            'pool': 'pump'
        },
        {
            "publicKey": str(signerKeypairs[1].pubkey()),
            "action": "buy", 
            "mint": str(mint_keypair.pubkey()), 
            "denominatedInSol": "true",
            "amount": 0.01,
            "slippage": 50,
            "priorityFee": 0.0001, # priority fee after first tx is ignored
            "pool": "pump"
        },
        {
            "publicKey": str(signerKeypairs[2].pubkey()),
            "action": "buy", 
            "mint": str(mint_keypair.pubkey()), 
            "denominatedInSol": "true",
            "amount": 0.01,
            "slippage": 50,
            "priorityFee": 0.0001, # priority fee after first tx is ignored
            "pool": "pump"
        },
        {
            "publicKey": str(signerKeypairs[3].pubkey()),
            "action": "buy", 
            "mint": str(mint_keypair.pubkey()), 
            "denominatedInSol": "true",
            "amount": 0.01,
            "slippage": 50,
            "priorityFee": 0.0001, # priority fee after first tx is ignored
            "pool": "pump"
        },
        {
            "publicKey": str(signerKeypairs[4].pubkey()),
            "action": "buy", 
            "mint": str(mint_keypair.pubkey()), 
            "denominatedInSol": "true",
            "amount": 0.01,
            "slippage": 50,
            "priorityFee": 0.0001, # priority fee after first tx is ignored
            "pool": "pump"
        }
        # use up to 5 transactions
    ]

    # Generate the bundled transactions
    response = requests.post(
        "https://pumpportal.fun/api/trade-local",
        headers={"Content-Type": "application/json"},
        json=bundledTransactionArgs
    )

    if response.status_code != 200: 
        print("Failed to generate transactions.")
        print(response.reason)
    else:
        encodedTransactions = response.json()
        encodedSignedTransactions = []
        txSignatures = []

        for index, encodedTransaction in enumerate(encodedTransactions):
            if bundledTransactionArgs[index]["action"] == "create":
                signedTx = VersionedTransaction(VersionedTransaction.from_bytes(base58.b58decode(encodedTransaction)).message, [mint_keypair, signerKeypairs[index]])
            else:
                signedTx = VersionedTransaction(VersionedTransaction.from_bytes(base58.b58decode(encodedTransaction)).message, [signerKeypairs[index]])
            
            encodedSignedTransactions.append(base58.b58encode(bytes(signedTx)).decode())
            txSignatures.append(str(signedTx.signatures[0]))

        jito_response = requests.post(
            "https://mainnet.block-engine.jito.wtf/api/v1/bundles",
            headers={"Content-Type": "application/json"},
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "sendBundle",
                "params": [
                    encodedSignedTransactions
                ]
            }
        )

        for i, signature in enumerate(txSignatures):
            print(f'Transaction {i}: https://solscan.io/tx/{signature}')

send_create_tx_bundle()