#!/bin/bash

MOCK_DIRECTORY=starknet_py/tests/e2e/mock
CONTRACTS_DIRECTORY="$MOCK_DIRECTORY"/contracts_v1
CONTRACTS_COMPILED_DIRECTORY="$MOCK_DIRECTORY"/contracts_compiled_v1

# get path to Cargo.toml
MANIFEST_PATH=`cat starknet_py/tests/e2e/manifest-path`

# delete all artifacts except precompiled ones
mkdir -p $CONTRACTS_COMPILED_DIRECTORY
find $CONTRACTS_COMPILED_DIRECTORY -maxdepth 1 -type f -delete

# compile Cairo1 test contracts
COMPILER_VERSION=`cargo run --bin starknet-compile --manifest-path $MANIFEST_PATH -- --version 2> /dev/null`
printf "Compiling Cairo1 contracts with $COMPILER_VERSION\n\n"

number_of_contracts=0
for contract in "$CONTRACTS_DIRECTORY"/*.cairo; do
    basename=$(basename "$contract")

    contract_json=$CONTRACTS_COMPILED_DIRECTORY/"${basename%.*}_compiled.json"
    contract_casm=$CONTRACTS_COMPILED_DIRECTORY/"${basename%.*}_compiled.casm"

    # make temporary file for stderr
    tmp=$(mktemp)

    echo "Compiling $contract..."

    echo "Using starknet-compile..."
    cargo run --bin starknet-compile --manifest-path $MANIFEST_PATH -- --allowed-libfuncs-list-name experimental_v0.1.0 $contract $contract_json &> "$tmp"

    # print stderr only if error occurred
    if (( $? )) ; then
        cat "$tmp"
        rm "$tmp"
        continue
    fi
    rm "$tmp"

    echo "Using starknet-sierra-compile..."
    cargo run --bin starknet-sierra-compile --manifest-path $MANIFEST_PATH -- --allowed-libfuncs-list-name experimental_v0.1.0 --add-pythonic-hints $contract_json $contract_casm &> "$tmp"

    # print stderr only if error occurred
    if (( $? )) ; then
        cat "$tmp"
    else
        number_of_contracts=$((number_of_contracts+1))
    fi
    rm "$tmp"
done

echo "Compiled $number_of_contracts Cairo1 files successfully"
