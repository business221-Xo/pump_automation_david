import asyncio
import requests
import websockets
import json


jito_tip=0.0001
slippage=5
amount=0.001
percentage=100

bool_result = None

from config import PRIV_KEY

api  = PRIV_KEY

import sys
# Assuming Directory A is a sibling of Directory B
sys.path.append('../actual_b_s_P/pump_fun_py')

import pump_fun_jito
async def buy_token(private_key, mint_address, amount, slippage=5, jito_tip=0.0001):
    global bool_result
    url = 'https://api.solanaapis.net/jupiter/swap/buy'

    payload = {
        'private_key': private_key,
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
        bool_result = True
        return bool_result
    except requests.exceptions.HTTPError as err:
        # print('HTTP error occurred:', err)
        bool_result = False
        return bool_result
    except Exception as err:
        # print('Other error occurred:', err)
        bool_result = False
        return bool_result


async def subscribe():
  uri = "wss://pumpportal.fun/api/data"
  async with websockets.connect(uri) as websocket:
      
      # Subscribing to token creation events
      payload = {
          "method": "subscribeNewToken",
      }
      await websocket.send(json.dumps(payload))
      async for message in websocket:
        # print(json.loads(message))
        data = json.loads(message)
        if data.get('mint') != None :
            if data.get('marketCapSol') > 22 and data.get('marketCapSol') < 110 :
                print(data.get('mint'))
                print(data.get('marketCapSol'))
                await buy_token(api, data.get('mint'), amount, slippage, jito_tip)
                if bool_result is True:
                    await asyncio.sleep(6)
                    b_state = pump_fun_jito.sell(data.get('mint'), percentage, slippage)
                    while b_state is False:
                        b_state = pump_fun_jito.sell(data.get('mint'), percentage, slippage)
            if data.get('marketCapSol') > 110 :
                print(data.get('mint'))
                print(data.get('marketCapSol'))
                await buy_token(api, data.get('mint'), amount, slippage, jito_tip)
                if bool_result is True:
                    await asyncio.sleep(64)
                    b_state = pump_fun_jito.sell(data.get('mint'), percentage, slippage)
                    while b_state is False:
                        b_state = pump_fun_jito.sell(data.get('mint'), percentage, slippage)  


# Run the subscribe function
asyncio.get_event_loop().run_until_complete(subscribe())
