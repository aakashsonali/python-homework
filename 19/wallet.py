from constants import *
import subprocess
import json
import os
from bit import PrivateKeyTestnet
from bit.network import NetworkAPI
from web3 import Web3, middleware, Account
from web3.gas_strategies.time_based import medium_gas_price_strategy
from web3.middleware import geth_poa_middleware
w3 = Web3(Web3.HTTPProvider('http://localhost:8545'))
w3.middleware_onion.inject(geth_poa_middleware,layer=0)
w3.eth.setGasPriceStrategy(medium_gas_price_strategy)

mnemonic = os.getenv('MNEMONIC', 'brand expire evolve ostrich patient comfort twelve boost inmate about page quality')

def derive_wallets(coin=BTC, mnemonic=mnemonic):
    command = f'./derive -g --mnemonic={mnemonic} --cols=path,address,privkey,pubkey --coin={coin} --numderive=3 --format=json'
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    p_status = p.wait()
    keys = json.loads(output)
    print(keys)

def priv_key_to_account(coin, private_key):
    if coin == ETH:
        return Account.privateKeyToAccount(private_key)
    if coin == BTCTEST:
        return PrivateKeyTestnet(private_key)

def create_tx(coin, account, to, amount):
    if coin == ETH:
        value = w3.toWei(amount, "ether")
        gasEstimate = w3.eth.estimateGas({"to":to,"from":account,"amount":value})
        return{
            "to":to,
            "from":account,
            "value":value,
            "gas":hasEstimate,
            "gasPrice":w3.eth.generateGasPrice(),
            "nonce":w3.eth.getTransactionCount(account),
            "chainID":w3.eth.chain_id
        }
    if coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address,[(to,amount,BTC)])
    
def send_tx(coin,account,to,amount):
    if coin == ETH:
        raw_tx = create_tx(coin,account.address,to,amount)
        signed = account.signTransaction(raw_tx)
        return w3.eth.sendRawTransaction(signed.rawTransaction)
    if coin == BTCTEST:
        raw_tx = create_tx(coin, account, to, amount)
        signed = account.sign_transaction(raw_tx)
        return NetworkAPI.broadcast_tx_testnet(signed)
    
coin = {ETH: derive_wallets(coin=ETH),
        BTCTEST: derive_wallets(coin=BTCTEST),
       }

print(coin)