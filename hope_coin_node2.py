# BlockChain
import datetime
import hashlib
import os
import json
import requests

from uuid import uuid4
from urllib.parse import urlparse
from flask import Flask, jsonify, request


############################### BlockChain ################################

class BlockChain:

	def __init__(self):
		self.chain = []
		self.transactions = []
		self.create_block(proof=1, prev_hash="0")
		self.nodes = set()

	def create_block(self, proof, prev_hash):
		block = {
			"index": len(self.chain) + 1,
			"timestamp": str(datetime.datetime.now()),
			"proof": proof,
			"previous_hash": prev_hash,
			"transactions": self.transactions
		}
		self.transactions = []
		self.chain.append(block)
		return block

	def get_previous_block(self):
		return self.chain[-1]

	def proof_of_work(self, previous_proof):
		new_proof = 1
		check_proof = False
		while check_proof is False:
			hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
			if hash_operation[:4] == "0000":
				check_proof = True
			else:
				new_proof += 1
		return new_proof

	def hash(self, block):
		encode_block = json.dumps(block, sort_keys=True).encode()
		return hashlib.sha256(encode_block).hexdigest()

	def is_chain_valid(self, chain):
		previous_block = chain[0]
		block_index = 1
		while block_index < len(chain):
			block = chain[block_index]
			if block['previous_hash'] != self.hash(previous_block):
				return False
			previous_proof = previous_block['proof']
			proof = block['proof']
			hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
			if hash_operation[:4] != '0000':
				return False
			previous_block = block
			block_index += 1
		return True

	def add_transaction(self, sender, receiver, amount):
		self.transactions.append({
				"sender": sender,
				"receiver": receiver,
				"amount": amount
			})
		previous_block = self.get_previous_block()
		# returning the new block index
		return previous_block['index'] + 1

	def add_node(self, node_address):
		parsed_url = urlparse(node_address)
		self.nodes.add(parsed_url.netloc)

	def replace_chain(self):
		"""	
			Inorder to decentralize we need to find the largest chain and put it inside the node
		"""
		network = self.nodes
		longest_chain = None
		max_length = len(self.chain)
		for node in network:
			response = requests.get(f'http://{node}/get-chain')
			if response.status_code == 200 and max_length < response.json()["length"] and self.is_chain_valid(response.json()["chain"]):
				max_length = response.json()["length"]
				longest_chain = response.json()["chain"]
		if longest_chain is not None:
			self.chain = longest_chain
			return True
		return False


################################## Mining BlockChain ######################################

app = Flask(__name__)

# Creating an address for the node on Port 5000
node_address = str(uuid4()).replace("-", "")

os.environ["FLASK_APP"] = "hope_coin_node2.py"

blockchain = BlockChain()

@app.route('/mine-block', methods=['GET'])
def mine_block():
	prev_block = blockchain.get_previous_block()
	prev_proof = prev_block['proof']
	proof = blockchain.proof_of_work(prev_proof)
	prev_hash = blockchain.hash(prev_block)
	blockchain.add_transaction(sender=node_address, receiver='Node2', amount=10)
	block = blockchain.create_block(proof, prev_hash)
	response = {
		'message': 'Congratulations for mining block', 
		'index': block['index'],
		'timestamp': block['timestamp'],
		'proof': block['proof'],
		'previous_hash': block['previous_hash'],
		'transactions': block['transactions']
	}

	return jsonify(response)

@app.route('/get-chain', methods=['GET'])
def get_chain():
	response = {'length': len(blockchain.chain), 'chain': blockchain.chain, }
	return jsonify(response)

@app.route('/is-valid-chain', methods=['GET'])
def is_valid_chain():
	is_valid = blockchain.is_chain_valid(blockchain.chain)
	response = {'chain': blockchain.chain, 'length': len(blockchain.chain), 'is_valid': is_valid}
	return jsonify(response)

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
	json_data = request.get_json()
	transaction_keys = ['sender', 'receiver', 'amount']
	if not all(key in json_data for key in transaction_keys):
		return jsonify({"message": "Missing keys"}), 400
	index = blockchain.add_transaction(json_data['sender'], json_data['receiver'], json_data['amount'])
	response = {"message": f'This transaction will be added to the block {index}'}
	return jsonify(response), 201

################################ Decentralizing BlockChain #####################################

# Connecting new node
@app.route('/connect_node', methods=['POST'])
def connect_node():
	json_data = request.get_json()
	nodes = json_data.get("nodes")
	if nodes is None:
		return "No node", 400
	for node in nodes:
		blockchain.add_node(node)
	response = {
		"message": "All nodes are connected",
		"total_nodes": list(blockchain.nodes)
	}
	return jsonify(response), 201

# Replacing the chain with longest chain if needed
@app.route('/replace_chain', methods=['GET'])
def replace_chain():
	is_chain_replaced = blockchain.replace_chain()
	response = {
		'is_chain_replaced': is_chain_replaced,
		'chain': blockchain.chain,
		'length': len(blockchain.chain)
	}
	return jsonify(response), 200


app.run(host="0.0.0.0", threaded=True, port=5002, debug=True)
