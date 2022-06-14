import functools
import os
from typing import List, Callable, Iterable, Optional
from dataclasses import dataclass

from starkware.cairo.common.hash_state import compute_hash_on_elements
from starkware.cairo.lang.vm.crypto import pedersen_hash as default_hash
from starkware.crypto.signature.signature import sign

from crypto_cpp_py.cpp_bindings import (
    cpp_hash,
    get_cpp_lib_file,
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


# PREFIX_TRANSACTION = 'StarkNet Transaction'
PREFIX_TRANSACTION = 476441609247967894954472788179128007176248455022


@dataclass(frozen=True)
class Call:
    to_addr: int
    selector: int
    calldata: List[int]


@dataclass(frozen=True)
class MultiCall:
    account: int
    calls: Iterable[Call]
    nonce: int
    max_fee: int = 0
    version: int = 0


# pylint: disable=too-many-arguments
def hash_multicall_with(
    multi_call: MultiCall,
    hash_fun: Callable[[int, int], int],
) -> int:
    """
    Mimics the behavior of
    https://github.com/argentlabs/cairo-contracts/blob/c2ff198e5de5b19514d99ecff604a7cbf3377d2f/contracts/Account.cairo#L248
    """

    calls_hash = compute_hash_on_elements(
        [hash_call_with(c, hash_fun=hash_fun) for c in multi_call.calls],
        hash_func=hash_fun,
    )

    return compute_hash_on_elements(
        [
            PREFIX_TRANSACTION,
            multi_call.account,
            calls_hash,
            multi_call.nonce,
            multi_call.max_fee,
            multi_call.version,
        ],
        hash_func=hash_fun,
    )


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
    # TODO: When sign from crypto-cpp is faster, uncomment this section # pylint: disable=fixme
    # if use_cpp_variant():
    #     return cpp_sign(msg_hash, priv_key, seed)
    return sign(msg_hash, priv_key, seed)


def pedersen_hash(left: int, right: int) -> int:
    if use_cpp_variant():
        return cpp_hash(left, right)
    return default_hash(left, right)


def hash_multicall(multi_call: MultiCall) -> int:
    return hash_multicall_with(
        multi_call=multi_call,
        hash_fun=pedersen_hash,
    )
