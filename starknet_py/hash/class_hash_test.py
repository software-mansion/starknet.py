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
        ("balance_compiled.json", 0x35074a58b8897ca3a38acdd7636ca5fc530bbda9f4ff896ab4205c6e846ff01),
        ("map_compiled.json", 0x27e20b6e9c825b8a2de1a6fae317c0c05b0a3f1bc158c68885bd0fdf74e7d8e),
        ("erc20_compiled.json", 0x7abcb4a526399039d84f20956d3dd25ec21ed56ac7a58841fc6d677f76f0f5e),
        ("oz_proxy_compiled.json", 0x395e64cc7304606742f955ee576c79ae1b67d93d73bfc9ffe21c1088a86de34),
        ("argent_proxy_compiled.json", 0x244c972f9ebd85f8390f1a4e56d5a10444933e75ad4fb4a1fc88f16c7fed148),
        ("universal_deployer_compiled.json", 0x3f9c23fab233e00720eb3acc797d8f0d2e08907eac198e74ccd2631cc982265),
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
