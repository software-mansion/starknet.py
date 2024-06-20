from enum import Enum
from typing import List

from poseidon_py.poseidon_hash import poseidon_hash, poseidon_hash_many

from starknet_py.hash.utils import compute_hash_on_elements, pedersen_hash


class HashMethod(Enum):
    """
    Enum representing hash method.
    """

    PEDERSEN = "pedersen"
    POSEIDON = "poseidon"

    def hash(self, left: int, right: int):
        if self == HashMethod.PEDERSEN:
            return pedersen_hash(left, right)
        if self == HashMethod.POSEIDON:
            return poseidon_hash(left, right)
        raise ValueError(f"Unsupported hash method: {self}.")

    def hash_many(self, values: List[int]):
        if self == HashMethod.PEDERSEN:
            return compute_hash_on_elements(values)
        if self == HashMethod.POSEIDON:
            return poseidon_hash_many(values)
        raise ValueError(f"Unsupported hash method: {self}.")
