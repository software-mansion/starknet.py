import warnings
from typing import Union, Optional
from typing_extensions import get_args

from starknet_py.net.client_models import Hash, Tag, Call


def hash_to_felt(value: Hash) -> str:
    """
    Convert hash to hexadecimal string
    """
    if isinstance(value, str):
        return value

    return hex(value)


def is_block_identifier(value: Union[int, Hash, Tag]) -> bool:
    return isinstance(value, str) and value in get_args(Tag)


def _invoke_tx_to_call(
    call: Optional[Call] = None, invoke_tx: Optional[Call] = None
) -> Call:
    if call is not None and invoke_tx is not None:
        raise ValueError("invoke_tx and call are mutually exclusive")

    if invoke_tx is not None:
        warnings.warn(
            "invoke_tx parameter is deprecated. Use call instead",
            category=DeprecationWarning,
        )
        call = invoke_tx

    if call is None:
        raise ValueError("Call is a required parameter")

    return call
