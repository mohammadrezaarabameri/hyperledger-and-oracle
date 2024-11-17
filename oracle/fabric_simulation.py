from concurrent.futures import ThreadPoolExecutor
from oracle_server import DecentralizedOracle


class SmartContract:
    def __init__(self, node_id, oracle):
        self.node_id = node_id
        self.oracle = oracle
        self.ledger = []

    def execute_transaction_proposal(self):
        print(f"Smart Contract on Node {self.node_id}: Executing transaction proposal...")

        aggregated_price = self.oracle.request_prices_from_nodes()
        
        if aggregated_price is not None:
            self.ledger.append(aggregated_price)
            print(f"Smart Contract on Node {self.node_id}: Aggregated Price stored in ledger - {aggregated_price}")
        else:
            print(f"Smart Contract on Node {self.node_id}: No valid aggregated price received.")

class Client:
    def __init__(self, smart_contracts):
        self.smart_contracts = smart_contracts

    def send_transaction_proposal(self):
        print("Client: Sending transaction proposal to all nodes in the channel...")

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(contract.execute_transaction_proposal) for contract in self.smart_contracts]
            for future in futures:
                future.result()

if __name__ == "__main__":
    try:
        num_nodes = int(input("Enter the number of nodes in the channel: "))
    except ValueError:
        print("Invalid input. Setting default number of nodes to 3.")
        num_nodes = 3

    oracle_ports = [5001, 5002, 5003, 5004, 5005]
    decentralized_oracle = DecentralizedOracle(oracle_ports)
    smart_contracts = [SmartContract(node_id=i, oracle=decentralized_oracle) for i in range(1, num_nodes + 1)]

    client = Client(smart_contracts)
    client.send_transaction_proposal()

    print("\n--- Ledgers of Each Node ---")
    for contract in smart_contracts:
        print(f"Node {contract.node_id} Ledger: {contract.ledger}")
