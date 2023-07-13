# fmt: off
import pytest

from starknet_py.common import create_casm_class
from starknet_py.hash.casm_class_hash import compute_casm_class_hash
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_COMPILED_V2_DIR
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.parametrize(
    "casm_contract_class_source, expected_casm_class_hash",
    [
        ("account_compiled.casm", 0x67f510792214d377fd1339f145d58620c8534d123c6a33784d1047a273fdc9b),
        ("erc20_compiled.casm", 0x68f383ca6e44752d0c45daf0115bfff471c8b1d3a8cec64a025d12beb3b3880),
        ("hello_starknet_compiled.casm", 0xdf4d3042eec107abe704619f13d92bbe01a58029311b7a1886b23dcbb4ea87),
        ("minimal_contract_compiled.casm", 0x46f2882281342dea7694207216f95d925ba08ef4be0cff5e81e9057f49ef3c2),
        ("test_contract_compiled.casm", 0x31945b2fcf27c7090d51e29ebdc5d9bf64f09860cf6c91e73cf7af54d444e5f),
        ("token_bridge_compiled.casm", 0x6febc54bb2b1f4f05e5fb70ce6bb13beefea4c423d77fb8435f97ef761ca4e2),
    ],
)
def test_compute_casm_class_hash(casm_contract_class_source, expected_casm_class_hash):
    casm_contract_class_str = read_contract(
        casm_contract_class_source, directory=CONTRACTS_COMPILED_V2_DIR
    )

    casm_class = create_casm_class(casm_contract_class_str)
    casm_class_hash = compute_casm_class_hash(casm_class)

    assert casm_class_hash == expected_casm_class_hash
