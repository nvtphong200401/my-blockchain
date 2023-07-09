import json
from datetime import datetime

from src.block.block import Block
from src.block.block_exception import BlockException
from src.block.block_header import BlockHeader
from src.common.constants import NUMBER_OF_LEADING_ZEROS
from src.common.io_blockchain import get_blockchain_from_memory
from src.common.io_mem_pool import get_transactions_from_memory
from src.common.utils import calculate_hash
from src.node.merkle_tree import get_merkle_root
from src.node.other_node import OtherNode


class ProofOfWork:
    def __init__(self):
        self.blockchain = get_blockchain_from_memory()
        self.new_block = None

    @staticmethod
    def get_nonce(block_header: BlockHeader) -> int:
        block_header_hash = ""
        nonce = block_header.nonce
        starting_zeros = "".join([str(0) for _ in range(NUMBER_OF_LEADING_ZEROS)])
        while not block_header_hash.startswith(starting_zeros):
            nonce = nonce + 1
            block_header_content = {
                "previous_block_hash": block_header.previous_block_hash,
                "merkle_root": block_header.merkle_root,
                "timestamp": block_header.timestamp,
                "nonce": nonce
            }
            block_header_hash = calculate_hash(json.dumps(block_header_content))
        return nonce

    def create_new_block(self):
        transactions = get_transactions_from_memory()
        if transactions:
            block_header = BlockHeader(
                merkle_root=get_merkle_root(transactions),
                previous_block_hash=self.blockchain.block_header.hash,
                timestamp=datetime.timestamp(datetime.now()),
                nonce=0
            )
            block_header.nonce = self.get_nonce(block_header)
            block_header.hash = block_header.get_hash()
            self.new_block = Block(transactions=transactions, block_header=block_header)
        else:
            raise BlockException("", "No transaction in mem_pool")

    def broadcast(self):
        node_list = [OtherNode("127.0.0.1", 5000)]
        for node in node_list:
            block_content = {
                "block": {
                    "header": self.new_block.block_header.to_dict,
                    "transactions": self.new_block.transactions
                }
            }
            node.send_new_block(block_content)
