from typing import List, Union, Optional

from starkware.starknet.public.abi_structs import identifier_manager_from_abi

from starknet_py.utils.data_transformer import FunctionCallSerializer


def translate_constructor_args(
    abi: List, constructor_args: Optional[Union[List, dict]]
) -> List[int]:
    constructor_abi = next(
        (member for member in abi if member["type"] == "constructor"),
        None,
    )

    # Constructor might not accept any arguments
    if not constructor_abi or not constructor_abi["inputs"]:
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
    calldata, _args = FunctionCallSerializer(
        constructor_abi, identifier_manager_from_abi(abi)
    ).from_python(*args, **kwargs)
    return calldata
