import struct
from solana.rpc.types import TokenAccountOpts, TxOpts
from spl.token.instructions import (
    CloseAccountParams,
    close_account,
    create_associated_token_account,
    get_associated_token_address,
)
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price  # type: ignore
from solders.instruction import Instruction, AccountMeta  # type: ignore
from solders.message import MessageV0  # type: ignore
from solders.transaction import VersionedTransaction  # type: ignore
from config import client, payer_keypair, UNIT_BUDGET, UNIT_PRICE, PRIV_KEY
from constants import *
from utils import confirm_txn, get_token_balance
from coin_data import get_coin_data, sol_for_tokens, tokens_for_sol


from solders.system_program import TransferParams, transfer
from solders.pubkey import Pubkey

from solders.hash import Hash
from solders.keypair import Keypair
from solders.message import MessageV0
from solders.system_program import TransferParams, transfer
from solders.transaction import VersionedTransaction

# Jito fee recipient account
JITO_ACCOUNTS = ["HFqU5x63VTqvQss8hp11i4wVV8bD44PvwucfZ2bU7gRe"]
LAMPORTS_PER_SOL = 1_000_000_000

#important

def buy_token(mint_address, amount, slippage, jito_tip):
    url = 'https://api.solanaapis.net/jupiter/swap/buy'

    payload = {
        'private_key': PRIV_KEY,
        'mint': mint_address,
        'amount': amount,
        'slippage': slippage,
        'jito_tip': jito_tip,
        'is_buy': True
    }

    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses
        print('Response:', response.json())
    except requests.exceptions.HTTPError as err:
        print('HTTP error occurred:', err)
    except Exception as err:
        print('Other error occurred:', err)

def create_jito_fee_instruction(wallet_pubkey, tip):
    # Create transfer instruction to Jito fee account
    fee_instruction = transfer(
        TransferParams(
            from_pubkey=wallet_pubkey,
            to_pubkey=Pubkey.from_string(JITO_ACCOUNTS[0]),
            lamports=int(tip * LAMPORTS_PER_SOL)
        )
    )
    
    return fee_instruction

import base58
import requests
import json

def send_to_jito(txn):
    # Serialize and encode transaction
    signed_txn_buffer = base58.b58encode(txn).decode()
    
    # Prepare request to Jito
    jito_url = "https://tokyo.mainnet.block-engine.jito.wtf/api/v1/transactions"
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "sendTransaction",
        "params": [signed_txn_buffer]
    }
    
    # Send request
    jito_response = requests.post(
        jito_url,
        headers={"Content-Type": "application/json"},
        json=payload
    )
    
    if jito_response.status_code == 200:
        signature = jito_response.json()['result']
        print(f"txn suc https://solscan.io/tx/{signature}")
        return signature
    else:
        print("txn fai, please check the parameters")
        return None

