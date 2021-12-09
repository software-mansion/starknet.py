import os
from typing import List, Callable

from starkware.cairo.common.hash_state import compute_hash_on_elements
from starkware.crypto.signature.signature import sign
from starkware.cairo.lang.vm.crypto import pedersen_hash as default_hash

from starknet.utils.crypto.cpp_bindings import (
    cpp_sign,
    cpp_hash,
    get_cpp_lib,
    cpp_binding_loaded,
    ECSignature,
)


# Implementation
def hash_message_with(
    account: int,
    to: int,
    selector: int,
    calldata: List[int],
    nonce: int,
    hash_fun: Callable[[int, int], int],
) -> int:
    return compute_hash_on_elements(
        [
            account,
            to,
            selector,
            compute_hash_on_elements(
                calldata,
                hash_func=hash_fun,
            ),
            nonce,
        ],
        hash_func=hash_fun,
    )


# Interface
def use_cpp_variant() -> bool:
    lib_path = os.environ.get("CRYPTO_C_EXPORTS_PATH")
    if lib_path and not cpp_binding_loaded():
        get_cpp_lib(lib_path)
    return bool(lib_path)


def message_signature(msg_hash, priv_key) -> ECSignature:
    if use_cpp_variant():
        return cpp_sign(msg_hash, priv_key)
    return sign(msg_hash, priv_key)


def hash_message(
    account: int,
    to: int,
    selector: int,
    calldata: List[int],
    nonce: int,
) -> int:
    hash_fun = default_hash
    if use_cpp_variant():
        hash_fun = cpp_hash
    return hash_message_with(
        account=account,
        to=to,
        selector=selector,
        calldata=calldata,
        nonce=nonce,
        hash_fun=hash_fun,
    )
