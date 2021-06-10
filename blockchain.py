import hashlib
import database
import time


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
    def __init__(self, blocks=[], data=[]):
        if not blocks:
            self.chain = []
            self.pending_transactions = []
            self.current_data = []
            self.construct_genesis()
            dbC = database.DatabaseConnector('testChain.sqlite')
            dbC.addBlock(self.latest_block())
        else:
            self.chain = []
            for block in blocks:
                rdat = [x for x in data if x[1] == block[0]]
                self.chain += [Block(block[0],
                                     block[1],
                                     block[2],
                                     rdat,
                                     block[3])]
            self.pending_transactions = []
            self.current_data = []

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
        return {'chain': chain_json, 'length': len(self.chain)}
