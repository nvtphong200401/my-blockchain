import binascii
import json

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

from common.utils import calculate_hash


class Stack:
    def __init__(self):
        self.elements = []

    def push(self, element):
        self.elements.append(element)

    def pop(self):
        return self.elements.pop()



class StackScript(Stack):
    """
    OP_DUP: Duplicates the top stack item (<pubKey>)
    OP_HASH_160: The top stack item (<pubKey>) is hashed twice, first with SHA-256 and then with RIPEMD-160.
    OP_EQUAL_VERIFY: Fails if the last 2 items in the stack don’t match ( <pubKey> and <pubKeyHash>)
    OP_CHECK_SIG: The entire transaction’s outputs, inputs, and script are hashed. The signature <sig> is validated against this hash.
    """
    def __init__(self, transaction_data: dict):
        super().__init__()
        for count, tx_input in enumerate(transaction_data["inputs"]):
            tx_input_dict = json.loads(tx_input)
            tx_input_dict.pop("unlocking_script")
            transaction_data["inputs"][count] = json.dumps(tx_input_dict)
        self.transaction_data = transaction_data
    def op_dup(self):
        """
        simply duplicates the top most element of the stack, which is the public key
        :return:
        """
        public_key = self.pop()
        self.push(public_key)
        self.push(public_key)

    def op_hash160(self):
        """
        hashes the last element from the stack (the public key) twice
        :return:
        """
        public_key = self.pop()
        self.push(calculate_hash(calculate_hash(public_key, hash_function="sha256"), hash_function="ripemd160"))

    def op_equalverify(self):
        """
        validates that the last 2 elements from the stack are equal
        :return:
        """
        last_element_1 = self.pop()
        last_element_2 = self.pop()
        assert last_element_1 == last_element_2

    def op_checksig(self, transaction_data: dict):
        """
        validates that the signature from the unlocking script is valid
        """
        public_key = self.pop()
        signature = self.pop()
        signature_decoded = binascii.unhexlify(signature.encode("utf-8"))
        public_key_bytes = public_key.encode("utf-8")
        public_key_object = RSA.import_key(binascii.unhexlify(public_key_bytes))
        transaction_bytes = json.dumps(self.transaction_data, indent=2).encode('utf-8')
        transaction_hash = SHA256.new(transaction_bytes)
        pkcs1_15.new(public_key_object).verify(transaction_hash, signature_decoded)