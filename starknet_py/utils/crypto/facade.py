import functools
import os
from typing import List, Callable, Iterable, Optional

from starkware.cairo.common.hash_state import compute_hash_on_elements
from starkware.cairo.lang.vm.crypto import pedersen_hash as default_hash
from starkware.crypto.signature.signature import sign

from starknet_py.utils.crypto.cpp_bindings import (
    cpp_sign,
    cpp_hash,
    get_cpp_lib,
    cpp_binding_loaded,
    ECSignature,
)


def sign_calldata(calldata: Iterable[int], priv_key: int):
    """
    Helper function that signs hash:
    hash = pedersen_hash(calldata[0], 0)
    hash = pedersen_hash(calldata[1], hash)
    hash = pedersen_hash(calldata[2], hash)
    ...

    :param calldata: iterable of ints
    :param priv_key: private key
    :return: signed calldata's hash
    """
    hashed_calldata = functools.reduce(lambda x, y: pedersen_hash(y, x), calldata, 0)
    return message_signature(hashed_calldata, priv_key)


# Implementation
# pylint: disable=too-many-arguments
def hash_message_with(
    account: int,
    to_addr: int,
    selector: int,
    calldata: List[int],
    nonce: int,
    hash_fun: Callable[[int, int], int],
) -> int:
    return compute_hash_on_elements(
        [
            account,
            to_addr,
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


def message_signature(msg_hash, priv_key, seed: Optional[int] = 32) -> ECSignature:
    if use_cpp_variant():
        return cpp_sign(msg_hash, priv_key, seed)
    return sign(msg_hash, priv_key, seed)


def pedersen_hash(left: int, right: int) -> int:
    return cpp_hash(left, right) if use_cpp_variant() else default_hash(left, right)


def hash_message(
    account: int,
    to_addr: int,
    selector: int,
    calldata: List[int],
    nonce: int,
) -> int:
    return hash_message_with(
        account=account,
        to_addr=to_addr,
        selector=selector,
        calldata=calldata,
        nonce=nonce,
        hash_fun=pedersen_hash,
    )
