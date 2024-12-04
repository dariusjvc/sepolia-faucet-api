from celery import shared_task
from web3 import Web3
from .models import Transaction 
from datetime import timedelta
from django.utils import timezone

import os

from celery import Celery

app = Celery('myproject')

# Using the redis broker
app.conf.broker_url = 'redis://redis:6379/0'
app.conf.result_backend = 'redis://redis:6379/0'

@shared_task
def send_funds(wallet_address, private_key):
    w3 = Web3(Web3.HTTPProvider("https://eth-sepolia.g.alchemy.com/v2/bv_j0Tcj4zJd-sGPWqBqFOD4aoPGxohe"))
    
    from_address = os.environ.get('FAUCET_ADDRESS')

    gas_price = w3.eth.gas_price 

    transaction = {
        'to': wallet_address,
        'value': w3.toWei(0.0001, 'ether'),
        'gas': 2000000,
        'gasPrice': gas_price,
        'nonce': w3.eth.getTransactionCount(from_address),
        'chainId': 11155111  # Sepolia ChaiId
    }

    # signed_txn = w3.eth.account.signTransaction(transaction, private_key)
    # txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    try:
        signed_txn = w3.eth.account.signTransaction(transaction, private_key) # added signed_tx and txn_hash inside try
        txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction) # added signed_tx and txn_hash inside try
        # Save the successful transaction to the database
        Transaction.objects.create(
            wallet_address=wallet_address,
            transaction_id=w3.toHex(txn_hash),
            status=Transaction.SUCCESS,
            timestamp=timezone.now()
        )
        return w3.toHex(txn_hash)
    except Exception as e:
        # Save the failed transaction to the database
        Transaction.objects.create(
            wallet_address=wallet_address,
            # transaction_id=None,
            status=Transaction.FAILED,
            timestamp=timezone.now(),
            error_message=str(e)
        )
        raise e