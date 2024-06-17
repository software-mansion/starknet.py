from enum import Enum
from typing import List

from poseidon_py.poseidon_hash import poseidon_hash_many

from starknet_py.hash.utils import compute_hash_on_elements


class HashMethod(Enum):
    """
    Enum representing hash method.
    """

    PEDERSEN = "pedersen"
    POSEIDON = "poseidon"

    def hash(self, values: List[int]):
        if self == HashMethod.PEDERSEN:
            return compute_hash_on_elements(values)
        if self == HashMethod.POSEIDON:
            return poseidon_hash_many(values)
        raise ValueError(f"Unsupported hash method: {self}.")
