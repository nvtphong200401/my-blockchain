from datetime import datetime

from Crypto.PublicKey import RSA

from block.block import Block
from block.block_header import BlockHeader
from common.io_blockchain import store_blockchain_in_memory
from node.merkle_tree import get_merkle_root
from transaction.transaction import Transaction
from transaction.transaction_input import TransactionInput
from transaction.transaction_output import TransactionOutput
from wallet.owner import Owner
from blockchain_user.albert import private_key as albert_private_key
from blockchain_user.bertrand import private_key as bertrand_private_key
from blockchain_user.camille import private_key as camille_private_key


satoshi_wallet = Owner()
albert_wallet = Owner(private_key=albert_private_key)
bertrand_wallet = Owner(private_key=bertrand_private_key)
camille_wallet = Owner(private_key=camille_private_key)


def initialize_blockchain():
    # initial block
    timestamp_0 = datetime.timestamp(datetime.fromisoformat('2011-11-04 00:05:23.111'))
    input_0 = TransactionInput(transaction_hash="abcd1234",
                               output_index=0)
    output_0 = TransactionOutput(public_key_hash=b"Albert",
                                 amount=40)
    transaction_0 = Transaction([input_0], [output_0])
    block_header_0 = BlockHeader(previous_block_hash="1111",
                                 timestamp=timestamp_0,
                                 nonce=2,
                                 merkle_root=get_merkle_root([transaction_0.transaction_data]))
    block_0 = Block(
        transactions=[transaction_0.transaction_data],
        block_header=block_header_0
    )

    timestamp_1 = datetime.timestamp(datetime.fromisoformat('2011-11-04 00:05:23.111'))
    input_0 = TransactionInput(transaction_hash=block_0.transactions[0]["transaction_hash"], output_index=0)
    output_0 = TransactionOutput(public_key_hash=bertrand_wallet.public_key_hash, amount=30)
    output_1 = TransactionOutput(public_key_hash=albert_wallet.public_key_hash, amount=10)
    transaction_1 = Transaction([input_0], [output_0, output_1])
    block_header_1 = BlockHeader(
        previous_block_hash=block_0.block_header.hash,
        timestamp=timestamp_1,
        nonce=3,
        merkle_root=get_merkle_root([transaction_1.transaction_data])
    )
    block_1 = Block(
        transactions=[transaction_1.transaction_data],
        block_header=block_header_1,
        previous_block=block_0,
    )
    timestamp_2 = datetime.timestamp(datetime.fromisoformat('2011-11-07 00:05:13.222'))
    input_0 = TransactionInput(transaction_hash=block_1.transactions[0]["transaction_hash"], output_index=1)
    output_0 = TransactionOutput(public_key_hash=camille_wallet.public_key_hash, amount=10)
    transaction_2 = Transaction([input_0], [output_0])
    block_header_2 = BlockHeader(
        previous_block_hash=block_1.block_header.hash,
        timestamp=timestamp_2,
        nonce=4,
        merkle_root=get_merkle_root([transaction_2.transaction_data])
    )
    block_2 = Block(
        transactions=[transaction_2.transaction_data],
        block_header=block_header_2,
        previous_block=block_1,
    )

    timestamp_3 = datetime.timestamp(datetime.fromisoformat('2011-11-09 00:11:13.333'))
    input_0 = TransactionInput(transaction_hash=block_1.transactions[0]["transaction_hash"], output_index=0)
    output_0 = TransactionOutput(public_key_hash=camille_wallet.public_key_hash, amount=5)
    output_1 = TransactionOutput(public_key_hash=bertrand_wallet.public_key_hash, amount=25)
    transaction_3 = Transaction([input_0], [output_0, output_1])
    block_header_3 = BlockHeader(
        previous_block_hash=block_2.block_header.hash,
        timestamp=timestamp_3,
        nonce=5,
        merkle_root=get_merkle_root([transaction_3.transaction_data])
    )
    block_3 = Block(
        transactions=[transaction_3.transaction_data],
        block_header=block_header_3,
        previous_block=block_2,
    )
    store_blockchain_in_memory(block_3)
