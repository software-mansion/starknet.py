# pylint: disable=line-too-long
# fmt: off
import copy

import pytest

from starknet_py.common import create_contract_class
from starknet_py.hash.class_hash import compute_class_hash
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.parametrize(
    "contract_source, expected_class_hash", [
        ("balance_compiled.json", 0x48ffaec133112e9976dbfb19d013698ec2cb28ebdf228de854cce33ab88ee0e),
        ("map_compiled.json", 0x262ff2219291b8f04462791d46d8c0e74b1f3ea1c23906e64a7adcc3a24e243),
        ("erc20_compiled.json", 0x5e04060ca7b540caf66caaed610288d26716bf838b55d6653147edfb2004bab),
        ("oz_proxy_compiled.json", 0x6d4b67a038d80d1f2cb986fb21d25e5adfc4948fab5c8535944e1e4200bc862),
        ("argent_proxy_compiled.json", 0x535e1fc9f47e6dce91aa03cd15db1fff03a6b9907c0a5788a6f2c8d3919327c),
        ("universal_deployer_compiled.json", 0x6f38fb91ddbf325a0625533576bb6f6eafd9341868a9ec3faa4b01ce6c4f4dc),
        ("precompiled/oz_proxy_address_0.8.1_compiled.json", 0x413C36C287CB410D42F9E531563F68AC60A2913B5053608D640FB9B643ACFE6),
    ]
)
def test_compute_class_hash(contract_source, expected_class_hash):
    compiled_contract = read_contract(contract_source)
    contract_class = create_contract_class(compiled_contract)
    initial_contract_class = copy.deepcopy(contract_class)
    class_hash = compute_class_hash(contract_class)

    assert class_hash == expected_class_hash
    assert contract_class == initial_contract_class
