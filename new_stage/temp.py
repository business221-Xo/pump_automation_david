import base58
from solders.keypair import Keypair
WALLETS_AMOUNT = 4
generated_wallets = []
def generate_wallet():
    for x in range(WALLETS_AMOUNT):
        account = Keypair()
        publicKey = str(account.pubkey())
        privateKey = base58.b58encode(account.secret() + base58.b58decode(str(account.pubkey()))).decode('utf-8')
        wallet = {
            "pubKey": publicKey,
            "priKey": privateKey
        }
        generated_wallets.append(wallet)
generate_wallet()
print(generated_wallets)