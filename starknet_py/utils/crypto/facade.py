import functools
import os
from typing import Optional, Sequence, Callable

from crypto_cpp_py.cpp_bindings import (
    cpp_hash,
    get_cpp_lib_file,
    ECSignature,
)
from starkware.cairo.lang.vm.crypto import pedersen_hash as default_hash
from starkware.crypto.signature.signature import sign

from starknet_py.constants import CONTRACT_ADDRESS_PREFIX, L2_ADDRESS_UPPER_BOUND
from starknet_py.net.client_models import Call


# Interface
def use_cpp_variant() -> bool:
    force_disable_ext = (
        os.getenv("DISABLE_CRYPTO_C_EXTENSION", "false").lower() == "true"
    )
    cpp_lib_file = get_cpp_lib_file()
    return not force_disable_ext and bool(cpp_lib_file)


def pedersen_hash(left: int, right: int) -> int:
    if use_cpp_variant():
        return cpp_hash(left, right)
    return default_hash(left, right)


def compute_hash_on_elements(
    data: Sequence, hash_func: Callable[[int, int], int] = pedersen_hash
):
    """
    Computes a hash chain over the data, in the following order:
        h(h(h(h(0, data[0]), data[1]), ...), data[n-1]), n).

    The hash is initialized with 0 and ends with the data length appended.
    The length is appended in order to avoid collisions of the following kind:
    H([x,y,z]) = h(h(x,y),z) = H([w, z]) where w = h(x,y).
    """
    return functools.reduce(hash_func, [*data, len(data)], 0)


def calculate_contract_address_from_hash(
    salt: int,
    class_hash: int,
    constructor_calldata: Sequence[int],
    deployer_address: int,
    hash_function: Callable[[int, int], int] = pedersen_hash,
) -> int:
    """
    Calculates the contract address in the StarkNet network - a unique identifier of the contract.
    The contract address is a hash chain of the following information:
        1. Prefix.
        2. Deployer address.
        3. Salt.
        4. Class hash.
    To avoid exceeding the maximum address we take modulus L2_ADDRESS_UPPER_BOUND of the above
    result.
    """
    constructor_calldata_hash = compute_hash_on_elements(
        data=constructor_calldata, hash_func=hash_function
    )
    raw_address = compute_hash_on_elements(
        data=[
            CONTRACT_ADDRESS_PREFIX,
            deployer_address,
            salt,
            class_hash,
            constructor_calldata_hash,
        ],
        hash_func=hash_function,
    )

    return raw_address % L2_ADDRESS_UPPER_BOUND


def hash_call_with(call: Call, hash_fun):
    return compute_hash_on_elements(
        [
            call.to_addr,
            call.selector,
            compute_hash_on_elements(
                call.calldata,
                hash_func=hash_fun,
            ),
        ]
    )


def message_signature(msg_hash, priv_key, seed: Optional[int] = 32) -> ECSignature:
    return sign(msg_hash, priv_key, seed)
