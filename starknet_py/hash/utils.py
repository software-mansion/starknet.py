import functools
from typing import Optional, Sequence

from crypto_cpp_py.cpp_bindings import ECSignature, cpp_hash
from eth_utils.crypto import keccak
from starkware.cairo.lang.vm.crypto import pedersen_hash as default_hash
from starkware.crypto.signature.signature import sign

from starknet_py.common import int_from_bytes
from starknet_py.utils.crypto.facade import use_cpp_variant

MASK_250 = 2**250 - 1


def _starknet_keccak(data: bytes) -> int:
    """
    A variant of eth-keccak that computes a value that fits in a StarkNet field element.
    """
    return int_from_bytes(keccak(data)) & MASK_250


def pedersen_hash(left: int, right: int) -> int:
    """
    One of two hash functions (along with _starknet_keccak) used throughout StarkNet.
    """
    if use_cpp_variant():
        return cpp_hash(left, right)
    return default_hash(left, right)


def compute_hash_on_elements(data: Sequence) -> int:
    """
    Computes a hash chain over the data, in the following order:
        h(h(h(h(0, data[0]), data[1]), ...), data[n-1]), n).

    The hash is initialized with 0 and ends with the data length appended.
    The length is appended in order to avoid collisions of the following kind:
    H([x,y,z]) = h(h(x,y),z) = H([w, z]) where w = h(x,y).
    """
    return functools.reduce(pedersen_hash, [*data, len(data)], 0)


def message_signature(
    msg_hash: int, priv_key: int, seed: Optional[int] = 32
) -> ECSignature:
    """
    Signs the message with private key.
    """
    return sign(msg_hash, priv_key, seed)
