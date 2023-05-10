from collections import OrderedDict

import pytest
from indexed import IndexedOrderedDict

from starknet_py.serialization.data_serializers.enum_serializer import EnumSerializer
from starknet_py.serialization.data_serializers.option_serializer import (
    OptionSerializer,
)
from starknet_py.serialization.data_serializers.struct_serializer import (
    StructSerializer,
)
from starknet_py.serialization.data_serializers.uint_serializer import UintSerializer

serializer = EnumSerializer(
    serializers=IndexedOrderedDict(
        a=UintSerializer(256),
        b=UintSerializer(128),
        c=StructSerializer(
            OrderedDict(
                my_option=OptionSerializer(UintSerializer(128)),
                my_uint=UintSerializer(256),
            )
        ),
    )
)


@pytest.mark.parametrize(
    "value, serialized_value",
    [
        ({"a": 100}, [0, 100, 0]),
        ({"b": 200}, [1, 200]),
        ({"c": {"my_option": 300, "my_uint": 300}}, [2, 0, 300, 300, 0]),
    ],
)
def test_output_serializer_deserialize(value, serialized_value):
    deserialized = serializer.deserialize(serialized_value)
    variant_name, variant_value = list(value.items())[0]

    assert deserialized.variant == variant_name
    assert deserialized.value == variant_value


def test_output_serializer_serialize():
    with pytest.raises(ValueError, match="Can't serialize more than one variant."):
        serializer.serialize({"a": 100, "b": 200})
