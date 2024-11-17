from flask import Flask, jsonify
import requests
import threading
import time

class OracleNode:
    def __init__(self, port, is_sybil):
        self.port = port
        self.is_sybil = is_sybil

    def start(self):
        app = Flask(__name__)

        @app.route('/fetch_usd_price', methods=['GET'])
        def fetch_usd_price():
            if self.is_sybil:
                fake_usd_price = 45000
                print(f"Sybil Node (Port {self.port}): Returning fake USD price - {fake_usd_price}")
                return jsonify({"price": fake_usd_price})
            else:
                try:
                    print(f"Honest Node (Port {self.port}): Fetching real USD price from external API...")
                    response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
                    data = response.json()
                    
                    if 'rates' in data and 'IRR' in data['rates']:
                        usd_to_irr = data['rates']['IRR']
                        print(f"Honest Node (Port {self.port}): Real USD to IRR rate is {usd_to_irr}")
                        return jsonify({"price": usd_to_irr})
                    else:
                        print("Structure of API response has changed.")
                        return jsonify({"error": "Structure of API response has changed"}), 500
                except Exception as e:
                    print(f"Honest Node (Port {self.port}): Failed to fetch USD price - {e}")
                    return jsonify({"error": "Failed to fetch USD price", "details": str(e)}), 500

        app.run(port=self.port)


class DecentralizedOracle:
    def __init__(self, ports):
        self.ports = ports

    def request_prices_from_nodes(self):
        prices = []
        
        for port in self.ports:
            try:
                response = requests.get(f'http://localhost:{port}/fetch_usd_price')
                data = response.json()
                
                if 'price' in data:
                    prices.append(data['price'])
                    print(f"Price received from Oracle on port {port}: {data['price']}")
                else:
                    print(f"Error from Oracle on port {port}: {data.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"Failed to get price from Oracle on port {port}: {e}")
        
        if prices:
            aggregated_price = sum(prices) / len(prices)
            print(f"Aggregated Price: {aggregated_price}")
            return aggregated_price
        else:
            print("No valid prices received from oracles.")
            return None

def start_oracle_nodes(node_count, sybil_count):
    ports = [5001 + i for i in range(node_count)]  
    nodes = []
    for i in range(node_count):
        is_sybil = i < sybil_count
        node = OracleNode(ports[i], is_sybil)
        nodes.append(node)
        threading.Thread(target=node.start).start()
        time.sleep(1)  

if __name__ == '__main__':
    total_nodes = 5
    sybil_nodes = 2
    start_oracle_nodes(total_nodes, sybil_nodes)
