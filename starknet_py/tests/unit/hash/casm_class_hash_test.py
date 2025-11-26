# fmt: off
import pytest
from semver import Version

from starknet_py.common import create_casm_class
from starknet_py.hash.casm_class_hash import (
    compute_casm_class_hash,
    get_casm_hash_method_for_starknet_version,
)
from starknet_py.hash.hash_method import HashMethod
from starknet_py.tests.e2e.fixtures.constants import PRECOMPILED_CONTRACTS_DIR
from starknet_py.tests.e2e.fixtures.misc import (
    ContractVersion,
    load_contract,
    read_contract,
)


@pytest.mark.parametrize(
    "contract, expected_casm_class_hash_poseidon",
    [
        ("Account", 0x778bce178afd1b39abd9729b80931e8c71661103b16de928c3187057254f601),
        ("ERC20", 0x3748ca8b6c53d65b5862e6f17850033baa117075e887708474aba110cc0e77a),
        ("HelloStarknet", 0x467aa3aa331f2d1f9ca24168ad6e9836685af53c35c53a4a828f3564efe79cd),
        ("TestContract", 0x5ab6a30579a54901b6e8be599d7cbdf00a1e05445e95e1d429ca0d70b408af7),
        ("TokenBridge", 0xf364f0d735b07f5a9a50a886e1f5bf6f0d82175d1955dc737f998d33990f8e),
    ],
)
def test_compute_casm_class_hash_with_poseidon(contract, expected_casm_class_hash_poseidon):
    casm_contract_class_str = load_contract(
        contract, version=ContractVersion.V2
    )['casm']

    casm_class = create_casm_class(casm_contract_class_str)
    casm_class_hash = compute_casm_class_hash(casm_class, HashMethod.POSEIDON)
    assert casm_class_hash == expected_casm_class_hash_poseidon

@pytest.mark.parametrize(
    "casm_contract_class_source, expected_casm_class_hash_poseidon",
    [
        ("minimal_contract_compiled_v2_1.casm",
         0x186f6c4ca3af40dbcbf3f08f828ab0ee072938aaaedccc74ef3b9840cbd9fb3),
        ("minimal_contract_compiled_v2_5_4.casm",
         0x1d055a90aa90db474fa08a931d5e63753c6f762fa3e9597b26c8d4b003a2de6),
        ("starknet_contract_v2_6.casm", 0x603dd72504d8b0bc54df4f1102fdcf87fc3b2b94750a9083a5876913eec08e4),
    ],
)
def test_precompiled_compute_casm_class_hash_with_poseidon(casm_contract_class_source, expected_casm_class_hash_poseidon): # pylint: disable=line-too-long
    casm_contract_class_str = read_contract(
        casm_contract_class_source, directory=PRECOMPILED_CONTRACTS_DIR
    )

    casm_class = create_casm_class(casm_contract_class_str)
    casm_class_hash = compute_casm_class_hash(casm_class, HashMethod.POSEIDON)
    assert casm_class_hash == expected_casm_class_hash_poseidon


@pytest.mark.parametrize(
    "starknet_version, expected_hash_method",
    [
        ("0.13.5", HashMethod.POSEIDON),
        ("0.14.0", HashMethod.POSEIDON),
        ("0.14.1", HashMethod.BLAKE2S),
        ("0.15.0", HashMethod.BLAKE2S),
        ("1.0.0", HashMethod.BLAKE2S),
        ("1.10.0", HashMethod.BLAKE2S),
    ],
)
def test_get_casm_hash_method_for_starknet_version(starknet_version, expected_hash_method):
    """Test that the correct hash method is returned for different Starknet versions."""
    starknet_version = Version.parse(starknet_version)
    hash_method = get_casm_hash_method_for_starknet_version(starknet_version)
    assert hash_method == expected_hash_method


@pytest.mark.parametrize(
    "contract, expected_casm_class_hash_blake2s",
    [
        ("Account", 0x714c833f7b359955f6a4a495ba995cca2114158db2178aff587f643daa19c80),
        ("ERC20", 0x44312efaec9c719168eee3586314b01ed7a1fd7e31d3cf0c5a17e0a5b4fbe7d),
        ("HelloStarknet", 0x5aaedd0566b5dd234f5f8d3d6b8cfd299cf0a99541aa9ca34db9259d546e82f),
        ("TestContract", 0x3135acde04efbc96d422c01822a517ae5b4e61f132d26bf8542e3b9d0d1500f),
        ("TokenBridge", 0x6409448fd244060b15748b02b6e0bdb185d5271be231492ca33a7147e43994c),
    ],
)

def test_compute_casm_class_hash_with_blake2s(contract, expected_casm_class_hash_blake2s):
    casm_contract_class_str = load_contract(
        contract, version=ContractVersion.V2
    )['casm']

    casm_class = create_casm_class(casm_contract_class_str)
    casm_class_hash = compute_casm_class_hash(casm_class, hash_method=HashMethod.BLAKE2S)
    assert casm_class_hash == expected_casm_class_hash_blake2s

@pytest.mark.parametrize(
    "casm_contract_class_source, expected_casm_class_hash_blake2s",
    [
        ("minimal_contract_compiled_v2_1.casm",
         0x195cfeec43b384e0f0ec83937149a1a4d88571772b2806ed7e4f41a1ecb4c74),
        ("minimal_contract_compiled_v2_5_4.casm",
         0x5ac03c50c46fc7b374d4e11d15693ae0d21e13f61c1704700294d1f378980f7),
        ("starknet_contract_v2_6.casm", 0xf8c27dd667e50ba127e5e0e469381606ffece27d8c5148548b6bbc4cacf717),
    ],
)
def test_precompiled_compute_casm_class_hash_with_blake2s(casm_contract_class_source, expected_casm_class_hash_blake2s):
    casm_contract_class_str = read_contract(
        casm_contract_class_source, directory=PRECOMPILED_CONTRACTS_DIR
    )

    casm_class = create_casm_class(casm_contract_class_str)
    casm_class_hash = compute_casm_class_hash(casm_class, hash_method=HashMethod.BLAKE2S)
    assert casm_class_hash == expected_casm_class_hash_blake2s
