import json
from collections import OrderedDict

import pytest

from starknet_py.cairo.type_parser import UnknownCairoTypeError
from starknet_py.net.models.abi.definition import AbiDefinition, AbiDecodingError
from starknet_py.cairo.data_types import StructType, FeltType, ArrayType
from starknet_py.tests.e2e.fixtures.misc import read_contract

uint256_dict = {
    "type": "struct",
    "name": "Uint256",
    "size": 2,
    "members": [
        # low and high were switched on purpose
        {"name": "high", "offset": 1, "type": "felt"},
        {"name": "low", "offset": 0, "type": "felt"},
    ],
}
uint256_struct = StructType("Uint256", OrderedDict(low=FeltType(), high=FeltType()))

pool_id_dict = {
    "type": "struct",
    "name": "PoolId",
    "size": 1,
    "members": [
        {"name": "value", "offset": 0, "type": "Uint256"},
    ],
}
pool_id_struct = StructType("PoolId", OrderedDict(value=uint256_struct))

user_dict = {
    "type": "struct",
    "name": "User",
    "size": 4,
    "members": [
        {"name": "id", "offset": 0, "type": "Uint256"},
        {"name": "name_len", "offset": 1, "type": "felt"},
        {"name": "name", "offset": 2, "type": "felt*"},
        {"name": "pool_id", "offset": 3, "type": "PoolId"},
    ],
}
user_struct = StructType(
    "User",
    OrderedDict(
        id=uint256_struct,
        name_len=FeltType(),
        name=ArrayType(FeltType()),
        pool_id=pool_id_struct,
    ),
)

user_added_dict = {
    "type": "event",
    "name": "UserAdded",
    "data": [
        {"name": "user", "type": "User"},
    ],
    "keys": [],
}
user_added_event: AbiDefinition.Event = AbiDefinition.Event(
    "UserAdded",
    OrderedDict(user=user_struct),
)

pool_id_added_dict = {
    "type": "event",
    "name": "PoolIdAdded",
    "data": [
        {"name": "pool_id", "type": "PoolId"},
    ],
    "keys": [],
}
pool_id_added_event: AbiDefinition.Event = AbiDefinition.Event(
    "PoolIdAdded",
    OrderedDict(pool_id=pool_id_struct),
)

get_user_dict = {
    "type": "function",
    "name": "get_user",
    "inputs": [
        {
            "name": "id",
            "type": "Uint256",
        }
    ],
    "outputs": [{"name": "user", "type": "User"}],
}
get_user_fn = AbiDefinition.Function(
    "get_user", OrderedDict(id=uint256_struct), OrderedDict(user=user_struct)
)

delete_pool_dict = {
    "type": "function",
    "name": "delete_pool",
    "inputs": [
        {
            "name": "id",
            "type": "PoolId",
        },
        {"name": "user_id", "type": "Uint256"},
    ],
    "outputs": [],
}
delete_pool_fn = AbiDefinition.Function(
    "delete_pool", OrderedDict(id=pool_id_struct, user_id=uint256_struct), OrderedDict()
)


def test_parsing_types_abi():
    # Even though user depend on pool id and uint256 it is defined first. Parser has to consider those cases
    abi = AbiDefinition.from_list(
        [
            user_dict,
            pool_id_dict,
            uint256_dict,
            user_added_dict,
            pool_id_added_dict,
            get_user_dict,
            delete_pool_dict,
        ]
    )

    assert abi.defined_structures == {
        "Uint256": uint256_struct,
        "PoolId": pool_id_struct,
        "User": user_struct,
    }
    assert abi.events == {
        "UserAdded": user_added_event,
        "PoolIdAdded": pool_id_added_event,
    }
    assert abi.functions == {"get_user": get_user_fn, "delete_pool": delete_pool_fn}


def test_duplicated_structure():
    with pytest.raises(
        AbiDecodingError,
        match="Name 'Uint256' was used more than once in defined structures",
    ):
        AbiDefinition.from_list([uint256_dict, pool_id_dict, uint256_dict])


def test_duplicated_function():
    with pytest.raises(
        AbiDecodingError,
        match="Name 'get_user' was used more than once in defined functions",
    ):
        AbiDefinition.from_list(
            [get_user_dict, delete_pool_dict, get_user_dict, delete_pool_dict]
        )


def test_duplicated_event():
    with pytest.raises(
        AbiDecodingError,
        match="Name 'UserAdded' was used more than once in defined events",
    ):
        AbiDefinition.from_list([user_added_dict, delete_pool_dict, user_added_dict])


