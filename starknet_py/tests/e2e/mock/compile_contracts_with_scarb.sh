#!/bin/bash

if !command -v asdf >/dev/null 2>&1; then
    echo "Install asdf, before execute this script is required to manage scarb version"
    exit 1
fi

asdf plugin add scarb
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
exit 0

echo "Compiled $number_of_contracts Cairo1 files successfully"
