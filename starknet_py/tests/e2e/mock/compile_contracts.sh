#!/bin/bash
set -e
MOCK_DIRECTORY=starknet_py/tests/e2e/mock
CONTRACTS_DIRECTORY_V1="$MOCK_DIRECTORY"/contracts_v1
CONTRACTS_DIRECTORY_V2="$MOCK_DIRECTORY"/contracts_v2

setup_asdf() {
    if ! command -v asdf >/dev/null 2>&1; then
        echo "asdf not found in PATH! Install asdf and run this script again"
        exit 1
    fi
    asdf plugin-add scarb
}

compile_contracts_with_scarb() {
    CONTRACTS_DIRECTORY=$1
    SCARB_WITH_VERSION=$(<"$CONTRACTS_DIRECTORY/.tool-versions")

    setup_asdf

    asdf install $SCARB_WITH_VERSION

    echo "Compiling Cairo contracts with $SCARB_WITH_VERSION"

    pushd $CONTRACTS_DIRECTORY
    scarb clean && scarb build
    popd
}

compile_contracts_v0() {
    CONTRACTS_DIRECTORY="$MOCK_DIRECTORY"/contracts
    CONTRACTS_COMPILED_DIRECTORY="$MOCK_DIRECTORY"/contracts_compiled

    # delete all artifacts except precompiled ones
    find $CONTRACTS_COMPILED_DIRECTORY -maxdepth 1 -type f -delete

    # compile Cairo test contracts
    echo "Compiling Cairo contracts with $(poetry run starknet-compile-deprecated --version)"

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
    done

}

case $1 in
"v0")
    compile_contracts_v0
    ;;
"v1")
    compile_contracts_with_scarb $CONTRACTS_DIRECTORY_V1
    ;;
"v2")
    compile_contracts_with_scarb $CONTRACTS_DIRECTORY_V2
    ;;
*)
    compile_contracts_v0
    compile_contracts_with_scarb $CONTRACTS_DIRECTORY_V1
    compile_contracts_with_scarb $CONTRACTS_DIRECTORY_V2
    ;;
esac

echo "Successfully compiled contracts!"

exit 0
