#!/bin/bash
set -e
MOCK_DIRECTORY=starknet_py/tests/e2e/mock

compile_contracts_v1() {
    CONTRACTS_DIRECTORY="$MOCK_DIRECTORY"/contracts_v1
    SCARB_WITH_VERSION=$(head -n 1 "$CONTRACTS_DIRECTORY/.tool-versions")

    if ! command -v asdf >/dev/null 2>&1; then
        echo "Install asdf, before executing this script is required to manage scarb version"
        exit 1
    fi
    asdf plugin-add scarb
    asdf install $SCARB_WITH_VERSION

    (cd $CONTRACTS_DIRECTORY && scarb build)
    echo "$output"
}

compile_contracts_v2() {
    CONTRACTS_DIRECTORY="$MOCK_DIRECTORY"/contracts_v2
    SCARB_WITH_VERSION=$(head -n 1 "$CONTRACTS_DIRECTORY/.tool-versions")

    if ! command -v asdf >/dev/null 2>&1; then
        echo "Install asdf, before executing this script is required to manage scarb version"
        exit 1
    fi

    asdf plugin-add scarb
    asdf install $SCARB_WITH_VERSION

    (cd $CONTRACTS_DIRECTORY && scarb build)
    echo "$output"
}

compile_contracts_v0() {
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

if [[ "$@" =~ .*"V0".* ]]; then
    compile_contracts_v0
fi

if [[ "$@" =~ .*"V1".* ]]; then
    compile_contracts_v1
fi

if [[ "$@" =~ .*"V2".* ]]; then
    compile_contracts_v2
fi


if [ -z "$@" ]; then
    compile_contracts_v0
    compile_contracts_v1
    compile_contracts_v2
fi

exit 0
