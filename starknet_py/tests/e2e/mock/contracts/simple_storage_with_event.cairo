%lang starknet
%builtins pedersen range_check

from starkware.cairo.common.cairo_builtins import HashBuiltin

@storage_var
func storage(key: felt) -> (value: felt) {
}

@event
func put_called(key: felt, prev_value: felt, value: felt) {
}

@external
func put{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(key: felt, value: felt) {
    let (prev_value) = storage.read(key);
    put_called.emit(key=key, prev_value=prev_value, value=value);
    storage.write(key, value);
    return ();
}
