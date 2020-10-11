from flask import Flask, request
import requests
import time
import json
from .blockchain import Blockchain, Block

app = Flask(__name__)

# initializing Blockchain

blockchain = Blockchain()


@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    tx_data = request.get_json()
    required_field = ['author', 'content']
    for field in required_field:
        if not tx_data.get(field):
            return "Invalid transaction data", 404

    tx_data['timestamp'] = time.time()
    blockchain.addNewTransaction(tx_data)
    return "Success", 201


@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({
        "Length": len(chain_data),
        "chain": chain_data})


@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if not result:
        return "No transaction to mine"
    return "Block #{} is mined.".format(result)


@app.route('/pending_tx')
def get_pending():
    return json.dumps(blockchain.unconfirmed_transactions)


# Contains the host addresses of other participating members of the network
peers = set()


# Endpoint to add new peers to the network
@app.route('/register_node', methods=['POST'])
def register_new_peers():
    # The host address to the peer node
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400
    # Add the node to the peer list
    peers.add(node_address)

    # Return the blockchain to the newly registered node so that
    return get_chain()


@app.route('/register_with', methods=['POST'])
def register_with_existing_node():
    """
    Internally calls the `register_node` endpoint to register current
    node with the remote note specified in the request, and sync
    the blockchain as well with the remote node
    """
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    data = {"node_address": request.host_url}
    headers = {'Content-Type': "application/json"}

    # Make a request to register with remote node and obtain information
    response = requests.post(node_address + "/register_node",
                             data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        global blockchain
        global peers
        # update chain and the peers
        chain_dump = response.json()['chain']
        blockchain = create_chain_from_dump(chain_dump)
        peers.update(response.json()['peers'])
        return "Registration successful", 200
    else:
        # if something goes wrong, pass it on to the API response
        return response.content, response.status_code


def create_chain_from_dump(chain_dump):
    blockchain = Blockchain()
    for idx, block_data in enumerate(chain_dump):
        block = Block(block_data["index"],
                      block_data["transactions"],
                      block_data["timestamp"],
                      block_data["previous_hash"])
        proof = block_data['hash']
        if idx > 0:
            added = blockchain.addBlock(block, proof)
            if not added:
                raise Exception("The chain dump is tampered!!")
        else:  # the block is genesis block, no verification needed
            blockchain.chain.append(block)
    return blockchain
