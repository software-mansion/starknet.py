import json

from marshmallow import EXCLUDE

from starknet_py.abi.v0.schemas import ContractAbiEntrySchema
from starknet_py.tests.e2e.fixtures.constants import CAIRO_0_CONTRACTS_ABI_DIR
from starknet_py.tests.e2e.fixtures.misc import read_contract


def test_deserialize_abi():
    abi = json.loads(
        read_contract("complex_contract_abi.json", directory=CAIRO_0_CONTRACTS_ABI_DIR)
    )

    deserialized = [
        ContractAbiEntrySchema().load(entry, unknown=EXCLUDE) for entry in abi
    ]

    assert len(deserialized) == len(abi)
