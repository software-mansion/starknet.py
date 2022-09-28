from typing import cast

import pytest

from starknet_py.compile.compiler import CairoSourceCode
from starknet_py.contract import Contract
from starknet_py.tests.e2e.conftest import contracts_dir

SOURCE = cast(
    CairoSourceCode,
    """
// Declare this file as a StarkNet contract and set the required
// builtins.
%lang starknet
%builtins pedersen range_check

from starkware.cairo.common.cairo_builtins import HashBuiltin

// Define a storage variable.
@storage_var
func balance() -> (res: felt) {
}

// Increases the balance by the given amount.
@external
func increase_balance{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    amount: felt
) {
    let (res) = balance.read();
    balance.write(res + amount);
    return ();
}

// Returns the current balance.
@view
func get_balance{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() -> (res: felt) {
    let (res) = balance.read();
    return (res,);
}

@constructor
func constructor{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    a: felt, b: felt
) {
    return ();
}
""",
)

SOURCE_WITH_IMPORTS = cast(
    CairoSourceCode,
    """
%lang starknet
%builtins pedersen range_check

from inner.inner import MockStruct

@external
func put{syscall_ptr: felt*, pedersen_ptr, range_check_ptr}(key: felt, value: felt) {
    return ();
}
""",
)

EXPECTED_HASH = (
    59796004090676193477156334357335769146616822222924884531861796638754858565
)


EXPECTED_HASH_WITH_IMPORTS = (
    1660283819326006729930852394676591088728841641287494160212970585278003471330
)

EXPECTED_ADDRESS = (
    1137929495741405662588620210985073364961683439179866224790109707037343317227
)

EXPECTED_ADDRESS_WITH_IMPORTS = (
    2215802380634391255523792220475859318374841631894501575098737573407681278580
)

search_path = contracts_dir


def test_compute_hash():
    assert Contract.compute_contract_hash(SOURCE) == EXPECTED_HASH


def test_compute_hash_with_search_path():
    assert (
        Contract.compute_contract_hash(
            SOURCE_WITH_IMPORTS, search_paths=[str(search_path)]
        )
        == EXPECTED_HASH_WITH_IMPORTS
    )


def test_compute_address():
    assert (
        Contract.compute_address(
            compilation_source=SOURCE, constructor_args=[21, 37], salt=1111
        )
        == EXPECTED_ADDRESS
    )


def test_compute_address_with_imports():
    assert (
        Contract.compute_address(
            compilation_source=SOURCE_WITH_IMPORTS,
            salt=1111,
            search_paths=[str(search_path)],
        )
        == EXPECTED_ADDRESS_WITH_IMPORTS
    )


def test_compute_address_throws_on_no_source():
    with pytest.raises(ValueError) as exinfo:
        Contract.compute_address(salt=1111)

    assert "One of compiled_contract or compilation_source is required." in str(
        exinfo.value
    )


def test_no_valid_source():
    with pytest.raises(ValueError) as v_err:
        Contract.compute_contract_hash()

    assert "One of compiled_contract or compilation_source is required." in str(
        v_err.value
    )
