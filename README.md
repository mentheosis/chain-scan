# chain-scan
A bare-bones playground for getting some raw data from various kinds of Blockchains  

2021-06-13: The file py-scan/scan.py is the most fun one in here at the moment. It will load eth blocks into a sqlite db
and attempt to decode underlying contracts (although the graph GRT is the only ABI included right now)  
todo: make the chain asyncrounously pull all historal blocks in batches too

# Notes
## Ethereum:
sweet blog on chain data: https://medium.com/coinmonks/defi-protocol-data-how-to-query-618c934dbbe2

## Polkadot:
### useful references:
polkadot.js lib: https://polkadot.js.org/docs/api  
public endpoints coming from their little react-app project: https://github.com/polkadot-js/apps/blob/master/packages/apps-config/src/endpoints/production.ts  
Polkadot wiki on running node: https://wiki.polkadot.network/docs/en/build-node-interaction  
sidecar thing from parity: https://github.com/paritytech/substrate-api-sidecar/blob/master/package.json  
polkadot.io telemetry scanner page: https://telemetry.polkadot.io/#/Polkadot  

another cool polka scanner thing: https://polkascan.io/polkadot  
polkascan's github: https://github.com/polkascan  
more polkascan github shortcut: https://github.com/polkascan/py-substrate-interface  

substrate docs: https://substrate.dev/docs/en/knowledgebase/learn-substrate/extrinsics  