import os, json
from web3 import Web3, exceptions as web3exceptions
from hexbytes import HexBytes
from sql.sql_client import SqlLiteClient

# used to format and stringify bytes, e.g. hashes from blocks
class HexJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, HexBytes):
          return obj.hex()
        return super().default(obj)

# little wrapper to get a nice string from json block data
def formatNice(obj):
  return json.dumps(obj, cls=HexJsonEncoder, indent=2)

'''
  Used to check an eth node for the most recent block, and then backfill any blocks missing from our sql records
'''
class EthScanner:
  def __init__(self, infura_id, infura_secret, db_file_path, emitterFn=None):
    self.db_file_path = db_file_path
    self.w3 = Web3(Web3.WebsocketProvider(f'wss://:{infura_secret}@mainnet.infura.io/ws/v3/{infura_id}'))

  '''
    a handy method to allow writing messages across threads/events or just print to console depending on context
    pass in any emitter fn to the constructor to write strings there instead of std print
  '''
  def printOrLog(self, message):
    if self.emitterFn != None:
      self.emitterFn(message)
    else:
      print(message)

  def writeBlockIfNotExist(self, eth_block):
    with SqlLiteClient(self.db_file_path) as sql:
      sql.c.execute("select * from blocks where number = :num",{"num": eth_block.number} )
      latestInSql = sql.c.fetchone()
      if latestInSql == None:
        print("Writing new block to sql:", eth_block.number, str(eth_block.hash.hex()))
        sql.c.execute("insert into blocks values (:number, :hash, :parentHash, :txCount, :raw)", 
            {
              "number": eth_block.number,
              "hash": str(eth_block.hash.hex()),
              "parentHash": str(eth_block.parentHash.hex()),
              "txCount": len(eth_block.transactions),
              "raw": latest_json
            }
          )
        sql.conn.commit()
      else:
        print("Not writing, already have block:", first[0], first[1])

  '''
    Checks sql for the max block_number we have, or if nothing in sql then it will return the latest block from eth node
  '''
  def getLatestStoredBlockNumber(self):
    with SqlLiteClient(self.db_file_path) as sql:
      sql.c.execute("select max(number) from blocks")
      res = sql.c.fetchone()[0]
      if res == None:
        print("getting latest number from node...")
        latest_block = self.w3.eth.get_block_number()
        # return number - 1, this is because normally we would seek the block after the one we have
        # but in this case we have none and we want to include the block number we just looked up
        # so minus one means that the next lookup step will increment back to this original number
        return latest_block - 1
      else:
        print("getting latest number from sql...", res)
        return res[0]


  '''
    Starting from the max block we already have, move forward writing any newer blocks and transactions into sql
  '''
  def fillInBlocksForward(self):
    blockNum = self.getLatestStoredBlockNumber()
    print("got our latest block number", blockNum)
    transactionInputs = []
    try:
      # use dict to convert from AttributeDict for easier handling down the line
      nextBlock = dict(self.w3.eth.get_block(block_identifier=12624935, full_transactions=True))
      for i in range(len(nextBlock['transactions'])):
        # again converting AttributeDict into Dict so we can serialize
        # and converting input data into readable
        #tx = nextBlock['transactions'][i]
        #tx = dict(tx)
        nextBlock['transactions'][i] = dict(nextBlock['transactions'][i])
        #transactionInputs.append(Web3.toText(nextBlock['transactions'][i]['input']))
      print("what happened", nextBlock)
    except web3exceptions.BlockNotFound as e:
      nextBlock = "not found!!!!"

    print("got next block", formatNice(nextBlock), "inputs", transactionInputs)

    graphContractAddress = '0xc944E90C64B2c07662A292be6244BDf05Cda44a7'
    graphABI = json.load(open('abis/the_graph.json'))['result']
    contract = self.w3.eth.contract(abi=graphABI, address=graphContractAddress)

    for tx in nextBlock['transactions']:
      if tx['hash'].hex() == '0xcb89cd25ab9d68b09d859b7657b169b57bf76886dbd78851980c39c90af1d129':
        graphTx = tx
        print("\nFound transaction to graph contract", formatNice(tx))
        decoded = contract.decode_function_input(graphTx['input'])
        print("decoded ", decoded[0], formatNice(decoded[1]))