def test_duplicated_type_members():
    type_dict = {
        "type": "struct",
        "name": "Record",
        "size": 4,
        "members": [
            {"name": "name", "offset": 0, "type": "felt"},
            {"name": "value", "offset": 1, "type": "felt"},
            {"name": "id", "offset": 2, "type": "felt"},
            {"name": "value", "offset": 3, "type": "felt"},
        ],
    }
    with pytest.raises(
        AbiDecodingError,
        match="Name 'value' was used more than once in members of structure 'Record'",
    ):
        AbiDefinition.from_list([type_dict])


def test_missing_type_used_by_other_type():
    with pytest.raises(UnknownCairoTypeError, match="Type 'Uint256' is not defined"):
        AbiDefinition.from_list([pool_id_dict])


def test_missing_type_used_by_function():
    with pytest.raises(UnknownCairoTypeError, match="Type 'Uint256' is not defined"):
        AbiDefinition.from_list([get_user_dict])


def test_missing_type_used_by_event():
    with pytest.raises(UnknownCairoTypeError, match="Type 'User' is not defined"):
        AbiDefinition.from_list([user_added_dict])


def test_deserialize_proxy_abi():
    # Contains all types of ABI apart from structures
    abi = json.loads(read_contract("oz_proxy_abi.json"))
    deserialized = AbiDefinition.from_list(abi)

    assert deserialized == AbiDefinition(
        defined_structures={},
        functions={
            "__default__": AbiDefinition.Function(
                name="__default__",
                inputs=OrderedDict(
                    [
                        ("selector", FeltType()),
                        ("calldata_size", FeltType()),
                        ("calldata", ArrayType(inner_type=FeltType())),
                    ]
                ),
                outputs=OrderedDict(
                    [
                        ("retdata_size", FeltType()),
                        ("retdata", ArrayType(inner_type=FeltType())),
                    ]
                ),
            )
        },
        constructor=AbiDefinition.Function(
            name="constructor",
            inputs=OrderedDict(
                [
                    ("implementation_hash", FeltType()),
                    ("selector", FeltType()),
                    ("calldata_len", FeltType()),
                    ("calldata", ArrayType(inner_type=FeltType())),
                ]
            ),
            outputs=OrderedDict(),
        ),
        l1_handler=AbiDefinition.Function(
            name="__l1_default__",
            inputs=OrderedDict(
                [
                    ("selector", FeltType()),
                    ("calldata_size", FeltType()),
                    ("calldata", ArrayType(inner_type=FeltType())),
                ]
            ),
            outputs=OrderedDict(),
        ),
        events={
            "Upgraded": AbiDefinition.Event(
                name="Upgraded", data=OrderedDict([("implementation", FeltType())])
            ),
            "AdminChanged": AbiDefinition.Event(
                name="AdminChanged",
                data=OrderedDict(
                    [("previousAdmin", FeltType()), ("newAdmin", FeltType())]
                ),
            ),
        },
    )


def test_deserialize_balance_struct_event_abi():
    # Contains all types of ABI apart from structures
    abi = json.loads(read_contract("balance_struct_event_abi.json"))
    deserialized = AbiDefinition.from_list(abi)

    print(deserialized)
    nested_struct = StructType(
        name="NestedStruct", types=OrderedDict([("value", FeltType())])
    )
    top_struct = StructType(
        name="TopStruct",
        types=OrderedDict(value=FeltType(), nested_struct=nested_struct),
    )
    assert deserialized == AbiDefinition(
        defined_structures={
            "TopStruct": top_struct,
            "NestedStruct": nested_struct,
        },
        functions={
            "increase_balance": AbiDefinition.Function(
                name="increase_balance",
                inputs=OrderedDict(
                    [
                        ("key", FeltType()),
                        (
                            "amount",
                            top_struct,
                        ),
                    ]
                ),
                outputs=OrderedDict(),
            ),
            "get_balance": AbiDefinition.Function(
                name="get_balance",
                inputs=OrderedDict([("key", FeltType())]),
                outputs=OrderedDict(value=top_struct),
            ),
        },
        constructor=None,
        l1_handler=None,
        events={
            "increase_balance_called": AbiDefinition.Event(
                name="increase_balance_called",
                data=OrderedDict(
                    key=FeltType(), prev_amount=top_struct, amount=top_struct
                ),
            )
        },
    )


def test_duplicated_constructor():
    constructor = {
        "inputs": [],
        "name": "constructor",
        "outputs": [],
        "type": "constructor",
    }
    with pytest.raises(
        AbiDecodingError, match="Constructor in ABI must be defined at most once"
    ):
        AbiDefinition.from_list([constructor, constructor])


def test_duplicated_l1_handler():
    l1_handler = {
        "inputs": [],
        "name": "__l1_default__",
        "outputs": [],
        "type": "l1_handler",
    }
    with pytest.raises(
        AbiDecodingError, match="L1 handler in ABI must be defined at most once"
    ):
        AbiDefinition.from_list([l1_handler, l1_handler])
