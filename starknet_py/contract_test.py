import pytest

from starknet_py.contract import Contract
from starknet_py.tests.e2e.conftest import contracts_dir

SOURCE = """
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
"""

SOURCE_WITH_IMPORTS = """
%lang starknet
%builtins pedersen range_check

from inner.inner import MockStruct

@external
func put{syscall_ptr: felt*, pedersen_ptr, range_check_ptr}(key: felt, value: felt) {
    return ();
}
"""

EXPECTED_HASH = (
    1688292534598790451057949508467835030243564096848945341781421603734773995268
)


EXPECTED_HASH_WITH_IMPORTS = (
    2467085149317457155287279889794209231367583529927798195223162392957233886584
)

EXPECTED_ADDRESS = (
    1369811099254663530533007926088345455337409146333603828325880844112617234253
)

EXPECTED_ADDRESS_WITH_IMPORTS = (
    1539179502839850929772015442738227060010315268355136760060396349750739505823
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
