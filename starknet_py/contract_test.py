import os
from pathlib import Path
import pytest

from starknet_py.contract import Contract, PreparedFunctionCall, ContractData
from starknet_py.net import Client

SOURCE = """
# Declare this file as a StarkNet contract and set the required
# builtins.
%lang starknet
%builtins pedersen range_check

from starkware.cairo.common.cairo_builtins import HashBuiltin

# Define a storage variable.
@storage_var
func balance() -> (res : felt):
end

# Increases the balance by the given amount.
@external
func increase_balance{
        syscall_ptr : felt*, pedersen_ptr : HashBuiltin*,
        range_check_ptr}(amount : felt):
    let (res) = balance.read()
    balance.write(res + amount)
    return ()
end

# Returns the current balance.
@view
func get_balance{
        syscall_ptr : felt*, pedersen_ptr : HashBuiltin*,
        range_check_ptr}() -> (res : felt):
    let (res) = balance.read()
    return (res)
end

@constructor
func constructor{
        syscall_ptr : felt*, pedersen_ptr : HashBuiltin*,
        range_check_ptr}(a: felt, b: felt):
    return ()
end
"""

SOURCE_WITH_IMPORTS = """
%lang starknet
%builtins pedersen range_check

from inner.inner import MockStruct

@external
func put{syscall_ptr : felt*, pedersen_ptr, range_check_ptr}(
        key : felt, value : felt):
    return ()
end
"""

EXPECTED_HASH = (
    2767133637016006695125577369743492278827480805001470205448944437134861258965
)


EXPECTED_HASH_WITH_IMPORTS = (
    2824740597818368748846455525738594583883439901518687339337045493609254033404
)

EXPECTED_ADDRESS = (
    3046198292581715633143389750649762877325412695701500547187874584238544215539
)

EXPECTED_ADDRESS_WITH_IMPORTS = (
    1220010402807226171903428091897681365505165756832763447362783771809682550518
)

directory = os.path.dirname(__file__)
search_path = Path(directory, "utils/compiler/mock-contracts")


def test_compute_hash():
    assert Contract.compute_contract_hash(SOURCE) == EXPECTED_HASH


def test_compute_hash_with_search_path():
    assert (
        Contract.compute_contract_hash(SOURCE_WITH_IMPORTS, search_paths=[search_path])
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
            search_paths=[search_path],
        )
        == EXPECTED_ADDRESS_WITH_IMPORTS
    )


def test_transaction_hash():
    # noinspection PyTypeChecker
    call = PreparedFunctionCall(
        calldata=[1234],
        arguments={},
        selector=1530486729947006463063166157847785599120665941190480211966374137237989315360,
        client=Client("testnet"),
        payload_transformer=None,
        contract_data=ContractData(
            address=0x03606DB92E563E41F4A590BC01C243E8178E9BA8C980F8E464579F862DA3537C,
            abi=None,
            identifier_manager=None,
        ),
        version=0,
        max_fee=0,
    )
    assert call.hash == 0xD0A52D6E77B836613B9F709AD7F4A88297697FEFBEF1ADA3C59692FF46702C


def test_no_valid_source():
    with pytest.raises(ValueError) as v_err:
        Contract.compute_contract_hash()

    assert "One of compiled_contract or compilation_source is required." in str(
        v_err.value
    )
