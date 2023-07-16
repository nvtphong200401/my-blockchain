from block.block import Block
from block.block_header import BlockHeader
from common.constants import BLOCK_REWARD, NUMBER_OF_LEADING_ZEROS
from common.io_blockchain import store_blockchain_in_memory
from node.network import Network
from node.node_transaction import NodeTransaction


class NewBlockException(Exception):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


class Blockchain:
    def __init__(self, blockchain: Block, network: Network):
        self.blockchain = blockchain
        self.network = network
        self.new_block = None

    def receive(self, new_block: dict):
        block_header = BlockHeader(**new_block["header"])
        self.new_block = Block(transactions=new_block["transactions"], block_header=block_header)
        try:
            assert self.blockchain.block_header.hash == self.new_block.block_header.previous_block_hash
        except AssertionError:
            print("Previous block provided is not the most recent block")
            raise NewBlockException("", "Previous block provided is not the most recent block")

    def validate(self):
        self._validate_hash()
        self._validate_transactions()

    def _validate_hash(self):
        new_block_hash = self.new_block.block_header.get_hash()
        number_of_zeros_string = "".join([str(0) for _ in range(NUMBER_OF_LEADING_ZEROS)])
        try:
            assert new_block_hash.startswith(number_of_zeros_string)
        except AssertionError:
            print('Proof of work validation failed')
            raise NewBlockException("", "Proof of work validation failed")

    def _validate_transactions(self):
        input_amount = 0
        output_amount = 0
        for transaction in self.new_block.transactions:
            transaction_validation = NodeTransaction(self.blockchain, self.network)
            transaction_validation.receive(transaction=transaction)
            transaction_validation.validate()
            input_amount = input_amount + transaction_validation.get_total_amount_in_inputs()
            output_amount = output_amount + transaction_validation.get_total_amount_in_outputs()
        self._validate_funds(input_amount, output_amount)

    @staticmethod
    def _validate_funds(input_amount: float, output_amount: float):
        assert input_amount + BLOCK_REWARD == output_amount

    def add(self):
        self.new_block.previous_block = self.blockchain
        store_blockchain_in_memory(self.new_block)

    def broadcast(self):
        node_list = self.network.known_nodes
        for node in node_list:
            if node.hostname != self.network.node.hostname:
                block_content = {
                    "block": {
                        "header": self.new_block.block_header.to_dict,
                        "transactions": self.new_block.transactions
                    }
                }
                node.send_new_block(block_content)
