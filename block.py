from flask import Flask, jsonify, request
from uuid import uuid4
import json
from blockchain import BlockChain
from database import DatabaseConnector


# Starts the basics of the flask app
app = Flask(__name__)
dbC = DatabaseConnector("testChain.sqlite")

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
    previous_hash = last_block.calculate_hash
    block = blockchain.construct_block(proof, previous_hash)

    response = {
        'message': 'The new block has been forged',
        'index': block.index,
        'transactions': block.data,
        'proof': block.proof_no,
        'previous_hash': block.prev_hash
    }
    dbC.addBlock(blockchain.latest_block())
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
        previous_hash = blockchain.latest_block().calculate_hash
        block = blockchain.construct_block(presented_proof, previous_hash)
        response = {
                'message': 'The new block has been forged',
                'index': block.index,
                'transactions': block.data,
                'proof': block.proof_no,
                'previous_hash': block.prev_hash
                }
        dbC.addBlock(blockchain.latest_block())
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


@app.route('/user/new', methods=["POST"])
def new_user():
    return


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
