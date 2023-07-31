import pytest

from starknet_py.common import create_sierra_compiled_contract
from starknet_py.hash.sierra_class_hash import compute_sierra_class_hash
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_COMPILED_V2_DIR
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.parametrize(
    "sierra_contract_class_source, expected_class_hash",
    # fmt: off
    [
        ("account_compiled.json", 0x6cb1e2b2b7a2eb8231357f8bee5cb6683476f350d35986afff6b67bf9e66b6c),
        ("erc20_compiled.json", 0x5dc48d64a0f3852a4ac2b06f9b2a801177f35952715f32d3a7ca60af235e762),
        ("hello_starknet_compiled.json", 0x4ec2ecf58014bc2ffd7c84843c3525e5ecb0a2cac33c47e9c347f39fc0c0944),
        ("minimal_contract_compiled.json", 0xa298b56801319b054855d39720eab22502e77627552e564d3bf50bd7844df9),
        ("test_contract_compiled.json", 0x28d7f03cced748cd9913afa5549edf4a02def8508fe1ca7feea2f8d403918a6),
        ("token_bridge_compiled.json", 0x4f2d81d7c0da5ec97f19b8195748a559de42207ff8bc3ac5f818e752c431c7b),
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
