from collections import OrderedDict

import pytest

from starknet_py.abi.v0 import Abi
from starknet_py.cairo.data_types import FeltType, NamedTupleType, StructType, TupleType
from starknet_py.serialization.data_serializers.array_serializer import ArraySerializer
from starknet_py.serialization.data_serializers.felt_serializer import FeltSerializer
from starknet_py.serialization.data_serializers.named_tuple_serializer import (
    NamedTupleSerializer,
)
from starknet_py.serialization.data_serializers.payload_serializer import (
    PayloadSerializer,
)
from starknet_py.serialization.data_serializers.struct_serializer import (
    StructSerializer,
)
from starknet_py.serialization.data_serializers.tuple_serializer import TupleSerializer
from starknet_py.serialization.data_serializers.uint256_serializer import (
    Uint256Serializer,
)
from starknet_py.serialization.data_serializers.uint_serializer import UintSerializer
from starknet_py.serialization.errors import InvalidTypeException
from starknet_py.serialization.factory import (
    serializer_for_event,
    serializer_for_function,
    serializer_for_type,
)
from starknet_py.serialization.function_serialization_adapter import (
    FunctionSerializationAdapterV0,
)
from starknet_py.tests.e2e.fixtures.abi_structures import (
    get_user_fn,
    pool_id_added_event,
    pool_id_struct,
    uint256_struct,
    user_struct,
)
from starknet_py.tests.e2e.fixtures.abi_v1_structures import abi_v1
from starknet_py.tests.e2e.fixtures.abi_v2_structures import abi_v2

abi = Abi(
    defined_structures={
        "Uint256": uint256_struct,
        "PoolId": pool_id_struct,
        "User": user_struct,
    },
    events={
        "PoolIdAdded": pool_id_added_event,
    },
    functions={
        "get_user_fn": get_user_fn,
    },
    constructor=None,
    l1_handler=None,
)

pool_id_serializer = StructSerializer(OrderedDict(value=Uint256Serializer()))
pool_id_serializer_v2 = StructSerializer(OrderedDict(value=UintSerializer(bits=256)))

user_serializer = StructSerializer(
    OrderedDict(
        id=Uint256Serializer(),
        name_len=FeltSerializer(),
        name=ArraySerializer(FeltSerializer()),
        pool_id=pool_id_serializer,
    )
)

event_serializer = PayloadSerializer(OrderedDict(pool_id=pool_id_serializer_v2))


@pytest.mark.parametrize(
    "structure, serializer",
    (
        (abi.defined_structures["Uint256"], Uint256Serializer()),
        (abi.defined_structures["PoolId"], pool_id_serializer),
        (abi.defined_structures["User"], user_serializer),
        (abi_v2.events["PoolIdAdded"], event_serializer),
        (
            StructType(
                "structure",
                OrderedDict(
                    regular=TupleType([FeltType()]),
                    named=NamedTupleType(OrderedDict(value=FeltType())),
                ),
            ),
            StructSerializer(
                OrderedDict(
                    regular=TupleSerializer([FeltSerializer()]),
                    named=NamedTupleSerializer(OrderedDict(value=FeltSerializer())),
                )
            ),
        ),
    ),
)
def test_getting_type_serializer(structure, serializer):
    assert serializer_for_type(structure) == serializer


def test_getting_payload_serializer_v0():
    assert serializer_for_event(abi.events["PoolIdAdded"]) == PayloadSerializer(
        OrderedDict(pool_id=pool_id_serializer)
    )


def test_getting_payload_serializer_v1():
    assert serializer_for_event(abi_v1.events["PoolIdAdded"]) == PayloadSerializer(
        OrderedDict(pool_id=pool_id_serializer_v2)
    )


def test_getting_payload_serializer_v2():
    assert serializer_for_event(abi_v2.events["PoolIdAdded"]) == PayloadSerializer(
        OrderedDict(pool_id=pool_id_serializer_v2)
    )


def test_getting_function_serializer():
    assert serializer_for_function(
        abi.functions["get_user_fn"]
    ) == FunctionSerializationAdapterV0(
        inputs_serializer=PayloadSerializer(OrderedDict(id=Uint256Serializer())),
        outputs_deserializer=PayloadSerializer(OrderedDict(user=user_serializer)),
    )


def test_invalid_type():
    with pytest.raises(
        InvalidTypeException, match="Received unknown Cairo type 'test'."
    ):
        serializer_for_type("test")  # type: ignore
