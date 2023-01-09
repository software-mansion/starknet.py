from typing import List, Optional, Union

from starknet_py.cairo.serialization.factory import serializer_for_function
from starknet_py.net.models.abi.parser import AbiParser


def translate_constructor_args(
    abi: List, constructor_args: Optional[Union[List, dict]]
) -> List[int]:
    parsed = AbiParser(abi).parse()

    # Constructor might not accept any arguments
    if not parsed.constructor or not parsed.constructor.inputs:
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
    return serializer_for_function(parsed.constructor).serialize(*args, **kwargs)
