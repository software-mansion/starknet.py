from typing import List, Optional, Union

import starknet_py.abi.v2.shape as ShapeV2
from starknet_py.abi.parser import AbiParser
from starknet_py.abi.v1.parser import AbiParser as AbiV1Parser
from starknet_py.abi.v2.parser import AbiParser as AbiV2Parser
from starknet_py.serialization import (
    FunctionSerializationAdapter,
    serializer_for_function,
)
from starknet_py.serialization.factory import (
    serializer_for_constructor_v2,
    serializer_for_function_v1,
)


def translate_constructor_args(
    abi: List, constructor_args: Optional[Union[List, dict]], *, cairo_version: int = 0
) -> List[int]:
    serializer = (
        _get_constructor_serializer_v1(abi)
        if cairo_version == 1
        else _get_constructor_serializer_v0(abi)
    )

    if serializer is None or len(serializer.inputs_serializer.serializers) == 0:
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
    if _is_abi_v2(abi):
        parsed = AbiV2Parser(abi).parse()
        constructor = parsed.constructor

        if constructor is None or not constructor.inputs:
            return None

        return serializer_for_constructor_v2(constructor)

    parsed = AbiV1Parser(abi).parse()
    constructor = parsed.functions.get("constructor", None)

    # Constructor might not accept any arguments
    if constructor is None or not constructor.inputs:
        return None

    return serializer_for_function_v1(constructor)


def _is_abi_v2(abi: List) -> bool:
    for entry in abi:
        if entry["type"] in [
            ShapeV2.CONSTRUCTOR_ENTRY,
            ShapeV2.L1_HANDLER_ENTRY,
            ShapeV2.INTERFACE_ENTRY,
            ShapeV2.IMPL_ENTRY,
        ]:
            return True
        if entry["type"] == ShapeV2.EVENT_ENTRY:
            if "inputs" in entry:
                return False
            if "kind" in entry:
                return True
    return False


def _get_constructor_serializer_v0(abi: List) -> Optional[FunctionSerializationAdapter]:
    parsed = AbiParser(abi).parse()

    # Constructor might not accept any arguments
    if not parsed.constructor or not parsed.constructor.inputs:
        return None

    return serializer_for_function(parsed.constructor)
