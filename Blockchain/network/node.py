# network/node.py
import threading
from collections import defaultdict

class NodeNetwork:
    def __init__(self, num_miners):
        self.num_miners = num_miners
        self.received_votes = defaultdict(list)
        self.vote_lock = threading.Lock()
        self.chain_lock = threading.Lock()
        self.blockchain = []

    def broadcast_block(self, block, stop_flag, vote_fn):
        stop_flag.set()
        print(f"[Network] Broadcasting block {block.hash}")
        threading.Thread(target=self.collect_votes, args=(block, vote_fn)).start()

    def collect_votes(self, block, vote_fn):
        for i in range(self.num_miners):
            vote = vote_fn(block)
            with self.vote_lock:
                self.received_votes[block.hash].append(vote)

            if len(self.received_votes[block.hash]) > self.num_miners // 2:
                with self.chain_lock:
                    self.blockchain.append(block)
                print(f"[Network] ✅ Block {block.hash[:10]}... added to blockchain by majority vote")
                break
