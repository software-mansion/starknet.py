from dataclasses import dataclass, field
from typing import List, Tuple

from starknet_py.hash.hash_method import HashMethod


@dataclass
class MerkleTree:
    """
    Dataclass representing a MerkleTree object.
    """

    leaves: List[int]
    hash_method: HashMethod
    root_hash: int = field(init=False)
    branches: List[List[int]] = field(init=False)

    def __post_init__(self):
        if self.leaves:
            self.root_hash, self.branches = MerkleTree.build(
                self.leaves, self.hash_method
            )

    @staticmethod
    def build(
        leaf_hashes: List[int], hash_method: HashMethod
    ) -> Tuple[int, List[List[int]]]:
        if not leaf_hashes:
            raise ValueError("Cannot build Merkle tree from an empty list of leaves.")

        leaves = leaf_hashes[:]
        branches: List[List[int]] = []

        while len(leaves) > 1:
            if len(leaves) != len(leaf_hashes):
                branches.append(leaves[:])

            new_leaves = []
            for i in range(0, len(leaves), 2):
                a, b = leaves[i], leaves[i + 1] if i + 1 < len(leaves) else 0
                new_leaves.append(MerkleTree.hash(a, b, hash_method))

            leaves = new_leaves

        return leaves[0], branches

    @staticmethod
    def hash(a: int, b: int, hash_method: HashMethod) -> int:
        return hash_method.hash(*sorted([a, b]))
