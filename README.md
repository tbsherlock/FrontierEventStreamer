# Frontier Event Streamer

This is my entry for the 2026 EVE Frontier hackathon. 

A checkpoint-driven event scanner for the **EVE Frontier** package on the Sui blockchain. It polls for new checkpoints, drains all on-chain Move events across every watched module, parses them into typed Python dataclasses. It can also scan through chain history for events matching a filter.

Currently development environment running live on [Stillness](http://fes.mywire.org:8766/) 

# Examples

Included are three example usages of this package.

## example 1: webhook server
Uses the event streamer to listen for the latest on-chain events. A WebHook server then allows consumers to subscribe to channels to then be streamed events. A web app acts as a web hook consumer and display events on a front-end.

## example 2: enricher
Scans through events in order to populate a database. This additional data can then be used to produced enriched events. For example, 'CharacterCreatedEvent' and 'MetadataChangedEvent' can be scanned to produce a lookup table to resolve player id's to their names. This data can then be used to create more meaningful events, such as KillMails that include player names and tribe. 

## example 3: discord bot
Uses the event streamer to listen for the latest on-chain events. On new events, the discord bot will notify a specified channel.


## Quick Start
 
By default this connects to the **testnet** RPC and scans the `utopia` package. Override with environment variables:
 
```bash
WH_HOST = 0.0.0.0
WH_PORT = 8765
STATIC_HOST = 0.0.0.0
STATIC_PORT = 80
RPC_URL = https://fullnode.mainnet.sui.io:443 \
PACKAGE_ID = 0xYOUR_PACKAGE_ID \
python3 examples/whwebserver.py
```