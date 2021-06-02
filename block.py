import hashlib
import time
from flask import Flask, jsonify, request
from uuid import uuid4
import json


# Class for the block entity
class Block:

    def __init__(self, index, proof_no, prev_hash, data, timestamp=None):
        self.index = index
        self.proof_no = proof_no
        self.prev_hash = prev_hash
        self.data = data
        self.timestamp = time.time()

    # Calculates the hash of the block
    @property
    def calculate_hash(self):
        block_of_string = "{}{}{}{}{}".format(
                self.index,
                self.proof_no,
                self.prev_hash,
                self.data,
                self.timestamp
                )
        return hashlib.sha256(block_of_string.encode()).hexdigest()

    # returns the data of the block in a set
    def set(self):
        return {
                'index': self.index,
                'proof_no': self.proof_no,
                'prev_hash': self.prev_hash,
                'data': self.data,
                'timestamp': self.timestamp
                }


# Class for the blockchain itself
class BlockChain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.current_data = []
        self.nodes = set()
        self.construct_genesis()

    def construct_genesis(self):
        self.construct_block(proof_no=0, prev_hash=0)

    def construct_block(self, proof_no, prev_hash):
        block = Block(
                index=len(self.chain),
                proof_no=proof_no,
                prev_hash=prev_hash,
                data=self.current_data)
        self.current_data = []

        self.chain.append(block)
        return block

    def check_validity(block, prev_block):
        if prev_block.index + 1 != block.index:
            return False
        elif prev_block.calculate_hash() != block.prev_hash:
            return False
        elif not BlockChain.verifying_proof(block.proof_no,
                                            prev_block.proof_no):
            return False
        elif block.timestamp <= prev_block.timestamp:
            return False
        return True

    # Adds a pending transaction to the list,
    # and checks if the request fulfills a transaction
    def add_pending(self, transaction_data):
        completed = False

        # Goes through the current pending transactions
        for pender in self.pending_transactions:

            # Removes expired transaction stubs
            if pender['timestamp'] + 3600 < time.time():
                self.pending_transactions.remove(pender)
                continue

            # Check whether there is an outstanding stub
            if ((pender['sender'] == transaction_data['transactor'] and
               pender['transactor'] == transaction_data['recipient'] and
               pender['amount'] == transaction_data['amount']) or
               (pender['recipient'] == transaction_data['transactor'] and
               pender['transactor'] == transaction_data['sender'] and
               pender['amount'] == transaction_data['amount'])):
                completed = True
                break

        # If there is a new complete transaction adds it
        if completed:
            self.pending_transactions.remove(pender)
            self.new_data(transaction_data['sender'],
                          transaction_data['recipient'],
                          transaction_data['amount'])
            return True
        else:
            transaction_data['timestamp'] = time.time()
            self.pending_transactions += [transaction_data]
            return False

    # Adds the new transaction to the next block
    def new_data(self, sender, recipient, quantity):
        self.current_data.append({
            'sender': sender,
            'recipient': recipient,
            'quantity': quantity
        })
        return len(self.chain) + 1

    # Mines the proof of work for the next block
    def proof_of_work(self, last_proof):
        proof_no = 0
        while BlockChain.verifying_proof(last_proof, proof_no) is False:
            proof_no += 1
        return proof_no

    # Checks whether the proof given is correct
    def proof_of_mine(self, proof_to_check):
        if BlockChain.verifying_proof(self.latest_block().proof_no,
                                      proof_to_check):
            return True
        else:
            return False

    # Returns the proof of the latest block
    def latest_proof(self):
        return self.latest_block().proof_no

    # Checks whether the provided proof is correct
    @staticmethod
    def verifying_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    # Returns the last block in the chain
    def latest_block(self):
        return self.chain[-1]

    # Returns the whole chain as a json object
    def get_chain(self):
        chain_json = []
        for i in self.chain:
            chain_json += [i.set()]
        return {'chain': chain_json, 'length': len(blockchain.chain)}


# Starts the basics of the flask app
app = Flask(__name__)

node_identifier = str(uuid4()).replace('-', '')
blockchain = BlockChain()


# Automatically mines the next proof, used for testing purposes
@app.route('/mine', methods=['GET'])
def mine():

    last_block = blockchain.latest_block()
    last_proof = last_block.proof_no
    proof = blockchain.proof_of_work(last_proof)

    # pays the 'miner'
    blockchain.new_data(
        sender="0",
        recipient=node_identifier,
        quantity=1,
    )

    # Creates a new block
    previous_hash = last_block.prev_hash
    block = blockchain.construct_block(proof, previous_hash)

    response = {
        'message': 'The new block has been forged',
        'index': block.index,
        'transactions': block.data,
        'proof': block.proof_no,
        'previous_hash': block.prev_hash
    }
    return jsonify(response), 200


# Allows a user to mine with their own proof
@app.route('/mine', methods=['POST'])
def user_mine():

    # checking validity
    values = request.get_json()
    required = ['miner', 'proof']
    if not all(k in values for k in required):
        return 'Missing values', 400
    presented_proof = values['proof']

    # Check if the proof number is correct
    if blockchain.proof_of_mine(presented_proof):

        # Pays the miner
        blockchain.new_data(
                sender="0",
                recipient=values['miner'],
                quantity=1
                )

        # Construct new block
        previous_hash = blockchain.latest_block().prev_hash
        block = blockchain.construct_block(presented_proof, previous_hash)
        response = {
                'message': 'The new block has been forged',
                'index': block.index,
                'transactions': block.data,
                'proof': block.proof_no,
                'previous_hash': block.prev_hash
                }
        return jsonify(response), 200
    else:
        return 'That is not the correct proof, sorry!', 400


# Endpoint to create a new transaction
@app.route('/transaction/new', methods=['POST'])
def new_transaction():

    # Check if the request is formatted correctly
    values = json.loads(request.data, strict=False)
    required = ['sender', 'recipient', 'amount', 'transactor']
    if not all(k in values for k in required):
        return 'Missing values', 400
    transaction_data = values

    # Check if the transaction is pending, or if this request completes it.
    if blockchain.add_pending(transaction_data):
        index = blockchain.latest_block().index + 1
        response = {
                'message':
                f'Transaction is scheduled to be added to Block No. {index}'
                }
        return jsonify(response), 201
    else:
        response = {'message':
                    'Transaction currently pending'
                    }
        return jsonify(response), 200


# Endpoint to retrieve the current blockchain in its entirety
@app.route('/chain', methods=["GET"])
def full_chain():
    response = blockchain.get_chain()
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
