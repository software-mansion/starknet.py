# pylint: disable=line-too-long
# fmt: off
import pytest

from starknet_py.common import create_contract_class
from starknet_py.hash.contract_class import compute_class_hash
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.parametrize(
    "contract_source, hash_", [
        ("map_compiled.json", 0x4be1e2dda2059b976e3e5efa3d5a892e0b4b3ff9edc4a3a58206358e7a0d30d),
        ("erc20_compiled.json", 0x417063f10bb36376154196dfffdb17fb757e71b228a8e147a4ec8bfc448d4c),
        ("oz_proxy_compiled.json", 0x601407cf04ab1fbab155f913db64891dc749f4343bc9e535bd012234a46dc61),
        ("argent_proxy_compiled.json", 0x358ef62c72e99b3e94923826c2090f3875cee2f059e6236a8ec2e070ebd046b),
        ("universal_deployer_compiled.json", 0x56679f765a989444f0db426e54ee779b7685ccfd4e39113b9c963eb903e20e3),
        ("precompiled/oz_proxy_address_0.8.1_compiled.json", 0x413c36c287cb410d42f9e531563f68ac60a2913b5053608d640fb9b643acfe6),
    ]
)
def test_compute_class_hash(contract_source, hash_):
    compiled_contract = read_contract(contract_source)
    contract_class = create_contract_class(compiled_contract)
    class_hash = compute_class_hash(contract_class)
    assert class_hash == hash_
