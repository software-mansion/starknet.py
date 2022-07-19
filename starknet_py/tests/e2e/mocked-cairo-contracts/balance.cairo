%lang starknet

%builtins pedersen range_check ecdsa

from starkware.cairo.common.uint256 import Uint256
from starkware.cairo.common.cairo_builtins import (HashBuiltin, SignatureBuiltin)
from starkware.cairo.common.hash import hash2
from starkware.cairo.common.signature import (verify_ecdsa_signature)
from starkware.starknet.common.syscalls import get_tx_signature

@storage_var
func balance(user) -> (res: Uint256):
end

@external
func set_balance{
        syscall_ptr : felt*, pedersen_ptr : HashBuiltin*,
        range_check_ptr, ecdsa_ptr : SignatureBuiltin*}(
        user : felt, amount : Uint256):
    let (sig_len : felt, sig : felt*) = get_tx_signature()

    # Verify the signature length.
    assert sig_len = 2

    let (hash) = hash2{hash_ptr=pedersen_ptr}(amount.low, 0)
    let (amount_hash) = hash2{hash_ptr=pedersen_ptr}(amount.high, hash)

    # Verify the user's signature.
    verify_ecdsa_signature(
        message=amount_hash,
        public_key=user,
        signature_r=sig[0],
        signature_s=sig[1])

    balance.write(user, amount)
    return ()
end

@external
func get_balance{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(user : felt) -> (balance: Uint256):
    let (value) = balance.read(user=user)
    return (value)
end