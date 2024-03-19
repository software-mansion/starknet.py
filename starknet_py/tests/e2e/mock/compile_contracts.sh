#!/bin/bash
MOCK_DIRECTORY=starknet_py/tests/e2e/mock
# Run the first script
bash $MOCK_DIRECTORY/compile_contracts_with_scarb.sh

# Run the second script
bash $MOCK_DIRECTORY/compile_contracts_v0.sh
