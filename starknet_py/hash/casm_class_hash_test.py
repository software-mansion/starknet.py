# fmt: off
import pytest

from starknet_py.common import create_casm_class
from starknet_py.hash.casm_class_hash import compute_casm_class_hash
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_COMPILED_V1_DIR
from starknet_py.tests.e2e.fixtures.misc import get_python_version, read_contract

if get_python_version()[:2] == (3, 9):
    from starkware.starknet.core.os.contract_class.compiled_class_hash import (
        compute_compiled_class_hash as sw_compute_compiled_class_hash,
    )
    from starkware.starknet.services.api.contract_class.contract_class import (
        CompiledClass as SwCompiledClass,
    )

@pytest.mark.parametrize(
    "casm_contract_class_source, expected_casm_class_hash",
    [
        ("account_compiled.casm", 0x3A5F170FB6C78CF35D952AF21576BC9AFA56F430C653BAB2FE577DD807DD9C7),
        ("erc20_compiled.casm", 0x55FF1834CD7C0A3743032864C99A43B5A924899983B49612B0446931F9368C6),
        ("hello_starknet_compiled.casm", 0x2C895E2F0AED646E6DEC493287B9EAF4CADCE8983AD3D60164E15A7B1C35F54),
        ("minimal_contract_compiled.casm", 0x46F2882281342DEA7694207216F95D925BA08EF4BE0CFF5E81E9057F49EF3C2),
        ("test_contract_compiled.casm", 0x636E18EAA5730715FDF7A618C00CA03F6F18F324E22482FA97406F8A2336E0F),
        ("token_bridge_compiled.casm", 0x762391DDFDC7C30D48ACE43AA714B14E0F876489BF6B0DC5DF6F1F018963754),
    ],
)
def test_compute_casm_class_hash(casm_contract_class_source, expected_casm_class_hash):
    casm_contract_class_str = read_contract(
        casm_contract_class_source, directory=CONTRACTS_COMPILED_V1_DIR
    )

    casm_class = create_casm_class(casm_contract_class_str)
    casm_class_hash = compute_casm_class_hash(casm_class)

    if get_python_version()[:2] == (3, 9):
        sw_compiled_class = SwCompiledClass.loads(casm_contract_class_str)
        expected_casm_class_hash = sw_compute_compiled_class_hash(sw_compiled_class)

    assert casm_class_hash == expected_casm_class_hash
