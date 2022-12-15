import os
from typing import Optional

from crypto_cpp_py.cpp_bindings import (
    cpp_hash,
    get_cpp_lib_file,
    ECSignature,
)
from starkware.cairo.common.hash_state import compute_hash_on_elements
from starkware.cairo.lang.vm.crypto import pedersen_hash as default_hash
from starkware.crypto.signature.signature import sign

from starknet_py.net.client_models import Call

# PREFIX_TRANSACTION = encoded 'StarkNet Transaction'
PREFIX_TRANSACTION = 476441609247967894954472788179128007176248455022


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


# Interface
def use_cpp_variant() -> bool:
    force_disable_ext = (
        os.getenv("DISABLE_CRYPTO_C_EXTENSION", "false").lower() == "true"
    )
    cpp_lib_file = get_cpp_lib_file()
    return not force_disable_ext and bool(cpp_lib_file)


def message_signature(msg_hash, priv_key, seed: Optional[int] = 32) -> ECSignature:
    return sign(msg_hash, priv_key, seed)


def pedersen_hash(left: int, right: int) -> int:
    if use_cpp_variant():
        return cpp_hash(left, right)
    return default_hash(left, right)
