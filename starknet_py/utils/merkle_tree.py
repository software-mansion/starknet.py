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
        self.root_hash, self.levels = self._build()

    def _build(self) -> Tuple[int, List[List[int]]]:
        if not self.leaves:
            raise ValueError("Cannot build Merkle tree from an empty list of leaves.")

        if len(self.leaves) == 1:
            return self.leaves[0], [self.leaves]

        curr_level_nodes = self.leaves[:]
        levels: List[List[int]] = []

        while len(curr_level_nodes) > 1:
            if len(curr_level_nodes) != len(self.leaves):
                levels.append(curr_level_nodes[:])

            new_nodes = []
            for i in range(0, len(curr_level_nodes), 2):
                a, b = (
                    curr_level_nodes[i],
                    curr_level_nodes[i + 1] if i + 1 < len(curr_level_nodes) else 0,
                )
                new_nodes.append(self.hash_method.hash(*sorted([a, b])))

            curr_level_nodes = new_nodes
        levels = [self.leaves] + levels + [curr_level_nodes]
        return curr_level_nodes[0], levels
