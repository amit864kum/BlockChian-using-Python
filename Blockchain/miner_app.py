# === miner_app.py ===
import threading
import time
import random
from blockchain.block import Block
from proof_of_work import mine_block
from utils.logger import setup_logger
from transactions.transaction import Transaction

class Miner(threading.Thread):
    def __init__(self, miner_id, blockchain, mempool, utxo_set, difficulty, stop_flag, broadcast_fn, miner_pub_key, miner_priv_key, max_tx_per_block=3):
        super().__init__()
        self.miner_id = miner_id
        self.blockchain = blockchain
        self.mempool = mempool
        self.utxo_set = utxo_set
        self.difficulty = difficulty
        self.stop_flag = stop_flag
        self.broadcast_fn = broadcast_fn
        self.miner_pub_key = miner_pub_key
        self.miner_priv_key = miner_priv_key
        self.max_tx_per_block = max_tx_per_block
        self.logger = setup_logger(f"Miner {self.miner_id}")
        self.daemon = True

    def run(self):
        while True:
            if self.stop_flag.is_set():
                self.logger.info("❌ Stopped: Another miner already mined the block.")
                break

            txs = self.mempool.get_transactions(self.max_tx_per_block)
            if len(txs) < self.max_tx_per_block:
                time.sleep(0.5)
                continue

            valid_txs = []
            for tx in txs:
                if tx.is_valid() and self.utxo_set.is_valid_transaction(tx):
                    valid_txs.append(tx)

            if len(valid_txs) < self.max_tx_per_block:
                continue

            last_block = self.blockchain[-1]
            base_reward = random.randint(10, 30)
            tx_fees = sum(tx.amount * 0.01 for tx in valid_txs)
            reward_amount = base_reward + tx_fees

            reward_tx = Transaction(
                sender_pub=self.miner_pub_key,
                recipient_pub=self.miner_pub_key,
                amount=reward_amount
            )
            reward_tx.tx_type = "reward"
            reward_tx.sign_transaction(self.miner_priv_key)
            valid_txs.append(reward_tx)

            self.utxo_set.apply_transaction(reward_tx)

            new_block = Block(index=last_block.index + 1,
                              transactions=valid_txs,
                              previous_hash=last_block.hash,
                              difficulty=self.difficulty)

            self.logger.info("Started mining a block.")
            mined_block = mine_block(new_block, self.difficulty, self.stop_flag)

            if mined_block:
                self.logger.info(f"✅ Block mined Successfully: {mined_block.hash}")
                self.logger.info(f"I am the winner miner: Miner {self.miner_id}")
                self.logger.info(f"💰 Reward Breakdown → Base: {base_reward:.2f} | Fees: {tx_fees:.2f} | Total: {reward_amount:.2f} tokens")
                self.logger.info(f"{mined_block}")
                self.broadcast_fn(mined_block)
                break
