from typing import List, Optional, Union

from starknet_py.abi.parser import AbiParser
from starknet_py.abi.v1.parser import AbiParser as AbiV1Parser
from starknet_py.serialization import (
    FunctionSerializationAdapter,
    serializer_for_function,
)
from starknet_py.serialization.factory import serializer_for_function_v1


def translate_constructor_args(
    abi: List, constructor_args: Optional[Union[List, dict]], *, cairo_version: int = 0
) -> List[int]:
    serializer = (
        _get_constructor_serializer_v1(abi)
        if cairo_version == 1
        else _get_constructor_serializer_v0(abi)
    )

    if serializer is None:
        return []

    if not constructor_args:
        raise ValueError(
            "Provided contract has a constructor and no arguments were provided."
        )

    args, kwargs = (
        ([], constructor_args)
        if isinstance(constructor_args, dict)
        else (constructor_args, {})
    )
    return serializer.serialize(*args, **kwargs)


def _get_constructor_serializer_v1(abi: List) -> Optional[FunctionSerializationAdapter]:
    parsed = AbiV1Parser(abi).parse()
    constructor = parsed.functions.get("constructor", None)

    # Constructor might not accept any arguments
    if constructor is None or not constructor.inputs:
        return None

    return serializer_for_function_v1(constructor)


def _get_constructor_serializer_v0(abi: List) -> Optional[FunctionSerializationAdapter]:
    parsed = AbiParser(abi).parse()

    # Constructor might not accept any arguments
    if not parsed.constructor or not parsed.constructor.inputs:
        return None

    return serializer_for_function(parsed.constructor)
