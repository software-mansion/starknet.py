# fmt: off
import pytest

from starknet_py.common import create_casm_class
from starknet_py.hash.casm_class_hash import compute_casm_class_hash
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_COMPILED_V1_DIR
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.parametrize(
    "casm_contract_class_source, expected_casm_class_hash",
    [
        ("account_compiled.casm", 0x3a5f170fb6c78cf35d952af21576bc9afa56f430c653bab2fe577dd807dd9c7),
        ("erc20_compiled.casm", 0x55ff1834cd7c0a3743032864c99a43b5a924899983b49612b0446931f9368c6),
        ("hello_starknet_compiled.casm", 0x2c895e2f0aed646e6dec493287b9eaf4cadce8983ad3d60164e15a7b1c35f54),
        ("minimal_contract_compiled.casm", 0x46f2882281342dea7694207216f95d925ba08ef4be0cff5e81e9057f49ef3c2),
        ("test_contract_compiled.casm", 0x636e18eaa5730715fdf7a618c00ca03f6f18f324e22482fa97406f8a2336e0f),
        ("token_bridge_compiled.casm", 0x762391ddfdc7c30d48ace43aa714b14e0f876489bf6b0dc5df6f1f018963754),
    ],
)
def test_compute_casm_class_hash(casm_contract_class_source, expected_casm_class_hash):
    casm_contract_class_str = read_contract(
        casm_contract_class_source, directory=CONTRACTS_COMPILED_V1_DIR
    )

    casm_class = create_casm_class(casm_contract_class_str)
    casm_class_hash = compute_casm_class_hash(casm_class)

    assert casm_class_hash == expected_casm_class_hash
