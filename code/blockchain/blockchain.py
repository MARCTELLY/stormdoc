""" this module is for the block chaine """
# Inspiration et source : https://developer.ibm.com/technologies/blockchain/tutorials/develop-a-blockchain-application-from-scratch-in-python/
# Importing modules
import datetime
import hashlib
import json



class Block:
    """ This class manage block """

    def __init__(self, index, transaction, timestamp, previous_hash):
        """
        Constructor for the 'Block' class

        :param index :          Unique ID of bloc.
        :param transaction :    List of transaction.
        :param timestamp :      Time of generation of the bock
        :param previous_hash :  Hash of the previous block in the chain which this block is part of 
        TODO : implement a tree Markel block Chaine https://www.codementor.io/blog/merkle-trees-5h9arzd3n8
        """

        self.index = index
        self.transaction = transaction
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = 0

    def hashBlock(self, block):
        """
        Returns the hash of block by converting it in JSON string
        """
        hashed_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(hashed_block).hexdigest()


class Blockchain:
    """
    Class of blockchain
    """
    DIFFICULTY = 2

    def __int__(self):
        """
        Constructor of `Blockchain` class
        """
        self.unconfirmed_transactions = []
        self.chain = []
        self.createGenesisBlock()

    def createGenesisBlock(self):
        """
        A function to generate genesis block and appends it to
        the chain. The block has index 0, previous_hash as 0, and
        a valid hash
        """
        genesis_block = Block(0, [], datetime.datetime.now(), "0"),
        genesis_block.hash = genesis_block.hash()
        self.chain.append(genesis_block)

    @property
    def lastBlock(self):
        """
         A quick pythonic way to retrieve the most recent block in the chain. Note that
        the chain will always consist of at least one block (i.e., genesis block)
        """
        return self.chain[-1]

    def proofOfWork(self, block):
        """
        Function that tries different values of the nonce to get a hash
        that satisfies our difficulty criteria.
        :param block:
        :return: computedHash
        """
        block.nonce = 0

        computedHash = block.hashBlock()
        while not computedHash.startswith("0"*Blockchain.DIFFICULTY):
            block.nonce += 1
            computedHash = block.hashBlock()
        return computedHash

    def addBlock(self, block, proof):
        """
        A function that adds the block to the chain after verification.
        Verification includes:
        * Checking if the proof is valid.
        * The previous_hash referred in the block and the hash of a latest block
        in the chain match.
        """
        previous_hash = self.lastBlock()
        if previous_hash != block.previous_hash():
            return False
        if not Blockchain.isValidProof(block, proof):
            return False
        block.hash = proof
        self.chain.append(block)
        return True

    def isValidProof(self, block, blockHash):
        """
        Check if block_hash is valid hash of block and satisfies
        the difficulty criteria.
        """
        return (blockHash.startswith("0"*Blockchain.DIFFICULTY) and blockHash == block.hashBlock())

    def addNewTransaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    def mine(self):
        """
        This function serves as an interface to add the pending
        transactions to the blockchain by adding them to the block
        and figuring out proof of work.
        """
        if not self.unconfirmed_transactions:
            return False
        lastBlock = self.lastBlock

        newBlock = Block(index = lastBlock.index+1,
            transaction = self.unconfirmed_transactions,
            timestamp = datetime.datetime.now(),
            previous_hash = lastBlock.hash)
        proof = self.proofOfWork()
        self.addBlock(newBlock, proof)
        self.unconfirmed_transactions = []
        return newBlock.index