from typing import List

import pytest
from poseidon_py.poseidon_hash import poseidon_hash

from starknet_py.hash.hash_method import HashMethod
from starknet_py.hash.utils import pedersen_hash
from starknet_py.net.client_utils import _to_rpc_felt
from starknet_py.utils.merkle_tree import MerkleTree


@pytest.mark.parametrize(
    "leaves, hash_method, expected_hash",
    [
        (
            ["0x12", "0xa"],
            HashMethod.PEDERSEN,
            "0x586699e3ba6f118227e094ad423313a2d51871507dcbc23116f11cdd79d80f2",
        ),
        (
            ["0x12", "0xa"],
            HashMethod.POSEIDON,
            "0x6257f1f60f7c9fd49e2718c8ad19cd8dce6b1ba4b553b2123113f22b1e9c379",
        ),
        (
            [
                "0x5bb9440e27889a364bcb678b1f679ecd1347acdedcbf36e83494f857cc58026",
                "0x3",
            ],
            HashMethod.PEDERSEN,
            "0x551b4adb6c35d49c686a00b9192da9332b18c9b262507cad0ece37f3b6918d2",
        ),
        (
            [
                "0x5bb9440e27889a364bcb678b1f679ecd1347acdedcbf36e83494f857cc58026",
                "0x3",
            ],
            HashMethod.POSEIDON,
            "0xc118a3963c12777b0717d1dc89baa8b3ceed84dfd713a6bd1354676f03f021",
        ),
    ],
)
def test_calculate_hash(leaves: List[str], hash_method: HashMethod, expected_hash: str):
    expected_hash_int = int(expected_hash, 16)
    if hash_method == HashMethod.PEDERSEN:
        apply_hash = pedersen_hash
    elif hash_method == HashMethod.POSEIDON:
        apply_hash = poseidon_hash
    else:
        raise ValueError(f"Unsupported hash method: {hash_method}.")

    a, b = int(leaves[0], 16), int(leaves[1], 16)
    merkle_hash = MerkleTree.hash(a, b, hash_method)
    raw_hash = apply_hash(b, a)

    assert raw_hash == merkle_hash
    assert expected_hash_int == merkle_hash


@pytest.mark.parametrize(
    "hash_method",
    [
        HashMethod.PEDERSEN,
        HashMethod.POSEIDON,
    ],
)
def test_build_from_0_elements(hash_method: HashMethod):
    with pytest.raises(ValueError):
        MerkleTree.build([], hash_method)


def build_tree(
    leaves: List[int],
    hash_method: HashMethod,
    expected_root: int,
    expected_branch_count: int,
):
    leaves_as_felts = [_to_rpc_felt(leaf) for leaf in leaves]
    tree = MerkleTree(leaves_as_felts, hash_method)
    assert tree.root_hash is not None
    assert tree.branches is not None
    assert tree.root_hash == _to_rpc_felt(expected_root)
    assert len(tree.branches) == expected_branch_count


@pytest.mark.parametrize("hash_method", list(HashMethod))
def test_build_from_1_element(hash_method: HashMethod):
    leaves = [1]
    manual_root_hash = leaves[0]
    build_tree(leaves, hash_method, manual_root_hash, 0)


@pytest.mark.parametrize("hash_method", list(HashMethod))
def test_build_from_2_elements(hash_method: HashMethod):
    leaves = [1, 2]
    manual_root_hash = MerkleTree.hash(leaves[0], leaves[1], hash_method)
    build_tree(leaves, hash_method, manual_root_hash, 0)


@pytest.mark.parametrize("hash_method", list(HashMethod))
def test_build_from_4_elements(hash_method: HashMethod):
    leaves = [1, 2, 3, 4]
    manual_root_hash = MerkleTree.hash(
        MerkleTree.hash(leaves[0], leaves[1], hash_method),
        MerkleTree.hash(leaves[2], leaves[3], hash_method),
        hash_method,
    )
    build_tree(leaves, hash_method, manual_root_hash, 1)


@pytest.mark.parametrize("hash_method", list(HashMethod))
def test_build_from_6_elements(hash_method: HashMethod):
    leaves = [1, 2, 3, 4, 5, 6]
    manual_root_hash = MerkleTree.hash(
        MerkleTree.hash(
            MerkleTree.hash(leaves[0], leaves[1], hash_method),
            MerkleTree.hash(leaves[2], leaves[3], hash_method),
            hash_method,
        ),
        MerkleTree.hash(
            MerkleTree.hash(leaves[4], leaves[5], hash_method), 0, hash_method
        ),
        hash_method,
    )
    build_tree(leaves, hash_method, manual_root_hash, 2)


@pytest.mark.parametrize("hash_method", list(HashMethod))
def test_build_from_7_elements(hash_method: HashMethod):
    leaves = [1, 2, 3, 4, 5, 6, 7]
    manual_root_hash = MerkleTree.hash(
        MerkleTree.hash(
            MerkleTree.hash(leaves[0], leaves[1], hash_method),
            MerkleTree.hash(leaves[2], leaves[3], hash_method),
            hash_method,
        ),
        MerkleTree.hash(
            MerkleTree.hash(leaves[4], leaves[5], hash_method),
            MerkleTree.hash(leaves[6], 0, hash_method),
            hash_method,
        ),
        hash_method,
    )
    build_tree(leaves, hash_method, manual_root_hash, 2)
