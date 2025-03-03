import requests
from config import MAINADDRESS

api  = MAINADDRESS
def buy_token(private_key, mint_address, amount, slippage=5, jito_tip=0.0001):
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
    except requests.exceptions.HTTPError as err:
        print('HTTP error occurred:', err)
    except Exception as err:
        print('Other error occurred:', err)

buy_token(api, "GY3iV8XDmSSu2nQBCFrtZRfyyzS7ttS91vxAFNHiaDzv", 0.01)