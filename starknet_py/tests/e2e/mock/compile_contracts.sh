#!/bin/bash
set -e

MOCK_DIRECTORY="$(git rev-parse --show-toplevel)/starknet_py/tests/e2e/mock"

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

apply_contract_salt() {
    SALT="$1"

    echo "Updating salted contracts with salt: ${SALT}"

    shopt -s nullglob # Make unmatched globs expand to nothing instead of a literal pattern

    for FILE in ./src/*.cairo; do
        sed -i.bak "s/__salt_placeholder__/${SALT}/g" "$FILE"
        rm "$FILE".bak 2> /dev/null
    done

    echo "Salted contracts updated"

    shopt -u nullglob
}

revert_contract_salt() {
    SALT="$1"
    echo "Restoring salted contracts to original state by removing salt: ${SALT}"
    shopt -s nullglob

    for FILE in ./src/*.cairo; do
        sed -i.bak "s/${SALT}/__salt_placeholder__/g" "$FILE"
        rm "$FILE.bak" 2> /dev/null
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

    SALT=$(uuidgen | tr -d '-')

    # Ensure revert_contract_salt is always executed on script exit (both on success and on failure)
    trap 'cd "$CONTRACTS_DIRECTORY" && revert_contract_salt "$SALT"' EXIT

    apply_contract_salt "$SALT"

    echo "Compiling Cairo contracts with scarb $SCARB_VERSION"
    scarb clean && scarb build
    popd >/dev/null || exit 1
}

if [ -n "$1" ]; then
    TARGET_DIR="$MOCK_DIRECTORY/$1"

    if [ ! -d "$TARGET_DIR" ]; then
        echo "Error: package '$1' does not exist in $MOCK_DIRECTORY"
        exit 1
    fi

    compile_contracts_with_scarb "$TARGET_DIR"
else
    for DIR in "$MOCK_DIRECTORY"/*; do
        if [[ -d "$DIR" && -f "$DIR/Scarb.toml" ]]; then
            compile_contracts_with_scarb "$DIR"
        fi
    done
fi


echo "Successfully compiled contracts!"
exit 0
