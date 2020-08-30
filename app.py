import hashlib
import time
import json
from flask import Flask, request

COIN_NAME = "KHC"

class Block:
    def __init__(self, index, previous_hash, timestamp, data, hash):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.hash = hash

class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_block(previous_hash='0', data={"genesis": True})  # Create the genesis block
        self.transactions = []

    def create_block(self, previous_hash, data):
        index = len(self.chain) + 1
        timestamp = time.time()
        hash = self.hash_block(index, previous_hash, timestamp, data)
        block = Block(index, previous_hash, timestamp, data, hash)
        self.chain.append(block)
        self.transactions = []  # Clear the transactions
        return block

    def hash_block(self, index, previous_hash, timestamp, data):
        block_string = f"{index}{previous_hash}{timestamp}{json.dumps(data, sort_keys=True)}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def add_transaction(self, sender, recipient, amount):
        self.transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })

    def mine_block(self):
        if not self.transactions:
            return False  # No transactions to mine
        last_block = self.chain[-1]
        new_block = self.create_block(previous_hash=last_block.hash, data=self.transactions)
        return new_block

    def get_chain(self):
        return [block.__dict__ for block in self.chain]

app = Flask(__name__)
blockchain = Blockchain()

@app.route('/transaction', methods=['POST'])
def create_transaction():
    data = request.get_json()
    blockchain.add_transaction(data['sender'], data['recipient'], data['amount'])
    return f'Transaction of {data["amount"]} {COIN_NAME} added!', 201

@app.route('/mine', methods=['GET'])
def mine():
    block = blockchain.mine_block()
    if block:
        return f'Block {block.index} mined with {len(block.data)} transactions!', 200
    return 'No transactions to mine!', 400

@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = blockchain.get_chain()
    return {
        'chain': chain_data,
        'coin': COIN_NAME
    }, 200

if __name__ == "__main__":
    app.run(port=5000)