# fmt: off
import pytest

from starknet_py.common import create_casm_class
from starknet_py.hash.casm_class_hash import compute_casm_class_hash
from starknet_py.tests.e2e.fixtures.constants import PRECOMPILED_CONTRACTS_DIR
from starknet_py.tests.e2e.fixtures.misc import (
    ContractVersion,
    load_contract,
    read_contract,
)


@pytest.mark.parametrize(
    "contract, expected_casm_class_hash",
    [
        ("Account", 0x778bce178afd1b39abd9729b80931e8c71661103b16de928c3187057254f601),
        ("ERC20", 0x3748ca8b6c53d65b5862e6f17850033baa117075e887708474aba110cc0e77a),
        ("HelloStarknet", 0x467aa3aa331f2d1f9ca24168ad6e9836685af53c35c53a4a828f3564efe79cd),
        ("TestContract", 0x5ab6a30579a54901b6e8be599d7cbdf00a1e05445e95e1d429ca0d70b408af7),
        ("TokenBridge", 0xf364f0d735b07f5a9a50a886e1f5bf6f0d82175d1955dc737f998d33990f8e),
    ],
)
def test_compute_casm_class_hash(contract, expected_casm_class_hash):
    casm_contract_class_str = load_contract(
        contract, version=ContractVersion.V2
    )['casm']

    casm_class = create_casm_class(casm_contract_class_str)
    casm_class_hash = compute_casm_class_hash(casm_class)
    assert casm_class_hash == expected_casm_class_hash

@pytest.mark.parametrize(
    "casm_contract_class_source, expected_casm_class_hash",
    [
        ("minimal_contract_compiled_v2_1.casm",
         0x186f6c4ca3af40dbcbf3f08f828ab0ee072938aaaedccc74ef3b9840cbd9fb3),
        ("minimal_contract_compiled_v2_5_4.casm",
         0x1d055a90aa90db474fa08a931d5e63753c6f762fa3e9597b26c8d4b003a2de6),
        ("starknet_contract_v2_6.casm", 0x603dd72504d8b0bc54df4f1102fdcf87fc3b2b94750a9083a5876913eec08e4),
    ],
)
def test_precompiled_compute_casm_class_hash(casm_contract_class_source, expected_casm_class_hash):
    casm_contract_class_str = read_contract(
        casm_contract_class_source, directory=PRECOMPILED_CONTRACTS_DIR
    )

    casm_class = create_casm_class(casm_contract_class_str)
    casm_class_hash = compute_casm_class_hash(casm_class)
    assert casm_class_hash == expected_casm_class_hash
