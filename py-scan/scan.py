from web3 import Web3

w3 = Web3(Web3.WebsocketProvider('wss://mainnet.infura.io/ws/v3/871114313d50416eab4ef3e8c22a96e7'))

# Get information about the latest block
w3.eth.getBlock('latest')

# Get the ETH balance of an address 
w3.eth.getBalance('YOUR_ADDRESS_HERE')