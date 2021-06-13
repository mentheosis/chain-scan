import os, json
from web3 import Web3
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


    def printOrLog(self, message):
            if self.emitterFn != None:
                self.emitterFn(message)
            else:
                print(message)

