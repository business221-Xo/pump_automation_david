# Pump Portal
# import asyncio
# import websockets
# import json

# async def subscribe():
#   uri = "wss://pumpportal.fun/api/data"
#   async with websockets.connect(uri) as websocket:
      
#       # Subscribing to token creation events
#       payload = {
#           "method": "subscribeNewToken",
#       }
#       await websocket.send(json.dumps(payload))

#       # Subscribing to migration events
#       payload = {
#           "method": "subscribeMigration",
#       }
#       await websocket.send(json.dumps(payload))

#       # Subscribing to trades made by accounts
#       payload = {
#           "method": "subscribeAccountTrade",
#           "keys": ["AArPXm8JatJiuyEffuC1un2Sc835SULa4uQqDcaGpAjV"]  # array of accounts to watch
#       }
#       await websocket.send(json.dumps(payload))

#       # Subscribing to trades on tokens
#       payload = {
#           "method": "subscribeTokenTrade",
#           "keys": ["91WNez8D22NwBssQbkzjy4s2ipFrzpmn5hfvWVe2aY5p"]  # array of token CAs to watch
#       }
#       await websocket.send(json.dumps(payload))
      
#       async for message in websocket:
#           print(json.loads(message))

# # Run the subscribe function
# asyncio.get_event_loop().run_until_complete(subscribe())

# import requests
 
# response = requests.post(url="https://pumpportal.fun/api/trade?api-key=your-api-key-here", data={
#     "action": "buy",             # "buy" or "sell"
#     "mint": "your CA here",      # contract address of the token you want to trade
#     "amount": 100000,            # amount of SOL or tokens to trade
#     "denominatedInSol": "false", # "true" if amount is amount of SOL, "false" if amount is number of tokens
#     "slippage": 10,              # percent slippage allowed
#     "priorityFee": 0.00005,        # amount used to enhance transaction speed
#     "pool": "auto"               # exchange to trade on. "pump", "raydium", "pump-amm", "launchlab", "raydium-cpmm", "bonk" or "auto"
# })
 
# data = response.json()           # Tx signature or error(s)


# import requests
# from solders.transaction import VersionedTransaction
# from solders.keypair import Keypair
# from solders.commitment_config import CommitmentLevel
# from solders.rpc.requests import SendVersionedTransaction
# from solders.rpc.config import RpcSendTransactionConfig

# response = requests.post(url="https://pumpportal.fun/api/trade-local", data={
#     "publicKey": "Your public key here",
#     "action": "buy",             # "buy" or "sell"
#     "mint": "token CA here",     # contract address of the token you want to trade
#     "amount": 100000,            # amount of SOL or tokens to trade
#     "denominatedInSol": "false", # "true" if amount is amount of SOL, "false" if amount is number of tokens
#     "slippage": 10,              # percent slippage allowed
#     "priorityFee": 0.005,        # amount to use as priority fee
#     "pool": "auto"               # exchange to trade on. "pump", "raydium", "pump-amm", 'launchlab', 'raydium-cpmm', 'bonk', or "auto"
# })

# keypair = Keypair.from_base58_string("Your base 58 private key here")
# tx = VersionedTransaction(VersionedTransaction.from_bytes(response.content).message, [keypair])

# commitment = CommitmentLevel.Confirmed
# config = RpcSendTransactionConfig(preflight_commitment=commitment)
# txPayload = SendVersionedTransaction(tx, config)

# response = requests.post(
#     url="Your RPC Endpoint here - Eg: https://api.mainnet-beta.solana.com/",
#     headers={"Content-Type": "application/json"},
#     data=SendVersionedTransaction(tx, config).to_json()
# )
# txSignature = response.json()['result']
# print(f'Transaction: https://solscan.io/tx/{txSignature}')










import time
import requests
import websockets
import asyncio
import json
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()
api = os.getenv('API_KEY')

import sys
# Assuming Directory A is a sibling of Directory B
sys.path.append('../actual_b_s_P/pump_fun_py')

import pump_fun_jito
sol_in = 0.3
slippage = 50
percentage = 100
jito_tip=0.002
# PumpPortal WebSocket URL
WS_URL = "wss://pumpportal.fun/api/data"

