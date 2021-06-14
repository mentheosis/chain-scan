import os, json, time
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
    blockNumber TEXT,
    blockHash TEXT,
    fromAdr TEXT,
    toAdr TEXT,
    value TEXT,
    type TEXT,
    nonce TEXT,
    inputStr TEXT,
    decodedInput BLOB, 
    txIndex TEXT, 
    gas TEXT, 
    gasPrice TEXT);
'''
class EthScanner:
  def __init__(self, infura_id, infura_secret, db_file_path, emitterFn=None):
    self.db_file_path = db_file_path
    self.w3 = Web3(Web3.WebsocketProvider(f'wss://:{infura_secret}@mainnet.infura.io/ws/v3/{infura_id}'))
    self.knownContracts = {}

    self.graphContractAddress = '0xc944E90C64B2c07662A292be6244BDf05Cda44a7'
    graphABI = json.load(open('abis/the_graph.json'))['result']
    self.knownContracts[self.graphContractAddress] = self.w3.eth.contract(abi=graphABI, address=self.graphContractAddress)


  '''
    a handy method to allow writing messages across threads/events or just print to console depending on context
    pass in any emitter fn to the constructor to write strings there instead of std print
  '''
  def printOrLog(self, message):
    if self.emitterFn != None:
      self.emitterFn(message)
    else:
      print(message)


  def writeBlockIfNotExist(self, eth_block, sql):
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


  def writeTransactionsForBlock(self, transactionsArr, sql):
    if len(transactionsArr) > 0:
      valsToInsert = []
      for tx in transactionsArr:
        #if tx['to'] == self.graphContractAddress:
        #  print("graph tx!", formatNice(tx))

        valsToInsert.append((
          # note that this is a tuple
          tx['hash'].hex(),
          tx['blockNumber'],
          tx['blockHash'].hex(),
          tx['from'],
          tx['to'],
          str(tx['value']),
          tx['type'],
          tx['nonce'],
          str(tx['inputStr']) if tx.get('inputStr') else None,
          str(tx['decodedInput']) if tx.get('decodedInput') else None,
          str(tx['transactionIndex']),
          str(tx['gas']),
          str(tx['gasPrice'])
        ))

      blockNum = transactionsArr[0]['blockNumber']
      sql.c.execute("delete from transactions where blockNumber = :blockNum", {"blockNum": blockNum})
      sql.c.executemany("insert into transactions values (?,?,?,?,?,?,?,?,?,?,?,?,?)", valsToInsert)
      print(f"Inserted {len(transactionsArr)} transaction rows")
      sql.conn.commit()


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
    recursively continue to scan through blocks until we pass the latest one.
    We'll recurse until we hit an exception, which we expect to be BlockNotFound,
    but it could also be infura req limit hit or something.
  '''
  def iterateBlocksForward(self, blockNum, sql):
    try:
      startTime = time.time()
      print("\nGetting block from eth node: ", blockNum)
      # use dict to convert from AttributeDict for easier serializing down the line
      nextBlock = dict(self.w3.eth.get_block(block_identifier=blockNum, full_transactions=True))
      fromNodeTime = time.time()
      print("got data from eth node, it took", fromNodeTime-startTime, "seconds")

      # move the transactions into their own object, they will write to sql separately
      blockTransactions = nextBlock.pop('transactions')
      nextBlock['txCount'] = len(blockTransactions)

      for i in range(len(blockTransactions)):
        # again converting AttributeDict into Dict so we can serialize
        blockTransactions[i] = dict(blockTransactions[i])
        tx = blockTransactions[i]

        # see if we know how to decode the tx input property based on known ABIs
        if self.knownContracts.get(tx['to']) != None:
          decoded = self.knownContracts[tx['to']].decode_function_input(tx['input'])
          #print("got decoded input", decoded)
          tx['decodedInput'] = decoded[1]
          tx['inputStr'] = str(decoded[0])

      self.writeBlockIfNotExist(nextBlock, sql)
      self.writeTransactionsForBlock(blockTransactions, sql)
      sqlDoneTime = time.time()
      print("Sql write finished, it took", sqlDoneTime-fromNodeTime, "seconds")

      # sucessfully wrote, return true to tell the caller to try continuing to the next block
      return (True, blockNum+1)

    except web3exceptions.BlockNotFound as e:
      print("We've caught up to the current block, stopping now.")
      # we hit the end of the blocks, so the tell the caller it can stop or wait.
      return (False, blockNum)


  '''
    Start from the max block we already have (to make sure we have its transactions)
    then move forward writing any newer blocks and transactions into sql
  '''
  def fillBlocksForward(self):
    nextBlockNum = self.getLatestStoredBlockNumber()
    with SqlLiteClient(self.db_file_path) as sql:
      keepGoing = True
      startTime = time.time()
      counter = 0
      while keepGoing:
        (keepGoing, nextBlockNum) = self.iterateBlocksForward(nextBlockNum, sql)
        counter += 1
        print("Blocks retrieved this run:", counter, "time so far", time.time()-startTime)

    print("Loop was escaped, all done for now.")
