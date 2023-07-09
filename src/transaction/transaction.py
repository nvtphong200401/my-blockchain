import binascii
import json

from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15
from src.transaction.transaction_input import TransactionInput
from src.transaction.transaction_output import TransactionOutput
from src.wallet.owner import Owner


class Transaction:
    def __init__(self, owner: Owner, inputs: [TransactionInput], outputs: [TransactionOutput]):
        self.owner = owner
        self.inputs = inputs
        self.outputs = outputs

    def sign_transaction_data(self):
        transaction_dict = {"inputs": [tx_input.to_json(with_unlocking_script=False) for tx_input in self.inputs],
                            "outputs": [tx_output.to_json() for tx_output in self.outputs]}
        transaction_bytes = json.dumps(transaction_dict, indent=2).encode('utf-8')
        hash_object = SHA256.new(transaction_bytes)
        signature = pkcs1_15.new(self.owner.private_key).sign(hash_object)
        return signature

    def sign(self):
        signature_hex = binascii.hexlify(self.sign_transaction_data()).decode("utf-8")
        for transaction_input in self.inputs:
            transaction_input.unlocking_script = f"{signature_hex} {self.owner.public_key_hex}"

    @property
    def transaction_data(self) -> dict:
        return {
            "inputs": [i.to_json() for i in self.inputs],
            "outputs": [i.to_json() for i in self.outputs]
        }