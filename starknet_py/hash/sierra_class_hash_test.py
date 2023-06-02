import pytest

from starknet_py.common import create_sierra_compiled_contract
from starknet_py.hash.sierra_class_hash import compute_sierra_class_hash
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_COMPILED_V1_DIR
from starknet_py.tests.e2e.fixtures.misc import read_contract

# if get_python_version()[:2] == (3, 9):
#     from starkware.starknet.core.os.contract_class.class_hash import (
#         compute_class_hash as sw_compute_class_hash,
#     )
#     from starkware.starknet.services.api.contract_class.contract_class import (
#         ContractClass as SwContractClass,
#     )


@pytest.mark.parametrize(
    "sierra_contract_class_source, expected_class_hash",
    # fmt: off
    [
        ("account_compiled.json", 0x1ADADAE7CE7ED3F5C39F275EF4758562E540F27AB0184B24E2B13861988751E),
        ("erc20_compiled.json", 0x6D8EDE036BB4720E6F348643221D8672BF4F0895622C32C11E57460B3B7DFFC),
        ("hello_starknet_compiled.json", 0x8448A68B5EA1AFFC45E3FD4B8B480EA36A51DC34E337A16D2567D32D0C6F8A),
        ("minimal_contract_compiled.json", 0x6C3953793645458C796905E660F81AD91EFC92AE22E13A2E63278A32750C3F9),
        ("test_contract_compiled.json", 0x44B969C50B167D2609EFCAEE50E309F0AD3D5899411F8DC9BBAB3FF7FDB9DF6),
        ("token_bridge_compiled.json", 0x21540B9775D44C9980D80C5E6D85422583C2985DF9AAC1F348FB7EE666AFCC3),
    ],
    # fmt: on
)
def test_compute_sierra_class_hash(sierra_contract_class_source, expected_class_hash):
    sierra_contract_class_str = read_contract(
        sierra_contract_class_source, directory=CONTRACTS_COMPILED_V1_DIR
    )

    sierra_contract_class = create_sierra_compiled_contract(sierra_contract_class_str)
    class_hash = compute_sierra_class_hash(sierra_contract_class)

    # if get_python_version()[:2] == (3, 9):
    #     sierra_contract_class_dict = json.loads(sierra_contract_class_str)
    #     sierra_contract_class_dict["abi"] = json.dumps(
    #         sierra_contract_class_dict["abi"]
    #     )
    #     del sierra_contract_class_dict["sierra_program_debug_info"]
    #
    #     sw_contract_class = SwContractClass.load(sierra_contract_class_dict)
    #     expected_class_hash = sw_compute_class_hash(sw_contract_class)

    assert class_hash == expected_class_hash
