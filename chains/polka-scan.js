// Required imports
const { ApiPromise, WsProvider } = require('@polkadot/api');
/*
  most bare-bones possible connection to polkadot.io's public API, using @polkadot/api from their doc example here:
  https://polkadot.js.org/docs/api/examples/promise/simple-connect
  */
async function main() {
    console.log("starting");
    const parityHosted = 'wss://rpc.polkadot.io';
    const provider = new WsProvider(parityHosted);
    // Create the API and wait until ready
    const api = await ApiPromise.create({ provider });
    // Retrieve the chain & node information information via rpc calls
    const [chain, nodeName, nodeVersion] = await Promise.all([
        api.rpc.system.chain(),
        api.rpc.system.name(),
        api.rpc.system.version()
    ]);
    console.log("Got api response");
    console.log(`You are connected to chain ${chain} using ${nodeName} v${nodeVersion}`);
    /*
      now read some blocks: https://polkadot.js.org/docs/api/examples/promise/listen-to-blocks
      Subscribe to the new headers on-chain. The callback is fired when new headers
      are found, the call itself returns a promise with a subscription that can be
      used to unsubscribe from the newHead subscription
    */
    console.log("subscribing for new blocks");
    // We only display a couple, then unsubscribe
    let count = 0;
    const unsubscribeHeads = await api.rpc.chain.subscribeNewHeads((header) => {
        console.log(`Chain is at block: #${header.number}`);
        //console.log(`Block header data: #${JSON.stringify(header,null,2)}`);
        if (++count === 256) {
            unsubscribeHeads();
            process.exit(0);
        }
    });
    /*
      Subscribe to system events via storage
      https://polkadot.js.org/docs/api/examples/promise/system-events
    */
    api.query.system.events((events) => {
        console.log(`\nReceived ${events.length} events:`);
        // Loop through the Vec<EventRecord>
        events.forEach((record) => {
            // Extract the phase, event and the event types
            const { event, phase } = record;
            const types = event.typeDef;
            // Show what we are busy with
            console.log(`\t${event.section}:${event.method}:: (phase=${phase.toString()})`);
            console.log(`\t\t${event.meta.documentation.toString()}`);
            // Loop through each of the parameters, displaying the type and data
            event.data.forEach((data, index) => {
                console.log(`\t\t\t${types[index].type}: ${data.toString()}`);
            });
        });
    });
}
main().catch((e) => {
    console.log("caught");
    console.error(e);
    process.exit(-1);
}); //.finally(() => process.exit());
