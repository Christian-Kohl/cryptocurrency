import hashlib
import time
from flask import Flask, jsonify, request
from uuid import uuid4


class Block:

    def __init__(self, index, proof_no, prev_hash, data, timestamp=None):
        self.index = index
        self.proof_no = proof_no
        self.prev_hash = prev_hash
        self.data = data
        self.timestamp = time.time()

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

    def set(self):
        return {
                'index': self.index,
                'proof_no': self.proof_no,
                'prev_hash': self.prev_hash,
                'data': self.data,
                'timestamp': self.timestamp
                }


class BlockChain:
    def __init__(self):
        self.chain = []
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

    def new_data(self, sender, recipient, quantity):
        self.current_data.append({
            'sender': sender,
            'recipient': recipient,
            'quantity': quantity
        })
        return len(self.chain) + 1

    def proof_of_work(self, last_proof):
        proof_no = 0
        while BlockChain.verifying_proof(last_proof, proof_no) is False:
            proof_no += 1
        return proof_no

    def proof_of_mine(self, proof_to_check):
        if BlockChain.verifying_proof(self.latest_block().proof_no,
                                      proof_to_check):
            return True
        else:
            return False

    def latest_proof(self):
        return self.latest_block().proof_no

    @staticmethod
    def verifying_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def latest_block(self):
        return self.chain[-1]

    def get_chain(self):
        chain_json = []
        for i in self.chain:
            chain_json += [i.set()]
        return {'chain': chain_json, 'length': len(blockchain.chain)}


app = Flask(__name__)

node_identifier = str(uuid4()).replace('-', '')
blockchain = BlockChain()


@app.route('/mine', methods=['GET'])
def mine():

    last_block = blockchain.latest_block()
    last_proof = last_block.proof_no
    proof = blockchain.proof_of_work(last_proof)

    blockchain.new_data(
        sender="0",
        recipient=node_identifier,
        quantity=1,
    )

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


@app.route('/mine', methods=['POST'])
def user_mine():
    values = request.get_json()
    required = ['miner', 'proof']
    if not all(k in values for k in required):
        return 'Missing valuse', 400
    presented_proof = values['proof']
    if blockchain.proof_of_mine(presented_proof):
        blockchain.new_data(
                sender="0",
                recipient=values['miner'],
                quantity=1
                )
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


@app.route('/transaction/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400
    index = blockchain.new_data(values['sender'],
                                values['recipient'],
                                values['amount'])
    response = {'message':
                f'Transaction is scheduled to be added to Block No. {index}'
                }
    return jsonify(response), 201


@app.route('/chain', methods=["GET"])
def full_chain():
    response = blockchain.get_chain()
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
