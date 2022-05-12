#!/bin/sh

DEVNET_ADDRESS=$1

starknet deploy --contract starknet_py/tests/e2e/setupy_scripts/balance_compiled.json \
  --gateway_url "$DEVNET_ADDRESS"/gateway \
  --feeder_gateway_url "$DEVNET_ADDRESS"/feeder_gateway \
  --salt 0x123

starknet invoke --address 0x043d95e049c7dece86574a8d3fb5c0f9e4422f8a7fec6d744f26006374642252 \
  --abi contracts/balance_abi.json \
  --function increase_balance \
  --inputs 1234 \
  --gateway_url "$DEVNET_ADDRESS"/gateway \
  --feeder_gateway_url "$DEVNET_ADDRESS"/feeder_gateway

starknet get_block --number 0 \
  --gateway_url "$DEVNET_ADDRESS"/gateway \
  --feeder_gateway_url "$DEVNET_ADDRESS"/feeder_gateway |
  python3 -c "import sys, json; print(json.load(sys.stdin)['block_hash'])"