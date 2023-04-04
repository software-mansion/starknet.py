%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.starknet.common.syscalls import delegate_call, delegate_l1_handler

@storage_var
func implementation_address_storage() -> (implementation_address: felt):
end

@constructor
func constructor{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    implementation_address: felt, selector: felt, calldata_len: felt, calldata: felt*
):
    implementation_address_storage.write(implementation_address)
    return ()
end

@external
@raw_input
@raw_output
func __default__{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    selector: felt, calldata_size: felt, calldata: felt*
) -> (retdata_size: felt, retdata: felt*):
    let (implementation_address) = implementation_address_storage.read()

    let (retdata_size: felt, retdata: felt*) = delegate_call(
        contract_address=implementation_address,
        function_selector=selector,
        calldata_size=calldata_size,
        calldata=calldata,
    )
    return (retdata_size=retdata_size, retdata=retdata)
end

@view
func implementation{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() -> (
    implementation_address: felt
):
    let (implementation_address) = implementation_address_storage.read()
    return (implementation_address=implementation_address)
end
