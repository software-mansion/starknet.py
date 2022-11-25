#!/bin/bash

MOCK_DIRECTORY=starknet_py/tests/e2e/mock
CONTRACTS_DIRECTORY="$MOCK_DIRECTORY"/contracts
CONTRACTS_COMPILED_DIRECTORY="$MOCK_DIRECTORY"/contracts_compiled

# delete all artifacts except precompiled ones
find $CONTRACTS_COMPILED_DIRECTORY -maxdepth 1 -type f -delete

# compile Cairo test contracts
echo "Compiling Cairo contracts with $(poetry run starknet-compile --version)"

number_of_contracts=0
for contract in "$CONTRACTS_DIRECTORY"/*.cairo; do
    basename=$(basename "$contract")

    output=$CONTRACTS_COMPILED_DIRECTORY/"${basename%.*}_compiled.json"
    abi=$CONTRACTS_COMPILED_DIRECTORY/"${basename%.*}_abi.json"

    # set account contract flag
    account_contract_flag=""
    if [[ $basename == *"account"* ]]; then
      account_contract_flag="--account_contract"
    fi

    echo "Compiling $contract..."
    # run starknet-compile
    poetry run starknet-compile $account_contract_flag --cairo_path $CONTRACTS_DIRECTORY:$MOCK_DIRECTORY --output $output --abi $abi $contract
    number_of_contracts=$((number_of_contracts+1))
done

echo "Compiled $number_of_contracts Cairo files successfully"
