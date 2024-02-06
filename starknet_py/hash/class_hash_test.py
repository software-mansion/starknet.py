# pylint: disable=line-too-long
# fmt: off
import copy

import pytest

from starknet_py.common import create_contract_class
from starknet_py.hash.class_hash import compute_class_hash
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_COMPILED_V0_DIR
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.parametrize(
    "contract_source, expected_class_hash", [
        ("balance_compiled.json", 0x12177ea61e5791cc068d7ee979b74f60a7205a23404c07440f4892b826147c0),
        ("map_compiled.json", 0x45dc8f1a90d242f9ebdd07c42301eb16845fbad294f7f9118cce544c16d64b4),
        ("erc20_compiled.json", 0x528d1ce44f53e888c2259738018e2e77bea9cb97c8b7fc7edab67aa4a880181),
        ("oz_proxy_compiled.json", 0x3e1526155defb7e26a017e9020e1043cce3c5a9144a9ce497c95648ababbdf1),
        ("argent_proxy_compiled.json", 0x191295ed4e4bbc63209aaf4d025979f8180fe998c761f616ccd29b5acc8ae1f),
        ("universal_deployer_compiled.json", 0x1fda6c88607d4edd7881671959cf73fb2172c952910a60f3d01ef0cd63a635),
        ("precompiled/oz_proxy_address_0.8.1_compiled.json", 0x413c36c287cb410d42f9e531563f68ac60a2913b5053608d640fb9b643acfe6),
    ]
)
def test_compute_class_hash(contract_source, expected_class_hash):
    compiled_contract = read_contract(contract_source, directory=CONTRACTS_COMPILED_V0_DIR)
    contract_class = create_contract_class(compiled_contract)
    initial_contract_class = copy.deepcopy(contract_class)
    class_hash = compute_class_hash(contract_class)

    assert class_hash == expected_class_hash
    assert contract_class == initial_contract_class
