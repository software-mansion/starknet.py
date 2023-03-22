from typing import cast

import pytest
from starkware.starknet.core.os.contract_class.compiled_class_hash import (
    compute_compiled_class_hash as sw_compute_compiled_class_hash,
)
from starkware.starknet.services.api.contract_class.contract_class import CompiledClass as SwCompiledClass

from starknet_py.hash.casm_class_hash import compute_casm_class_hash
from starknet_py.net.client_models import CasmClass
from starknet_py.net.schemas.gateway import CasmClassSchema
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.parametrize(
    "casm_contract_class_source",
    [
        "minimal_contract_compiled.casm",
        "hello_starknet_compiled.casm",
    ],
)
def test_compute_casm_class_hash(casm_contract_class_source):
    casm_contract_class_str = read_contract("precompiled/" + casm_contract_class_source)

    sw_compiled_class = SwCompiledClass.loads(casm_contract_class_str)
    sw_compiled_class_hash = sw_compute_compiled_class_hash(sw_compiled_class)

    casm_class = cast(CasmClass, CasmClassSchema().load(sw_compiled_class.dump()))
    casm_class_hash = compute_casm_class_hash(casm_class)

    assert casm_class_hash == sw_compiled_class_hash
