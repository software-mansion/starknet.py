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
from starknet_py.tests.e2e.fixtures.misc import load_contract, read_contract


@pytest.mark.parametrize(
    "contract, expected_casm_class_hash_poseidon",
    [
        ("Account", 0x5dbbf9ef0cec2412b55b47f9e0f327705d134a4005a7f5047e21a87c73cefc1),
        ("ERC20", 0x63d770d6182d0e98a99dc16811313acea7599abb4cbe080bc7ec6afbc993ba2),
        ("HelloStarknet", 0x1309591e96340c14b6730aa531ca37fc870d1ad5abdbc27e114a5ec05c53fe4),
        ("TestContract", 0x45fb3526adabe6b3f4c2e11fcc818496cd68065f6ca02e9cd0549f2095bd72d),
        ("TokenBridge", 0x6d7fef17688c5a6758164e13abf21bb3b25778e19b2b8de9bae9929e57391ac),
    ],
)
def test_compute_casm_class_hash_with_poseidon(contract, expected_casm_class_hash_poseidon):
    casm_contract_class_str = load_contract(
        contract,
        package="contracts_v2",
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
        ("Account", 0x4bea807d465f6eff9e66ba735cdba0bff688c1198f9679652e8cfd6e09a7895),
        ("ERC20", 0x5970d51ec18663ca5359a4de3c73b975ca2af80cb3674a72653f1d5bfda58f2),
        ("HelloStarknet", 0x33ed25fb8b61014debccfc269d9e47b87035c16b5d361df3e71650ed17dfd30),
        ("TestContract", 0x6169b4bc8cbf4bed3f6b94c0de6ccfc48e78eb240cbdbd2a88a42bdb800818),
        ("TokenBridge", 0x24925be8856a1528cca4b8a53ccd51ec92ab0318b512949abeca7bcb746a55e),
    ],
)

def test_compute_casm_class_hash_with_blake2s(contract, expected_casm_class_hash_blake2s):
    casm_contract_class_str = load_contract(contract, package="contracts_v2")['casm']

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
