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
    levels: List[List[int]] = field(init=False)

    def __post_init__(self):
        if self.leaves:
            self.root_hash, self.branches = MerkleTree.build(
                self.leaves, self.hash_method
            )

    @staticmethod
    def build(
        leaves: List[int], hash_method: HashMethod
    ) -> Tuple[int, List[List[int]]]:
        if not leaves:
            raise ValueError("Cannot build Merkle tree from an empty list of leaves.")

        curr_level_nodes = leaves[:]
        branches: List[List[int]] = []

        while len(curr_level_nodes) > 1:
            if len(curr_level_nodes) != len(leaves):
                branches.append(curr_level_nodes[:])

            new_nodes = []
            for i in range(0, len(curr_level_nodes), 2):
                a, b = (
                    curr_level_nodes[i],
                    curr_level_nodes[i + 1] if i + 1 < len(curr_level_nodes) else 0,
                )
                new_nodes.append(MerkleTree.hash(a, b, hash_method))

            curr_level_nodes = new_nodes

        return curr_level_nodes[0], branches

    @staticmethod
    def hash(a: int, b: int, hash_method: HashMethod) -> int:
        return hash_method.hash(*sorted([a, b]))
