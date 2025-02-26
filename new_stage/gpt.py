import os
from solana.rpc.api import Client
from solana.publickey import PublicKey
from solana.keypair import Keypair
from solana.system_program import create_account, CreateAccountParams
from solana.transaction import Transaction, TransactionInstruction, AccountMeta
from spl.token.instructions import create_mint, create_associated_token_account, mint_to
from spl.token.constants import TOKEN_PROGRAM_ID
from config import MAINADDRESS, ADDRESS1, ADDRESS2, ADDRESS3, ADDRESS4
from jito import JitoClient

# Set up your Solana client
solana_url = "https://api.mainnet-beta.solana.com/"
client = Client(solana_url)

# Generate keypairs for the signer and the mint
signerKeypairs = [Keypair.from_base58_string(MAINADDRESS), Keypair.from_base58_string(ADDRESS1)]
mint_keypair = Keypair()
print(str(mint_keypair.pubkey()))

# Token metadata placeholder
token_metadata = {
        'name': 'UARUSTrump',
        'symbol': 'UARUSTrump',
        'description': 'Who will be the winner',
        'twitter': 'https://x.com/a1lon9/status/1812970586420994083',
        'telegram': 'https://x.com/a1lon9/status/1812970586420994083',
        'website': 'https://UA-RUS.net',
        'showName': 'true'
}

# Function to create a transaction instruction
def create_instruction(action, **kwargs):
    if action == 'create':
        return create_mint_instruction(mint_keypair, **kwargs)
    elif action == 'buy':
        return buy_instruction(**kwargs)
    else:
        raise ValueError("Invalid action")

# Function to create a mint instruction
def create_mint_instruction(mint_keypair, **kwargs):
    # Create mint instruction
    mint_instruction = create_mint(
        CreateAccountParams(
            from_pubkey=signerKeypairs[0].public_key,
            new_account_pubkey=mint_keypair.public_key,
            lamports=client.get_minimum_balance_for_rent_exemption(82, commitment="finalized")['result'],
            space=82,
            program_id=TOKEN_PROGRAM_ID,
        )
    )
    return mint_instruction

# Function to create a buy instruction (this is a placeholder, as buying tokens typically involves a more complex process)
def buy_instruction(**kwargs):
    # For simplicity, this example assumes you're transferring tokens from one account to another.
    # In a real scenario, you'd need to implement a more complex logic for buying tokens, possibly involving Serum or other DEXs.
    # Here, we'll just create an associated token account and mint tokens to it.
    associated_token_account = Keypair()
    create_associated_token_account_instruction = create_associated_token_account(
        payer=signerKeypairs[1].public_key,
        owner=signerKeypairs[1].public_key,
        mint=mint_keypair.public_key,
    )
    
    mint_to_instruction = mint_to(
        mint=mint_keypair.public_key,
        to=associated_token_account.public_key,
        mint_authority=signerKeypairs[0].public_key,
        amount=kwargs['amount'],
    )
    
    return [create_associated_token_account_instruction, mint_to_instruction]

# Bundle transaction arguments
bundledTransactionArgs = [
    {
        'publicKey': str(signerKeypairs[0].public_key),
        'action': 'create',
        'tokenMetadata': token_metadata,
        'mint': str(mint_keypair.public_key),
        'denominatedInSol': 'true',
        'amount': 0.001, # Dev buy of 1000000 tokens
        'slippage': 10,
        'priorityFee': 0.0005,
        'pool': 'pump'
    },
    {
        "publicKey": str(signerKeypairs[1].public_key),
        "action": "buy",
        "mint": str(mint_keypair.public_key),
        "denominatedInSol": "true",
        "amount": 0.001,
        "slippage": 50,
        "priorityFee": 0.0001, 
        "pool": "pump"
    }
]

# Create transaction
def create_bundled_transaction(args):
    transaction = Transaction()
    for arg in args:
        instruction = create_instruction(arg['action'], **arg)
        if isinstance(instruction, list):
            for i in instruction:
                transaction.add(i)
        else:
            transaction.add(instruction)
    return transaction

transaction = create_bundled_transaction(bundledTransactionArgs)

# Convert transaction to a serialized form
serialized_transactions = transaction.serialize().hex()

# Set up Jito client
jito_url = "https://mainnet.block-engine.jito.wtf/api/v1/bundles"  # Replace with your actual Jito endpoint
jito_client = JitoClient(jito_url)

# Send the bundle using Jito
def send_jito_bundle(transactions):
    try:
        bundle_id = jito_client.send_bundle(transactions)
        print(f"Bundle sent with ID: {bundle_id}")
    except Exception as e:
        print(f"Error sending bundle: {e}")

send_jito_bundle([serialized_transactions])

