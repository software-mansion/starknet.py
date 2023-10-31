from typing import Union

from typing_extensions import get_args

from starknet_py.hash.utils import encode_uint, encode_uint_list
from starknet_py.net.client_models import Hash, L1HandlerTransaction, Tag


def hash_to_felt(value: Hash) -> str:
    """
    Convert hash to hexadecimal string
    """
    if isinstance(value, str):
        return value

    return hex(value)


def is_block_identifier(value: Union[int, Hash, Tag]) -> bool:
    return isinstance(value, str) and value in get_args(Tag)


def encode_l1_message(tx: L1HandlerTransaction) -> bytes:
    # TODO (#1047): remove this assert once GatewayClient is deprecated and nonce is always required
    assert tx.nonce is not None

    from_address = tx.calldata[0]
    # Pop first element to have in calldata the actual payload
    tx.calldata.pop(0)

    return (
        encode_uint(from_address)
        + encode_uint(tx.contract_address)
        + encode_uint(tx.nonce)
        + encode_uint(tx.entry_point_selector)
        + encode_uint(len(tx.calldata))
        + encode_uint_list(tx.calldata)
    )
