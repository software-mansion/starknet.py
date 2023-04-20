# pylint: disable=line-too-long
# fmt: off
import pytest

from starknet_py.common import create_contract_class
from starknet_py.hash.class_hash import compute_class_hash
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.parametrize(
    "contract_source, expected_class_hash", [
        ("map_compiled.json", 0x5F50ECC5F65B7B3FBBA3B040D06C7A0B2EEE6C38A7630290682361B6D385171),
        ("erc20_compiled.json", 0x7E1C623D92AE179D36C7DF1899596B7A5CACE76DE55A41F181B2474F5CA5A8),
        ("oz_proxy_compiled.json", 0x1D841DA0CDEE91624CF1C265A86842214F3DAAC30525AC5C505FD3BAA6AECAA),
        ("argent_proxy_compiled.json", 0x660F41E2FFEBE07703729569EAC75F2A68000488B24DF74E65ACF59FE225B1E),
        ("universal_deployer_compiled.json", 0x453EDFE167BDADB12E27CEAB113CEA29124AD086EDF035B546C84631E5BBC13),
        ("precompiled/oz_proxy_address_0.8.1_compiled.json", 0x413C36C287CB410D42F9E531563F68AC60A2913B5053608D640FB9B643ACFE6),
    ]
)
def test_compute_class_hash(contract_source, expected_class_hash):
    compiled_contract = read_contract(contract_source)
    contract_class = create_contract_class(compiled_contract)
    class_hash = compute_class_hash(contract_class)
    assert class_hash == expected_class_hash
