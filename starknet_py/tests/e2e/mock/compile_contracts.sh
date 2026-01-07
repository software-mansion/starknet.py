#!/bin/bash
set -e

MOCK_DIRECTORY="$(git rev-parse --show-toplevel)/starknet_py/tests/e2e/mock"
CONTRACTS_DIRECTORY_V1="$MOCK_DIRECTORY/contracts_v1"
CONTRACTS_DIRECTORY_V2="$MOCK_DIRECTORY/contracts_v2"

setup_scarb() {
    SCARB_VERSION="$1"

    if ! command -v asdf >/dev/null 2>&1; then
        echo "asdf not found in PATH! Install asdf and run this script again"
        exit 1
    fi

    if ! asdf plugin list | grep -q 'scarb'; then
        asdf plugin add scarb
    fi

    if ! asdf list scarb 2>/dev/null | grep -q "$SCARB_VERSION"; then
        asdf install scarb "$SCARB_VERSION"
    fi
}

update_salted_contracts() {
    SALT="$1"

    echo "Updating salted contracts with salt: ${SALT}"

    shopt -s nullglob # Enable nullglob to avoid issues if no files match

    for FILE in ./src/salted_*.cairo; do
        sed -i.bak "s/__salt_placeholder__/${SALT}/g" "$FILE"
        rm "$FILE.bak"
    done

    echo "Salted contracts updated"

    shopt -u nullglob
}

restore_salted_contracts() {
    SALT="$1"
    shopt -s nullglob # Enable nullglob to avoid issues if no files match

    for FILE in ./src/salted_*.cairo; do
        sed -i.bak "s/${SALT}/__salt_placeholder__/g" "$FILE"
        rm "$FILE.bak"
    done

    echo "Restored salted contracts to original state"

    shopt -u nullglob

}

compile_contracts_with_scarb() {
    CONTRACTS_DIRECTORY="$1"
    SCARB_VERSION=$(awk '/scarb/ {print $2}' "${CONTRACTS_DIRECTORY}/.tool-versions")

    setup_scarb "$SCARB_VERSION"

    pushd "$CONTRACTS_DIRECTORY" >/dev/null || exit 1

    echo "Checking Cairo contracts formatting"
    scarb fmt --check

    SALT=$(date +%s%3)

    update_salted_contracts "$SALT"

    echo "Compiling Cairo contracts with scarb $SCARB_VERSION"
    scarb clean && scarb build

    restore_salted_contracts "$SALT"

    popd >/dev/null || exit 1
}

case "$1" in
"v1")
    compile_contracts_with_scarb "$CONTRACTS_DIRECTORY_V1"
    ;;
"v2")
    compile_contracts_with_scarb "$CONTRACTS_DIRECTORY_V2"
    ;;
*)
    compile_contracts_with_scarb "$CONTRACTS_DIRECTORY_V1"
    compile_contracts_with_scarb "$CONTRACTS_DIRECTORY_V2"
    ;;
esac

echo "Successfully compiled contracts!"
exit 0
