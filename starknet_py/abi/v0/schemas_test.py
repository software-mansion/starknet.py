import json

import pytest
from marshmallow import EXCLUDE

from starknet_py.abi.v0.schemas import ContractAbiEntrySchema


@pytest.fixture(scope="package")
def cairo_0_balance_struct_event_abi():
    return [
        {
            "members": [
                {"name": "value", "offset": 0, "type": "felt"},
                {"name": "nested_struct", "offset": 1, "type": "NestedStruct"},
            ],
            "name": "TopStruct",
            "size": 2,
            "type": "struct",
        },
        {
            "members": [{"name": "value", "offset": 0, "type": "felt"}],
            "name": "NestedStruct",
            "size": 1,
            "type": "struct",
        },
        {
            "data": [
                {"name": "key", "type": "felt"},
                {"name": "prev_amount", "type": "TopStruct"},
                {"name": "amount", "type": "TopStruct"},
            ],
            "keys": [],
            "name": "increase_balance_called",
            "type": "event",
        },
        {
            "inputs": [
                {"name": "key", "type": "felt"},
                {"name": "amount", "type": "TopStruct"},
            ],
            "name": "increase_balance",
            "outputs": [],
            "type": "function",
        },
        {
            "inputs": [{"name": "key", "type": "felt"}],
            "name": "get_balance",
            "outputs": [{"name": "value", "type": "TopStruct"}],
            "stateMutability": "view",
            "type": "function",
        },
    ]


def test_deserialize_abi(cairo_0_balance_struct_event_abi):

    deserialized = [
        ContractAbiEntrySchema().load(entry, unknown=EXCLUDE)
        for entry in cairo_0_balance_struct_event_abi
    ]

    assert len(deserialized) == len(cairo_0_balance_struct_event_abi)
