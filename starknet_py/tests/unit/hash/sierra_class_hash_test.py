import pytest

from starknet_py.common import create_sierra_compiled_contract
from starknet_py.hash.sierra_class_hash import compute_sierra_class_hash
from starknet_py.tests.e2e.fixtures.misc import load_contract


@pytest.mark.parametrize(
    "contract_name, expected_class_hash",
    # fmt: off
    [
        ("Account", 0x69ff59110d9e200023af324c1a7ad13a70fdfc6f2656b10e1a734b4b4c42e99),
        ("ERC20", 0x6336c9e7111249a053c440269ea00200b6f35abb5fdb6d3d2ebf2a5259123c2),
        ("HelloStarknet", 0x320e2f48a32633cf00ce939762d7b99339bb05b5c33fe6a2fa22803e1ccad6),
        ("MinimalContract", 0x693b548e52c4a84765c161ba7675c204b562a298e274dc9a7daf01a9ea101d4),
        ("TestContract", 0x296b0e338ebfd8066d26e2c7e43585c45c2b4c92cf0f33e634f767964a9504),
        ("TokenBridge", 0x2691be4815fff40860df24e1c97c44dc4c37c260ea48446ecd2e5bf49344a9f),
    ],
    # fmt: on
)
def test_compute_sierra_class_hash(contract_name, expected_class_hash):
    sierra_contract_class_str = load_contract(contract_name=contract_name)["sierra"]

    sierra_contract_class = create_sierra_compiled_contract(sierra_contract_class_str)
    class_hash = compute_sierra_class_hash(sierra_contract_class)

    assert class_hash == expected_class_hash
