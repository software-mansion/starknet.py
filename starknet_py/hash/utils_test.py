import pytest

from starknet_py.hash.utils import compute_hash_on_elements


@pytest.mark.parametrize(
    "data, calculated_hash",
    (
        (
            [1, 2, 3, 4, 5],
            3442134774288875752012730520904650962184640568595562887119811371865001706826,
        ),
        (
            [28, 15, 39, 74],
            1457535610401978056129941705021139155249904351968558303142914517100335003071,
        ),
    ),
)
def test_compute_hash_on_elements(data, calculated_hash):
    assert compute_hash_on_elements(data) == calculated_hash
