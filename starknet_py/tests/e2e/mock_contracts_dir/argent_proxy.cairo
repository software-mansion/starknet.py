%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.math import assert_not_zero
from starkware.starknet.common.syscalls import library_call, library_call_l1_handler

####################
# CONSTRUCTOR
####################

@constructor
func constructor{
        syscall_ptr: felt*,
        pedersen_ptr: HashBuiltin*,
        range_check_ptr
    } (
        implementation: felt
    ):
    _set_implementation(implementation)
    return ()
end

####################
# EXTERNAL FUNCTIONS
####################

@external
@raw_input
@raw_output
func __default__{
        syscall_ptr: felt*,
        pedersen_ptr: HashBuiltin*,
        range_check_ptr
    } (
        selector : felt,
        calldata_size : felt,
        calldata : felt*
    ) -> (
        retdata_size : felt,
        retdata : felt*
    ):
    let (implementation) = _get_implementation()

    let (retdata_size : felt, retdata : felt*) = library_call(
        class_hash=implementation,
        function_selector=selector,
        calldata_size=calldata_size,
        calldata=calldata)
    return (retdata_size=retdata_size, retdata=retdata)
end

@l1_handler
@raw_input
func __l1_default__{
        syscall_ptr : felt*,
        pedersen_ptr : HashBuiltin*,
        range_check_ptr
    } (
        selector : felt,
        calldata_size : felt,
        calldata : felt*
    ):
    let (implementation) = _get_implementation()

    library_call_l1_handler(
        class_hash=implementation,
        function_selector=selector,
        calldata_size=calldata_size,
        calldata=calldata)
    return ()
end

####################
# VIEW FUNCTIONS
####################

@view
func get_implementation{
        syscall_ptr: felt*,
        pedersen_ptr: HashBuiltin*,
        range_check_ptr
    } () -> (implementation: felt):
    let (implementation) = _get_implementation()
    return (implementation=implementation)
end

####################
# STORAGE VARIABLES
####################

@storage_var
func _implementation() -> (address : felt):
end

####################
# INTERNAL FUNCTIONS
####################

func _get_implementation{
        syscall_ptr: felt*,
        pedersen_ptr: HashBuiltin*,
        range_check_ptr
    } () -> (implementation: felt):
    let (res) = _implementation.read()
    return (implementation=res)
end

# added for testing purposes
@external
func _set_implementation{
        syscall_ptr : felt*,
        pedersen_ptr : HashBuiltin*,
        range_check_ptr
    } (
        implementation: felt
    ):
    assert_not_zero(implementation)
    _implementation.write(implementation)
    return ()
end