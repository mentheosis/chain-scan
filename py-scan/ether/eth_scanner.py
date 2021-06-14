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

  Here is the SQL schema for transactions:
  create table transactions (
    hash TEXT, 
    blockNumber INTEGER
    blockHash TEXT
    fromAdr TEXT
    toAdr TEXT
    value INTEGER
    type TEXT
    nonce INTEGER
    inputStr TEXT
    decodedInput JSON, 
    txIndex INTEGER, 
    gas INTEGER, 
    gasPrice INTEGER);
'''
class EthScanner:
  def __init__(self, infura_id, infura_secret, db_file_path, emitterFn=None):
    self.db_file_path = db_file_path
    self.w3 = Web3(Web3.WebsocketProvider(f'wss://:{infura_secret}@mainnet.infura.io/ws/v3/{infura_id}'))
    self.knownContracts = {}

    graphContractAddress = '0xc944E90C64B2c07662A292be6244BDf05Cda44a7'
    graphABI = json.load(open('abis/the_graph.json'))['result']
    self.knownContracts[graphContractAddress] = self.w3.eth.contract(abi=graphABI, address=graphContractAddress)


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
      sql.c.execute("select * from blocks where number = :num",{"num": eth_block['number']} )
      latestInSql = sql.c.fetchone()
      if latestInSql == None:
        print("Writing new block to sql:", eth_block['number'], str(eth_block['hash'].hex()))
        sql.c.execute("insert into blocks values (:number, :hash, :parentHash, :txCount, :raw)", 
            {
              "number": eth_block['number'],
              "hash": str(eth_block['hash'].hex()),
              "parentHash": str(eth_block['parentHash'].hex()),
              "txCount": eth_block['txCount'],
              "raw": formatNice(eth_block)
            }
          )
        sql.conn.commit()
      else:
        print("Not writing, already have block:", latestInSql[0], latestInSql[1])


  def writeTransactionsForBlock(self, transactionsArr):
    print("write transactions not implemented")
    for tx in transactionsArr:
      print("tx array", formatNice(tx))


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
        return res


  '''
    Starting from the max block we already have, move forward writing any newer blocks and transactions into sql
    for tx in nextBlock['transactions']:
      if tx['hash'].hex() == '0xcb89cd25ab9d68b09d859b7657b169b57bf76886dbd78851980c39c90af1d129':
        graphTx = tx
        print("\nFound transaction to graph contract", formatNice(tx))
        decoded = contract.decode_function_input(graphTx['input'])
        print("decoded ", decoded[0], formatNice(decoded[1]))
  '''
  def fillInBlocksForward(self):
    blockNum = self.getLatestStoredBlockNumber()
    print("Filling forwards starting from ", blockNum)
    try:
      # use dict to convert from AttributeDict for easier serializing down the line
      nextBlock = dict(self.w3.eth.get_block(block_identifier=12624935, full_transactions=True))
      blockTransactions = nextBlock.pop('transactions')
      nextBlock['txCount'] = len(blockTransactions)

      for i in range(len(blockTransactions)):
        # again converting AttributeDict into Dict so we can serialize
        blockTransactions[i] = dict(blockTransactions[i])
        tx = blockTransactions[i]

        # see if we know how to decode the tx input property based on known ABIs
        if self.knownContracts.get(tx['to']) != None:
          decoded = self.knownContracts[tx['to']].decode_function_input(tx['input'])
          tx['decodedInput'] = decoded[1]
          tx['inputStr'] = str(decoded[0])
          print("got decoded input", decoded)

      self.writeBlockIfNotExist(nextBlock)
      self.writeTransactionsForBlock(blockTransactions)

    except web3exceptions.BlockNotFound as e:
      nextBlock = "We've caught up to the current block."

    #print("got next block", formatNice(nextBlock))
