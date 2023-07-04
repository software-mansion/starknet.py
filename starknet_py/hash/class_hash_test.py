# pylint: disable=line-too-long
# fmt: off
import copy

import pytest

from starknet_py.common import create_contract_class
from starknet_py.hash.class_hash import compute_class_hash
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.parametrize(
    "contract_source, expected_class_hash", [
        ("balance_compiled.json", 0xf6c57433d98d26b9add810effadd20fac9c9e716efc882e509cd016d3a1c71),
        ("map_compiled.json", 0x4472f76ad0241ef47087cb55e6a414a7d66619a2b77e80bc9e8e79939fd6337),
        ("erc20_compiled.json", 0x1d3507676871860a57ff982bb323b7208430441d42b7792a67793f14618086b),
        ("oz_proxy_compiled.json", 0x746e3066bc46bd8019c37a37690107278ebec55020fb1b81e4f98c05fc15af9),
        ("argent_proxy_compiled.json", 0x401d1875f49ad9f2e833f74841db03cebf8eeaa767ed31736049a3eeef7fa7f),
        ("universal_deployer_compiled.json", 0x1cd10148443965964701fd22dc252b92027ac429e61e792f9cef6771db52444),
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
