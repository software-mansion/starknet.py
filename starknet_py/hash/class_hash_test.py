# pylint: disable=line-too-long
# fmt: off
import pytest

from starknet_py.common import create_contract_class
from starknet_py.hash.class_hash import compute_class_hash
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.parametrize(
    "contract_source, expected_class_hash", [
        ("balance_compiled.json", 0xD267E6A11EED91056994AA6A89B20CA2FA989385E88429B57A9FDCE84C58E6),
        ("map_compiled.json", 0x33DD7CD3C861824BB7E30669BCE71D80595FDF0D06AAE2B1760451B9EC34AD2),
        ("erc20_compiled.json", 0x3C255A783732B0D710FC3CE03EE89278B7851136EE4BCAE44F7085E4262B216),
        ("oz_proxy_compiled.json", 0x3B5E875B6ED7BBD0C5008EA8EA9845C44E30B0A203A4FB6460AA2535D37F390),
        ("argent_proxy_compiled.json", 0x7A3B9A62DB488B69A8E7942EC50B369816E5107AF64E5063065A451BF0DFA25),
        ("universal_deployer_compiled.json", 0x4569FFD48C2A3D455437C16DC843801FB896B1AF845BC8BC7BA83EBC4358B7F),
        ("precompiled/oz_proxy_address_0.8.1_compiled.json", 0x413C36C287CB410D42F9E531563F68AC60A2913B5053608D640FB9B643ACFE6),
    ]
)
def test_compute_class_hash(contract_source, expected_class_hash):
    compiled_contract = read_contract(contract_source)
    contract_class = create_contract_class(compiled_contract)
    class_hash = compute_class_hash(contract_class)

    assert class_hash == expected_class_hash
