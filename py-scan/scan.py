import os, json
from web3 import Web3
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


infura_id = os.getenv('WEB3_INFURA_PROJECT_ID')
infura_secret = os.getenv('WEB3_INFURA_API_SECRET')
w3 = Web3(Web3.WebsocketProvider(f'wss://:{infura_secret}@mainnet.infura.io/ws/v3/{infura_id}'))

# Get information about the latest block
latest_block = w3.eth.getBlock('latest')
print("\n\nlatest eth block nonce", latest_block['nonce'])
# Get the ETH balance of an address 
#w3.eth.getBalance('YOUR_ADDRESS_HERE')

urlGraphScanIo = "https://node.graphscan.io/subgraphs/id/Qmbczgf8UErptVoCVTgby48Z1Pk4HC4Z7TYgLQDGEK7Bkz"
variables = '{"indexer_id":"0x4d6a8776a164776c93618233a0003e8894e7e6c2","block":11559948}'
#qryGraphScanIo = '{ query: query ($indexer_id: String, $block:Int!){\n  indexer(id:$indexer_id block:{number:$block}){\n    stakedTokens\n    delegatedTokens\n    indexingRewardCut\n    queryFeeCut\n    lastDelegationParameterUpdate\n  }\n}\n\n, variables:variables}'
qryGraphScanIo = '''
  query Named($indexer_id: String, $block: Int!) {
    indexer(id:$indexer_id, block:$block) {
      stakedTokens
      delegatedTokens
      indexingRewardCut
      queryFeeCut
      lastDelegationParameterUpdate
    }
  }
'''

urlTheGraph = "https://api.thegraph.com/subgraphs/name/centrifuge/tinlake"
qryTheGraph = '''
query {
  loans(where: {opened_gt: 0, debt_gt: 0}) {
    id
    opened
    closed
    debt
  }
}
'''

transport = RequestsHTTPTransport(
   url = urlTheGraph,
   verify = True,
   retries = 3,
)
client = Client(transport=transport)

query = gql(qryTheGraph)
print("wht??", query)
res = client.execute(query, variable_values=variables)

print("\n\ngraph response", json.dumps(res, indent=2))
