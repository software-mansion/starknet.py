#!/bin/sh

DEVNET_ADDRESS=$1
CONTRACT_COMPILED=$2
CONTRACT_ABI=$3

curl  -X POST -H "Content-Type: application/json" -d '{"time": 2137}' "$DEVNET_ADDRESS"/set_time

starknet deploy --contract "$CONTRACT_COMPILED" \
  --gateway_url "$DEVNET_ADDRESS"/gateway \
  --feeder_gateway_url "$DEVNET_ADDRESS"/feeder_gateway \
  --salt 0x123 \
  --no_wallet

starknet invoke --address 0x043d95e049c7dece86574a8d3fb5c0f9e4422f8a7fec6d744f26006374642252 \
  --abi "$CONTRACT_ABI" \
  --function increase_balance \
  --inputs 1234 \
  --gateway_url "$DEVNET_ADDRESS"/gateway \
  --feeder_gateway_url "$DEVNET_ADDRESS"/feeder_gateway \
  --no_wallet

starknet get_block --number 0 \
  --gateway_url "$DEVNET_ADDRESS"/gateway \
  --feeder_gateway_url "$DEVNET_ADDRESS"/feeder_gateway |
  python3 -c "import sys, json; print(json.load(sys.stdin))"