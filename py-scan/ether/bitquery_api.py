import os, json, time
import requests

class BitQueryAPI:
	def __init__(self, apiKey, emitterFn=None):
		self.apiUrl = "https://graphql.bitquery.io"
		self.apiKey = apiKey
		self.GRT_token_address = '0xc944E90C64B2c07662A292be6244BDf05Cda44a7'

	def get_balances_at_block(self, block, address_list):

		addresses_string = ''
		for address in address_list:
			addresses_string = addresses_string + f'"{address}",'

		qry = '''
		{ethereum {
			address(address: {in:''' f'[{addresses_string}]' '''})
			{	
				address
				balances(
				height: {''' f'lteq: {block}' '''}
				currency: {is: "''' f'{self.GRT_token_address}' '''" }
				) {
					currency {
						symbol
					}
					value
				}
			}
		} }
		'''

		print("sending bitquery call...")
		h = {'X-API-KEY': self.apiKey}
		r = requests.post(self.apiUrl, headers=h, json={'query':qry})
		parsed = json.loads(r.text)

		res = []
		for address in parsed["data"]["ethereum"]["address"]:
			res.append({
				"address": address["address"],
				"balance": address["balances"],
			})
		print("Bitquery res: ", r, json.dumps(res, indent=2))



	##############################
	### random old shit below

	def try_bitquery(self):
		bitquery_tx_history = '''
		{ ethereum(network: ethereum) {
				address(address: {is: "0xF55041E37E12cD407ad00CE2910B8269B01263b9"}) {
				balances {
					value
					history {
					value
					timestamp
					block
					transferAmount
					}
				}
				address
				annotation
				balance
				}
			}
		}
		'''

		balance_qry = '''
		{ethereum {
			address(address: {is: "0xF55041E37E12cD407ad00CE2910B8269B01263b9"}) 
			{	balances(
				height: {lteq: 12782835}
				currency: {in: ["ETH", "0xc944E90C64B2c07662A292be6244BDf05Cda44a7"]}
				) {
					currency {
						symbol
					}
					value
				}
			}
		}}
		'''

		qry = balance_qry
		print("sending bitquery wtf", balance_qry)

		h = {'X-API-KEY': self.apiKey}
		r = requests.post(self.apiUrl, headers=h, json={'query':qry})
		print(r, r.text)



graphscan_cut_history = '''
query test {
	rewardCutHistoryEntities {
		id
		indexer {
			id
			createdAt
		}
		indexingRewardCut
		indexingRewardEffectiveCut
		queryFeeCut
		queryFeeEffectiveCut
		blockNumber
		timestamp
		epoch
	}
}
'''

#0x0003ca24e19c30db588aabb81d55bfcec6e196c4
graphscan_tx_history = '''
query test {
	delegatorRewardHistoryEntities ( where: {
		indexer:"0x4d6a8776a164776c93618233a0003e8894e7e6c2", 
		delegator:"0x4d6a8776a164776c93618233a0003e8894e7e6c2"
	}){
		id
		indexer{
			id
			createdAt
		}
		delegator{
			id
			createdAt
		}
		reward
		blockNumber
		timestamp
		epoch
	}
}
'''

example_request = '''
curl 'https://graphql.bitquery.io/' \
  -H 'Connection: keep-alive' \
  -H 'Accept: application/json' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'X-API-KEY: keyredacted' \
  -H 'Content-Type: application/json' \
  -H 'Origin: https://graphql.bitquery.io' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Referer: https://graphql.bitquery.io/ide/uB7ahiUfXg' \
  -H 'Accept-Language: en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7' \
  --data-raw '{"query":"{\n  ethereum(network: ethereum) {\n    address(address: {is: \"0x4d6a8776a164776c93618233a0003e8894e7e6c2\"}) {\n      balances {\n        value\n        history {\n          value\n          timestamp\n          block\n          transferAmount\n        }\n      }\n      address\n      annotation\n      balance\n    }\n  }\n}\n","variables":"{}"}' \
  --compressed

POST / HTTP/1.1
Host: graphql.bitquery.io
Connection: keep-alive
Content-Length: 359
sec-ch-ua: " Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"
Accept: application/json
sec-ch-ua-mobile: ?0
Content-Type: application/json
Origin: https://graphql.bitquery.io
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
Referer: https://graphql.bitquery.io/ide/uB7ahiUfXg
Accept-Encoding: gzip, deflate, br
Accept-Language: en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7
'''