# Frontier Event Streamer
 
A checkpoint-driven event scanner for the **EVE Frontier** world package on the Sui blockchain. It polls for new checkpoints, drains all on-chain Move events across every watched module, parses them into typed Python dataclasses.

## Quick Start
 
```bash
python3 main.py
```
 
By default this connects to the **testnet** RPC and scans the `utopia` package. Override with environment variables:
 
```bash
RPC_URL=https://fullnode.mainnet.sui.io:443 \
PACKAGE_ID=0xYOUR_PACKAGE_ID \
python3 main.py
```