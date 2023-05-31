# pylint: disable=line-too-long
# fmt: off
import pytest

from starknet_py.common import create_contract_class
from starknet_py.hash.class_hash import compute_class_hash
from starknet_py.tests.e2e.fixtures.misc import get_python_version, read_contract

if get_python_version()[:2] == (3, 9):
    from starkware.starknet.core.os.contract_class.deprecated_class_hash import (
        compute_deprecated_class_hash as sw_compute_deprecated_class_hash,
    )
    from starkware.starknet.services.api.contract_class.contract_class import (
        DeprecatedCompiledClass as SwDeprecatedCompiledClass,
    )

@pytest.mark.parametrize(
    "contract_source, expected_class_hash", [
        ("map_compiled.json", 0x2C73E5CF1538CA1FD44018FAB311C8BE3B96BD9136912512FA4789FE1733FF9),
        ("erc20_compiled.json", 0x24CFB287EF1F88912FBD71BD1D763C53D863B473BE5D54086B46A4DED8BDFB0),
        ("oz_proxy_compiled.json", 0x5A157230E2584204FC5C0CA5F766457CBB2B5B140EE3BFBFA5E4F6178420611),
        ("argent_proxy_compiled.json", 0x5E8378EF0C0D90472094025F6B0541E31D6BC2FCF2E268C33BCEA201F2921AD),
        ("universal_deployer_compiled.json", 0x37A1CD95937B83C4FE77B30F727CD7E3BE9208CBB00BD8607122CB981032448),
        ("precompiled/oz_proxy_address_0.8.1_compiled.json", 0x413C36C287CB410D42F9E531563F68AC60A2913B5053608D640FB9B643ACFE6),
    ]
)
def test_compute_class_hash(contract_source, expected_class_hash):
    compiled_contract = read_contract(contract_source)
    contract_class = create_contract_class(compiled_contract)
    class_hash = compute_class_hash(contract_class)

    if get_python_version()[:2] == (3, 9):
        sw_deprecated_class = SwDeprecatedCompiledClass.loads(compiled_contract)
        expected_class_hash = sw_compute_deprecated_class_hash(sw_deprecated_class)

    assert class_hash == expected_class_hash
