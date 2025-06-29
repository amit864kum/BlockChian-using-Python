# blockchain/block.py
import time
import hashlib

class Block:
    def __init__(self, index, transactions, previous_hash, difficulty):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.difficulty = difficulty
        self.hash = self.compute_hash()
        self.merkle_root = self.compute_merkle_root()

    def compute_hash(self):
        block_string = f"{self.index}{self.timestamp}{self.transactions}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def compute_merkle_root(self):
        tx_hashes = [hashlib.sha256(str(tx.to_dict()).encode()).hexdigest() for tx in self.transactions]
        if not tx_hashes:
            return ''
        while len(tx_hashes) > 1:
            if len(tx_hashes) % 2 != 0:
                tx_hashes.append(tx_hashes[-1])
            tx_hashes = [
                hashlib.sha256((tx_hashes[i] + tx_hashes[i + 1]).encode()).hexdigest()
                for i in range(0, len(tx_hashes), 2)
            ]
        return tx_hashes[0]

    def mine(self):
        prefix = '0' * self.difficulty
        while not self.hash.startswith(prefix):
            self.nonce += 1
            self.hash = self.compute_hash()
        return self.hash

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash,
            "difficulty": self.difficulty,
            "merkle_root": self.merkle_root
        }

    def __repr__(self):
        return (
            f"\nBlock #{self.index}\n"
            f"Timestamp   : {time.ctime(self.timestamp)}\n"
            f"Nonce       : {self.nonce}\n"
            f"Difficulty  : {self.difficulty}\n"
            f"Merkle Root : {self.merkle_root}\n"
            f"Prev Hash   : {self.previous_hash}\n"
            f"Curr Hash   : {self.hash}\n"
            f"Tx Count    : {len(self.transactions)}\n"
            f"Transactions: {[tx.to_dict() for tx in self.transactions]}\n"
        )
