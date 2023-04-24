import pytest
from starkware.starknet.core.os.contract_class.compiled_class_hash import (
    compute_compiled_class_hash as sw_compute_compiled_class_hash,
)
from starkware.starknet.services.api.contract_class.contract_class import (
    CompiledClass as SwCompiledClass,
)

from starknet_py.common import create_casm_class
from starknet_py.hash.casm_class_hash import compute_casm_class_hash
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_COMPILED_V1_DIR
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.parametrize(
    "casm_contract_class_source",
    [
        "account_compiled.casm",
        "erc20_compiled.casm",
        "hello_starknet_compiled.casm",
        "minimal_contract_compiled.casm",
        "test_contract_compiled.casm",
        "token_bridge_compiled.casm",
    ],
)
def test_compute_casm_class_hash(casm_contract_class_source):
    casm_contract_class_str = read_contract(
        casm_contract_class_source, directory=CONTRACTS_COMPILED_V1_DIR
    )

    sw_compiled_class = SwCompiledClass.loads(casm_contract_class_str)
    sw_compiled_class_hash = sw_compute_compiled_class_hash(sw_compiled_class)

    casm_class = create_casm_class(sw_compiled_class.dumps())
    casm_class_hash = compute_casm_class_hash(casm_class)

    assert casm_class_hash == sw_compiled_class_hash
