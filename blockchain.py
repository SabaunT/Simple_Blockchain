import hashlib
import json
import requests
from time import time
from flask import Flask, jsonify, request
from uuid import uuid4
from urllib.parse import urlparse


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.new_block(proof=100, previous_hash=1)
        self.nodes = set()

    def new_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash
        }
        self.chain.append(block)
        self.current_transactions = []
        return block

    def new_transactions(self, sender, reciever, amount):
        self.current_transactions.append({
            'sender': sender,
            'reciever': reciever,
            'amount': amount
        })
        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        block_string_form = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string_form).hexdigest()

    @staticmethod
    def validation_task(proof, last_proof):
        task = f'{last_proof}{proof}'.encode()
        task_hash = hashlib.sha256(task).hexdigest()
        return task_hash[:4] == '0000'

    def proof_of_work(self, last_proof):
        proof = 0
        while self.validation_task(proof, last_proof) is False:
            proof += 1
        return proof

    def register_nodes(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]

            if block['previous_hash'] != self.hash(last_block):
                return False
            if not self.validation_task(block['proof'], last_block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain)

        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False


app = Flask(__name__)
node_identifier = str(uuid4()).replace('-', '')

blockchain = Blockchain()


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    val_args = request.get_json()

    obligatory_values = ['sender', 'reciever', 'amount']
    if not all(x in val_args for x in obligatory_values):
        return 'Missing value', 400

    index = blockchain.new_transactions(val_args['sender'],
                                        val_args['reciever'],
                                        val_args['amount'])
    statement = {'msg': f'Transactions will be added to the block {index}'}
    return jsonify(statement), 201


@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    if len(blockchain.current_transactions) < 5:
        return 'No Tx in UTXO', 400
    else:
        blockchain.new_transactions(0, node_identifier, 1)

        block = blockchain.new_block(proof, blockchain.hash(last_block))

        statement = {
            'msg': 'New block was found',
            'index': block['index'],
            'transactions': block['transactions'],
            'proof': block['proof'],
            'previous_hash': block['previous_hash']
        }
        return jsonify(statement), 200


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_nodes(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
















