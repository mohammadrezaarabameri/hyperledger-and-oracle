from flask import Flask, jsonify
import requests
from multiprocessing import Process

class OracleNode:
    def start(port):
      app = Flask(__name__)

      @app.route('/fetch_usd_price', methods=['GET'])
      def get_usd_price():
        try:
            print(f"Oracle Node on port {port}: Fetching USD price from external API...")
            response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
            data = response.json()
            usd_to_irr = data['rates']['IRR']
            print(f"Oracle Node on port {port}: USD to IRR rate received from API is {usd_to_irr}")
            return jsonify({"usd_price": usd_to_irr})
        except Exception as e:
            print(f"Oracle Node on port {port}: Failed to fetch USD price - {e}")
            return jsonify({"error": "Failed to fetch USD price", "details": str(e)}), 500

      app.run(port=port)

class DecentralizedOracle:
    def __init__(self, ports):
        self.ports = ports

    def request_prices_from_nodes(self):
        prices = []
        for port in self.ports:
            try:
                oracle_url = f"http://localhost:{port}/fetch_usd_price"
                response = requests.get(oracle_url)
                if response.status_code == 200:
                    usd_price = response.json().get("usd_price")
                    if usd_price:
                        prices.append(usd_price)
                        print(f"Decentralized Oracle: Price received from Oracle Node on port {port} - {usd_price}")
            except Exception as e:
                print(f"Decentralized Oracle: Error connecting to Oracle Node on port {port} - {e}")

        if prices:
            aggregated_price = sum(prices) / len(prices)
            print(f"Decentralized Oracle: Aggregated USD Price - {aggregated_price}")
            return aggregated_price
        else:
            print("Decentralized Oracle: No valid prices received.")
            return None



if __name__ == "__main__":
    oracle_ports = [5001, 5002, 5003, 5004, 5005]
    processes = []
    
    for port in oracle_ports:
        p = Process(target=OracleNode.start, args=(port,))
        p.start()
        processes.append(p)
    
    for process in processes:
        process.join()
