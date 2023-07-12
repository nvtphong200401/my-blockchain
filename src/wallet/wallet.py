import base58
from Crypto.PublicKey import RSA

from common.utils import calculate_hash
from node.node import Node
from transaction.transaction import Transaction
from transaction.transaction_input import TransactionInput
from transaction.transaction_output import TransactionOutput
from wallet.owner import Owner
import requests


class Wallet:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.node = Node(ip="127.0.0.1", port=5000)

    def process_transaction(self, inputs: [TransactionInput], outputs: [TransactionOutput]) -> requests.Response:
        transaction = Transaction(self.owner, inputs, outputs)
        transaction.sign()
        return self.node.post(endpoint="transactions", data={"transaction": transaction.transaction_data})
