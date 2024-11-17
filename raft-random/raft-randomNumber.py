import threading
import random
import time

class Channel:
    def __init__(self):
        self.nodes = []

    def add_node(self, node):
        self.nodes.append(node)

    def broadcast(self, message, sender_id):
        for node in self.nodes:
            if node.node_id != sender_id:
                node.receive_message(message)

class SmartContract:
    def __init__(self, num_nodes, channel):
        self.num_nodes = num_nodes
        self.channel = channel

    def conduct_voting(self, node_id, vote):
        print(f"Node {node_id} voted for Node {vote}")
        self.channel.broadcast({'vote': vote}, node_id)

    def determine_leader(self, nodes):
        all_votes = [node.vote for node in nodes]
        vote_counts = [all_votes.count(i) for i in range(len(nodes))]
        leader_id = vote_counts.index(max(vote_counts))
        return leader_id

    def generate_random_number(self):
        return random.randint(1, 100)

class Node:
    def __init__(self, node_id, channel, contract):
        self.node_id = node_id
        self.channel = channel
        self.contract = contract
        self.is_leader = False
        self.vote = None
        self.received_votes = []
        self.received_random_number = None
        self.leader_id = None  

    def receive_message(self, message):
        if 'vote' in message:
            self.received_votes.append(message['vote'])
        elif 'random_number' in message:
            self.received_random_number = message['random_number']
        elif 'heartbeat' in message:
            self.leader_id = message['leader_id']
            print(f"Node {self.node_id} received heartbeat from Leader {self.leader_id}")

    def simulate_transaction(self):
        self.vote = random.randint(0, len(self.channel.nodes) - 1)
        self.contract.conduct_voting(self.node_id, self.vote)
        
        time.sleep(1)
        self.received_votes.append(self.vote)

    def count_votes(self):
        vote_counts = [self.received_votes.count(i) for i in range(len(self.channel.nodes))]
        leader_id = vote_counts.index(max(vote_counts))
        if self.node_id == leader_id:
            self.is_leader = True
            print(f"Node {self.node_id} is the Leader")
            threading.Thread(target=self.send_heartbeat).start() 
        return leader_id

    def send_heartbeat(self):
        while self.is_leader:
            print(f"Leader Node {self.node_id} is sending heartbeat...")
            self.channel.broadcast({'heartbeat': True, 'leader_id': self.node_id}, self.node_id)
            time.sleep(2)

    def execute_contract(self):
        if self.is_leader:
            random_number = self.contract.generate_random_number()
            print(f"Leader Node {self.node_id} generated random number: {random_number}")
            self.channel.broadcast({'random_number': random_number}, self.node_id)

    def wait_for_random_number(self):
        while self.received_random_number is None:
            time.sleep(0.1)
        print(f"Node {self.node_id} received random number: {self.received_random_number}")

class Client:
    def __init__(self, channel):
        self.channel = channel

    def send_transaction(self):
        print("Client: Sending transaction proposal to the network...")
        for node in self.channel.nodes:
            node.simulate_transaction()

def simulate_network(num_nodes):
    channel = Channel()
    contract = SmartContract(num_nodes, channel)

    for i in range(num_nodes):
        node = Node(i, channel, contract)
        channel.add_node(node)

    client = Client(channel)
    client.send_transaction()

    leader_id = None
    for node in channel.nodes:
        leader_id = node.count_votes()

    for node in channel.nodes:
        if node.is_leader:
            node.execute_contract()

    for node in channel.nodes:
        if not node.is_leader:
            node.wait_for_random_number()

if __name__ == "__main__":
    num_nodes = int(input("Enter the number of nodes: "))
    simulate_network(num_nodes)
