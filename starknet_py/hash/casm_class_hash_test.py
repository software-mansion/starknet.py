# fmt: off
import pytest

from starknet_py.common import create_casm_class
from starknet_py.hash.casm_class_hash import compute_casm_class_hash
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_COMPILED_V1_DIR
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.parametrize(
    "casm_contract_class_source, expected_casm_class_hash",
    [
        ("account_compiled.casm", 0x3cdd0f6bf354a568c950a679594d3eeb86dc16403c3bc26601baa73ed557289),
        ("erc20_compiled.casm", 0x6cd0956406e7d3accb97c743b777f6f0bc50a6297817cdfa34363ad6f50e17),
        ("hello_starknet_compiled.casm", 0x3ed389c91c1e6d532ac767b00e236a3b209c853eca7f250a5399d65f39ab86f),
        ("minimal_contract_compiled.casm", 0x46f2882281342dea7694207216f95d925ba08ef4be0cff5e81e9057f49ef3c2),
        ("test_contract_compiled.casm", 0x81a647af555f5be4da1a4460afc0e4943f1454192b166794cc8688e0882af),
        ("token_bridge_compiled.casm", 0x40ae3f4ad29089ae6c68eaaf075f887fd8db47d74ae277903e24b344724ebf1),
    ],
)
def test_compute_casm_class_hash(casm_contract_class_source, expected_casm_class_hash):
    casm_contract_class_str = read_contract(
        casm_contract_class_source, directory=CONTRACTS_COMPILED_V1_DIR
    )

    casm_class = create_casm_class(casm_contract_class_str)
    casm_class_hash = compute_casm_class_hash(casm_class)

    assert casm_class_hash == expected_casm_class_hash
