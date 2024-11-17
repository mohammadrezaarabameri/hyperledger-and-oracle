import hashlib
import random

class NodeSmartContract:
    def __init__(self, node_id):
        self.node_id = node_id
        self.commitment = None
        self.reveal_value = None

    def generate_random_and_commit(self):
        random_value = random.randint(1, 100)
        self.reveal_value = random_value
        self.commitment = hashlib.sha256(str(random_value).encode()).hexdigest()
        return self.commitment

    def get_commitment(self):
        return self.commitment

    def get_reveal_value(self):
        return self.reveal_value

    def verify_commitment(self, commitment, reveal_value):
        return hashlib.sha256(str(reveal_value).encode()).hexdigest() == commitment

class Node:
    def __init__(self, id):
        self.id = id
        self.smart_contract = NodeSmartContract(id)

    def send_commitment(self):
        return self.smart_contract.generate_random_and_commit()

    def send_reveal(self):
        return self.smart_contract.get_reveal_value()

    def verify_and_calculate(self, all_commitments, all_reveals):
        for i, (commitment, reveal) in enumerate(zip(all_commitments, all_reveals)):
            if not self.smart_contract.verify_commitment(commitment, reveal):
                raise ValueError(f"Commitment mismatch at Node {i}")

        final_random_number = sum(all_reveals) // len(all_reveals)
        return final_random_number

class Ledger:
    def __init__(self):
        self.transactions = []
    
    def record_transaction(self, data):
        self.transactions.append(data)

class Channel:
    def __init__(self):
        self.nodes = []

    def add_node(self, node):
        self.nodes.append(node)

    def broadcast_commitments(self, ledger):
        commitments = [node.send_commitment() for node in self.nodes]
        for i, commitment in enumerate(commitments):
            ledger.record_transaction(f"Node {i} commitment: {commitment}")
        return commitments

    def broadcast_reveals(self, ledger):
        reveals = [node.send_reveal() for node in self.nodes]
        for i, reveal in enumerate(reveals):
            ledger.record_transaction(f"Node {i} reveal: {reveal}")
        return reveals

if __name__ == "__main__":
    num_nodes = int(input("Enter the number of nodes: "))

    ledger = Ledger()
    channel = Channel()

    nodes = [Node(id=i) for i in range(num_nodes)]
    for node in nodes:
        channel.add_node(node)

    print("Recording commitments...")
    commitments = channel.broadcast_commitments(ledger)

    for transaction in ledger.transactions:
        print(transaction)
    print("\n")

    print("Recording reveals and calculating final random number...")
    reveals = channel.broadcast_reveals(ledger)

    final_random_number = None
    for node in nodes:
        final_random_number = node.verify_and_calculate(commitments, reveals)
        ledger.record_transaction(f"Node {node.id} calculated Final Random Number: {final_random_number}")

    for transaction in ledger.transactions:
        print(transaction)
