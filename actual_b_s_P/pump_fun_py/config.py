from solana.rpc.api import Client
from solders.keypair import Keypair #type: ignore
from dotenv import load_dotenv
import os

load_dotenv()
PRIV_KEY = os.getenv('API_KEY')
# PRIV_KEY = ""
RPC = os.getenv('GETBLOCK')
UNIT_BUDGET =  100_000
UNIT_PRICE =  1_000_000
client = Client(RPC)
payer_keypair = Keypair.from_base58_string(PRIV_KEY)
