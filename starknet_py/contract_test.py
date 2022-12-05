import pytest

from starknet_py.contract import Contract
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_DIR

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
    503253050526186908280124384407865038867585652783408167932765780369167667415
)


EXPECTED_HASH_WITH_IMPORTS = (
    261412312091196127884045926298824262716023266111934769893960173054947391504
)

EXPECTED_ADDRESS = (
    189023603034557919684596652904755695539249539924658863620932079547695762912
)

EXPECTED_ADDRESS_WITH_IMPORTS = (
    1265406736018442209950241864397668901077908617314293391280948790921629758434
)

search_path = CONTRACTS_DIR


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
