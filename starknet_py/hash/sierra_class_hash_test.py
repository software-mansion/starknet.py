import pytest

from starknet_py.common import create_sierra_compiled_contract
from starknet_py.hash.sierra_class_hash import compute_sierra_class_hash
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_COMPILED_V2_DIR
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.parametrize(
    "sierra_contract_class_source, expected_class_hash",
    # fmt: off
    [
        ("account_compiled.json", 0x12f3bdfbb32ab45078a0af658b78617023d0ece273e7b2e3d14f03a7a9cba4e),
        ("erc20_compiled.json", 0x9e3dbe53e170edc8b6817251a0e5a6e417cd04295015017a1d4e86a4a40d1a),
        ("hello_starknet_compiled.json", 0x5cb6ab123cf9f06798dcd8227d46f4d5d5d157b4ce51ae2236aa5d9b1cb01ea),
        ("minimal_contract_compiled.json", 0x614cde60994efdac8c95401809e98abd4221b02b5174f25b599f8145c11fb80),
        ("test_contract_compiled.json", 0x40e041157a32a43e0c20389f4dcec0a97a22718ddbc24f223f7553fa0de3c08),
        ("token_bridge_compiled.json", 0x4586bfabdc8e8e9334c73650b68a824ae5fab191bc4bb290af31b8e36005012),
    ],
    # fmt: on
)
def test_compute_sierra_class_hash(sierra_contract_class_source, expected_class_hash):
    sierra_contract_class_str = read_contract(
        sierra_contract_class_source, directory=CONTRACTS_COMPILED_V2_DIR
    )

    sierra_contract_class = create_sierra_compiled_contract(sierra_contract_class_str)
    class_hash = compute_sierra_class_hash(sierra_contract_class)

    assert class_hash == expected_class_hash
