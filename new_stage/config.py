from solana.rpc.api import Client
from solders.keypair import Keypair #type: ignore
from dotenv import load_dotenv
import os

load_dotenv()

# RPC = os.getenv('GETBLOCK')
# UNIT = os.getenv('UNIT_BUDGET')
# print(f"jito_mint _ {RPC}")
# print(f"jito_mint _ {UNIT}")
MAINADDRESS  = os.getenv('MAINADDRESS')
ADDRESS1 = os.getenv('ADDRESS1')
ADDRESS2 = os.getenv('ADDRESS2')
ADDRESS3 = os.getenv('ADDRESS3')
ADDRESS4 = os.getenv('ADDRESS4')
