import json

import pytest
from marshmallow import EXCLUDE

from starknet_py.abi.v2.schemas import ContractAbiEntrySchema
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_COMPILED_V2_DIR
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.parametrize(
    "contract_name",
    [
        "abi_types",
        "account",
        "erc20",
        "hello2",
        "hello_starknet",
        "minimal_contract",
        "new_syntax_test_contract",
        "test_contract",
        "test_enum",
        "test_option",
        "token_bridge",
    ],
)
def test_deserialize_abi(contract_name):
    abi = json.loads(
        read_contract(
            f"{contract_name}_compiled.json", directory=CONTRACTS_COMPILED_V2_DIR
        )
    )["abi"]
    deserialized = [
        ContractAbiEntrySchema().load(entry, unknown=EXCLUDE) for entry in abi
    ]

    assert len(deserialized) == len(abi)
