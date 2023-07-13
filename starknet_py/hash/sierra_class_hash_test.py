import pytest

from starknet_py.common import create_sierra_compiled_contract
from starknet_py.hash.sierra_class_hash import compute_sierra_class_hash
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_COMPILED_V2_DIR
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.parametrize(
    "sierra_contract_class_source, expected_class_hash",
    # fmt: off
    [
        ("account_compiled.json", 0x33a3216293eab7fce7da337a39db0358eb8838b6f865dee85a563c3fcee2c48),
        ("erc20_compiled.json", 0x21074834d251687180a8d007c5ffc5819e3e68993de9d2d2c32a67d9f3091ff),
        ("hello_starknet_compiled.json", 0x5eb29a274db250647dd8a274aff727e569c5213224e4b16276492e3b7883baf),
        ("minimal_contract_compiled.json", 0x215e92d0cc44d6c665aa798ff80bbda0d551e503a453d5d28ef2fd568e2aea6),
        ("test_contract_compiled.json", 0x157fd44d882dd261b40264c4fccc1f6d30a486ea6e6764c1ce2274367a4bbd7),
        ("token_bridge_compiled.json", 0x609336ce91584447cc6a7d591a6dd098b75053ca8bbe5dbfa24b91be5636917),
    ],
    # fmt: on
)
def test_compute_sierra_class_hash(sierra_contract_class_source, expected_class_hash):
    sierra_contract_class_str = read_contract(
        sierra_contract_class_source, directory=CONTRACTS_COMPILED_V2_DIR
    )

    sierra_contract_class = create_sierra_compiled_contract(sierra_contract_class_str)
    class_hash = compute_sierra_class_hash(sierra_contract_class)

    assert class_hash == expected_class_hash
