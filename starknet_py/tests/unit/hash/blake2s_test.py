"""
The test values are taken from sequencer repository:
https://github.com/starkware-libs/sequencer/blob/b29c0e8c61f7b2340209e256cf87dfe9f2c811aa/crates/blake2s/tests/blake2s_tests.rs
"""

import pytest

from starknet_py.hash.blake2s import encode_felt252_data_and_calc_blake_hash


@pytest.mark.parametrize(
    "input_felts, expected_result",
    [
        # Empty array
        (
            [],
            874258848688468311465623299960361657518391155660316941922502367727700287818,
        ),
        # Boundary: small felt at (2^63 - 1)
        (
            [(1 << 63) - 1],
            94160078030592802631039216199460125121854007413180444742120780261703604445,
        ),
        # Boundary: at 2^63
        (
            [1 << 63],
            318549634615606806810268830802792194529205864650702991817600345489579978482,
        ),
        # Very large felt
        (
            [0x800000000000011000000000000000000000000000000000000000000000000],
            3505594194634492896230805823524239179921427575619914728883524629460058657521,
        ),
        # Mixed: small and large felts
        (
            [42, 1 << 63, 1337],
            1127477916086913892828040583976438888091205536601278656613505514972451246501,
        ),
    ],
    ids=[
        "empty",
        "boundary_small_felt",
        "boundary_at_2_63",
        "very_large_felt",
        "mixed_small_large",
    ],
)
def test_encode_felt252_data_and_calc_blake_hash(input_felts, expected_result):
    result = encode_felt252_data_and_calc_blake_hash(input_felts)
    assert (
        result == expected_result
    ), f"StarknetPy implementation: {result} != Cairo implementation: {expected_result}"
