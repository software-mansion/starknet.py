#!/bin/sh

DEVNET_ADDRESS=$1
CONTRACT_ADDRESS=$2

starknet get_class_hash_at \
  --contract_address "$CONTRACT_ADDRESS" \
  --gateway_url "$DEVNET_ADDRESS"/gateway \
  --feeder_gateway_url "$DEVNET_ADDRESS"/feeder_gateway