import json

from block.block_header import BlockHeader


class Block:
    def __init__(
            self,
            transactions: [dict],
            block_header: BlockHeader,
            previous_block=None,
    ):
        self.block_header = block_header
        self.transactions = transactions
        self.previous_block = previous_block

    def __eq__(self, other):
        try:
            assert self.block_header == other.block_header
            assert self.transactions == other.transactions
            return True
        except AssertionError:
            return False

    def __len__(self) -> int:
        i = 1
        current_block = self
        while current_block.previous_block:
            i = i + 1
            current_block = current_block.previous_block
        return i

    def __str__(self):
        return json.dumps({"timestamp": self.block_header.timestamp,
                           "hash": self.block_header.hash,
                           "transactions": self.transactions})

    @property
    def to_dict(self):
        block_list = []
        current_block = self
        while current_block:
            block_data = {
                "header": current_block.block_header.to_dict,
                "transactions": current_block.transactions
            }
            block_list.append(block_data)
            current_block = current_block.previous_block
        return block_list

    @property
    def to_json(self) -> str:
        return json.dumps(self.to_dict)
    #
    # @staticmethod
    # def set_transactions_hashes(transactions: list) -> list:
    #     for transaction in transactions:
    #         transaction_data = {"inputs": transaction["inputs"],
    #                             "outputs": transaction["outputs"]}
    #         transaction_str = json.dumps(transaction_data, indent=2)
    #         transaction["transaction_hash"] = calculate_hash(transaction_str)
    #     return transactions

    def get_transaction(self, transaction_hash: dict) -> dict:
        current_block = self
        while current_block.previous_block:
            for transaction in current_block.transactions:
                if transaction["transaction_hash"] == transaction_hash:
                    return transaction
            current_block = current_block.previous_block
        return {}

    def get_user_utxos(self, user: str) -> dict:
        return_dict = {
            "user": user,
            "total": 0,
            "utxos": []
        }
        current_block = self
        while current_block.previous_block:
            for transaction in current_block.transactions:
                print(transaction)
                for output in transaction["outputs"]:
                    locking_script = output["locking_script"]
                    for element in locking_script.split(" "):
                        if not element.startswith("OP") and element == user:
                            return_dict["total"] = return_dict["total"] + output["amount"]
                            return_dict["utxos"].append(
                                {"amount": output["amount"], "transaction_hash": transaction["transaction_hash"]})
            current_block = current_block.previous_block
        return return_dict

    def get_transaction_from_utxo(self, utxo_hash: str) -> dict:
        current_block = self
        while current_block:
            for transaction in current_block.transactions:
                if utxo_hash == transaction["transaction_hash"]:
                    return transaction
            current_block = current_block.previous_block

    def get_locking_script_from_utxo(self, utxo_hash: str, utxo_index: int):
        transaction_data = self.get_transaction_from_utxo(utxo_hash)
        return transaction_data["outputs"][utxo_index]["locking_script"]