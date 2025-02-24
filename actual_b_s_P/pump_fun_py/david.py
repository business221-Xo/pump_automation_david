import websocket
import json
from datetime import datetime
import time
from pump_fun import buy
from pump_fun import sell

sol_in = .002
slippage = 5
percentage = 100
# PumpPortal WebSocket URL
WS_URL = "wss://pumpportal.fun/api/data"

def format_sol(value):
    return f"{value:.6f} SOL"

def format_timestamp(timestamp):
    return datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')

def listen_for_new_tokens():
    ws = websocket.WebSocket()
    ws.connect(WS_URL)
    
    # Subscribe to new token events
    ws.send(json.dumps({
        "method": "subscribeNewToken",
        "params": []
    }))

    print("Listening for creations...")
    
    while True:
        try:
            message = ws.recv()
            data = json.loads(message)

            if 'method' in data and data['method'] == 'newToken':
                token_info = data.get('params', [{}])[0]
            elif 'signature' in data and 'mint' in data:
                token_info = data
            else:
                continue
            
            if token_info.get('marketCapSol') > 42:
                if token_info.get('marketCapSol') < 110:
                    mint_str = token_info.get('mint')
                    print(mint_str)
                    print(f"created: {token_info.get('name')} ({token_info.get('symbol')})")
                    print(f"{format_sol(token_info.get('marketCapSol', 0))}")
                    buy(mint_str, sol_in, slippage)
                    time.sleep(20)
                    sell(mint_str, percentage, slippage)
                    print("done20")
                else:
                    mint_str = token_info.get('mint')
                    print(mint_str)
                    print(f"created: {token_info.get('name')} ({token_info.get('symbol')})")
                    print(f"{format_sol(token_info.get('marketCapSol', 0))}")
                    buy(mint_str, sol_in, slippage)
                    time.sleep(40)
                    sell(mint_str, percentage, slippage)
                    print("done40")
        except websocket.WebSocketException as e:
            print(f"\nWebSocket connection closed. Reconnecting...")
            break
        except json.JSONDecodeError:
            print(f"\nReceived non-JSON message: {message}")
        except Exception as e:
            print(f"\nAn error occurred: {e}")

def main():
    while True:
        try:
            listen_for_new_tokens()
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            print("Reconnecting in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    main()
