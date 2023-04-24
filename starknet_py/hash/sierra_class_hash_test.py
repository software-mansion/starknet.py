import pytest

from starknet_py.common import create_sierra_compiled_contract
from starknet_py.hash.sierra_class_hash import compute_sierra_class_hash
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_COMPILED_V1_DIR
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.parametrize(
    "sierra_contract_class_source, expected_class_hash",
    # fmt: off
    [
        ("account_compiled.json", 0x6EEEDC89C94B6B3F9C20C79E65809B67BF00A835BD5BFEA8CD91E0CDCCFC9EA),
        ("erc20_compiled.json", 0x734FD32EDED6D2957DEEBF401790DDFBB21873C5779785F588313D15918F337),
        ("hello_starknet_compiled.json", 0x4DDFF767F4CD2964D146BE535E2B5427C75B9A7DEDF6165080BE3727A6C4CD4),
        ("minimal_contract_compiled.json", 0x73D76FB4C8B79D9F462F9D776A5E16B05365E5E0799CE7684C64AF29F391AB7),
        ("test_contract_compiled.json", 0x6859F9EA4C92ACCA2B3FF41F52B6462EC6F90C582F038B08ECF0BE6DD02E95),
        ("token_bridge_compiled.json", 0x15C69E37DE24A247D2D319D69085C2F484080CD2FC8CA87F48BC5CCD8419CA9),
    ],
    # fmt: on
)
def test_compute_sierra_class_hash(sierra_contract_class_source, expected_class_hash):
    sierra_contract_class_str = read_contract(
        sierra_contract_class_source, directory=CONTRACTS_COMPILED_V1_DIR
    )
    sierra_contract_class = create_sierra_compiled_contract(sierra_contract_class_str)
    class_hash = compute_sierra_class_hash(sierra_contract_class)

    assert class_hash == expected_class_hash