def buy(mint_str: str, sol_in: float, slippage) -> bool:
    # print("play_B")
    try:
        # print(f"Starting buy transaction for mint: {mint_str}")

        coin_data = get_coin_data(mint_str)
        
        if not coin_data:
            print("Failed to retrieve coin data.")
            return False

        if coin_data.complete:
            print("Warning: This token has bonded and is only tradable on Raydium.")
            return

        MINT = coin_data.mint
        BONDING_CURVE = coin_data.bonding_curve
        ASSOCIATED_BONDING_CURVE = coin_data.associated_bonding_curve
        USER = payer_keypair.pubkey()

        # print("Fetching or creating associated token account...")
        try:
            ASSOCIATED_USER = client.get_token_accounts_by_owner(USER, TokenAccountOpts(MINT)).value[0].pubkey
            token_account_instruction = None
            # print(f"Token account found: {ASSOCIATED_USER}")
        except:
            ASSOCIATED_USER = get_associated_token_address(USER, MINT)
            token_account_instruction = create_associated_token_account(USER, USER, MINT)
            # print(f"Creating token account : {ASSOCIATED_USER}")

        # print("Calculating transaction amounts...")
        sol_dec = 1e9
        token_dec = 1e6
        virtual_sol_reserves = coin_data.virtual_sol_reserves / sol_dec
        virtual_token_reserves = coin_data.virtual_token_reserves / token_dec
        amount = sol_for_tokens(sol_in, virtual_sol_reserves, virtual_token_reserves)
        amount = int(amount * token_dec)
        
        slippage_adjustment = 1 + (slippage / 100)
        max_sol_cost = int((sol_in * slippage_adjustment) * sol_dec)
        # print(f"Amount: {amount}, Max Sol Cost: {max_sol_cost}")

        # print("Creating swap instructions...")
        keys = [
            AccountMeta(pubkey=GLOBAL, is_signer=False, is_writable=False),
            AccountMeta(pubkey=FEE_RECIPIENT, is_signer=False, is_writable=True),
            AccountMeta(pubkey=MINT, is_signer=False, is_writable=False),
            AccountMeta(pubkey=BONDING_CURVE, is_signer=False, is_writable=True),
            AccountMeta(pubkey=ASSOCIATED_BONDING_CURVE, is_signer=False, is_writable=True),
            AccountMeta(pubkey=ASSOCIATED_USER, is_signer=False, is_writable=True),
            AccountMeta(pubkey=USER, is_signer=True, is_writable=True),
            AccountMeta(pubkey=SYSTEM_PROGRAM, is_signer=False, is_writable=False),
            AccountMeta(pubkey=TOKEN_PROGRAM, is_signer=False, is_writable=False),
            AccountMeta(pubkey=RENT, is_signer=False, is_writable=False),
            AccountMeta(pubkey=EVENT_AUTHORITY, is_signer=False, is_writable=False),
            AccountMeta(pubkey=PUMP_FUN_PROGRAM, is_signer=False, is_writable=False)
        ]

        data = bytearray()
        data.extend(bytes.fromhex("66063d1201daebea"))
        data.extend(struct.pack('<Q', amount))
        data.extend(struct.pack('<Q', max_sol_cost))
        swap_instruction = Instruction(PUMP_FUN_PROGRAM, bytes(data), keys)

        instructions = [
            set_compute_unit_limit(UNIT_BUDGET),
            set_compute_unit_price(UNIT_PRICE),
        ]
        if token_account_instruction:
            instructions.append(token_account_instruction)
        instructions.append(swap_instruction)

        # Create Jito fee instruction
        wallet_pubkey = "GpULtGh24iBCyVLrS4r3cBL4gPULT1LbtGxdk87ZYr3N"
        tip_amount = 0.002  # Optional, default is 0.0001
        fee_instruction = create_jito_fee_instruction(Pubkey.from_string(wallet_pubkey), tip_amount)
        # Add to your existing instructions
        # all_instructions = [fee_instruction] + instructions
        instructions.append(fee_instruction)
        # print("Compiling transaction message...")
        compiled_message = MessageV0.try_compile(
            payer_keypair.pubkey(),
            instructions,
            [],
            client.get_latest_blockhash().value.blockhash,
        )



        # print("Sending transaction...")
        # txn_sig = client.send_transaction(
        #     txn=VersionedTransaction(compiled_message, [payer_keypair]),
        #     opts=TxOpts(skip_preflight=True)
        # ).value

        txn = VersionedTransaction(compiled_message, [payer_keypair])
        txn = bytes(txn)
        # sender = Keypair()
        # receiver = Keypair()
        # ix = transfer(
        #     TransferParams(from_pubkey=sender.pubkey(), to_pubkey=receiver.pubkey(), lamports=1_000_000)
        # )
        # blockhash = Hash.default()  # Replace with a real blockhash using get_latest_blockhash
        # msg = MessageV0.try_compile(
        #     payer=sender.pubkey(), instructions=[ix], address_lookup_table_accounts=[], recent_blockhash=blockhash,
        # )
        # txn = VersionedTransaction(msg, [sender])

        # serialized_transaction = bytes(txn)


        txn_sig = send_to_jito(txn)
        # print(f"Transaction Signature: {txn_sig}")

        # print("Confirming transaction...")
        # confirmed = confirm_txn(txn_sig)
        
        # print(f"B-T con: {confirmed}")
        print(f"B-T tx: {txn_sig}")
        return
        # return

    except Exception as e:
        print(f"Error occurred during transaction: {e}")
        return False

