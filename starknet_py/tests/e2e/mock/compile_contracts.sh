#!/bin/bash

compile_contracts_with_scarb() {
    if ! command -v asdf >/dev/null 2>&1; then
        echo "Install asdf, before executing this script is required to manage scarb version"
        exit 1
    fi

    asdf plugin-add scarb
    asdf install scarb 0.4.1
    asdf install scarb 2.6.3

    output=$(find . -type f -name "Scarb.toml" -execdir sh -c '
        echo "Running \"scarb fmt\" in directory: $PWD"
        find target/dev -maxdepth 1 -type f -delete
        scarb build
    ' \;)

    echo "$output"
    if grep -iq "Diff" <<<"$output"; then
        exit 1
    fi

    echo "Compiled $number_of_contracts Cairo1 files successfully"
    exit 0
}

compile_cairo_v0() {
    MOCK_DIRECTORY=starknet_py/tests/e2e/mock
    CONTRACTS_DIRECTORY="$MOCK_DIRECTORY"/contracts
    CONTRACTS_COMPILED_DIRECTORY="$MOCK_DIRECTORY"/contracts_compiled

    # delete all artifacts except precompiled ones
    find $CONTRACTS_COMPILED_DIRECTORY -maxdepth 1 -type f -delete

    # compile Cairo test contracts
    echo "Compiling Cairo contracts with $(poetry run starknet-compile-deprecated --version)"

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
        # run starknet-compile-deprecated
        poetry run starknet-compile-deprecated $account_contract_flag --cairo_path $CONTRACTS_DIRECTORY:$MOCK_DIRECTORY --output $output --abi $abi $contract
        number_of_contracts=$((number_of_contracts + 1))
    done

    echo "Compiled $number_of_contracts Cairo files successfully"

}

if [[ "$@" =~ .*"cairo0".* ]]; then
    compile_cairo_v0
fi


if [ -z "$@" ]; then
    compile_contracts_with_scarb
    compile_cairo_v0
fi
