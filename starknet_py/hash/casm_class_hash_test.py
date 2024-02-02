# fmt: off
import pytest

from starknet_py.common import create_casm_class
from starknet_py.hash.casm_class_hash import compute_casm_class_hash
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_COMPILED_V2_DIR
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.parametrize(
    "casm_contract_class_source, expected_casm_class_hash",
    [
        ("account_compiled.casm", 0x1cf09a2ab1c531bfd02cb26a3fa9ed02986fd3bb86e6b8874072fba4e55f504),
        ("erc20_compiled.casm", 0x6d53db94c64d3562370253db94529b99f6837cb2f3b7062e11c657be89c1dae),
        ("hello_starknet_compiled.casm", 0x785fa5f2bacf0bfe3bc413be5820a61e1ea63f2ec27ef00331ee9f46ad07603),
        ("minimal_contract_compiled.casm", 0x186f6c4ca3af40dbcbf3f08f828ab0ee072938aaaedccc74ef3b9840cbd9fb3),
        ("test_contract_compiled.casm", 0x379b75c0922c68e73f6451b69e8e50b7f0745e6fa3f67ffc0b9608238eeaf45),
        ("token_bridge_compiled.casm", 0x1d60f20e5dd449af4e6b0d63821cfa95f3469faa942caf78eba2172e2ec3468),
    ],
)
def test_compute_casm_class_hash(casm_contract_class_source, expected_casm_class_hash):
    casm_contract_class_str = read_contract(
        casm_contract_class_source, directory=CONTRACTS_COMPILED_V2_DIR
    )

    casm_class = create_casm_class(casm_contract_class_str)
    casm_class_hash = compute_casm_class_hash(casm_class)

    assert casm_class_hash == expected_casm_class_hash
