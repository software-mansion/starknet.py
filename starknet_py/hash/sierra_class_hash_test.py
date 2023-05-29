import pytest

from starknet_py.common import create_sierra_compiled_contract
from starknet_py.hash.sierra_class_hash import compute_sierra_class_hash
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_COMPILED_V1_DIR
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.parametrize(
    "sierra_contract_class_source, expected_class_hash",
    # fmt: off
    [
        ("account_compiled.json", 0x2667df3ad273b0854eaa617ed48a7de7842520c46594d6f6739d67e81bf924f),
        ("erc20_compiled.json", 0x56733688e86f849a47311df4eeed8a8b4470cf932d73c27346091d5117c1369),
        ("hello_starknet_compiled.json", 0x3431184635c20edcdf0a60063e02ce285a809943ab194eaa7c0c2e4f7732f1c),
        ("minimal_contract_compiled.json", 0x25c69990757baf3bef190cd427b81c157e11b886ec2471a8fc22ad7a01ce50c),
        ("test_contract_compiled.json", 0x7a6b84c9d65c83bb26129c7e60216f31d947e9e980ee7ed59b806f95c2abbd2),
        ("token_bridge_compiled.json", 0x55b214df5c3529173c8f23e0813ea2cb54835d4b3a8a193db27b78e26469634),
    ],
    # fmt: on
)
def test_compute_sierra_class_hash(sierra_contract_class_source, expected_class_hash):
    sierra_contract_class_str = read_contract(
        sierra_contract_class_source, directory=CONTRACTS_COMPILED_V1_DIR
    )
    sierra_contract_class = create_sierra_compiled_contract(sierra_contract_class_str)
    class_hash = compute_sierra_class_hash(sierra_contract_class)

    assert class_hash == expected_class_hash
