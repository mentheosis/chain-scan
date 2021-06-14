import os
from ether.eth_scanner import EthScanner

db_file_path = './eth.db'
infura_id = os.getenv('WEB3_INFURA_PROJECT_ID')
infura_secret = os.getenv('WEB3_INFURA_API_SECRET')

scanner = EthScanner(infura_id, infura_secret, db_file_path)
scanner.fillBlocksForward()

print("done")
