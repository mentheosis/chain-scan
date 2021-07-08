import os, json, time
import requests

class EtherscanAPI:
	def __init__(self, apiKey, emitterFn=None):
		#self.apiUrl = "https://api.etherscan.io/api?module=account&action=tokenbalancehistory&contractaddress=0x57d90b64a1a57749b0f932f1a3395792e12e7055&address=0xe04f27eb70e025b78871a2ad7eabe85e61212761&blockno=8000000&apikey=YourApiKeyToken"
		self.apiUrl = "https://api.etherscan.io/api"
		self.GRT_token_address = '0xc944E90C64B2c07662A292be6244BDf05Cda44a7'
		self.params = {
			'module': 'account',
			'action': 'tokenbalancehistory',
			'contractaddress': self.GRT_token_address,
			'address': '',
			'blockno': 1,
			'apikey': apiKey,
		}
		self.apiKey = apiKey

	def try_etherscan(self, address, blockno):
		self.params["address"] = address
		self.params["blockno"] = blockno
		print("sending etherscan query", self.params)
		r = requests.post(self.apiUrl, params=self.params)
		print(r, r.text)
