import os, json, time
import requests

class GraphscanAPI:
	def __init__(self, emitterFn=None):
		self.apiUrl = "https://api.thegraph.com/subgraphs/name/ryabina-io/graphscan"

	def get_delegators_for_indexer(self, address_list):
		addresses_string = ''
		for address in address_list:
			addresses_string = addresses_string + f'"{address}",'

		qry = '''{
			delegatedStakes (filter: {
			''' f'''indexer: [{addresses_string}] ''' '''
			}) {
				id
				indexer {
					id
					createdAt
					indexingRewardCut
					indexingRewardEffectiveCut
					stakingEfficiency
					delegatorsCount
				}
				delegator {
					id
					account {
						balance
						subgraphQueryFees
					}
					totalStakedTokens
					totalUnstakedTokens
					totalRealizedRewards
					unreleasedReward
					unreleasedPercent
					totalRewards
					stakesCount
					currentStaked
				}
				stakedTokens
				lockedTokens
				lockedUntil
				shareAmount
				personalExchangeRate
				realizedRewards
				totalRewards
				lastUndelegatedAt
				currentDelegationAmount
			}
		}
		'''

		#qry = qry_that_works
		print("sending graphscan delegators call...")
		r = requests.post(self.apiUrl, json={'query':qry})
		parsed = json.loads(r.text)
		#print("Graphscan res: ", r, json.dumps(parsed, indent=2))

		delegations = parsed["data"]["delegatedStakes"]
		res = []
		for delegation in delegations:
			res.append({
				"id": delegation['delegator']['id'],
				"staked": delegation['stakedTokens'],
				"delegated": delegation['currentDelegationAmount'],
				"share": delegation['shareAmount'],
			})
		return res


	def get_latest_block(self):
		print("sending graphscan latest block call...")
		r = requests.post(self.apiUrl, json={'query':block_qry})
		parsed = json.loads(r.text)
		latest_block = parsed["data"]["epoches"][0]["endBlock"]
		print("Graphscan latest block: ", latest_block, r, json.dumps(parsed, indent=2))
		return latest_block




#########################################################################################################
## some graphql queries for graphscan below


block_qry = '''
{
  epoches (
      orderBy: startBlock
      orderDirection: desc
      first: 1
  ) {
      id
      startBlock
      endBlock
      signalledTokens
      stakeDeposited
      queryFeeRebates
      totalRewards
      totalIndexerRewards
      totalDelegatorRewards
  }
}
'''

epoch_qry = '''
{
  graphNetwork (id:1) {
    lastRunEpoch
    epochCount
    subgraphDeploymentCount
    delegatorCount
    stakedIndexersCount
    currentEpoch
  }
}
'''

qry_that_works = '''
{
	delegatedStakes (filter: {
		indexer: ["0x4d6a8776a164776c93618233a0003e8894e7e6c2","0x4140d3d0086fce37ebadd965dff88e12cf78b1fb"]
	}) {
		id
		indexer {
			id
			createdAt
			indexingRewardCut
			indexingRewardEffectiveCut
			stakingEfficiency
			delegatorsCount
		}
		delegator {
			id
			account {
				balance
				subgraphQueryFees
			}
			totalStakedTokens
			totalUnstakedTokens
			totalRealizedRewards
			unreleasedReward
			unreleasedPercent
			totalRewards
			stakesCount
			currentStaked
		}
		stakedTokens
		lockedTokens
		lockedUntil
		shareAmount
		personalExchangeRate
		realizedRewards
		totalRewards
		lastUndelegatedAt
		currentDelegationAmount
	}
}
'''


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

