# pylint: disable=line-too-long
# fmt: off
from typing import cast

import pytest

from starknet_py.class_hash import compute_class_hash
from starknet_py.net.client_models import DeclaredContract
from starknet_py.net.schemas.gateway import DeclaredContractSchema
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.parametrize(
    "contract_source, hash_", [
        ("map_compiled.json", 0x4be1e2dda2059b976e3e5efa3d5a892e0b4b3ff9edc4a3a58206358e7a0d30d),
        ("erc20_compiled.json", 0x6d157eb6e8cc2a587ed2cb22f29778c326a814d1375fc374981c82f6581332b),
        ("oz_proxy_compiled.json", 0x601407cf04ab1fbab155f913db64891dc749f4343bc9e535bd012234a46dc61),
        ("argent_proxy_compiled.json", 0x358ef62c72e99b3e94923826c2090f3875cee2f059e6236a8ec2e070ebd046b),
        ("universal_deployer_compiled.json", 0x56679f765a989444f0db426e54ee779b7685ccfd4e39113b9c963eb903e20e3),
    ]
)
def test(contract_source, hash_):
    compiled_contract = read_contract(contract_source)
    contract_class = cast(DeclaredContract, DeclaredContractSchema().loads(compiled_contract))
    class_hash = compute_class_hash(contract_class)
    assert class_hash == hash_


@pytest.mark.parametrize(
    "contract_source", ["precompiled/oz_proxy_address_0.8.1_compiled.json"]
)
def test_old_compiler_version(contract_source):
    compiled_contract = read_contract(contract_source)
    contract_class = cast(DeclaredContract, DeclaredContractSchema().loads(compiled_contract))

    with pytest.raises(ValueError, match=r"compiler before version 0\.10\.0"):
        compute_class_hash(contract_class)
