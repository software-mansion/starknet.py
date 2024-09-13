from typing import List

import pytest
from poseidon_py.poseidon_hash import poseidon_hash

from starknet_py.hash.hash_method import HashMethod
from starknet_py.hash.utils import pedersen_hash
from starknet_py.utils.merkle_tree import MerkleTree


@pytest.mark.parametrize(
    "leaves, hash_method, expected_root_hash",
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
def test_calculate_hash(
    leaves: List[str], hash_method: HashMethod, expected_root_hash: str
):
    if hash_method == HashMethod.PEDERSEN:
        apply_hash = pedersen_hash
    elif hash_method == HashMethod.POSEIDON:
        apply_hash = poseidon_hash
    else:
        raise ValueError(f"Unsupported hash method: {hash_method}.")

    a, b = int(leaves[0], 16), int(leaves[1], 16)
    merkle_hash = hash_method.hash(*sorted([b, a]))
    raw_hash = apply_hash(*sorted([b, a]))

    assert raw_hash == merkle_hash
    assert int(expected_root_hash, 16) == merkle_hash


@pytest.mark.parametrize(
    "hash_method",
    [
        HashMethod.PEDERSEN,
        HashMethod.POSEIDON,
    ],
)
def test_build_from_0_elements(hash_method: HashMethod):
    with pytest.raises(
        ValueError, match="Cannot build Merkle tree from an empty list of leaves."
    ):
        MerkleTree([], hash_method)


@pytest.mark.parametrize(
    "leaves, hash_method, expected_root_hash, expected_levels_count",
    [
        (["0x1"], HashMethod.PEDERSEN, "0x1", 1),
        (["0x1"], HashMethod.POSEIDON, "0x1", 1),
        (
            ["0x1", "0x2"],
            HashMethod.PEDERSEN,
            "0x5bb9440e27889a364bcb678b1f679ecd1347acdedcbf36e83494f857cc58026",
            2,
        ),
        (
            ["0x1", "0x2"],
            HashMethod.POSEIDON,
            "0x5d44a3decb2b2e0cc71071f7b802f45dd792d064f0fc7316c46514f70f9891a",
            2,
        ),
        (
            ["0x1", "0x2", "0x3", "0x4"],
            HashMethod.PEDERSEN,
            "0x38118a340bbba28e678413cd3b07a9436a5e60fd6a7cbda7db958a6d501e274",
            3,
        ),
        (
            ["0x1", "0x2", "0x3", "0x4"],
            HashMethod.POSEIDON,
            "0xa4d02f1e82fc554b062b754d3a4995e0ed8fc7e5016a7ca2894a451a4bae64",
            3,
        ),
        (
            ["0x1", "0x2", "0x3", "0x4", "0x5", "0x6"],
            HashMethod.PEDERSEN,
            "0x329d5b51e352537e8424bfd85b34d0f30b77d213e9b09e2976e6f6374ecb59",
            4,
        ),
        (
            ["0x1", "0x2", "0x3", "0x4", "0x5", "0x6"],
            HashMethod.POSEIDON,
            "0x34d525f018d8d6b3e492b1c9cda9bbdc3bc7834b408a30a417186c698c34766",
            4,
        ),
        (
            ["0x1", "0x2", "0x3", "0x4", "0x5", "0x6", "0x7"],
            HashMethod.PEDERSEN,
            "0x7f748c75e5bdb7ae28013f076b8ab650c4e01d3530c6e5ab665f9f1accbe7d4",
            4,
        ),
        (
            ["0x1", "0x2", "0x3", "0x4", "0x5", "0x6", "0x7"],
            HashMethod.POSEIDON,
            "0x3308a3c50c25883753f82b21f14c644ec375b88ea5b0f83d1e6afe74d0ed790",
            4,
        ),
    ],
)
def test_build_from_elements(
    leaves: List[str],
    hash_method: HashMethod,
    expected_root_hash: str,
    expected_levels_count: int,
):
    tree = MerkleTree([int(leaf, 16) for leaf in leaves], hash_method)

    assert tree.root_hash is not None
    assert tree.levels is not None
    assert tree.root_hash == int(expected_root_hash, 16)
    assert len(tree.levels) == expected_levels_count
