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

EXPECTED_HASH = (
    1296395137456368839993793774656077365717081707850199132015420167798246992965
)
EXPECTED_ADDRESS = (
    1420872929128670766694786702640106101468453910861612404633095347796994319944
)


def test_compute_hash():
    assert Contract.compute_contract_hash(SOURCE) == EXPECTED_HASH


def test_compute_address():
    assert (
        Contract.compute_address(
            compilation_source=SOURCE, constructor_args=[21, 37], salt=1111
        )
        == EXPECTED_ADDRESS
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
    )
    assert (
        call.hash == 0x203BFF8307C3266B0749A0D1DBA143907F32F7E55C84A4A34077690C9C91BAC
    )
