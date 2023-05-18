import json

from marshmallow import EXCLUDE

from starknet_py.abi.v1.schemas import ContractAbiEntrySchema
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_COMPILED_V1_DIR
from starknet_py.tests.e2e.fixtures.misc import read_contract


def test_deserialize_abi():
    abi = json.loads(
        read_contract("erc20_compiled.json", directory=CONTRACTS_COMPILED_V1_DIR)
    )["abi"]
    deserialized = [
        ContractAbiEntrySchema().load(entry, unknown=EXCLUDE) for entry in abi
    ]

    assert len(deserialized) == len(abi)