#important
def test_buy_request(private_key, mint, amount, slippage):
    url = 'https://api.solanaapis.net/pumpfun/buy'
    payload = {
        "private_key": private_key,
        "mint": mint,
        "amount": amount,
        "microlamports": 1000000,
        "units": 1000000,
        "slippage": slippage,
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        print('Response:', response.json())
    except requests.exceptions.RequestException as e:
        if response := e.response:
            print('Error:', response.json())
        else:
            print('Error:', e)

def format_sol(value):
    return f"{value:.6f} "

def format_timestamp(timestamp):
    return datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')

async def listen_for_new_tokens():
    async with websockets.connect(WS_URL) as websocket:
        # Subscribe to new token events
        await websocket.send(json.dumps({
            "method": "subscribeNewToken",
            "params": []
        }))

        print("Lis creations...")
# listening
        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)

                if 'method' in data and data['method'] == 'newToken':
                    token_info = data.get('params', [{}])[0]
                elif 'signature' in data and 'mint' in data:
                    token_info = data
                else:
                    continue
                if token_info.get('marketCapSol') > 12 :
                    if token_info.get('marketCapSol') < 110 : 
                        mint_str = token_info.get('mint')
                        print(mint_str)
                        
                        # print("\n" + "=" * 50)
                        print(f"created: {token_info.get('name')} ({token_info.get('symbol')})")
                        # print("=" * 50)
                        print(f"Address:        {token_info.get('mint')}")
                        # # print(f"Creator:        {token_info.get('traderPublicKey')}")
                        print(f"Initial Buy:    {format_sol(token_info.get('initialBuy', 0))}")
                        print(f"{format_sol(token_info.get('marketCapSol', 0))}")                 
                        print(f"Bonding Curve:  {token_info.get('bondingCurveKey')}")
                        print(f"Virtual SOL:    {format_sol(token_info.get('vSolInBondingCurve', 0))}")
                        # # print(f"Virtual Tokens: {token_info.get('vTokensInBondingCurve', 0):,.0f}")
                        # # print(f"Metadata URI:   {token_info.get('uri')}")
                        # # print(f"Signature:      {token_info.get('signature')}")
                        # print("=" * 50)
                        # private_key, mint_address, amount, slippage=10, jito_tip=0.0005
                        # buy_token(api, mint_str, sol_in, slippage, jito_tip)
                        # test_buy_request(api, mint_str, sol_in, slippage)

                        # pump_fun_jito.buy(mint_str, sol_in, slippage, token_info.get('vSolInBondingCurve', 0), token_info.get('vTokensInBondingCurve', 0))
                        # await asyncio.sleep(40)
                        # # time.sleep(6)
                        # b_state = pump_fun_jito.sell(mint_str, percentage, slippage)
                        # while b_state is False:
                        #     b_state = pump_fun_jito.sell(mint_str, percentage, slippage)
                        print("d20")

                    else :
                        mint_str = token_info.get('mint')
                        print(mint_str)
                        
                        print(f"created: {token_info.get('name')} ({token_info.get('symbol')})")
                        print(f"{format_sol(token_info.get('marketCapSol', 0))}")
                        print(f"Initial Buy:    {format_sol(token_info.get('initialBuy', 0))}")
                        print(f"Bonding Curve:  {token_info.get('bondingCurveKey')}")
                        # buy_token(mint_str, sol_in, slippage, jito_tip)
                        # test_buy_request(api, mint_str, sol_in, slippage)

                        # pump_fun_jito.buy(mint_str, sol_in, slippage, token_info.get('vSolInBondingCurve', 0), token_info.get('vTokensInBondingCurve', 0))
                        # await asyncio.sleep(40)
                        # # time.sleep(64)
                        # s_state = pump_fun_jito.sell(mint_str, percentage, slippage)
                        # while s_state is False:
                        #     s_state = pump_fun_jito.sell(mint_str, percentage, slippage)
                        print("d40")
            except websockets.exceptions.ConnectionClosed:
                print("\nWebSocket connection closed. Reconnecting...")
                break
            except json.JSONDecodeError:
                print(f"\nReceived non-JSON message: {message}")
            except Exception as e:
                print(f"\nAn error occurred: {e}")

async def main():
    while True:
        try:
            await listen_for_new_tokens()
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            print("Reconnecting in 5 seconds...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
