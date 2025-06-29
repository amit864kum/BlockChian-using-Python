#mempool.py
import threading
from collections import deque

class Mempool:
    def __init__(self):
        self.transactions = deque()
        self.lock = threading.Lock()

    def add_transaction(self, tx):
        with self.lock:
            self.transactions.append(tx)

    def get_transactions(self, count):
        with self.lock:
            if len(self.transactions) >= count:
                txs = [self.transactions.popleft() for _ in range(count)]
                return txs
            return []

    def size(self):
        with self.lock:
            return len(self.transactions)

    def all_transactions(self):
        with self.lock:
            return list(self.transactions)
