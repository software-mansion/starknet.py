import pytest

from starknet_py.common import create_sierra_compiled_contract
from starknet_py.hash.sierra_class_hash import compute_sierra_class_hash
from starknet_py.tests.e2e.fixtures.misc import ContractVersion, load_contract


@pytest.mark.parametrize(
    "contract_name, expected_class_hash",
    # fmt: off
    [
        ("Account", 0x55e75d605058b805446f530b8fbfb06dea6cbffc9bb0f480ea3da5fc1c7dc6e),
        ("ERC20", 0x5171d1adbaef84e5b0aa50112700b6fa9b4e67f2178ded86fa111b098d3d939),
        ("HelloStarknet", 0x54f5df27a89fa5a6ff30e4cef95a0f59339c64d510182c1605b065daa42bb24),
        ("MinimalContract", 0x7e66d69bdfee64e13c9b1e3bc6f5377aae2c081b722518ccdd8ea0e5eb4e4ee),
        ("TestContract", 0x471280dc8638e5a66bea76cb7765a9a797d444600c0a74e4d3e65f0a6f111c7),
        ("TokenBridge", 0x5604704d135c1859fe0613ae71f006d2d9ff5dd68fab03995d0a04f37e6f5eb),
    ],
    # fmt: on
)
def test_compute_sierra_class_hash(contract_name, expected_class_hash):
    sierra_contract_class_str = load_contract(
        contract_name=contract_name, version=ContractVersion.V2
    )["sierra"]

    sierra_contract_class = create_sierra_compiled_contract(sierra_contract_class_str)
    class_hash = compute_sierra_class_hash(sierra_contract_class)

    assert class_hash == expected_class_hash
