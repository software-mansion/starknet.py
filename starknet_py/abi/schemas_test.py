import json

from marshmallow import EXCLUDE

from starknet_py.abi.schemas import ContractAbiEntrySchema
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_COMPILED_V0_DIR
from starknet_py.tests.e2e.fixtures.misc import read_contract


def test_deserialize_abi():
    abi = json.loads(
        read_contract(
            "balance_struct_event_abi.json", directory=CONTRACTS_COMPILED_V0_DIR
        )
    )
    deserialized = [
        ContractAbiEntrySchema().load(entry, unknown=EXCLUDE) for entry in abi
    ]

    assert len(deserialized) == len(abi)
