# pylint: disable=line-too-long
# fmt: off
import pytest

from starknet_py.common import create_contract_class
from starknet_py.hash.class_hash import compute_class_hash
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.parametrize(
    "contract_source, expected_class_hash", [
        ("map_compiled.json", 0x2c73e5cf1538ca1fd44018fab311c8be3b96bd9136912512fa4789fe1733ff9),
        ("erc20_compiled.json", 0x24cfb287ef1f88912fbd71bd1d763c53d863b473be5d54086b46a4ded8bdfb0),
        ("oz_proxy_compiled.json", 0x5a157230e2584204fc5c0ca5f766457cbb2b5b140ee3bfbfa5e4f6178420611),
        ("argent_proxy_compiled.json", 0x5e8378ef0c0d90472094025f6b0541e31d6bc2fcf2e268c33bcea201f2921ad),
        ("universal_deployer_compiled.json", 0x37a1cd95937b83c4fe77b30f727cd7e3be9208cbb00bd8607122cb981032448),
        ("precompiled/oz_proxy_address_0.8.1_compiled.json", 0x413c36c287cb410d42f9e531563f68ac60a2913b5053608d640fb9b643acfe6),
    ]
)
def test_compute_class_hash(contract_source, expected_class_hash):
    compiled_contract = read_contract(contract_source)
    contract_class = create_contract_class(compiled_contract)
    class_hash = compute_class_hash(contract_class)
    assert class_hash == expected_class_hash
