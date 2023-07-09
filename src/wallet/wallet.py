import base58
from Crypto.PublicKey import RSA

from src.common.utils import calculate_hash
from src.node.node import Node
from src.transaction.transaction import Transaction
from src.transaction.transaction_input import TransactionInput
from src.transaction.transaction_output import TransactionOutput
from src.wallet.owner import Owner
import requests


class Wallet:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.node = Node(ip="127.0.0.1", port=5000)

    def process_transaction(self, inputs: [TransactionInput], outputs: [TransactionOutput]) -> requests.Response:
        transaction = Transaction(self.owner, inputs, outputs)
        transaction.sign()
        return self.node.post(endpoint="transactions", data={"transaction": transaction.transaction_data})
