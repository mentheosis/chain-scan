import os, json, time
from ether.eth_scanner import EthScanner
from ether.bitquery_api import BitQueryAPI
from ether.etherscan_api import EtherscanAPI
from ether.graphscan_api import GraphscanAPI

startTime = time.time()

db_file_path = './eth.db'
infura_id = os.getenv('WEB3_INFURA_PROJECT_ID')
infura_secret = os.getenv('WEB3_INFURA_API_SECRET')
bitquery_key = os.getenv('BITQUERY_KEY')
etherscan_key = os.getenv('ETHERSCAN_KEY')

graphscan = GraphscanAPI()
bitquery = BitQueryAPI(bitquery_key)
indexers = [
  #"0xF55041E37E12cD407ad00CE2910B8269B01263b9",
  #"0x4140d3d0086fce37ebadd965dff88e12cf78b1fb",
  "0x4d6a8776a164776c93618233a0003e8894e7e6c2"
]

latest_block = graphscan.get_latest_block()
delegations = graphscan.get_delegators_for_indexer(indexers)
# is it faster calling for one at a time?
#for address in addresses_we_want:
#  print("address", address)
#  graphscan.get_delegators_for_indexer(address)

addresses_for_balances = []
for delegation in delegations:
  print("\ndelegation - - ", json.dumps(delegation, indent=2))
  addresses_for_balances.append(delegation["id"])

#override to check these
addresses_for_balances = [
  "0xF55041E37E12cD407ad00CE2910B8269B01263b9", # holding?
  "0xe9e284277648fcdb09b8efc1832c73c09b5ecf59", # beneficiary?
]
bitquery.get_balances_at_block(latest_block, addresses_for_balances)


#scanner = EtherscanAPI(etherscan_key)
#scanner.try_etherscan("0x4d6a8776a164776c93618233a0003e8894e7e6c2","12780505")

#scanner = EthScanner(infura_id, infura_secret, db_file_path)
#scanner.fillBlocksForward()

endTime = time.time()
print("done in ", endTime-startTime, " seconds")
