from typing import Union, Sequence

from starkware.cairo.common.hash_state import compute_hash_on_elements
from starkware.starknet.services.api.gateway.contract_address import (
    CONTRACT_ADDRESS_PREFIX,
)
from starkware.starknet.services.api.feeder_gateway.feeder_gateway_client import (
    BlockIdentifier,
)

from starknet_py.utils.crypto.facade import pedersen_hash
from starknet_py.utils.docs import as_our_module

AddressRepresentation = Union[int, str]
Address = int


def parse_address(value: AddressRepresentation) -> Address:
    if isinstance(value, int):
        return value

    try:
        return int(value, 16)
    except TypeError as t_err:
        raise TypeError("Invalid address format.") from t_err


def compute_address(
    contract_hash: int, constructor_calldata: Sequence[int], salt: int
) -> int:
    """
    Computes contract's address.

    :param contract_hash: int
    :param constructor_calldata: Sequence[int]
    :param salt: int
    :return: Contract's address
    """
    constructor_calldata_hash = compute_hash_on_elements(
        data=constructor_calldata, hash_func=pedersen_hash
    )
    caller_address = 0
    return compute_hash_on_elements(
        data=[
            CONTRACT_ADDRESS_PREFIX,
            caller_address,
            salt,
            contract_hash,
            constructor_calldata_hash,
        ],
        hash_func=pedersen_hash,
    )


BlockIdentifier = as_our_module(BlockIdentifier)
