import requests
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
import json
import binascii
import copy

from src.common.io_mem_pool import get_transactions_from_memory, store_transactions_in_memory
from src.contract.script import StackScript
from src.block.block import Block
from src.common.utils import calculate_hash
from src.node.other_node import OtherNode


class NodeTransaction:
    """
    For each transaction, nodes will combine the unlocking script from the transaction’s input to the locking script
    associated with the UTXO stored on the blockchain and compute the script. If the script passes, the transaction
    is valid, and if it fails, it’s invalid


    Example:
    {
        'inputs': [
            {
            "transaction_hash": "a26d9501f3fa92ffa9991cf05a72f8b9ca2d66e31e6221cecb66973671a81898", "output_index": 0,
             "unlocking_script": "<sender signature> <sender public key>"
            }
        ],
        'outputs': [
            {"amount": 10,
             "locking_script": "OP_DUP OP_HASH160 <receiver public key hash> OP_EQUAL_VERIFY OP_CHECKSIG"
             }
        ]
    }
    """

    def __init__(self, blockchain: Block):
        self.blockchain = blockchain
        self.transaction_data = {}
        self.signature = ""
        self.inputs = ""
        self.outputs = ""
        self.is_valid = False
        self.is_funds_sufficient = False

    def store(self):
        if self.is_valid and self.is_funds_sufficient:
            current_transactions = get_transactions_from_memory()
            current_transactions.append(self.transaction_data)
            store_transactions_in_memory(current_transactions)

    def receive(self, transaction: dict):
        self.transaction_data = transaction
        self.inputs = transaction["inputs"]
        self.outputs = transaction["outputs"]

    def validate_signature(self):
        transaction_data = copy.deepcopy(self.transaction_data)
        for count, tx_input in enumerate(transaction_data["inputs"]):
            tx_input_dict = json.loads(tx_input)
            public_key = tx_input_dict.pop("public_key")
            signature = tx_input_dict.pop("signature")
            transaction_data["inputs"][count] = json.dumps(tx_input_dict)
            signature_decoded = binascii.unhexlify(signature.encode("utf-8"))
            public_key_bytes = public_key.encode("utf-8")
            public_key_object = RSA.import_key(binascii.unhexlify(public_key_bytes))
            transaction_bytes = json.dumps(transaction_data, indent=2).encode('utf-8')
            transaction_hash = SHA256.new(transaction_bytes)
            pkcs1_15.new(public_key_object).verify(transaction_hash, signature_decoded)

    def get_transaction_from_utxo(self, utxo_hash: str) -> dict:
        current_block = self.blockchain
        while current_block:
            if utxo_hash == current_block.transaction_hash:
                return current_block.transaction_data
            current_block = current_block.previous_block

    def validate(self):
        for tx_input in self.inputs:
            input_dict = json.loads(tx_input)
            locking_script = self.get_locking_script_from_utxo(input_dict["transaction_hash"],
                                                               input_dict["output_index"])
            self.execute_script(input_dict["unlocking_script"], locking_script)

    def validate_funds(self):
        assert self.get_total_amount_in_inputs() == self.get_total_amount_in_outputs()

    def get_total_amount_in_inputs(self) -> int:
        total_in = 0
        for tx_input in self.inputs:
            input_dict = json.loads(tx_input)
            transaction_data = self.get_transaction_from_utxo(input_dict["transaction_hash"])
            utxo_amount = json.loads(transaction_data["outputs"][input_dict["output_index"]])["amount"]
            total_in = total_in + utxo_amount
        return total_in

    def get_total_amount_in_outputs(self) -> int:
        total_out = 0
        for tx_output in self.outputs:
            output_dict = json.loads(tx_output)
            amount = output_dict["amount"]
            total_out = total_out + amount
        return total_out

    def validate_funds_are_owned_by_sender(self):
        for tx_input in self.inputs:
            input_dict = json.loads(tx_input)
            public_key = input_dict["public_key"]
            sender_public_key_hash = calculate_hash(calculate_hash(public_key, hash_function="sha256"),
                                                    hash_function="ripemd160")
            transaction_data = self.get_transaction_from_utxo(input_dict["transaction_hash"])
            public_key_hash = json.loads(transaction_data["outputs"][input_dict["output_index"]])["public_key_hash"]
            assert public_key_hash == sender_public_key_hash

    def execute_script(self, unlocking_script, locking_script):
        """
        we simply create an empty stack, scroll through each element of each script and apply the methods to the stack

        :param unlocking_script:
        :param locking_script:
        :return:
        """
        unlocking_script_list = unlocking_script.split(" ")
        locking_script_list = locking_script.split(" ")
        stack_script = StackScript(self.transaction_data)
        for element in unlocking_script_list:
            if element.startswith("OP"):
                class_method = getattr(StackScript, element.lower())
                class_method(stack_script)
            else:
                stack_script.push(element)
        for element in locking_script_list:
            if element.startswith("OP"):
                class_method = getattr(StackScript, element.lower())
                class_method(stack_script)
            else:
                stack_script.push(element)

    def get_locking_script_from_utxo(self, utxo_hash: str, utxo_index: int):
        transaction_data = self.get_transaction_from_utxo(utxo_hash)
        return json.loads(transaction_data["outputs"][utxo_index])["locking_script"]

    def broadcast(self):
        node_list = [OtherNode("127.0.0.1", 5001), OtherNode("127.0.0.1", 5002)]
        for node in node_list:
            try:
                node.send(self.transaction_data)
            except requests.ConnectionError:
                pass