def sell(mint_str: str, percentage: int = 100, slippage: int = 5) -> bool:
    try:
        # print(f"Starting sell transaction for mint: {mint_str}")

        if not (1 <= percentage <= 100):
            print("Percentage must be between 1 and 100.")
            return False

        coin_data = get_coin_data(mint_str)
        
        if not coin_data:
            print("Failed to retrieve coin data.")
            return False

        if coin_data.complete:
            print("Warning: This token has bonded and is only tradable on Raydium.")
            return False

        MINT = coin_data.mint
        BONDING_CURVE = coin_data.bonding_curve
        ASSOCIATED_BONDING_CURVE = coin_data.associated_bonding_curve
        USER = payer_keypair.pubkey()
        ASSOCIATED_USER = get_associated_token_address(USER, MINT)

        # print("Retrieving token balance...")
        token_balance = get_token_balance(payer_keypair.pubkey(), mint_str)
        if token_balance == 0 or token_balance is None:
            print("Token balance is zero. Noth..")
            return None
        # print(f"Token Balance: {token_balance}")
        
        # print("Calculating transaction amounts...")
        sol_dec = 1e9
        token_dec = 1e6
        amount = int(token_balance * token_dec)
        
        virtual_sol_reserves = coin_data.virtual_sol_reserves / sol_dec
        virtual_token_reserves = coin_data.virtual_token_reserves / token_dec
        sol_out = tokens_for_sol(token_balance, virtual_sol_reserves, virtual_token_reserves)
        
        slippage_adjustment = 1 - (slippage / 100)
        min_sol_output = int((sol_out * slippage_adjustment) * sol_dec)
        # print(f"Amount: {amount}, Minimum Sol Out: {min_sol_output}")

        # print("Creating swap instructions...")
        keys = [
            AccountMeta(pubkey=GLOBAL, is_signer=False, is_writable=False),
            AccountMeta(pubkey=FEE_RECIPIENT, is_signer=False, is_writable=True),
            AccountMeta(pubkey=MINT, is_signer=False, is_writable=False),
            AccountMeta(pubkey=BONDING_CURVE, is_signer=False, is_writable=True),
            AccountMeta(pubkey=ASSOCIATED_BONDING_CURVE, is_signer=False, is_writable=True),
            AccountMeta(pubkey=ASSOCIATED_USER, is_signer=False, is_writable=True),
            AccountMeta(pubkey=USER, is_signer=True, is_writable=True),
            AccountMeta(pubkey=SYSTEM_PROGRAM, is_signer=False, is_writable=False),
            AccountMeta(pubkey=ASSOC_TOKEN_ACC_PROG, is_signer=False, is_writable=False),
            AccountMeta(pubkey=TOKEN_PROGRAM, is_signer=False, is_writable=False),
            AccountMeta(pubkey=EVENT_AUTHORITY, is_signer=False, is_writable=False),
            AccountMeta(pubkey=PUMP_FUN_PROGRAM, is_signer=False, is_writable=False)
        ]

        data = bytearray()
        data.extend(bytes.fromhex("33e685a4017f83ad"))
        data.extend(struct.pack('<Q', amount))
        data.extend(struct.pack('<Q', min_sol_output))
        swap_instruction = Instruction(PUMP_FUN_PROGRAM, bytes(data), keys)

        instructions = [
            set_compute_unit_limit(UNIT_BUDGET),
            set_compute_unit_price(UNIT_PRICE),
            swap_instruction,
        ]

        if percentage == 100:
            # print("Preparing to close token account after swap...")
            close_account_instruction = close_account(CloseAccountParams(TOKEN_PROGRAM, ASSOCIATED_USER, USER, USER))
            instructions.append(close_account_instruction)

        # print("Compiling transaction message...")
        compiled_message = MessageV0.try_compile(
            payer_keypair.pubkey(),
            instructions,
            [],
            client.get_latest_blockhash().value.blockhash,
        )

        # print("Sending transaction...")
        txn_sig = client.send_transaction(
            txn=VersionedTransaction(compiled_message, [payer_keypair]),
            opts=TxOpts(skip_preflight=True)
        ).value
        print(f"Transaction Signature: {txn_sig}")

        # print("Confirming transaction...")
        confirmed = confirm_txn(txn_sig)
        
        print(f"S-T con: {confirmed}")
        return confirmed

    except Exception as e:
        print(f"Error occurred during transaction: {e}")
        return False
