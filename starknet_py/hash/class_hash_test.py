# pylint: disable=line-too-long
# fmt: off
import pytest
from starkware.starknet.core.os.contract_class.deprecated_class_hash import (
    compute_deprecated_class_hash as sw_compute_class_hash,
)
from starkware.starknet.services.api.contract_class.contract_class import (
    DeprecatedCompiledClass,
)

from starknet_py.common import create_contract_class
from starknet_py.hash.class_hash import compute_class_hash
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.parametrize(
    "contract_source", [
        "map_compiled.json",
        "erc20_compiled.json",
        "oz_proxy_compiled.json",
        "argent_proxy_compiled.json",
        "universal_deployer_compiled.json",
        "precompiled/oz_proxy_address_0.8.1_compiled.json",
    ]
)
def test_compute_class_hash(contract_source):
    compiled_contract = read_contract(contract_source)
    contract_class = create_contract_class(compiled_contract)
    class_hash = compute_class_hash(contract_class)
    sw_class_hash = sw_compute_class_hash(DeprecatedCompiledClass.loads(compiled_contract))
    assert class_hash == sw_class_hash
