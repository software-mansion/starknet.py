from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

from starknet_py.cairo.felt import CairoData
from starknet_py.cairo.serialization.data_serializers.payload_serializer import (
    PayloadSerializer,
)
from starknet_py.cairo.serialization.errors import InvalidTypeException
from starknet_py.utils.tuple_dataclass import TupleDataclass


@dataclass
class FunctionSerializationAdapter:
    """
    Class serializing *args and **kwargs  by adapting them to function inputs.
    """

    inputs_serializer: PayloadSerializer
    outputs_deserializer: PayloadSerializer

    expected_args: Tuple[str] = field(init=False)

    def __post_init__(self):
        self.expected_args = tuple(self.inputs_serializer.serializers.keys())

    def serialize(self, *args, **kwargs) -> CairoData:
        """
        Method using args and kwargs to match members and serialize them separately.

        :return: Members serialized separately in SerializedPayload.
        """
        named_arguments = dict(kwargs)

        if len(args) > len(self.expected_args):
            raise InvalidTypeException(
                f"Provided {len(args)} positional arguments, {len(self.expected_args)} possible."
            )

        # Assign args to named arguments
        for arg, input_name in zip(args, self.expected_args):
            if input_name in named_arguments:
                raise InvalidTypeException(
                    f"Both positional and named argument provided for '{input_name}'."
                )
            named_arguments[input_name] = arg

        expected_args = set(self.expected_args)
        provided_args = set(named_arguments.keys())

        excessive_arguments = provided_args - expected_args
        if excessive_arguments:
            raise InvalidTypeException(
                f"Unnecessary named arguments provided: '{', '.join(excessive_arguments)}'."
            )

        # Missing arguments
        missing_arguments = expected_args - provided_args
        if missing_arguments:
            raise InvalidTypeException(
                f"Missing arguments: '{', '.join(missing_arguments)}'."
            )

        return self.inputs_serializer.serialize(named_arguments)

    def deserialize(self, data: List[int]) -> TupleDataclass:
        """
        Deserializes data into TupleDataclass containing python representations.

        :return: cairo data.
        """
        return self.outputs_deserializer.deserialize(data)
