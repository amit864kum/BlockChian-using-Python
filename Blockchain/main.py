# main.py
import threading
import time
import random
from miner_app import Miner
from blockchain.block import Block
from transactions.utxo_set import UTXOSet
from transactions.transaction import Transaction
from mempool.mempool import Mempool
from network.node import NodeNetwork
from Signatures import generate_keys
from utils.logger import setup_logger

NUM_MINERS = 3
DIFFICULTY = 3
logger = setup_logger("Main")

def vote_fn(block):
    for tx in block.transactions:
        if not tx.is_valid():
            return False
    if not block.hash.startswith('0' * block.difficulty):
        return False
    return True

def generate_transactions(wallets, mempool, utxo_set):
    while True:
        sender, recipient = wallets[0], wallets[1]
        amount = random.randint(1, 20)
        tx = Transaction(sender[1], recipient[1], amount)
        tx.sign_transaction(sender[0])
        if tx.is_valid():
            mempool.add_transaction(tx)
        time.sleep(1)

def run_simulation():
    blockchain = []
    utxo_set = UTXOSet()
    mempool = Mempool()
    node = NodeNetwork(num_miners=NUM_MINERS)
    wallets = [generate_keys() for _ in range(2)]
    utxo_set.add_utxo(wallets[0][1], 100)

    miner_keys = [generate_keys() for _ in range(NUM_MINERS)]

    genesis_block = Block(0, [], "0", DIFFICULTY)
    genesis_block.hash = genesis_block.compute_hash()
    blockchain.append(genesis_block)
    node.blockchain = blockchain
    logger.info("Initialized blockchain with genesis block.")

    tx_thread = threading.Thread(target=generate_transactions, args=(wallets, mempool, utxo_set))
    tx_thread.daemon = True
    tx_thread.start()
    logger.info("Transaction generator started.")

    while True:
        stop_flag = threading.Event()
        miners = []
        miner_ids = list(range(NUM_MINERS))
        random.shuffle(miner_ids)
        for i in miner_ids:
            miner = Miner(
                miner_id=i,
                blockchain=node.blockchain,
                mempool=mempool,
                utxo_set=utxo_set,
                difficulty=DIFFICULTY,
                stop_flag=stop_flag,
                broadcast_fn=lambda block: node.broadcast_block(block, stop_flag, vote_fn),
                miner_pub_key=miner_keys[i][1],
                miner_priv_key=miner_keys[i][0]
            )
            miners.append(miner)
            miner.start()
            logger.info(f"Started Miner {i}")
            time.sleep(random.uniform(0.001, 0.01))

        for miner in miners:
            miner.join()

        time.sleep(1)
        logger.info("Starting next mining round...\n")

if __name__ == '__main__':
    run_simulation()
