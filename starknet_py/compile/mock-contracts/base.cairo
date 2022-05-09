%lang starknet
%builtins pedersen range_check

from inner.inner import MockStruct

@external
func put{syscall_ptr : felt*, pedersen_ptr, range_check_ptr}(
        key : felt, value : felt):
    return ()
end