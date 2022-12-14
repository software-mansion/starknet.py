from eth_utils.crypto import keccak

from starknet_py.common import int_from_bytes
from starknet_py.constants import MASK_250


def _starknet_keccak(data: bytes) -> int:
    """
    A variant of eth-keccak that computes a value that fits in a StarkNet field element.
    """
    return int_from_bytes(keccak(data)) & MASK_250
