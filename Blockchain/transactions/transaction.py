#transaction.py
import json
from hashlib import sha256
from Signatures import sign, verify, serialize_public_key, deserialize_public_key

class Transaction:
    def __init__(self, sender_pub, recipient_pub, amount, signature=None):
        self.sender_pub = serialize_public_key(sender_pub).decode()
        self.recipient_pub = serialize_public_key(recipient_pub).decode()
        self.amount = amount
        self.signature = signature

    def to_dict(self):
        return {
            'sender': self.sender_pub,
            'recipient': self.recipient_pub,
            'amount': self.amount
        }

    def sign_transaction(self, sender_private_key):
        tx_str = json.dumps(self.to_dict(), sort_keys=True).encode()
        self.signature = sign(tx_str, sender_private_key)

    def is_valid(self):
        if not self.signature:
            return False
        tx_str = json.dumps(self.to_dict(), sort_keys=True).encode()
        pub_key = deserialize_public_key(self.sender_pub.encode())
        return verify(tx_str, self.signature, pub_key)

    def __repr__(self):
        return f"Tx({self.sender_pub[:8]} -> {self.recipient_pub[:8]} : {self.amount})"
