from __future__ import annotations

from collections import OrderedDict
from typing import Dict

from starknet_py.abi.model import Abi
from starknet_py.cairo.data_types import (
    ArrayType,
    CairoType,
    FeltType,
    NamedTupleType,
    StructType,
    TupleType,
)
from starknet_py.serialization.data_serializers.array_serializer import ArraySerializer
from starknet_py.serialization.data_serializers.cairo_data_serializer import (
    CairoDataSerializer,
)
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
from starknet_py.serialization.errors import InvalidTypeException
from starknet_py.serialization.function_serialization_adapter import (
    FunctionSerializationAdapter,
)

_uint256_type = StructType("Uint256", OrderedDict(low=FeltType(), high=FeltType()))


def serializer_for_type(cairo_type: CairoType) -> CairoDataSerializer:
    """
    Create a serializer for cairo type.

    :param cairo_type: CairoType.
    :return: CairoDataSerializer.
    """
    if isinstance(cairo_type, FeltType):
        return FeltSerializer()

    if isinstance(cairo_type, StructType):
        # Special case: Uint256 is represented as struct
        if cairo_type == _uint256_type:
            return Uint256Serializer()

        return StructSerializer(
            OrderedDict(
                (name, serializer_for_type(member_type))
                for name, member_type in cairo_type.types.items()
            )
        )

    if isinstance(cairo_type, ArrayType):
        return ArraySerializer(serializer_for_type(cairo_type.inner_type))

    if isinstance(cairo_type, TupleType):
        return TupleSerializer(
            [serializer_for_type(member) for member in cairo_type.types]
        )

    if isinstance(cairo_type, NamedTupleType):
        return NamedTupleSerializer(
            OrderedDict(
                (name, serializer_for_type(member_type))
                for name, member_type in cairo_type.types.items()
            )
        )

    raise InvalidTypeException(f"Received unknown Cairo type '{cairo_type}'.")


# We don't want to require users to use OrderedDict. Regular python requires order since python 3.7.
def serializer_for_payload(payload: Dict[str, CairoType]) -> PayloadSerializer:
    """
    Create PayloadSerializer for types listed in a dictionary. Please note that the order of fields in the dict is
    very important. Make sure the keys are provided in the right order.

    :param payload: dictionary with cairo types.
    :return: PayloadSerializer that can be used to (de)serialize events/function calls.
    """
    return PayloadSerializer(
        OrderedDict(
            (name, serializer_for_type(cairo_type))
            for name, cairo_type in payload.items()
        )
    )


def serializer_for_event(event: Abi.Event) -> PayloadSerializer:
    """
    Create serializer for an event.

    :param event: parsed event.
    :return: PayloadSerializer that can be used to (de)serialize events.
    """
    return serializer_for_payload(event.data)


def serializer_for_function(abi_function: Abi.Function) -> FunctionSerializationAdapter:
    """
    Create FunctionSerializationAdapter for serializing function inputs and deserializing function outputs.

    :param abi_function: parsed function's abi.
    :return: FunctionSerializationAdapter.
    """
    return FunctionSerializationAdapter(
        inputs_serializer=serializer_for_payload(abi_function.inputs),
        outputs_deserializer=serializer_for_payload(abi_function.outputs),
    )
