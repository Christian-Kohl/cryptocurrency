from flask import Flask, jsonify, request
from sqlite3 import Error
from uuid import uuid4
import json
from blockchain import BlockChain
from database import DatabaseConnector


# Starts the basics of the flask app
dbC = DatabaseConnector("testChain.sqlite")

node_identifier = str(uuid4()).replace('-', '')
users = dbC.loadUsers()
userDict = {user[0]: list(user[1:]) for user in users}

blocks = dbC.loadBlocks()
datas = dbC.loadData()

blockchain = BlockChain(blocks, datas)
app = Flask(__name__)


# Automatically mines the next proof, used for testing purposes
@app.route('/mine', methods=['GET'])
def mine():

    last_block = blockchain.latest_block()
    last_proof = last_block.proof_no
    proof = blockchain.proof_of_work(last_proof)

    # pays the 'miner'
    blockchain.new_data(
        sender="0",
        recipient="Christian",
        quantity=1,
    )
    userDict['Christian'][1] += 1
    dbC.updateUser("Christian", userDict['Christian'][1])
    # Creates a new block
    previous_hash = last_block.calculate_hash
    for dat in blockchain.current_data:
        if dat['sender'] != '0':
            dbC.updateUser(dat['sender'], userDict[dat['sender']][1])
        dbC.updateUser(dat['recipient'], userDict[dat['recipient']][1])
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

        try:
            user = values['miner']
            userDict[user]
            # Pays the miner
            blockchain.new_data(
                    sender="0",
                    recipient=user,
                    quantity=1
                    )
            userDict[user][1] += 1
            dbC.updateUser(user, userDict[user][1])

            # Construct new block
            previous_hash = blockchain.latest_block().calculate_hash
            for dat in blockchain.current_data:
                print(dat)
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
        except Error as e:
            print(e)
            return "user doesn't exist", 401
    else:
        return 'That is not the correct proof, sorry!', 400


# Endpoint to create a new transaction
@app.route('/transaction/new', methods=['POST'])
def new_transaction():

    # Check if the request is formatted correctly
    values = json.loads(request.data, strict=False)
    required = ['sender', 'recipient', 'amount', 'transactor', 'password']
    if not all(k in values for k in required):
        return 'Missing values', 400
    transaction_data = values

    if userDict[
            transaction_data['transactor']
            ][0] == transaction_data['password']:
        # Check if the transaction is pending, or if this request completes it.
        try:
            userDict[transaction_data['sender']]
            userDict[transaction_data['recipient']]
            if userDict[
                    transaction_data['sender']
                    ][1] < transaction_data['amount']:
                return "Not enough funds in sender account", 400
        except Error:
            print("some of the users didn't exist")
            return "Please send/receive money from a real user", 401
        if blockchain.add_pending(transaction_data):
            am = transaction_data['amount']
            userDict[transaction_data['sender']][1] -= am
            userDict[transaction_data['recipient']][1] += am
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
    else:
        return "Not Authorized", 401


# Endpoint to retrieve the current blockchain in its entirety
@app.route('/chain', methods=["GET"])
def full_chain():
    response = blockchain.get_chain()
    return jsonify(response), 200


@app.route('/user/new', methods=["POST"])
def new_user():
    values = json.loads(request.data, strict=False)
    required = ["user", "pass"]
    if not all(k in values for k in required):
        return "Missing values", 400
    dbC.addUser(values['user'], values['pass'])
    userDict[values['user']] = {values['pass'], 0}
    return "user created", 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
