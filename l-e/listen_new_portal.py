import websockets
import asyncio
import json
from datetime import datetime
import sys
# Assuming Directory A is a sibling of Directory B
sys.path.append('../actual_b_s_P/pump_fun_py')

import pump_fun
sol_in = .002
slippage = 5
percentage = 100
# PumpPortal WebSocket URL
WS_URL = "wss://pumpportal.fun/api/data"

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
                if token_info.get('marketCapSol') > 22 :
                    if token_info.get('marketCapSol') < 110 : 
                        mint_str = token_info.get('mint')
                        print(mint_str)
                        
                        # print("\n" + "=" * 50)
                        print(f"created: {token_info.get('name')} ({token_info.get('symbol')})")
                        # print("=" * 50)
                        # print(f"Address:        {token_info.get('mint')}")
                        # # print(f"Creator:        {token_info.get('traderPublicKey')}")
                        # print(f"Initial Buy:    {format_sol(token_info.get('initialBuy', 0))}")
                        print(f"{format_sol(token_info.get('marketCapSol', 0))}")                 
                        # # print(f"Bonding Curve:  {token_info.get('bondingCurveKey')}")
                        # # print(f"Virtual SOL:    {format_sol(token_info.get('vSolInBondingCurve', 0))}")
                        # # print(f"Virtual Tokens: {token_info.get('vTokensInBondingCurve', 0):,.0f}")
                        # # print(f"Metadata URI:   {token_info.get('uri')}")
                        # # print(f"Signature:      {token_info.get('signature')}")
                        # print("=" * 50)

                        # pump_fun.buy(mint_str, sol_in, slippage)
                        # # await asyncio.sleep(12)
                        # b_state = pump_fun.sell(mint_str, percentage, slippage)
                        # while b_state is False:
                        #     b_state = pump_fun.sell(mint_str, percentage, slippage)
                        # print("done20")
                    else :
                        mint_str = token_info.get('mint')
                        print(mint_str)
                        
                        print(f"created: {token_info.get('name')} ({token_info.get('symbol')})")
                        print(f"{format_sol(token_info.get('marketCapSol', 0))}")

                        # pump_fun.buy(mint_str, sol_in, slippage)
                        # # await asyncio.sleep(27)
                        # s_state = pump_fun.sell(mint_str, percentage, slippage)
                        # while s_state is False:
                        #     s_state = pump_fun.sell(mint_str, percentage, slippage)
                        # print("done40")
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