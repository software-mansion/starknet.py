from collections import OrderedDict

import pytest

from starknet_py.cairo.serialization.data_serializers.felt_serializer import (
    FeltSerializer,
)
from starknet_py.cairo.serialization.data_serializers.payload_serializer import (
    PayloadSerializer,
)
from starknet_py.cairo.serialization.errors import (
    InvalidTypeException,
    InvalidValueException,
)
from starknet_py.cairo.serialization.function_serialization_adapter import (
    FunctionSerializationAdapter,
)
from starknet_py.utils.tuple_dataclass import TupleDataclass

payload_serializer = PayloadSerializer(
    OrderedDict(
        x=FeltSerializer(),
        y=FeltSerializer(),
        z=FeltSerializer(),
    )
)
serializer = FunctionSerializationAdapter(
    payload_serializer,
    payload_serializer,
)


def test_serialize():
    # pylint: disable=invalid-name
    serialized = [1, 2, 3]
    x, y, z = serialized

    assert serializer.serialize(x, y, z) == serialized
    assert serializer.serialize(x=x, y=y, z=z) == serialized
    assert serializer.serialize(x, y=y, z=z) == serialized

    with pytest.raises(
        InvalidTypeException, match="Provided 4 positional arguments, 3 possible."
    ):
        serializer.serialize(1, 2, 3, 4)

    with pytest.raises(
        InvalidTypeException,
        match="Both positional and named argument provided for 'x'.",
    ):
        serializer.serialize(1, 2, x=1, y=3)

    with pytest.raises(
        InvalidTypeException,
        match="Unnecessary named arguments provided: 'unknown_key'.",
    ):
        serializer.serialize(1, 2, unknown_key=3)

    with pytest.raises(InvalidTypeException, match="Missing arguments: 'z'."):
        serializer.serialize(1, 2)


def test_deserialize():
    assert serializer.deserialize([1, 2, 3]) == TupleDataclass.from_dict(
        {"x": 1, "y": 2, "z": 3}
    )

    with pytest.raises(
        InvalidValueException,
        match="Error: 2 values out of total 5 values were not used during deserialization.",
    ):
        serializer.deserialize([1, 2, 3, 4, 5])

    with pytest.raises(
        InvalidValueException,
        match="Error at path 'z': not enough data to deserialize. Can't read 1 values at position 2, 0 available.",
    ):
        serializer.deserialize([1, 2])
