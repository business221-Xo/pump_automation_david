import time
from dataclasses import dataclass
from typing import Optional
from construct import Flag, Int64ul, Padding, Struct
from solders.pubkey import Pubkey  # type: ignore
from spl.token.instructions import get_associated_token_address
from config import client
from constants import PUMP_FUN_PROGRAM

@dataclass
class CoinData:
    mint: Pubkey
    bonding_curve: Pubkey
    associated_bonding_curve: Pubkey
    virtual_token_reserves: int
    virtual_sol_reserves: int
    token_total_supply: int
    complete: bool

def get_virtual_reserves(bonding_curve: Pubkey):
    bonding_curve_struct = Struct(
        Padding(8),
        "virtualTokenReserves" / Int64ul,
        "virtualSolReserves" / Int64ul,
        "realTokenReserves" / Int64ul,
        "realSolReserves" / Int64ul,
        "tokenTotalSupply" / Int64ul,
        "complete" / Flag
    )
    
    # Manually set the values
    manual_values = {
        "virtualTokenReserves": 1000000,
        "virtualSolReserves": 20,
        "realTokenReserves": 1000000,
        "realSolReserves": 40,
        "tokenTotalSupply": 5000,
        "complete": False
    }
    
    # Pack the values into a byte array
    packed_data = bonding_curve_struct.build(manual_values)
    
    # Parse the manually packed data using the struct
    parsed_data = bonding_curve_struct.parse(packed_data)
    
    return parsed_data

def derive_bonding_curve_accounts(mint_str: str):
    try:
        mint = Pubkey.from_string(mint_str)
        bonding_curve, _ = Pubkey.find_program_address(
            ["bonding-curve".encode(), bytes(mint)],
            PUMP_FUN_PROGRAM
        )
        associated_bonding_curve = get_associated_token_address(bonding_curve, mint)
        return bonding_curve, associated_bonding_curve
    except Exception:
        return None, None

def get_coin_data(mint_str: str) -> Optional[CoinData]:
    bonding_curve, associated_bonding_curve = derive_bonding_curve_accounts(mint_str)
    # print(f"giet_coin_data {bonding_curve} {associated_bonding_curve}")

    if bonding_curve is None or associated_bonding_curve is None:
        return None

    virtual_reserves = get_virtual_reserves(bonding_curve)
    # max_attempts = 60
    # attempt = 0
    # while virtual_reserves is None and attempt < max_attempts:
    #     # print(f"Waiting for data... Attempt {attempt+1}/{max_attempts}")
    #     time.sleep(0.5)  # Wait for 1 second
    #     virtual_reserves = get_virtual_reserves(bonding_curve)  # Try fetching again
    #     attempt += 1
    # print(f"{attempt}")
    # if virtual_reserves is None:
    #     return None

    try:
        return CoinData(
            mint=Pubkey.from_string(mint_str),
            bonding_curve=bonding_curve,
            associated_bonding_curve=associated_bonding_curve,
            virtual_token_reserves=int(virtual_reserves.virtualTokenReserves),
            virtual_sol_reserves=int(virtual_reserves.virtualSolReserves),
            token_total_supply=int(virtual_reserves.tokenTotalSupply),
            complete=bool(virtual_reserves.complete),
        )
    except Exception as e:
        # print(e)
        return None

def sol_for_tokens(sol_spent, sol_reserves, token_reserves):
    new_sol_reserves = sol_reserves + sol_spent
    new_token_reserves = (sol_reserves * token_reserves) / new_sol_reserves
    token_received = token_reserves - new_token_reserves
    return round(token_received)

def tokens_for_sol(tokens_to_sell, sol_reserves, token_reserves):
    new_token_reserves = token_reserves + tokens_to_sell
    new_sol_reserves = (sol_reserves * token_reserves) / new_token_reserves
    sol_received = sol_reserves - new_sol_reserves
    return sol_received
