import json


# Each transaction output contains two field: the amount and the locking script.
# The locking script encumbers the output with the receiver address.
class TransactionOutput:
    def __init__(self, public_key_hash: bytes, amount: float):
        self.amount = amount
        self.locking_script = f"OP_DUP OP_HASH160 {public_key_hash} OP_EQUAL_VERIFY OP_CHECKSIG"

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict:
        return {
            "amount": self.amount,
            "locking_script": self.locking_script
        }
