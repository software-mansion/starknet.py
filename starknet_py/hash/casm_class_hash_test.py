# fmt: off
import pytest

from starknet_py.common import create_casm_class
from starknet_py.hash.casm_class_hash import compute_casm_class_hash
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_COMPILED_V2_DIR
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.parametrize(
    "casm_contract_class_source, expected_casm_class_hash",
    [
        ("account_compiled.casm", 0x18799df07f230e6ae5440dd3396afd6a2d6e627be3b8ab3e4fa64edb30f64d2),
        ("erc20_compiled.casm", 0x5adc857416202a5902c01168542e188c3aa6380f57c911ae98cf20bc52be367),
        ("hello_starknet_compiled.casm", 0x6ff9f7df06da94198ee535f41b214dce0b8bafbdb45e6c6b09d4b3b693b1f17),
        ("minimal_contract_compiled.casm", 0x5fd87fec0614148ce800defb1ad3dbb9212451672e244d24fb1aa359e342055),
        ("test_contract_compiled.casm", 0x2193add92c182c9236f0c156f11dc4f18d5a78fd9b763a3c0f4a1d3bd8b87d4),
        ("token_bridge_compiled.casm", 0x87c179b5f09a8137eb7b28c621eb8337b61216e4381d6e200200f22c511aad),
        ("precompiled/starknet_contract_v2_6.casm", 0x603dd72504d8b0bc54df4f1102fdcf87fc3b2b94750a9083a5876913eec08e4),
    ],
)
def test_compute_casm_class_hash(casm_contract_class_source, expected_casm_class_hash):
    casm_contract_class_str = read_contract(
        casm_contract_class_source, directory=CONTRACTS_COMPILED_V2_DIR
    )

    casm_class = create_casm_class(casm_contract_class_str)
    casm_class_hash = compute_casm_class_hash(casm_class)

    assert casm_class_hash == expected_casm_class_hash
