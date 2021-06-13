import os, json
from web3 import Web3
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from hexbytes import HexBytes
from sql.sql_client import SqlLiteClient

class HexJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, HexBytes):
          return obj.hex()
        return super().default(obj)

def formatNice(obj):
  return json.dumps(obj, cls=HexJsonEncoder, indent=2)

db_file_path = './eth.db'
infura_id = os.getenv('WEB3_INFURA_PROJECT_ID')
infura_secret = os.getenv('WEB3_INFURA_API_SECRET')
w3 = Web3(Web3.WebsocketProvider(f'wss://:{infura_secret}@mainnet.infura.io/ws/v3/{infura_id}'))

with SqlLiteClient(db_file_path) as sql:

  # Get information about the latest block
  latest_block = w3.eth.getBlock('latest')
  latest_json = formatNice(dict(latest_block))
  print("\n latest eth block", latest_block.number)
  if len(latest_block.transactions) > 0:
    print(" latest transaction", latest_block.transactions[0])
  print(" num transaction", len(latest_block.transactions), "\n")

  #for tx in latest_block.transactions:
  #  print("a tx", tx)

  #tx = w3.eth.getTransaction(latest_block.transactions[0])
  #print("\ntest", tx)

  latestInSql = sql.c.execute("select * from blocks where number = :num",{"num": latest_block.number} )
  #rowct = len(list(sql.c)) # always gives 2?
  first = sql.c.fetchone()
  if first == None:
    print("gonna insert..", latest_block.number, str(latest_block.hash.hex()))
    sql.c.execute("insert into blocks values (:number, :hash, :parentHash, :txCount, :raw)", 
        {
          "number": latest_block.number,
          "hash": str(latest_block.hash.hex()),
          "parentHash": str(latest_block.parentHash.hex()),
          "txCount": len(latest_block.transactions),
          "raw": latest_json
        }
      )
    sql.conn.commit()
  else:
    #row = next(sql.c)
    #print("already have!", formatNice(json.loads(first[4])))
    print("already have!", first[0], first[1])

  #j = json.loads(row[0])
  #for row in sql.c:
  #  print("already have?", row)
  test = sql.query_and_print("select number, hash from blocks")

# Get the ETH balance of an address 
#w3.eth.getBalance('YOUR_ADDRESS_HERE')





#####################
### graphQL things

urlGraphScanIo = "https://node.graphscan.io/subgraphs/id/Qmbczgf8UErptVoCVTgby48Z1Pk4HC4Z7TYgLQDGEK7Bkz"
#variables = '{"indexer_id":"0x4d6a8776a164776c93618233a0003e8894e7e6c2","block":11559948}'
#qryGraphScanIo = '{ query: query ($indexer_id: String, $block:Int!){\n  indexer(id:$indexer_id block:{number:$block}){\n    stakedTokens\n    delegatedTokens\n    indexingRewardCut\n    queryFeeCut\n    lastDelegationParameterUpdate\n  }\n}\n\n, variables:variables}'
variables = {"indexer":"0x4d6a8776a164776c93618233a0003e8894e7e6c2", "block":11536509}
qryGraphScanIo = '''
  query ($indexer: String, $block: Int!) {
    indexer(id:$indexer) {
      id
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
   url = urlGraphScanIo,
   verify = True,
   retries = 3,
)
client = Client(transport=transport)

#query = gql(qryGraphScanIo)
#res = client.execute(query, variables)
#print("\n\ngraph response", json.dumps(res, indent=2))
