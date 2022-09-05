%lang starknet
%builtins pedersen range_check ecdsa

from starkware.cairo.common.cairo_builtins import HashBuiltin, SignatureBuiltin
from starkware.cairo.common.hash import hash2
from starkware.cairo.common.signature import verify_ecdsa_signature
from starkware.starknet.common.syscalls import get_tx_signature

struct UserDetails {
    favourite_number: felt,
    favourite_tuple: (felt, felt, felt),
}

// A map from user (public key) to a balance.
@storage_var
func balance(user: felt) -> (details: UserDetails) {
}

// Increases the balance of the given user by the given amount.
@external
func set_details{
    syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr, ecdsa_ptr: SignatureBuiltin*
}(user: felt, details: UserDetails) {
    // Fetch the signature.
    let (sig_len: felt, sig: felt*) = get_tx_signature();

    // Verify the signature length.
    assert sig_len = 2;

    // Compute the hash of the message.
    // The hash of (x, 0) is equivalent to the hash of (x).
    let (hash) = hash2{hash_ptr=pedersen_ptr}(details.favourite_number, 0);
    let (hash) = hash2{hash_ptr=pedersen_ptr}(details.favourite_tuple[0], hash);
    let (hash) = hash2{hash_ptr=pedersen_ptr}(details.favourite_tuple[1], hash);
    let (hash) = hash2{hash_ptr=pedersen_ptr}(details.favourite_tuple[2], hash);

    // Verify the user's signature.
    verify_ecdsa_signature(message=hash, public_key=user, signature_r=sig[0], signature_s=sig[1]);

    balance.write(user, details);
    return ();
}

// Returns the balance of the given user.
@view
func get_details{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(user: felt) -> (
    details: UserDetails
) {
    let (details) = balance.read(user=user);
    return (details,);
}
