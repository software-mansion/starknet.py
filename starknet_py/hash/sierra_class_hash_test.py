import json

import pytest

from starknet_py.common import create_sierra_compiled_contract
from starknet_py.hash.sierra_class_hash import compute_sierra_class_hash
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_COMPILED_V1_DIR
from starknet_py.tests.e2e.fixtures.misc import get_python_version, read_contract

if get_python_version()[:2] == (3, 9):
    from starkware.starknet.core.os.contract_class.class_hash import (
        compute_class_hash as sw_compute_class_hash,
    )
    from starkware.starknet.services.api.contract_class.contract_class import (
        ContractClass as SwContractClass,
    )


@pytest.mark.parametrize(
    "sierra_contract_class_source, expected_class_hash",
    # fmt: off
    [
        ("account_compiled.json", 0x2667DF3AD273B0854EAA617ED48A7DE7842520C46594D6F6739D67E81BF924F),
        ("erc20_compiled.json", 0x56733688E86F849A47311DF4EEED8A8B4470CF932D73C27346091D5117C1369),
        ("hello_starknet_compiled.json", 0x3431184635C20EDCDF0A60063E02CE285A809943AB194EAA7C0C2E4F7732F1C),
        ("minimal_contract_compiled.json", 0x25C69990757BAF3BEF190CD427B81C157E11B886EC2471A8FC22AD7A01CE50C),
        ("test_contract_compiled.json", 0x7A6B84C9D65C83BB26129C7E60216F31D947E9E980EE7ED59B806F95C2ABBD2),
        ("token_bridge_compiled.json", 0x55B214DF5C3529173C8F23E0813EA2CB54835D4B3A8A193DB27B78E26469634),
    ],
    # fmt: on
)
def test_compute_sierra_class_hash(sierra_contract_class_source, expected_class_hash):
    sierra_contract_class_str = read_contract(
        sierra_contract_class_source, directory=CONTRACTS_COMPILED_V1_DIR
    )

    sierra_contract_class = create_sierra_compiled_contract(sierra_contract_class_str)
    class_hash = compute_sierra_class_hash(sierra_contract_class)

    if get_python_version()[:2] == (3, 9):
        sierra_contract_class_dict = json.loads(sierra_contract_class_str)
        sierra_contract_class_dict["abi"] = json.dumps(
            sierra_contract_class_dict["abi"]
        )
        del sierra_contract_class_dict["sierra_program_debug_info"]

        sw_contract_class = SwContractClass.load(sierra_contract_class_dict)
        expected_class_hash = sw_compute_class_hash(sw_contract_class)

    assert class_hash == expected_class_hash
