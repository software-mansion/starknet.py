import pytest

from starknet_py.common import create_casm_class
from starknet_py.hash.casm_class_hash import compute_casm_class_hash
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_COMPILED_V1_DIR
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.parametrize(
    "casm_contract_class_source, expected_casm_class_hash",
    [
        ("account_compiled.casm", 0x72B483338596AE5613652402A3B86B15B967C5F8214BECC1EB5C56BCA17CFCC),
        ("erc20_compiled.casm", 0x1C2FA751AE6D1C3155B8BBE28704D3DF5DFE3BB66244E80A28C292271A7410E),
        ("hello_starknet_compiled.casm", 0x395097ed3bda54f78824d00e6e5898d5e16a0e57fa021e54060683cb5706ce7),
        ("minimal_contract_compiled.casm", 0x73F17E5E8C771A97CB07BF6024753D514ED9A1B5DE4EC151E06D0926B015694),
        ("test_contract_compiled.casm", 0x58200D59D5C4B43145D9CCF9232D6BE12483923ED788DB7C3C06BDE5CDAE6EF),
        ("token_bridge_compiled.casm", 0x71AD7A62064E7BA2681CAC07DF817701B24A92C3E752739769EAC1812F105),
    ],
)
def test_compute_casm_class_hash(casm_contract_class_source, expected_casm_class_hash):
    casm_contract_class_str = read_contract(
        casm_contract_class_source, directory=CONTRACTS_COMPILED_V1_DIR
    )

    casm_class = create_casm_class(casm_contract_class_str)
    casm_class_hash = compute_casm_class_hash(casm_class)

    assert casm_class_hash == expected_casm_class_hash
